from pydantic import BaseModel, Field, field_validator

from app.core.sanitize import clean_line, clean_text


class JobCreate(BaseModel):
    title: str = Field(min_length=2, max_length=150)
    company: str = Field(min_length=1, max_length=150)
    description: str = Field(min_length=10, max_length=10000)
    required_skills: str = Field(default="", max_length=2000)
    min_experience: float = Field(default=0, ge=0, le=50)

    # Stored as plain text (no HTML at all). The frontend escapes it when it draws it.
    @field_validator("title", "company")
    @classmethod
    def one_line(cls, v: str) -> str:
        v = clean_line(v)
        if not v:
            raise ValueError("This field cannot be empty")
        return v

    @field_validator("description")
    @classmethod
    def multi_line(cls, v: str) -> str:
        v = clean_text(v)
        if len(v) < 10:
            raise ValueError("Description must be at least 10 characters")
        return v

    @field_validator("required_skills")
    @classmethod
    def skills_line(cls, v: str) -> str:
        return clean_line(v)


class JobOut(BaseModel):
    id: int
    title: str
    company: str
    description: str
    required_skills: str | None = None
    min_experience: float

    model_config = {"from_attributes": True}
