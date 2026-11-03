import logging

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.dep import get_db
from app.core.limiter import limiter
from app.core.security import decode_unsubscribe_token
from app.models.email_optout import EmailOptOut
from app.routers.auth import mask_email

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Email"])


# Public on purpose: the link in an email must work without logging in. The token is signed,
# only ever unsubscribes the one address inside it, and cannot be used to log in.
# POST (not GET) so mail scanners that pre-fetch links cannot unsubscribe people by accident;
# it is also the method required by "one-click" unsubscribe (RFC 8058).
@router.post("/unsubscribe/{token}")
@limiter.limit("20/minute")
def unsubscribe(request: Request, token: str, db: Session = Depends(get_db)):
    email = decode_unsubscribe_token(token)
    if not email:
        raise HTTPException(status_code=400, detail="This unsubscribe link is invalid or has expired.")
    email = email.strip().lower()
    if not db.query(EmailOptOut).filter(EmailOptOut.email == email).first():
        db.add(EmailOptOut(email=email))
        try:
            db.commit()
        except IntegrityError:  # clicked twice at the same moment: already unsubscribed
            db.rollback()
    logger.info("Unsubscribed %s", mask_email(email))
    return {"message": "You have been unsubscribed and will not receive these emails any more.", "email": mask_email(email)}
