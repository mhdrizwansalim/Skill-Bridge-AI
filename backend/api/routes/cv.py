from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import Optional
from backend.config import PROJECT_ROOT
from backend.services.cv_service import generate_cv, load_profile

router = APIRouter(
    prefix="/cv",
    tags=["CV Builder"]
)

CV_PATH = (
    PROJECT_ROOT / "data" / "processed" /
    "cv_builder" / "skillbridge_generated_cv.pdf"
)


class CVProfileUpdate(BaseModel):
    name: str = Field(default="", max_length=150)
    email: str = Field(default="", max_length=150)
    phone: str = Field(default="", max_length=50)
    linkedin: str = Field(default="", max_length=300)
    github: str = Field(default="", max_length=300)
    summary: str = Field(default="", max_length=5000)
    skills: list[str] = Field(default_factory=list)
    education: str = Field(default="", max_length=10000)
    experience: str = Field(default="", max_length=10000)
    projects: str = Field(default="", max_length=10000)
    certifications: str = Field(default="", max_length=5000)
    achievements: str = Field(default="", max_length=5000)
    languages: str = Field(default="", max_length=3000)


@router.get("/profile")
def get_cv_profile():
    profile = load_profile()
    return {
        "status": "success",
        "candidate": profile,
    }


@router.post("/generate")
def generate_candidate_cv(profile: CVProfileUpdate):
    candidate = generate_cv(profile.model_dump())
    return {
        "status": "success",
        "candidate": candidate,
        "download_url": "/cv/download",
        "message": "CV generated from the provided profile data",
    }

@router.get("/download")
def download_cv():

    if not CV_PATH.exists():
        raise HTTPException(
            status_code=404,
            detail="Generated CV not found"
        )

    return FileResponse(
        path=CV_PATH,
        media_type="application/pdf",
        filename="SkillBridge_Generated_CV.pdf"
    )