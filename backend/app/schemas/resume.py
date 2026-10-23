from pydantic import BaseModel


class ResumeOut(BaseModel):
    id: int
    file_name: str
    experience_years: float
    verification_status: str

    model_config = {"from_attributes": True}
