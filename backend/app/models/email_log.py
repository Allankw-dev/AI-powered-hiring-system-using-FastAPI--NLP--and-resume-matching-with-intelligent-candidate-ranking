from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.sql import func
from app.core.database import Base


class EmailLog(Base):
    __tablename__ = "email_logs"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id"), nullable=False)
    recipient_email = Column(String(120), nullable=False)
    subject = Column(String(255), nullable=False)
    message_body = Column(Text, nullable=False)
    sent_at = Column(DateTime, server_default=func.now())
    sent_by = Column(Integer, ForeignKey("users.id"), nullable=False)