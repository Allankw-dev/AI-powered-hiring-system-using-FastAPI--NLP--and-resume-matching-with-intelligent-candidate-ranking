from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime, Text, Numeric
from sqlalchemy.sql import func
from app.core.database import Base


class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    cover_letter = Column(Text, nullable=True)
    status = Column(String(50), default="Pending")
    overall_score = Column(Numeric(5, 2), nullable=True)
    matched_skills = Column(Text, nullable=True)
    missing_skills = Column(Text, nullable=True)
    ranking_position = Column(Integer, nullable=True)
    applied_at = Column(DateTime, server_default=func.now())
    semantic_score = Column(Float, nullable=True)
    skills_score = Column(Float, nullable=True)
    experience_score = Column(Float, nullable=True)
    verification_score = Column(Float, nullable=True)
    ai_score = Column(Float, nullable=True)
    created_at = Column(DateTime, server_default=func.now())