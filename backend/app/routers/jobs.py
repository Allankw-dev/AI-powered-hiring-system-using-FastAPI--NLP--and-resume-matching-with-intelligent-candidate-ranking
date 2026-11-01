import logging

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from app.core.dep import get_current_user, get_db, require_admin
from app.core.limiter import limiter
from app.models.application import Application
from app.models.job import Job
from app.models.user import User
from app.schemas.job import JobCreate, JobOut

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/jobs", tags=["Jobs"])


# Input is cleaned by the JobCreate schema (no HTML, no control characters).
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=JobOut)
@limiter.limit("20/minute")
def create_job(
    request: Request,
    payload: JobCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    job = Job(**payload.model_dump(), created_by=current_user.id)
    db.add(job)
    db.commit()
    db.refresh(job)
    logger.info("AUDIT admin=%s created job=%s", current_user.id, job.id)
    return job


@router.get("/", response_model=list[JobOut])
def list_jobs(
    limit: int = Query(default=200, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(Job).order_by(Job.id.desc()).offset(offset).limit(limit).all()


@router.get("/{job_id}", response_model=JobOut)
def get_job(job_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return job


@router.put("/{job_id}", response_model=JobOut)
@limiter.limit("30/minute")
def update_job(
    request: Request,
    job_id: int,
    payload: JobCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    for field, value in payload.model_dump().items():
        setattr(job, field, value)

    db.commit()
    db.refresh(job)
    logger.info("AUDIT admin=%s updated job=%s", current_user.id, job.id)
    return job


@router.delete("/{job_id}")
@limiter.limit("20/minute")
def delete_job(
    request: Request, job_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_admin)
):
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
    logger.info("AUDIT admin=%s deleted job=%s", current_user.id, job_id)
    return {"message": "Job deleted successfully"}
