
import json

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

from backend.database import SessionLocal
from backend.models.candidate import Candidate

from backend.config import CV_PATH


# --------------------------------------------------
# ROUTER CONFIGURATION
# --------------------------------------------------

router = APIRouter(
    prefix="/candidate",
    tags=["Candidate"]
)

RESUME_LIBRARY = CV_PATH / "resume_library"


class CandidateProfileUpdate(BaseModel):
    name: Optional[str] = Field(default=None, max_length=150)
    email: Optional[str] = Field(default=None, max_length=150)
    phone: Optional[str] = Field(default=None, max_length=50)
    linkedin: Optional[str] = Field(default=None, max_length=300)
    github: Optional[str] = Field(default=None, max_length=300)
    summary: Optional[str] = Field(default=None, max_length=5000)
    skills: Optional[list[str]] = Field(default=None)
    education: Optional[str] = Field(default=None, max_length=10000)
    experience: Optional[str] = Field(default=None, max_length=10000)
    projects: Optional[str] = Field(default=None, max_length=10000)
    certifications: Optional[str] = Field(default=None, max_length=5000)
    languages: Optional[str] = Field(default=None, max_length=3000)


# --------------------------------------------------
# 1. LIST ALL SAVED CANDIDATE RESUMES
# --------------------------------------------------

@router.get("/resumes")
def list_candidate_resumes():

    # Create the resume library folder if it does not exist.
    RESUME_LIBRARY.mkdir(parents=True, exist_ok=True)

    profiles = []

    # Read every saved candidate JSON profile.
    for path in sorted(RESUME_LIBRARY.glob("*.json")):

        try:
            with open(path, "r", encoding="utf-8") as file:
                profile = json.load(file)

            # Support both old and new profile formats.
            # Old format: personal_details.full_name
            # New format: name
            personal = profile.get("personal_details") or {}

            candidate_name = (
                personal.get("full_name")
                or profile.get("name")
                or profile.get("full_name")
                or "Unknown"
            )

            candidate_email = (
                personal.get("email")
                or profile.get("email")
                or ""
            )

            # Add candidate information to the response.
            profiles.append({
                "resume_id": path.stem,
                "candidate_name": candidate_name,
                "email": candidate_email,
                "file_name": path.name
            })

        except (OSError, json.JSONDecodeError):
            # Skip files that cannot be read or contain invalid JSON.
            continue

    return {
        "status": "success",
        "resumes": profiles,
        "total": len(profiles)
    }


# --------------------------------------------------
# 2. GET A SPECIFIC CANDIDATE PROFILE
# --------------------------------------------------

@router.get("/profile")
def get_candidate_profile(resume_id: str = None):

    # Ensure the resume library exists.
    RESUME_LIBRARY.mkdir(parents=True, exist_ok=True)

    # If a resume ID is provided, load that candidate.
    if resume_id:

        # Prevent directory traversal.
        if (
            "/" in resume_id
            or "\\" in resume_id
            or resume_id in {".", ".."}
        ):
            raise HTTPException(
                status_code=400,
                detail="Invalid resume ID"
            )

        profile_path = RESUME_LIBRARY / f"{resume_id}.json"

        if not profile_path.exists():
            raise HTTPException(
                status_code=404,
                detail="Requested resume not found"
            )

    else:

        # Otherwise, select the most recently updated profile.
        saved_profiles = sorted(
            RESUME_LIBRARY.glob("*.json"),
            key=lambda path: path.stat().st_mtime,
            reverse=True
        )

        if saved_profiles:
            profile_path = saved_profiles[0]
        else:
            # Fallback to the original candidate profile.
            profile_path = CV_PATH / "updated_candidate.json"

    # Check whether the profile exists.
    if not profile_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Candidate profile not found"
        )

    # Read the candidate profile.
    try:

        with open(profile_path, "r", encoding="utf-8") as file:
            profile = json.load(file)

    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500,
            detail="Candidate profile JSON is invalid"
        )

    except OSError:
        raise HTTPException(
            status_code=500,
            detail="Unable to read candidate profile"
        )

    return {
        "status": "success",
        "resume_id": profile_path.stem,
        "candidate": profile
    }


@router.put("/profile")
@router.put("/profile/{resume_id}")
def update_candidate_profile(update: CandidateProfileUpdate, resume_id: str = None):
    RESUME_LIBRARY.mkdir(parents=True, exist_ok=True)

    if resume_id:
        if "/" in resume_id or "\\" in resume_id or resume_id in {".", ".."}:
            raise HTTPException(status_code=400, detail="Invalid resume ID")
        profile_path = RESUME_LIBRARY / f"{resume_id}.json"
    else:
        saved_profiles = sorted(
            RESUME_LIBRARY.glob("*.json"),
            key=lambda path: path.stat().st_mtime,
            reverse=True,
        )
        if not saved_profiles:
            raise HTTPException(status_code=404, detail="Candidate profile not found")
        profile_path = saved_profiles[0]

    if not profile_path.exists():
        raise HTTPException(status_code=404, detail="Candidate profile not found")

    with profile_path.open("r", encoding="utf-8") as file:
        profile = json.load(file)

    values = update.model_dump(exclude_unset=True)
    personal = profile.setdefault("personal_details", {})
    field_mapping = {
        "name": ("name", "full_name"),
        "email": ("email", "email"),
        "phone": ("phone", "phone"),
        "linkedin": ("linkedin", "linkedin"),
        "github": ("github", "github"),
        "summary": ("summary", "professional_summary"),
    }
    for field, value in values.items():
        if field in field_mapping:
            top_level, legacy = field_mapping[field]
            profile[top_level] = value
            personal[legacy] = value
        elif field == "skills":
            profile["skills"] = sorted(
                set(skill.strip() for skill in value if skill and skill.strip()),
                key=str.lower,
            )
        else:
            profile[field] = value

    with profile_path.open("w", encoding="utf-8") as file:
        json.dump(profile, file, indent=2, ensure_ascii=False)

    db = SessionLocal()
    try:
        email = (profile.get("email") or personal.get("email") or "").strip().lower() or None
        candidate = db.query(Candidate).filter(Candidate.email == email).first() if email else None
        if candidate is None:
            candidate = Candidate(
                full_name=profile.get("name") or personal.get("full_name"),
                email=email,
                phone=profile.get("phone") or personal.get("phone"),
                education=profile.get("education"),
                experience=profile.get("experience"),
            )
            db.add(candidate)
        else:
            candidate.full_name = profile.get("name") or personal.get("full_name") or candidate.full_name
            candidate.phone = profile.get("phone") or personal.get("phone")
            candidate.education = profile.get("education")
            candidate.experience = profile.get("experience")
        db.commit()
    finally:
        db.close()

    return {
        "status": "success",
        "resume_id": profile_path.stem,
        "candidate": profile,
        "message": "Candidate profile updated",
    }
