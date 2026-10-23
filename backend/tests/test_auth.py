from datetime import timedelta

from app.core.timeutil import utcnow
from app.models.user import User
from tests.conftest import PASSWORD, make_user


def signup(client, email="new@example.com", password=PASSWORD, **extra):
    return client.post("/auth/signup", json={"full_name": "New Person", "email": email, "password": password, **extra})


def test_signup_and_login_candidate(client):
    assert signup(client).status_code == 200
    r = client.post("/auth/login", json={"email": "new@example.com", "password": PASSWORD})
    assert r.status_code == 200 and r.json()["role"] == "candidate"


def test_signup_never_creates_an_admin_even_with_old_sex_field(client, db, monkeypatch):
    monkeypatch.setenv("ADMIN_EMAILS", "boss@example.com")
    assert signup(client, email="boss@example.com", sex="Male").status_code == 200
    assert db.query(User).filter(User.email == "boss@example.com").one().role == "candidate"


def test_weak_passwords_rejected(client):
    for pw in ("short1A", "alllowercase1", "ALLUPPERCASE1", "NoNumbersHere"):
        assert signup(client, password=pw).status_code == 422


def test_wrong_password_and_unknown_user_look_identical(client, db):
    make_user(db, "a@example.com")
    r1 = client.post("/auth/login", json={"email": "a@example.com", "password": "WrongPass1"})
    r2 = client.post("/auth/login", json={"email": "nobody@example.com", "password": "WrongPass1"})
    assert r1.status_code == r2.status_code == 401 and r1.json() == r2.json()


def test_admin_cannot_bypass_2fa_with_password_login(client, db):
    make_user(db, "boss@example.com", role="admin")
    r = client.post("/auth/login", json={"email": "boss@example.com", "password": PASSWORD})
    assert r.status_code == 403 and "2FA" in r.json()["detail"]


def test_admin_otp_flow_works(client, db):
    admin = make_user(db, "boss@example.com", role="admin")
    assert client.post("/auth/admin/request-otp", json={"email": admin.email, "password": PASSWORD}).status_code == 200
    db.refresh(admin)
    assert len(admin.otp_code) == 6
    r = client.post("/auth/admin/verify-otp", json={"email": admin.email, "otp_code": admin.otp_code})
    assert r.status_code == 200 and r.json()["role"] == "admin"
    # code is single-use
    assert client.post("/auth/admin/verify-otp", json={"email": admin.email, "otp_code": admin.otp_code}).status_code == 400


def test_otp_request_requires_admin_and_password(client, db):
    make_user(db, "cand@example.com")
    assert client.post("/auth/admin/request-otp", json={"email": "cand@example.com", "password": PASSWORD}).status_code == 403
    make_user(db, "boss@example.com", role="admin")
    assert client.post("/auth/admin/request-otp", json={"email": "boss@example.com", "password": "WrongPass1"}).status_code == 401


def test_expired_otp_rejected(client, db):
    admin = make_user(db, "boss@example.com", role="admin")
    client.post("/auth/admin/request-otp", json={"email": admin.email, "password": PASSWORD})
    db.refresh(admin)
    admin.otp_expiry = utcnow() - timedelta(minutes=1)
    db.commit()
    assert client.post("/auth/admin/verify-otp", json={"email": admin.email, "otp_code": admin.otp_code}).status_code == 400


def test_otp_destroyed_after_five_wrong_guesses(client, db):
    admin = make_user(db, "boss@example.com", role="admin")
    client.post("/auth/admin/request-otp", json={"email": admin.email, "password": PASSWORD})
    db.refresh(admin)
    real = admin.otp_code
    wrong = "000000" if real != "000000" else "111111"
    for _ in range(5):
        assert client.post("/auth/admin/verify-otp", json={"email": admin.email, "otp_code": wrong}).status_code == 400
    # even the correct code no longer works
    assert client.post("/auth/admin/verify-otp", json={"email": admin.email, "otp_code": real}).status_code == 400


def test_otp_email_failure_returns_503_and_clears_code(client, db, monkeypatch):
    from app.core.config import settings
    monkeypatch.setattr(settings, "OTP_DELIVERY", "email")  # no provider configured -> EmailError
    admin = make_user(db, "boss@example.com", role="admin")
    r = client.post("/auth/admin/request-otp", json={"email": admin.email, "password": PASSWORD})
    assert r.status_code == 503
    db.refresh(admin)
    assert admin.otp_code is None


def test_password_reset_flow_hashes_token_and_enforces_strength(client, db, monkeypatch):
    sent = {}
    monkeypatch.setattr("app.routers.password_reset.send_reset_email", lambda email, link: sent.update(link=link))
    user = make_user(db, "cand@example.com")

    r = client.post("/password/forgot", json={"email": "cand@example.com"})
    assert r.status_code == 200
    token = sent["link"].split("reset_token=")[1]

    db.refresh(user)
    assert user.reset_token and user.reset_token != token  # only a hash is stored

    assert client.post("/password/reset", json={"token": token, "new_password": "weak"}).status_code == 422
    assert client.post("/password/reset", json={"token": "bogus", "new_password": "NewStr0ngPass"}).status_code == 400
    assert client.post("/password/reset", json={"token": token, "new_password": "NewStr0ngPass"}).status_code == 200
    # token is single-use, new password works
    assert client.post("/password/reset", json={"token": token, "new_password": "Another1Pass"}).status_code == 400
    assert client.post("/auth/login", json={"email": "cand@example.com", "password": "NewStr0ngPass"}).status_code == 200


def test_forgot_password_does_not_reveal_accounts_and_skips_admins(client, db, monkeypatch):
    sent = []
    monkeypatch.setattr("app.routers.password_reset.send_reset_email", lambda email, link: sent.append(email))
    make_user(db, "boss@example.com", role="admin")
    a = client.post("/password/forgot", json={"email": "boss@example.com"})
    b = client.post("/password/forgot", json={"email": "ghost@example.com"})
    assert a.json() == b.json() and sent == []


def test_rate_limit_returns_json_detail(client, db):
    from app.core.limiter import limiter
    limiter.enabled = True
    make_user(db, "a@example.com")
    codes = [client.post("/auth/login", json={"email": "a@example.com", "password": "WrongPass1"}).status_code for _ in range(7)]
    assert codes[:5] == [401] * 5 and 429 in codes[5:]
    r = client.post("/auth/login", json={"email": "a@example.com", "password": "WrongPass1"})
    assert r.status_code == 429 and "detail" in r.json()


def test_errors_never_leak_internals(client, monkeypatch, db):
    def boom(*a, **k):
        raise RuntimeError("secret internal detail")
    monkeypatch.setattr("app.routers.auth.hash_password", boom)
    r = client.post("/auth/signup", json={"full_name": "Boom Boom", "email": "boom@example.com", "password": PASSWORD})
    assert r.status_code == 500 and "secret" not in r.text
