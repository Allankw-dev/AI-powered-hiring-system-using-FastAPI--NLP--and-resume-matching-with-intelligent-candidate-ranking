"""Privacy and compliance features: consents, 18+, data export, account deletion, unsubscribe."""
import os

import pytest
from sqlalchemy import inspect

from app.core import security
from app.core.config import settings
from app.core.database import engine
from app.core.db_setup import ensure_tables
from app.core.legal import CONSENT_ADULT, CONSENT_TERMS_PRIVACY, LEGAL_VERSION
from app.models.application import Application
from app.models.consent import ConsentRecord
from app.models.email_log import EmailLog
from app.models.email_optout import EmailOptOut
from app.models.resume import Resume
from app.models.user import User
from app.services import email_service
from tests.conftest import CONSENT, PASSWORD, make_user
from tests.test_hiring_flow import create_job, upload_txt

SIGNUP = {"full_name": "Pat Doe", "email": "pat@example.com", "password": "Another1Pass"}


def _signup(client, **extra):
    return client.post("/auth/signup", json={**SIGNUP, **extra})


def _login(client, email, password=PASSWORD):
    r = client.post("/auth/login", json={"email": email, "password": password})
    return {"Authorization": f"Bearer {r.json()['access_token']}"} if r.status_code == 200 else None


# ───────────────────────── consents and age ─────────────────────────
def test_signup_needs_both_boxes_ticked(client, db):
    for payload in ({}, {"accepted_terms": True}, {"confirm_adult": True}, {"accepted_terms": False, "confirm_adult": True}):
        r = _signup(client, **payload)
        assert r.status_code == 422, payload
    assert "Terms" in str(_signup(client, confirm_adult=True).json())
    assert "18" in str(_signup(client, accepted_terms=True).json())
    assert db.query(User).filter(User.email == SIGNUP["email"]).first() is None  # nothing was created


def test_signup_stores_proof_of_consent_with_the_text_version(client, db):
    assert _signup(client, **CONSENT).status_code == 200
    user = db.query(User).filter(User.email == SIGNUP["email"]).one()
    rows = {c.kind: c for c in db.query(ConsentRecord).filter(ConsentRecord.user_id == user.id)}
    assert set(rows) == {CONSENT_TERMS_PRIVACY, CONSENT_ADULT}
    assert all(r.version == LEGAL_VERSION and r.accepted_at is not None for r in rows.values())


def test_duplicate_email_signup_leaves_no_orphan_consent_rows(client, db):
    assert _signup(client, **CONSENT).status_code == 200
    assert _signup(client, **CONSENT).status_code == 400
    assert db.query(ConsentRecord).count() == 2


# ───────────────────────── data export ─────────────────────────
def _full_account(client, db, admin_headers):
    """A candidate with a resume, an application and an email from an admin."""
    _signup(client, **CONSENT)
    headers = _login(client, SIGNUP["email"], SIGNUP["password"])
    job = create_job(client, admin_headers)
    rid = upload_txt(client, headers).json()["id"]
    app_id = client.post("/applications/", json={"job_id": job["id"], "resume_id": rid}, headers=headers).json()["application_id"]
    user = db.query(User).filter(User.email == SIGNUP["email"]).one()
    db.add(EmailLog(application_id=app_id, recipient_email=user.email, subject="Interview", message_body="Hello Pat", sent_by=1))
    db.commit()
    return headers, user, job, rid, app_id


def test_export_contains_my_data_but_no_secrets(client, db, admin_headers):
    headers, user, job, rid, app_id = _full_account(client, db, admin_headers)
    r = client.get("/users/me/export", headers=headers)
    assert r.status_code == 200 and "attachment" in r.headers["content-disposition"]
    data = r.json()
    assert data["profile"]["email"] == SIGNUP["email"]
    assert [x["id"] for x in data["resumes"]] == [rid] and data["resumes"][0]["text"]
    assert data["applications"][0]["id"] == app_id
    assert data["emails_received"][0]["subject"] == "Interview"
    assert {c["kind"] for c in data["consents"]} == {CONSENT_TERMS_PRIVACY, CONSENT_ADULT}
    blob = r.text.lower()
    for secret in ("password_hash", "$argon2", "otp", "reset_token"):
        assert secret not in blob


def test_export_never_includes_someone_elses_data(client, db, admin_headers, candidate_headers):
    _full_account(client, db, admin_headers)
    other = client.get("/users/me/export", headers=candidate_headers).json()  # cand@example.com
    assert other["resumes"] == [] and other["applications"] == [] and other["emails_received"] == []
    assert other["profile"]["email"] == "cand@example.com"


# ───────────────────────── account deletion ─────────────────────────
def test_delete_needs_the_right_password(client, db, admin_headers):
    headers, user, *_ = _full_account(client, db, admin_headers)
    r = client.request("DELETE", "/users/me", headers=headers, json={"password": "Wrong1Password"})
    assert r.status_code == 403 and "Incorrect password" in r.json()["detail"]  # NOT 401: that would sign the user out
    assert db.query(User).filter(User.id == user.id).first() is not None
    assert client.get("/users/me", headers=headers).status_code == 200  # and the session is still valid
    assert client.request("DELETE", "/users/me", headers=headers, json={}).status_code == 422


def test_delete_erases_everything_including_files(client, db, admin_headers):
    headers, user, job, rid, app_id = _full_account(client, db, admin_headers)
    pic = b"\x89PNG\r\n\x1a\n" + b"0" * 64
    assert client.post("/users/me/upload-picture", headers=headers, files={"file": ("a.png", pic, "image/png")}).status_code == 200
    db.expire_all()
    user = db.query(User).filter(User.email == SIGNUP["email"]).one()
    files = [r.file_path for r in db.query(Resume).filter(Resume.user_id == user.id)] + [user.profile_picture]
    assert files and all(os.path.isfile(f) for f in files)
    uid = user.id

    r = client.request("DELETE", "/users/me", headers=headers, json={"password": SIGNUP["password"]})
    assert r.status_code == 200, r.text
    db.expire_all()
    assert db.query(User).filter(User.id == uid).first() is None
    assert db.query(Resume).filter(Resume.user_id == uid).count() == 0
    assert db.query(Application).filter(Application.user_id == uid).count() == 0
    assert db.query(ConsentRecord).filter(ConsentRecord.user_id == uid).count() == 0
    assert db.query(EmailLog).filter(EmailLog.application_id == app_id).count() == 0
    assert not any(os.path.exists(f) for f in files)  # the CV and the picture are gone from disk
    # the old session is dead, the login fails, and the address can be used again
    assert client.get("/users/me", headers=headers).status_code == 401
    assert _login(client, SIGNUP["email"], SIGNUP["password"]) is None
    assert _signup(client, **CONSENT).status_code == 200


def test_delete_renumbers_the_other_candidates_ranking(client, db, admin_headers):
    job = create_job(client, admin_headers)
    users = []
    from tests.test_hiring_flow import CV
    for i, text in enumerate([CV, CV.replace("Python", "Java")]):
        u = make_user(db, f"c{i}@example.com", name="Cand " + "AB"[i])
        h = _login(client, u.email)
        rid = upload_txt(client, h, text=text).json()["id"]
        client.post("/applications/", json={"job_id": job["id"], "resume_id": rid}, headers=h)
        users.append((u, h))
    ranks = lambda: sorted(a.ranking_position for a in db.query(Application).all())  # noqa: E731
    db.expire_all()
    assert ranks() == [1, 2]
    first = users[0][1]
    assert client.request("DELETE", "/users/me", headers=first, json={"password": PASSWORD}).status_code == 200
    db.expire_all()
    assert ranks() == [1]  # no hole where the deleted candidate used to be


def test_admins_cannot_delete_themselves_through_the_api(client, db, admin_headers):
    r = client.request("DELETE", "/users/me", headers=admin_headers, json={"password": PASSWORD})
    assert r.status_code == 403
    assert db.query(User).filter(User.role == "admin").count() == 1


def test_wrong_passwords_on_the_delete_endpoint_count_towards_the_lockout(client, db):
    make_user(db, "del@example.com")
    h = _login(client, "del@example.com")
    codes = [client.request("DELETE", "/users/me", headers=h, json={"password": "Wrong1Password"}).status_code for _ in range(6)]
    assert codes[:5] == [403] * 5 and codes[5] == 429


# ───────────────────────── unsubscribe ─────────────────────────
def test_unsubscribe_token_works_only_for_unsubscribing():
    token = security.create_unsubscribe_token("a@b.co")
    assert security.decode_unsubscribe_token(token) == "a@b.co"
    # an ordinary login token is not an unsubscribe token...
    login_token = security.create_access_token({"user_id": 1, "pwv": "x"})
    assert security.decode_unsubscribe_token(login_token) is None
    # ...and an unsubscribe token is not a login token
    assert security.decode_token(token).get("user_id") is None
    assert security.decode_unsubscribe_token(token + "x") is None


def test_unsubscribe_link_opts_the_address_out_and_is_idempotent(client, db):
    token = security.create_unsubscribe_token("Pat@Example.com")
    for _ in range(2):
        r = client.post(f"/unsubscribe/{token}")
        assert r.status_code == 200 and r.json()["email"] == "pa***@example.com"
    assert [o.email for o in db.query(EmailOptOut)] == ["pat@example.com"]


def test_bad_unsubscribe_links_are_rejected(client, db, candidate_headers):
    assert client.post("/unsubscribe/not-a-token").status_code == 400
    login_token = candidate_headers["Authorization"].split()[1]
    assert client.post(f"/unsubscribe/{login_token}").status_code == 400  # a login token must not unsubscribe anyone
    assert db.query(EmailOptOut).count() == 0


def test_admin_cannot_email_someone_who_unsubscribed(client, db, admin_headers, candidate_headers, monkeypatch):
    sent = []
    monkeypatch.setattr("app.routers.admin.send_admin_email", lambda **kw: sent.append(kw))
    job = create_job(client, admin_headers)
    rid = upload_txt(client, candidate_headers).json()["id"]
    app_id = client.post("/applications/", json={"job_id": job["id"], "resume_id": rid}, headers=candidate_headers).json()["application_id"]
    body = {"application_id": app_id, "subject": "Hi", "message_body": "Hello"}
    assert client.post("/admin/send-email", headers=admin_headers, json=body).status_code == 200
    client.post(f"/unsubscribe/{security.create_unsubscribe_token('cand@example.com')}")
    r = client.post("/admin/send-email", headers=admin_headers, json=body)
    assert r.status_code == 409 and "unsubscribed" in r.json()["detail"]
    assert len(sent) == 1
    assert db.query(EmailLog).count() == 1  # nothing was logged for the blocked send


def test_candidate_emails_carry_an_unsubscribe_link_and_one_click_headers(monkeypatch):
    sent = {}
    monkeypatch.setattr(email_service, "send_email", lambda to, subject, body, headers=None: sent.update(body=body, headers=headers))
    monkeypatch.setattr(settings, "API_PUBLIC_URL", "https://api.example.com")
    monkeypatch.setattr(settings, "CONTACT_EMAIL", "privacy@example.com")
    email_service.send_admin_email("pat@example.com", "Interview", "See you <b>Monday</b>")
    assert "?unsubscribe=" in sent["body"] and "Unsubscribe from these emails" in sent["body"]
    assert "privacy@example.com" in sent["body"] and "Nairobi, Kenya" in sent["body"]
    assert "&lt;b&gt;" in sent["body"]  # still escaped
    h = sent["headers"]
    assert h["List-Unsubscribe"].startswith("<https://api.example.com/unsubscribe/") and h["List-Unsubscribe-Post"] == "List-Unsubscribe=One-Click"
    token = h["List-Unsubscribe"].split("/unsubscribe/")[1].rstrip(">")
    assert security.decode_unsubscribe_token(token) == "pat@example.com"


def test_security_emails_are_not_unsubscribable(monkeypatch):
    sent = []
    monkeypatch.setattr(email_service, "send_email", lambda to, subject, body, headers=None: sent.append(body))
    monkeypatch.setattr(email_service, "send_email_safely", lambda to, subject, body, headers=None: sent.append(body))
    email_service.send_otp_email("boss@example.com", "123456")
    email_service.send_reset_email("pat@example.com", "https://x.example/?reset_token=abc")
    assert len(sent) == 2
    for body in sent:
        assert "unsubscribe" in body.lower() and "cannot be unsubscribed from" in body
        assert "?unsubscribe=" not in body


def test_email_footer_text_is_readable_on_white():
    # #94a3b8 on white is only 2.5:1 - the footer must use a darker grey
    assert "#94a3b8" not in email_service._wrap("x")


# ───────────────────────── tables created by an update ─────────────────────────
def test_missing_tables_are_created_without_touching_existing_ones(db):
    EmailOptOut.__table__.drop(engine)
    ConsentRecord.__table__.drop(engine)
    assert "email_optouts" not in inspect(engine).get_table_names()
    created = ensure_tables()
    assert set(created) == {"email_optouts", "consent_records"}
    assert {"users", "resumes", "applications"} <= set(inspect(engine).get_table_names())
    assert ensure_tables() == []  # second run changes nothing


def test_rls_statements_only_name_the_given_tables():
    from app.core.db_setup import rls_statements
    stmts = rls_statements(["consent_records", "email_optouts"])
    assert stmts[0] == 'ALTER TABLE public."consent_records" ENABLE ROW LEVEL SECURITY;'
    assert "anon" in stmts[-1] and "users" not in " ".join(stmts)
