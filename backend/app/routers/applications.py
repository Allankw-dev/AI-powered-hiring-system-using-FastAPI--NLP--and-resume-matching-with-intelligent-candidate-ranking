from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.core.dep import get_current_user, get_db
from app.core.limiter import limiter
from app.models.application import Application
from app.models.job import Job
from app.models.resume import Resume
from app.schemas.application import ApplicationCreate
from app.services.ranking import apply_scores, loads_list, refresh_rankings, score_application

router = APIRouter(prefix="/applications", tags=["Applications"])


@router.post("/")
@limiter.limit("20/minute")
def apply_to_job(
    request: Request,
    payload: ApplicationCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    job = db.query(Job).filter(Job.id == payload.job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    resume = db.query(Resume).filter(Resume.id == payload.resume_id, Resume.user_id == current_user.id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    already = db.query(Application).filter(
        Application.user_id == current_user.id,
        Application.job_id == payload.job_id,
        Application.resume_id == payload.resume_id,
    ).first()
    if already:
        raise HTTPException(status_code=400, detail="You have already applied for this job with this resume")

    result = score_application(job, resume)

    application = Application(
        user_id=current_user.id,
        job_id=job.id,
        resume_id=resume.id,
        status="submitted",
    )
    apply_scores(application, result)
    db.add(application)
    db.flush()
    refresh_rankings(db, job.id)
    db.commit()
    db.refresh(application)

    return {
        "application_id": application.id,
        "job_id": job.id,
        "resume_id": resume.id,
        "overall_score": application.overall_score,
        "semantic_score": application.semantic_score,
        "skills_score": application.skills_score,
        "experience_score": application.experience_score,
        "verification_score": application.verification_score,
        "ai_score": application.ai_score,
        "status": application.status,
        "ranking_label": result["ranking_label"],
        "matched_skills": result["matched_skills"],
        "missing_skills": result["missing_skills"],
        "ranking_position": application.ranking_position,
    }


@router.get("/my")
def list_my_applications(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    rows = (
        db.query(Application)
        .filter(Application.user_id == current_user.id)
        .order_by(Application.id.desc())
        .all()
    )
    # Explicit fields: a candidate must not see how they rank against others.
    return [
        {
            "id": a.id,
            "job_id": a.job_id,
            "resume_id": a.resume_id,
            "status": a.status,
            "cover_letter": a.cover_letter,
            "overall_score": a.overall_score,
            "semantic_score": a.semantic_score,
            "skills_score": a.skills_score,
            "experience_score": a.experience_score,
            "verification_score": a.verification_score,
            "ai_score": a.ai_score,
            "matched_skills": loads_list(a.matched_skills),
            "missing_skills": loads_list(a.missing_skills),
            "applied_at": a.applied_at,
        }
        for a in rows
    ]
