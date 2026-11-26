import json
from fastapi import APIRouter, HTTPException
from backend.config import PROJECT_ROOT
from backend.services.career_service import normalize_career_recommendations

router = APIRouter(
    prefix="/career",
    tags=["Career Recommendations"]
)

REPORT_PATH = (
    PROJECT_ROOT / "data" / "processed" /
    "candidates" / "complete_candidate_career_report.json"
)

@router.get("/recommendations")
def get_career_recommendations():
    recommendations, candidate = normalize_career_recommendations()
    if not recommendations:
        raise HTTPException(
            status_code=404,
            detail="Career recommendations are not available",
        )

    return {
        "status": "success",
        "candidate": candidate,
        "recommendations": recommendations,
        "total_recommendations": len(recommendations),
    }