import json
from fastapi import APIRouter, HTTPException
from backend.config import PROJECT_ROOT
from backend.services.career_service import normalize_skill_gap

router = APIRouter(
    prefix="/career",
    tags=["Skill Gap Analysis"]
)

REPORT_PATH = (
    PROJECT_ROOT / "data" / "processed" /
    "candidates" / "complete_candidate_career_report.json"
)

@router.get("/skill-gap")
def get_skill_gap():
    skill_gap = normalize_skill_gap()
    if not skill_gap.get("candidate_skills") and not skill_gap.get("target_skills"):
        raise HTTPException(
            status_code=404,
            detail="Skill-gap analysis is not available",
        )

    return {
        "status": "success",
        "candidate": skill_gap.get("candidate_skills"),
        "skill_gap_analysis": skill_gap,
    }