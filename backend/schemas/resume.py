from typing import Optional

from pydantic import BaseModel, Field


class CandidateProfile(BaseModel):
    candidate_id: str
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    skills: list[str] = Field(default_factory=list)
    summary: str = ""
    education: str = ""
    experience: str = ""
    projects: str = ""
    certifications: str = ""
    achievements: str = ""
    languages: str = ""
    source_file: str
    extraction_method: str
