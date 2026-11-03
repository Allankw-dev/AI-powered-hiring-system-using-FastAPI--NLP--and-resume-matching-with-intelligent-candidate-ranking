import logging
import os
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, status
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, EmailStr, Field, field_validator
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.dep import get_current_user, get_db
from app.core.limiter import limiter
from app.core.sanitize import clean_line
from app.core.timeutil import utcnow
from app.models.application import Application
from app.models.consent import ConsentRecord
from app.models.email_log import EmailLog
from app.models.email_optout import EmailOptOut
from app.models.resume import Resume
from app.models.user import User
from app.routers.auth import check_credentials
from app.services.ranking import refresh_rankings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/users", tags=["Users"])

_IMAGE_SIGNATURES = (
    (b"\xff\xd8\xff", "jpg"),
    (b"\x89PNG\r\n\x1a\n", "png"),
)


class ProfileUpdateRequest(BaseModel):
    full_name: str = Field(max_length=300)
    email: EmailStr

    @field_validator("full_name")
    @classmethod
    def name_valid(cls, v: str) -> str:
        v = clean_line(v)  # no HTML, no control characters, single line
        if not 2 <= len(v) <= 255:
            raise ValueError("Full name must be between 2 and 255 characters")
        return v

    @field_validator("email")
    @classmethod
    def email_lower(cls, v: str) -> str:
        return v.strip().lower()


def _profile(user: User) -> dict:
    return {
        "id": user.id,
        "full_name": user.full_name,
        "email": user.email,
        "role": user.role,
        # Never expose the server-side file path, only whether a picture exists.
        "has_profile_picture": bool(user.profile_picture),
    }


@router.get("/me")
def get_my_profile(current_user: User = Depends(get_current_user)):
    return _profile(current_user)


@router.put("/me")
@limiter.limit("10/minute")
def update_my_profile(
    request: Request,
    payload: ProfileUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if db.query(User).filter(User.email == payload.email, User.id != current_user.id).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already in use")

    current_user.full_name = payload.full_name
    current_user.email = payload.email
    db.commit()
    db.refresh(current_user)

    return {"message": "Profile updated successfully", "user": _profile(current_user)}


@router.post("/me/upload-picture")
@limiter.limit("6/minute")
def upload_profile_picture(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    data = file.file.read(settings.max_picture_bytes + 1)
    if len(data) > settings.max_picture_bytes:
        raise HTTPException(status_code=413, detail=f"Image too large (max {settings.MAX_PICTURE_MB} MB)")

    # Trust the file's real signature, not the client-supplied name/content-type.
    ext = next((e for sig, e in _IMAGE_SIGNATURES if data.startswith(sig)), None)
    if ext is None:
        raise HTTPException(status_code=400, detail="Only JPG and PNG images are allowed.")

    upload_dir = os.path.join(settings.UPLOAD_DIR, "profile_pictures")
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, f"{uuid.uuid4()}.{ext}")
    with open(file_path, "wb") as buffer:
        buffer.write(data)

    old_path = current_user.profile_picture
    current_user.profile_picture = file_path
    db.commit()

    if old_path and os.path.isfile(old_path) and os.path.dirname(old_path) == upload_dir:
        try:
            os.remove(old_path)
        except OSError:
            logger.warning("Could not remove old profile picture")

    return {"message": "Profile picture uploaded successfully"}


@router.get("/me/picture")
@limiter.limit("60/minute")
def get_my_picture(request: Request, current_user: User = Depends(get_current_user)):
    """Streams the caller's OWN picture. There is no URL that serves anyone else's."""
    path = current_user.profile_picture
    upload_dir = os.path.realpath(os.path.join(settings.UPLOAD_DIR, "profile_pictures"))
    if not path or os.path.dirname(os.path.realpath(path)) != upload_dir or not os.path.isfile(path):
        raise HTTPException(status_code=404, detail="No profile picture")
    media = "image/png" if path.lower().endswith(".png") else "image/jpeg"
    return FileResponse(path, media_type=media, headers={"Cache-Control": "private, no-store"})


# ───────────────────────── your data: export and deletion ─────────────────────────
def _iso(value):
    return value.isoformat() if value else None


@router.get("/me/export")
@limiter.limit("5/hour")
def export_my_data(request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Everything we hold about the caller, as a JSON download (right of access / portability).
    Password hashes and one-time codes are deliberately left out."""
    resumes = db.query(Resume).filter(Resume.user_id == current_user.id).order_by(Resume.id).all()
    applications = db.query(Application).filter(Application.user_id == current_user.id).order_by(Application.id).all()
    app_ids = [a.id for a in applications]
    emails = (
        db.query(EmailLog).filter(EmailLog.application_id.in_(app_ids)).order_by(EmailLog.id).all() if app_ids else []
    )
    consents = db.query(ConsentRecord).filter(ConsentRecord.user_id == current_user.id).order_by(ConsentRecord.id).all()
    data = {
        "exported_at": _iso(utcnow()),
        "profile": {
            "id": current_user.id,
            "full_name": current_user.full_name,
            "email": current_user.email,
            "role": current_user.role,
            "created_at": _iso(current_user.created_at),
            "has_profile_picture": bool(current_user.profile_picture),
        },
        "resumes": [
            {
                "id": r.id, "file_name": r.file_name, "uploaded_at": _iso(r.created_at),
                "experience_years": r.experience_years, "extracted_skills": r.extracted_skills,
                "verification_status": r.verification_status, "risk_flags": r.risk_flags, "text": r.parsed_text,
            }
            for r in resumes
        ],
        "applications": [
            {
                "id": a.id, "job_id": a.job_id, "resume_id": a.resume_id, "status": a.status,
                "applied_at": _iso(a.applied_at), "overall_score": float(a.overall_score) if a.overall_score is not None else None,
                "text_similarity_score": a.semantic_score, "skills_score": a.skills_score,
                "experience_score": a.experience_score, "verification_score": a.verification_score,
                "matched_skills": a.matched_skills, "missing_skills": a.missing_skills, "ranking_position": a.ranking_position,
            }
            for a in applications
        ],
        "emails_received": [{"subject": e.subject, "message": e.message_body, "sent_at": _iso(e.sent_at)} for e in emails],
        "consents": [{"kind": c.kind, "version": c.version, "accepted_at": _iso(c.accepted_at)} for c in consents],
    }
    logger.info("User %s exported their data", current_user.id)
    return JSONResponse(data, headers={"Content-Disposition": 'attachment; filename="my-data.json"'})


class DeleteAccountRequest(BaseModel):
    password: str = Field(min_length=1, max_length=256)


def _remove_files(paths: list[str | None]) -> None:
    """Best-effort removal, and only ever inside the upload folder."""
    root = os.path.realpath(settings.UPLOAD_DIR)
    for path in paths:
        if not path:
            continue
        try:
            real = os.path.realpath(path)
            if real.startswith(root + os.sep) and os.path.isfile(real):
                os.remove(real)
        except OSError:
            logger.warning("Could not remove file %s", path)


@router.delete("/me")
@limiter.limit("5/hour")
def delete_my_account(
    request: Request,
    payload: DeleteAccountRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Permanently erase the caller's account and everything attached to it.

    Needs the password again (a stolen session alone cannot wipe an account) and goes through
    the same wrong-password lock-out as the login page.
    """
    if current_user.role == "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin accounts cannot be deleted here because they own job posts. Ask the site owner.",
        )
    try:
        user = check_credentials(request, db, current_user.email, payload.password)
    except HTTPException as exc:
        if exc.status_code == 401:
            # 401 means "your login is invalid" to clients (they sign the user out). The user IS logged in,
            # they just typed the wrong confirmation password, so answer 403.
            raise HTTPException(status_code=403, detail="Incorrect password. Nothing was deleted.") from None
        raise
    if user.id != current_user.id:  # cannot happen, but never delete the wrong account
        raise HTTPException(status_code=403, detail="Not allowed")

    user_id, email = user.id, user.email
    applications = db.query(Application).filter(Application.user_id == user_id).all()
    app_ids = [a.id for a in applications]
    job_ids = {a.job_id for a in applications}
    files = [r.file_path for r in db.query(Resume).filter(Resume.user_id == user_id).all()]
    files.append(user.profile_picture)

    # Children first, so foreign keys are never violated.
    if app_ids:
        db.query(EmailLog).filter(EmailLog.application_id.in_(app_ids)).delete(synchronize_session=False)
    db.query(Application).filter(Application.user_id == user_id).delete(synchronize_session=False)
    db.query(Resume).filter(Resume.user_id == user_id).delete(synchronize_session=False)
    db.query(ConsentRecord).filter(ConsentRecord.user_id == user_id).delete(synchronize_session=False)
    db.query(EmailOptOut).filter(EmailOptOut.email == email).delete(synchronize_session=False)
    db.delete(user)
    db.flush()
    for job_id in job_ids:  # other candidates' rank numbers must close the gap
        refresh_rankings(db, job_id)
    db.commit()

    _remove_files(files)
    logger.info("AUDIT user=%s deleted their account", user_id)
    return {"message": "Your account and all its data have been permanently deleted."}
