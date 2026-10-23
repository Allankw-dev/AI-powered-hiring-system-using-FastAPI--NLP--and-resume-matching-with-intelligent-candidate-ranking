import json
import logging
import os
import re
from io import BytesIO

import pdfplumber
from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.dep import get_current_user, get_db
from app.core.limiter import limiter
from app.models.application import Application
from app.models.resume import Resume
from app.services.ai_engine import estimate_experience, extract_skills
from app.services.resume_validator import check_fake_resume
from app.services.verifier import basic_resume_verification, file_checksum

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/resumes", tags=["Resumes"])

ALLOWED_EXTENSIONS = {".pdf", ".txt"}
MAX_PDF_PAGES = 15


def safe_display_name(filename: str | None) -> str:
    """Original file name made safe for display/storage (no paths, no control chars)."""
    name = os.path.basename((filename or "resume").replace("\\", "/"))
    name = re.sub(r"[^A-Za-z0-9._\- ()]", "_", name).strip(" .")
    return (name or "resume")[:150]


def extract_text_from_upload(ext: str, file_bytes: bytes) -> str:
    if ext == ".txt":
        return file_bytes.decode("utf-8", errors="ignore").strip()

    if not file_bytes.startswith(b"%PDF-"):
        raise HTTPException(status_code=400, detail="This file is not a valid PDF")
    try:
        parts = []
        with pdfplumber.open(BytesIO(file_bytes)) as pdf:
            for page in pdf.pages[:MAX_PDF_PAGES]:
                parts.append(page.extract_text() or "")
        return "\n".join(parts).strip()
    except Exception:  # pdfplumber/pdfminer raise many different errors on bad files
        logger.warning("Could not parse an uploaded PDF", exc_info=True)
        raise HTTPException(status_code=400, detail="Could not read this PDF. Try exporting it again.")


@router.post("/upload")
@limiter.limit("10/minute")
def upload_resume(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    display_name = safe_display_name(file.filename)
    ext = os.path.splitext(display_name)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Only .pdf and .txt files are supported")

    # Read at most limit+1 bytes so a huge upload cannot exhaust memory.
    file_bytes = file.file.read(settings.max_upload_bytes + 1)
    if len(file_bytes) > settings.max_upload_bytes:
        raise HTTPException(status_code=413, detail=f"File too large (max {settings.MAX_UPLOAD_MB} MB)")
    if not file_bytes:
        raise HTTPException(status_code=400, detail="The file is empty")

    checksum = file_checksum(file_bytes)

    if db.query(Resume).filter(Resume.user_id == current_user.id, Resume.checksum == checksum).first():
        raise HTTPException(status_code=400, detail="You have already uploaded this resume")

    parsed_text = extract_text_from_upload(ext, file_bytes)
    if not parsed_text:
        raise HTTPException(status_code=400, detail="No readable text found in this file (scanned image?)")

    experience_years = estimate_experience(parsed_text)
    skills = extract_skills(parsed_text)

    verification_status, flags, _score = basic_resume_verification(parsed_text)

    fake_flags = check_fake_resume(parsed_text)
    if fake_flags:
        flags.extend(fake_flags)
        verification_status = "flagged"

    # The same CV on two different accounts is a fraud signal: flag, don't block,
    # and never reveal whose account it is.
    if db.query(Resume).filter(Resume.user_id != current_user.id, Resume.checksum == checksum).first():
        flags.append("resume_used_by_another_account")
        if verification_status == "verified":
            verification_status = "pending"

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    save_path = os.path.join(settings.UPLOAD_DIR, f"{current_user.id}_{checksum[:16]}{ext}")
    with open(save_path, "wb") as out_file:
        out_file.write(file_bytes)

    resume = Resume(
        user_id=current_user.id,
        file_name=display_name,
        file_path=save_path,
        checksum=checksum,
        parsed_text=parsed_text,
        extracted_skills=json.dumps(skills),
        experience_years=experience_years,
        verification_status=verification_status,
        risk_flags=json.dumps(flags),
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)

    return {
        "id": resume.id,
        "file_name": resume.file_name,
        "experience_years": resume.experience_years,
        "verification_status": resume.verification_status,
        "risk_flags": flags,
        "skills": skills,
    }


@router.get("/my")
def list_my_resumes(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    resumes = db.query(Resume).filter(Resume.user_id == current_user.id).order_by(Resume.id.desc()).all()
    return [
        {
            "id": r.id,
            "file_name": r.file_name,
            "experience_years": r.experience_years,
            "verification_status": r.verification_status,
        }
        for r in resumes
    ]


@router.delete("/{resume_id}")
def delete_my_resume(resume_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == current_user.id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    if db.query(Application).filter(Application.resume_id == resume_id).first():
        raise HTTPException(status_code=409, detail="This resume was used in an application and cannot be deleted")

    path = resume.file_path
    db.delete(resume)
    db.commit()
    try:
        if path and os.path.isfile(path):
            os.remove(path)
    except OSError:
        logger.warning("Could not remove file %s", path)
    return {"message": "Resume deleted"}
