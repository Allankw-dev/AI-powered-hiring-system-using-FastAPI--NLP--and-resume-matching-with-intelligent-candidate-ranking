import logging
import os
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from pydantic import BaseModel, EmailStr, field_validator
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.dep import get_current_user, get_db
from app.models.user import User

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/users", tags=["Users"])

_IMAGE_SIGNATURES = (
    (b"\xff\xd8\xff", "jpg"),
    (b"\x89PNG\r\n\x1a\n", "png"),
)


class ProfileUpdateRequest(BaseModel):
    full_name: str
    email: EmailStr

    @field_validator("full_name")
    @classmethod
    def name_valid(cls, v: str) -> str:
        v = v.strip()
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
        "profile_picture": user.profile_picture,
    }


@router.get("/me")
def get_my_profile(current_user: User = Depends(get_current_user)):
    return _profile(current_user)


@router.put("/me")
def update_my_profile(
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
def upload_profile_picture(
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

    return {"message": "Profile picture uploaded successfully", "path": file_path}
