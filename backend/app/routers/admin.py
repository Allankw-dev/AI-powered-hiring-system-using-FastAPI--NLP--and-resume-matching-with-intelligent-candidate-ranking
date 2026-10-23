from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from app.core.dep import get_db, require_admin
from app.core.limiter import client_ip, limiter
from app.models.application import Application
from app.models.email_log import EmailLog
from app.models.job import Job
from app.models.resume import Resume
from app.models.user import User
from app.schemas.admin import CandidateEmailRequest
from app.services.email_service import send_admin_email
from app.services.ranking import apply_scores, loads_list, refresh_rankings, score_application

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/top-candidates")
@limiter.limit("30/minute")
def top_candidates(
    request: Request,
    job_id: int | None = Query(default=None, description="Only this job"),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    query = (
        db.query(Application, User, Job)
        .join(User, Application.user_id == User.id)
        .join(Job, Application.job_id == Job.id)
    )
    if job_id is not None:
        query = query.filter(Application.job_id == job_id)

    rows = query.order_by(Application.overall_score.desc().nullslast(), Application.id.asc()).limit(limit).all()

    return [
        {
            "application_id": app_row.id,
            "job_id": job.id,
            "applicant_name": user.full_name,
            "applicant_email": user.email,
            "job_title": job.title,
            "company": job.company,
            "overall_score": float(app_row.overall_score or 0),
            "semantic_score": app_row.semantic_score,
            "skills_score": app_row.skills_score,
            "experience_score": app_row.experience_score,
            "verification_score": app_row.verification_score,
            "matched_skills": loads_list(app_row.matched_skills),
            "missing_skills": loads_list(app_row.missing_skills),
            "ranking_position": app_row.ranking_position,
            "status": app_row.status,
        }
        for app_row, user, job in rows
    ]


def _set_status(db: Session, application_id: int, new_status: str) -> None:
    application = db.query(Application).filter(Application.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    application.status = new_status
    db.commit()


@router.post("/applications/{application_id}/shortlist")
@limiter.limit("20/minute")
def shortlist_candidate(
    request: Request, application_id: int, db: Session = Depends(get_db), current_user=Depends(require_admin)
):
    _set_status(db, application_id, "shortlisted")
    return {"message": "Candidate shortlisted successfully"}


@router.post("/applications/{application_id}/reject")
@limiter.limit("20/minute")
def reject_candidate(
    request: Request, application_id: int, db: Session = Depends(get_db), current_user=Depends(require_admin)
):
    _set_status(db, application_id, "rejected")
    return {"message": "Candidate rejected successfully"}


@router.post("/send-email")
@limiter.limit("10/minute")
def send_email_to_candidate(
    request: Request,
    payload: CandidateEmailRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    application = db.query(Application).filter(Application.id == payload.application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    user = db.query(User).filter(User.id == application.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    background_tasks.add_task(
        send_admin_email,
        recipient_email=user.email,
        subject=payload.subject,
        message_body=payload.message_body,
    )

    db.add(EmailLog(
        application_id=application.id,
        recipient_email=user.email,
        subject=payload.subject,
        message_body=payload.message_body,
        sent_by=current_user.id,
    ))
    db.commit()

    return {"message": f"Email queued for {user.email}"}


@router.post("/jobs/{job_id}/rescore")
@limiter.limit("5/minute")
def rescore_job_applications(
    request: Request, job_id: int, db: Session = Depends(get_db), current_user=Depends(require_admin)
):
    """Re-run the matching for every application to this job (use after editing the job)."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    applications = db.query(Application).filter(Application.job_id == job_id).all()
    rescored = 0
    for application in applications:
        resume = db.query(Resume).filter(Resume.id == application.resume_id).first()
        if not resume:
            continue
        apply_scores(application, score_application(job, resume))
        rescored += 1

    db.flush()
    refresh_rankings(db, job_id)
    db.commit()
    return {"message": f"Re-scored {rescored} application(s)", "rescored": rescored}


@router.get("/client-ip")
def debug_client_ip(request: Request, current_user=Depends(require_admin)):
    """Shows which IP the rate limiter sees. If every visitor shows the same
    address, raise TRUSTED_PROXY_HOPS (e.g. to 2)."""
    return {
        "rate_limit_key": client_ip(request),
        "x_forwarded_for": request.headers.get("x-forwarded-for"),
        "socket_peer": request.client.host if request.client else None,
    }
