"""Shared helpers for scoring applications and keeping per-job rankings."""
import json

from sqlalchemy.orm import Session

from app.models.application import Application
from app.models.job import Job
from app.models.resume import Resume
from app.services.ai_engine import calculate_match
from app.services.verifier import basic_resume_verification


def score_application(job: Job, resume: Resume) -> dict:
    """Run verification + matching for one job/resume pair."""
    text = resume.parsed_text or ""
    _status, _flags, verification_score = basic_resume_verification(text)
    result = calculate_match(
        job_desc=job.description or "",
        resume_text=text,
        verification_score=verification_score,
        required_skills=job.required_skills,
        min_experience=job.min_experience,
        job_title=job.title or "",
    )
    return result


def apply_scores(application: Application, result: dict) -> None:
    application.ai_score = result["overall_score"]
    application.overall_score = result["overall_score"]
    application.semantic_score = result["semantic_score"]
    application.skills_score = result["skills_score"]
    application.experience_score = result["experience_score"]
    application.verification_score = result["verification_score"]
    application.matched_skills = json.dumps(result["matched_skills"])
    application.missing_skills = json.dumps(result["missing_skills"])


def refresh_rankings(db: Session, job_id: int) -> None:
    """Number the job's applications 1..n by overall score (best = 1). Caller commits."""
    rows = (
        db.query(Application)
        .filter(Application.job_id == job_id)
        .order_by(Application.overall_score.desc().nullslast(), Application.id.asc())
        .all()
    )
    for position, row in enumerate(rows, start=1):
        row.ranking_position = position


def loads_list(value: str | None) -> list:
    try:
        data = json.loads(value) if value else []
        return data if isinstance(data, list) else []
    except (TypeError, ValueError):
        return []
