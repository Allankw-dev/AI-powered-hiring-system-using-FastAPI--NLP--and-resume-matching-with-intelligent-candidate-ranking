import os
import tempfile

_TMP = tempfile.mkdtemp(prefix="hiring-tests-")
os.environ.update({
    "ENVIRONMENT": "test",
    "DATABASE_URL": f"sqlite:///{_TMP}/test.db",
    "SECRET_KEY": "test-secret-key-test-secret-key-0123456789",
    "UPLOAD_DIR": f"{_TMP}/uploads",
    "OTP_DELIVERY": "log",
    "RESEND_API_KEY": "",
    "ADMIN_EMAIL": "",
    "ADMIN_EMAIL_PASSWORD": "",
    "ANTHROPIC_API_KEY": "",
    "GEMINI_API_KEY": "",
})

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.core.database import Base, SessionLocal, engine  # noqa: E402
from app.core.limiter import limiter  # noqa: E402
from app.core.security import hash_password  # noqa: E402
from app.main import app  # noqa: E402
from app.models.user import User  # noqa: E402
from app.services import otp_service  # noqa: E402

PASSWORD = "Str0ngPass1"


@pytest.fixture(autouse=True)
def fresh_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    otp_service._failures.clear()
    limiter.enabled = False
    limiter.reset()
    yield


@pytest.fixture
def client():
    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture
def db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def make_user(db, email, role="candidate", password=PASSWORD, name="Test User"):
    user = User(full_name=name, email=email, password_hash=hash_password(password), role=role, is_active=True)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def candidate_headers(client, db):
    make_user(db, "cand@example.com")
    token = client.post("/auth/login", json={"email": "cand@example.com", "password": PASSWORD}).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_headers(client, db):
    admin = make_user(db, "boss@example.com", role="admin", name="The Boss")
    assert client.post("/auth/admin/request-otp", json={"email": admin.email, "password": PASSWORD}).status_code == 200
    db.refresh(admin)
    r = client.post("/auth/admin/verify-otp", json={"email": admin.email, "otp_code": admin.otp_code})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def minimal_pdf(text: str) -> bytes:
    """Hand-built single-page PDF containing ``text`` (no extra libraries needed)."""
    safe = text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    stream = f"BT /F1 12 Tf 50 750 Td ({safe}) Tj ET".encode()
    objs = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>",
        b"<< /Length %d >>\nstream\n" % len(stream) + stream + b"\nendstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    out, offsets = b"%PDF-1.4\n", []
    for i, body in enumerate(objs, start=1):
        offsets.append(len(out))
        out += f"{i} 0 obj\n".encode() + body + b"\nendobj\n"
    xref = len(out)
    out += f"xref\n0 {len(objs) + 1}\n0000000000 65535 f \n".encode()
    for off in offsets:
        out += f"{off:010d} 00000 n \n".encode()
    out += f"trailer\n<< /Size {len(objs) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode()
    return out
