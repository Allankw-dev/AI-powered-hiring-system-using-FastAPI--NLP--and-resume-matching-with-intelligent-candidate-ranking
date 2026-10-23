from pydantic import BaseModel, EmailStr, Field


class CandidateEmailRequest(BaseModel):
    application_id: int
    subject: str = Field(min_length=1, max_length=200)
    message_body: str = Field(min_length=1, max_length=5000)


class CandidateRankingOut(BaseModel):
    application_id: int
    applicant_name: str
    applicant_email: EmailStr
    job_title: str
    company: str
    overall_score: float
    semantic_score: float
    skills_score: float
    experience_score: float
    verification_score: float
    status: str