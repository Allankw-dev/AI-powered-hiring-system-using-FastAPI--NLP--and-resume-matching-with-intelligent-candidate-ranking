import bleach
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dep import get_current_user, get_db, require_admin
from app.models.application import Application
from app.models.job import Job
from app.models.user import User
from app.schemas.job import JobCreate

router = APIRouter(prefix="/jobs", tags=["Jobs"])


def sanitize(text: str | None) -> str | None:
    """Strip any HTML/script from admin input."""
    if not text:
        return text
    return bleach.clean(text.strip(), strip=True)


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_job(payload: JobCreate, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    job = Job(
        title=sanitize(payload.title),
        company=sanitize(payload.company),
        description=sanitize(payload.description),
        required_skills=sanitize(payload.required_skills),
        min_experience=payload.min_experience,
        created_by=current_user.id,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


@router.get("/")
def list_jobs(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Job).order_by(Job.id.desc()).all()


@router.get("/{job_id}")
def get_job(job_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return job


@router.put("/{job_id}")
def update_job(
    job_id: int,
    payload: JobCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    job.title = sanitize(payload.title)
    job.company = sanitize(payload.company)
    job.description = sanitize(payload.description)
    job.required_skills = sanitize(payload.required_skills)
    job.min_experience = payload.min_experience

    db.commit()
    db.refresh(job)
    return job


@router.delete("/{job_id}")
def delete_job(job_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    application_count = db.query(Application).filter(Application.job_id == job_id).count()
    if application_count:
        raise HTTPException(
            status_code=409,
            detail=f"This job has {application_count} application(s) and cannot be deleted. Reject them first or keep the job.",
        )

    db.delete(job)
    db.commit()
    return {"message": "Job deleted successfully"}
