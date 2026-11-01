from pydantic import BaseModel, Field, field_validator

from app.core.sanitize import clean_line, strip_controls


class CandidateEmailRequest(BaseModel):
    application_id: int = Field(gt=0)
    subject: str = Field(min_length=1, max_length=200)
    message_body: str = Field(min_length=1, max_length=5000)

    @field_validator("subject")
    @classmethod
    def subject_is_one_clean_line(cls, v: str) -> str:
        # Line breaks in a subject are how email header injection works ("Bcc: ...").
        v = clean_line(v)
        if not v:
            raise ValueError("Subject cannot be empty")
        return v

    @field_validator("message_body")
    @classmethod
    def body_has_no_control_chars(cls, v: str) -> str:
        v = strip_controls(v)
        if not v:
            raise ValueError("Message cannot be empty")
        return v
