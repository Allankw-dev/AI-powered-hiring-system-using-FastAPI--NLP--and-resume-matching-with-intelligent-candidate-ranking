"""Security regression tests: if any of these fail, something that protects users broke."""
import json
import logging
import ssl
import subprocess
import sys
from pathlib import Path

import bcrypt
import jwt
import pytest
from pydantic import ValidationError

from app.core import security
from app.core.config import Settings
from app.core.limiter import limiter
from app.main import app
from app.models.user import User
from tests.conftest import CONSENT, PASSWORD, make_user

BACKEND = Path(__file__).resolve().parents[1]

# Every endpoint that is allowed to be called without a token. Anything NOT listed
# here must reject anonymous callers. Adding a public route means adding it here on purpose.
PUBLIC = {
    ("GET", "/"), ("HEAD", "/"), ("GET", "/health"), ("HEAD", "/health"),
    ("POST", "/auth/signup"), ("POST", "/auth/login"),
    ("POST", "/auth/admin/request-otp"), ("POST", "/auth/admin/verify-otp"),
    ("POST", "/password/forgot"), ("POST", "/password/reset"),
    ("POST", "/chat"), ("POST", "/unsubscribe/{token}"),
}


def _routes():
    """Every (METHOD, path) the app exposes, read from the OpenAPI schema (independent of FastAPI internals)."""
    for path, operations in app.openapi()["paths"].items():
        for method in operations:
            if method.upper() in {"GET", "POST", "PUT", "DELETE", "PATCH"}:
                yield method.upper(), path


def _fill(path: str) -> str:
    return path.replace("{job_id}", "1").replace("{resume_id}", "1").replace("{application_id}", "1")


# ───────────────────────── access control ─────────────────────────
def test_every_non_public_route_rejects_anonymous_callers(client):
    checked = 0
    for method, path in _routes():
        if (method, path) in PUBLIC:
            continue
        r = client.request(method, _fill(path))
        assert r.status_code in (401, 403), f"{method} {path} answered {r.status_code} to an anonymous caller"
        checked += 1
    assert checked >= 20


def test_every_admin_route_rejects_candidates(client, candidate_headers):
    admin_only = [(m, p) for m, p in _routes() if p.startswith("/admin")]
    admin_only += [("POST", "/jobs/"), ("PUT", "/jobs/{job_id}"), ("DELETE", "/jobs/{job_id}")]
    assert len(admin_only) >= 7
    for method, path in admin_only:
        r = client.request(method, _fill(path), headers=candidate_headers, json={})
        assert r.status_code == 403, f"{method} {path} let a candidate in ({r.status_code})"


def test_admin_router_is_protected_at_router_level():
    from app.core.dep import require_admin
    from app.routers import admin
    assert any(d.dependency is require_admin for d in admin.router.dependencies)


def test_roles_come_from_the_database_not_from_the_token(client, db):
    user = make_user(db, "sneaky@example.com")
    token = jwt.encode(
        {"user_id": user.id, "role": "admin", "iss": security.TOKEN_ISSUER, "iat": 1, "exp": 4102444800,
         "pwv": security.password_fingerprint(user.password_hash)},
        security.settings.SECRET_KEY.get_secret_value(), algorithm="HS256",
    )
    r = client.get("/admin/top-candidates", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 403  # a correctly signed token still cannot grant a role


def test_users_cannot_touch_each_others_resumes(client, db, candidate_headers):
    from tests.conftest import minimal_pdf
    up = client.post("/resumes/upload", headers=candidate_headers,
                     files={"file": ("cv.pdf", minimal_pdf("Python developer 5 years experience email a@b.com"), "application/pdf")})
    assert up.status_code == 200, up.text
    other = make_user(db, "other@example.com")
    tok = client.post("/auth/login", json={"email": other.email, "password": PASSWORD}).json()["access_token"]
    assert client.delete(f"/resumes/{up.json()['id']}", headers={"Authorization": f"Bearer {tok}"}).status_code == 404
    assert client.get("/resumes/my", headers={"Authorization": f"Bearer {tok}"}).json() == []


def test_user_responses_never_contain_secrets(client, candidate_headers):
    me = client.get("/users/me", headers=candidate_headers).json()
    signup = client.post("/auth/signup", json={"full_name": "Pat Doe", "email": "pat@example.com", "password": "Another1Pass", **CONSENT}).json()
    for body in (me, signup):
        assert not {"password_hash", "otp_code", "otp_expiry", "reset_token", "profile_picture"} & set(body)


# ───────────────────────── authentication / tokens ─────────────────────────
def test_tampered_none_expired_and_unsigned_tokens_are_rejected(client, candidate_headers):
    good = candidate_headers["Authorization"].split()[1]
    key = security.settings.SECRET_KEY.get_secret_value()
    claims = jwt.decode(good, key, algorithms=["HS256"], options={"verify_exp": False})
    bad_tokens = [
        good[:-3] + ("AAA" if not good.endswith("AAA") else "BBB"),            # signature tampered
        jwt.encode(claims, "", algorithm="none"),                              # alg=none
        jwt.encode({**claims, "exp": 1}, key, algorithm="HS256"),              # expired
        jwt.encode(claims, "wrong-key-wrong-key-wrong-key-123456", algorithm="HS256"),
        jwt.encode({**claims, "iss": "someone-else"}, key, algorithm="HS256"),
        jwt.encode({k: v for k, v in claims.items() if k != "exp"}, key, algorithm="HS256"),
        jwt.encode({k: v for k, v in claims.items() if k != "pwv"}, key, algorithm="HS256"),  # no password binding
        "not.a.jwt", "",
    ]
    for tok in bad_tokens:
        r = client.get("/users/me", headers={"Authorization": f"Bearer {tok}"})
        assert r.status_code in (401, 403), f"accepted bad token {tok[:25]!r}"
    assert client.get("/users/me", headers=candidate_headers).status_code == 200


def test_password_reset_signs_out_existing_sessions(client, db, candidate_headers, monkeypatch):
    assert client.get("/users/me", headers=candidate_headers).status_code == 200
    user = db.query(User).filter(User.email == "cand@example.com").one()
    user.password_hash = security.hash_password("BrandNew1Pass")  # what /password/reset does
    db.commit()
    r = client.get("/users/me", headers=candidate_headers)
    assert r.status_code == 401 and "sign in again" in r.json()["detail"].lower()


def test_disabled_account_token_stops_working(client, db, candidate_headers):
    user = db.query(User).filter(User.email == "cand@example.com").one()
    user.is_active = False
    db.commit()
    assert client.get("/users/me", headers=candidate_headers).status_code == 401


# ───────────────────────── password hashing ─────────────────────────
def test_signup_stores_argon2id_never_plaintext(client, db):
    client.post("/auth/signup", json={"full_name": "Pat Doe", "email": "pat@example.com", "password": "Another1Pass", **CONSENT})
    stored = db.query(User).filter(User.email == "pat@example.com").one().password_hash
    assert stored.startswith("$argon2id$") and "Another1Pass" not in stored


def test_legacy_bcrypt_hash_is_upgraded_on_login_and_still_works(client, db):
    user = make_user(db, "legacy@example.com")
    user.password_hash = bcrypt.hashpw(PASSWORD.encode(), bcrypt.gensalt(4)).decode()
    db.commit()
    r = client.post("/auth/login", json={"email": "legacy@example.com", "password": PASSWORD})
    assert r.status_code == 200
    db.expire_all()
    assert db.query(User).filter(User.email == "legacy@example.com").one().password_hash.startswith("$argon2id$")
    # the fresh token is bound to the NEW hash, so it keeps working
    assert client.get("/users/me", headers={"Authorization": f"Bearer {r.json()['access_token']}"}).status_code == 200
    # and the password still works afterwards
    assert client.post("/auth/login", json={"email": "legacy@example.com", "password": PASSWORD}).status_code == 200


@pytest.mark.parametrize("pw", ["Password1", "Qwerty123", "Welcome1", "ALLUPPER1", "alllower1", "NoNumbersHere", "Sh0rt"])
def test_weak_and_common_passwords_are_refused(client, pw):
    r = client.post("/auth/signup", json={"full_name": "Pat Doe", "email": "pat@example.com", "password": pw, **CONSENT})
    assert r.status_code == 422


# ───────────────────────── brute-force protection ─────────────────────────
def _login(client, email, password, ip="198.51.100.7"):
    # TRUSTED_PROXY_HOPS=1 -> the last X-Forwarded-For entry is the visitor
    return client.post("/auth/login", json={"email": email, "password": password}, headers={"x-forwarded-for": ip})


def test_repeated_wrong_passwords_lock_the_login_for_that_ip_only(client, db):
    make_user(db, "victim@example.com")
    for _ in range(5):
        assert _login(client, "victim@example.com", "Wrong1Pass").status_code == 401
    locked = _login(client, "victim@example.com", PASSWORD)  # even the RIGHT password is refused while locked
    assert locked.status_code == 429 and "Retry-After" in locked.headers
    # the real owner on another connection is not locked out by the attacker
    assert _login(client, "victim@example.com", PASSWORD, ip="203.0.113.50").status_code == 200


def test_lockout_applies_to_unknown_emails_too_so_it_leaks_nothing(client):
    codes = [_login(client, "ghost@example.com", "Wrong1Pass").status_code for _ in range(6)]
    assert codes == [401] * 5 + [429]


def test_botnet_rotating_ips_is_stopped_by_the_per_account_limit(client, db):
    make_user(db, "target@example.com")
    codes = [_login(client, "target@example.com", "Wrong1Pass", ip=f"192.0.2.{i}").status_code for i in range(1, 25)]
    assert 429 in codes  # more than 4x the per-IP limit of failures across IPs locks the account


def test_admin_otp_request_is_also_throttled(client, db):
    make_user(db, "boss2@example.com", role="admin")
    for _ in range(5):
        client.post("/auth/admin/request-otp", json={"email": "boss2@example.com", "password": "Wrong1Pass"})
    assert client.post("/auth/admin/request-otp", json={"email": "boss2@example.com", "password": PASSWORD}).status_code == 429


def test_global_rate_limit_applies_to_routes_without_their_own(client):
    limiter.enabled = True
    limiter.reset()
    try:
        codes = [client.get("/health").status_code for _ in range(130)]
        assert 429 in codes and codes[0] == 200
    finally:
        limiter.enabled = False
        limiter.reset()


def test_chat_has_a_per_visitor_daily_allowance(monkeypatch):
    from app.services import chat_service
    monkeypatch.setattr(chat_service.settings, "CHAT_PER_IP_DAILY_LIMIT", 2)
    chat_service._usage["count"] = 0
    chat_service._take_daily_slot("1.1.1.1"); chat_service._take_daily_slot("1.1.1.1")
    with pytest.raises(chat_service.ChatLimitReached):
        chat_service._take_daily_slot("1.1.1.1")
    chat_service._take_daily_slot("2.2.2.2")  # a different visitor is unaffected


# ───────────────────────── headers / CORS / docs / debug ─────────────────────────
def test_error_and_preflight_responses_also_carry_security_headers(client, monkeypatch):
    r404 = client.get("/does-not-exist")
    assert r404.status_code == 404 and r404.headers["x-content-type-options"] == "nosniff"
    pre = client.options("/auth/login", headers={
        "Origin": "https://ai-powered-hiring-system.streamlit.app",
        "Access-Control-Request-Method": "POST", "Access-Control-Request-Headers": "authorization,content-type"})
    assert pre.status_code == 200 and pre.headers["x-frame-options"] == "DENY"
    evil = client.options("/auth/login", headers={"Origin": "https://evil.example", "Access-Control-Request-Method": "POST"})
    assert "access-control-allow-origin" not in evil.headers


def test_unhandled_errors_return_no_details_but_keep_headers(db, monkeypatch):
    from fastapi.testclient import TestClient
    from app.core import dep

    def boom():
        raise RuntimeError("secret-internal-detail postgres://u:pw@host/db")
    app.dependency_overrides[dep.get_db] = boom
    try:
        r = TestClient(app, raise_server_exceptions=False).get("/jobs/", headers={"Authorization": "Bearer x"})
        r2 = TestClient(app, raise_server_exceptions=False).post("/auth/login", json={"email": "a@b.co", "password": "x"})
    finally:
        app.dependency_overrides.clear()
    assert r2.status_code == 500 and r2.json() == {"detail": "Internal server error"}
    assert "secret-internal-detail" not in r2.text and r2.headers["x-content-type-options"] == "nosniff"


def test_hsts_only_in_production(client, monkeypatch):
    assert "strict-transport-security" not in client.get("/health").headers
    monkeypatch.setattr(security.settings, "ENVIRONMENT", "production")
    assert "max-age=31536000" in client.get("/health").headers["strict-transport-security"]


def test_docs_are_off_in_production_and_debug_is_off():
    assert Settings(ENVIRONMENT="production", SECRET_KEY="k" * 40, DATABASE_URL="sqlite://").docs_enabled is False
    assert Settings(ENVIRONMENT="production", SECRET_KEY="k" * 40, DATABASE_URL="sqlite://", ENABLE_DOCS=True).docs_enabled is True
    assert Settings(ENVIRONMENT="test", SECRET_KEY="k" * 40, DATABASE_URL="sqlite://").docs_enabled is True
    assert app.debug is False
    code = (
        "from fastapi.testclient import TestClient\nfrom app.main import app\nc = TestClient(app)\n"
        "print([c.get(p).status_code for p in ('/docs', '/redoc', '/openapi.json')])"
    )
    env = {"ENVIRONMENT": "production", "SECRET_KEY": "k" * 40, "DATABASE_URL": "sqlite:///:memory:", "PATH": "/usr/bin:/bin"}
    out = subprocess.run([sys.executable, "-c", code], cwd=BACKEND, env=env, capture_output=True, text=True, timeout=120)
    assert out.stdout.strip() == "[404, 404, 404]", out.stderr[-500:]


def test_cors_default_is_only_the_frontend_and_never_wildcard_credentials():
    prod = Settings(ENVIRONMENT="production", SECRET_KEY="k" * 40, DATABASE_URL="sqlite://", FRONTEND_URL="https://app.example.com/")
    assert prod.cors_origin_list == ["https://app.example.com"]
    dev = Settings(ENVIRONMENT="test", SECRET_KEY="k" * 40, DATABASE_URL="sqlite://", FRONTEND_URL="https://app.example.com")
    assert "http://localhost:8501" in dev.cors_origin_list and "*" not in dev.cors_origin_list
    explicit = Settings(ENVIRONMENT="production", SECRET_KEY="k" * 40, DATABASE_URL="sqlite://", CORS_ORIGINS="https://a.io, https://b.io/")
    assert explicit.cors_origin_list == ["https://a.io", "https://b.io"]


# ───────────────────────── request size limits ─────────────────────────
def test_oversized_json_body_is_rejected_before_it_is_read(client):
    huge = {"message": "x" * 300_000, "history": []}
    r = client.post("/chat", json=huge)
    assert r.status_code == 413 and r.json() == {"detail": "Request body too large"}


def test_oversized_chunked_body_without_content_length_is_rejected(client):
    def chunks():
        for _ in range(40):
            yield b"a" * 10_000
    r = client.post("/auth/login", content=chunks(), headers={"content-type": "application/json"})
    assert r.status_code == 413


def test_upload_limit_is_larger_but_still_bounded(client, candidate_headers):
    r = client.post("/resumes/upload", headers=candidate_headers, files={"file": ("a.txt", b"a" * (8 * 1024 * 1024), "text/plain")})
    assert r.status_code == 413


# ───────────────────────── XSS / form sanitising ─────────────────────────
XSS = '<script>alert(1)</script><img src=x onerror=alert(1)><a href="javascript:alert(1)">click</a>'


def test_signup_name_is_stripped_of_html_and_control_chars(client, db):
    r = client.post("/auth/signup", json={"full_name": "<b>Eve</b> \u202eLee\x00 <script>x</script>", "email": "eve@example.com", "password": "Another1Pass", **CONSENT})
    assert r.status_code == 200
    name = r.json()["full_name"]
    assert "<" not in name and ">" not in name and "\x00" not in name and "\u202e" not in name


def test_profile_update_strips_html(client, candidate_headers):
    r = client.put("/users/me", headers=candidate_headers, json={"full_name": "<img src=x onerror=alert(1)>Mallory", "email": "cand@example.com"})
    assert r.status_code == 200 and r.json()["user"]["full_name"] == "Mallory"


def test_job_fields_are_stored_as_plain_text(client, admin_headers):
    r = client.post("/jobs/", headers=admin_headers, json={
        "title": f"Dev {XSS}", "company": f"ACME {XSS}", "description": f"Great role. {XSS} Apply now.", "required_skills": f"python, {XSS}"})
    assert r.status_code == 201, r.text
    stored = json.dumps(r.json())
    for needle in ("<script", "<img", "<a ", "onerror=", "href="):
        assert needle not in stored


def test_email_subject_cannot_inject_headers(client, admin_headers, candidate_headers, monkeypatch):
    from tests.test_hiring_flow import create_job, upload_txt
    sent = []
    monkeypatch.setattr("app.routers.admin.send_admin_email", lambda **kw: sent.append(kw))
    job = create_job(client, admin_headers)
    rid = upload_txt(client, candidate_headers).json()["id"]
    app_id = client.post("/applications/", json={"job_id": job["id"], "resume_id": rid}, headers=candidate_headers).json()["application_id"]
    r = client.post("/admin/send-email", headers=admin_headers,
                    json={"application_id": app_id, "subject": "Hello\r\nBcc: attacker@evil.com", "message_body": "Hi\x00 there"})
    assert r.status_code == 200
    assert "\n" not in sent[0]["subject"] and "\r" not in sent[0]["subject"]
    assert "\x00" not in sent[0]["message_body"]


def test_smtp_connection_verifies_the_server_certificate(monkeypatch):
    from pydantic import SecretStr
    from app.services import email_service
    seen = {}

    class FakeSMTP:
        def __init__(self, *a, **kw): seen["init"] = kw
        def ehlo(self): pass
        def starttls(self, **kw): seen["tls"] = kw
        def __enter__(self): return self
        def __exit__(self, *a): return False
        def login(self, *a): pass
        def sendmail(self, *a): seen["msg"] = a[2]

    monkeypatch.setattr(email_service.smtplib, "SMTP", FakeSMTP)
    monkeypatch.setattr(email_service.settings, "ADMIN_EMAIL", "me@example.com")
    monkeypatch.setattr(email_service.settings, "ADMIN_EMAIL_PASSWORD", SecretStr("app-password"))
    email_service._send_smtp("to@example.com", "Hi\nBcc: x@evil.com", "<p>hi</p>")
    ctx = seen["tls"]["context"]
    assert ctx.verify_mode == ssl.CERT_REQUIRED and ctx.check_hostname is True
    assert "Bcc: x@evil.com\n" not in seen["msg"].replace("Subject: Hi Bcc: x@evil.com", "")


# ───────────────────────── secrets / environment ─────────────────────────
def test_secrets_never_appear_in_repr_or_logs(caplog):
    s = Settings(ENVIRONMENT="test", SECRET_KEY="super-secret-key-" + "k" * 30, DATABASE_URL="postgres://u:hunter2pass@h/db",
                 ANTHROPIC_API_KEY="sk-ant-REALKEY123", GEMINI_API_KEY="AIzaREALKEY456", RESEND_API_KEY="re_REALKEY789",
                 ADMIN_EMAIL_PASSWORD="smtp-pass-123")
    text = repr(s) + str(s) + json.dumps(s.model_dump(mode="json"))
    for secret in ("super-secret-key", "hunter2pass", "REALKEY123", "REALKEY456", "REALKEY789", "smtp-pass-123"):
        assert secret not in text, f"{secret} leaked"
    assert s.email_configured and s.DATABASE_URL.get_secret_value().startswith("postgresql+psycopg2://")


@pytest.mark.parametrize("bad", [
    dict(SECRET_KEY="short"), dict(SECRET_KEY="changeme"), dict(ALGORITHM="none"), dict(ALGORITHM="RS256"),
    dict(ACCESS_TOKEN_EXPIRE_MINUTES=0), dict(ACCESS_TOKEN_EXPIRE_MINUTES=100000), dict(ENVIRONMENT="prodd"),
    dict(DB_SSLMODE="maybe"), dict(TRUSTED_PROXY_HOPS=-1), dict(MAX_UPLOAD_MB=500), dict(OTP_DELIVERY="sms"),
    dict(DATABASE_URL=""),
])
def test_production_refuses_unsafe_or_nonsense_settings(bad):
    base = dict(ENVIRONMENT="production", SECRET_KEY="k" * 40, DATABASE_URL="sqlite://")
    with pytest.raises(ValidationError):
        Settings(**{**base, **bad})


def test_no_secrets_are_committed_in_the_current_files():
    out = subprocess.run([sys.executable, "-m", "scripts.scan_secrets"], cwd=BACKEND, capture_output=True, text=True, timeout=120)
    assert out.returncode == 0, out.stdout


def test_the_secret_scanner_actually_catches_secrets():
    from scripts.scan_secrets import scan_text
    fake = (
        'DATABASE_URL = "postgresql://postgres:Sup3rS3cretPw@db.abc.supabase.co:5432/postgres"\n'
        "key = " + "sk-ant-" + "api03-" + "A" * 24 + "\n"  # assembled at runtime so this file itself holds no key-shaped text
        'SECRET_KEY = "a-very-long-hardcoded-secret-value-1234"\n'
    )
    kinds = " ".join(scan_text(fake, "app/x.py"))
    assert "database URL" in kinds and "Anthropic" in kinds and "hard-coded secret" in kinds
    assert scan_text("postgres://u:p@h/db", "app/x.py") == []  # placeholders are fine


def test_uploaded_and_secret_files_are_not_tracked_by_git():
    repo = BACKEND.parent
    if not (repo / ".git").exists():
        pytest.skip("not a git checkout")
    tracked = subprocess.run(["git", "ls-files"], cwd=repo, capture_output=True, text=True).stdout.splitlines()
    bad = [f for f in tracked if f.endswith((".env", ".db", ".sqlite3", ".pem", ".key")) or "/uploads/" in f or f.startswith("uploads/")
           or f.endswith("secrets.toml")]
    assert bad == []


def test_no_route_serves_uploaded_files_statically():
    assert not any("static" in p or p.startswith("/uploads") for _, p in _routes())
    assert not [r for r in app.routes if r.__class__.__name__ == "Mount"]  # no StaticFiles mounted anywhere
