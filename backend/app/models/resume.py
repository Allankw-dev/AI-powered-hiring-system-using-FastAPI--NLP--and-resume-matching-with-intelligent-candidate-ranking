from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime, Text
from sqlalchemy.sql import func
from app.core.database import Base


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    checksum = Column(String(255), nullable=False)
    parsed_text = Column(Text, nullable=False)
    extracted_skills = Column(Text, nullable=True)
    experience_years = Column(Float, default=0)
    verification_status = Column(String(50), default="pending")
    risk_flags = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())