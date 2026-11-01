import logging
import os
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, status
from fastapi.responses import FileResponse
from pydantic import BaseModel, EmailStr, Field, field_validator
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.dep import get_current_user, get_db
from app.core.limiter import limiter
from app.core.sanitize import clean_line
from app.models.user import User

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
