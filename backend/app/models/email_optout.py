from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.sql import func

from app.core.database import Base


class EmailOptOut(Base):
    """Addresses that unsubscribed from application emails sent by admins."""

    __tablename__ = "email_optouts"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())
