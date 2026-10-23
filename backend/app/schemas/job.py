from pydantic import BaseModel, Field


class JobCreate(BaseModel):
    title: str = Field(min_length=2, max_length=150)
    company: str = Field(min_length=1, max_length=150)
    description: str = Field(min_length=10, max_length=10000)
    required_skills: str = Field(default="", max_length=2000)
    min_experience: float = Field(default=0, ge=0, le=50)


class JobOut(BaseModel):
    id: int
    title: str
    company: str
    description: str
    required_skills: str | None = None
    min_experience: float

    model_config = {"from_attributes": True}
