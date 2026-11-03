from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.sql import func

from app.core.database import Base


class ConsentRecord(Base):
    """Proof of what a user agreed to, and when. No IP address is stored (data minimisation)."""

    __tablename__ = "consent_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    kind = Column(String(40), nullable=False)      # terms_and_privacy | age_18_plus
    version = Column(String(20), nullable=False)   # app.core.legal.LEGAL_VERSION at the time
    accepted_at = Column(DateTime, server_default=func.now())
