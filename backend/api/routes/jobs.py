import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from backend.config import PROJECT_ROOT
from backend.database import SessionLocal
from backend.models.candidate import Candidate
from backend.models.job_match import JobMatch
from backend.services.job_service import analyze_job_description

router = APIRouter(
    prefix="/jobs",
    tags=["Job Matching"]
)

REPORT_PATH = (
    PROJECT_ROOT / "data" / "processed" /
    "job_analyzer" / "complete_job_analysis_report.json"
)


class JobDescriptionRequest(BaseModel):
    text: str = Field(min_length=20, max_length=50000)


@router.post("/analyze")
def analyze_job(data: JobDescriptionRequest):
    analysis = analyze_job_description(data.text.strip())

    db = SessionLocal()
    try:
        candidate = db.query(Candidate).order_by(Candidate.id.desc()).first()
        if candidate is None:
            from backend.services.cv_service import load_profile
            profile = load_profile()
            candidate = Candidate(
                full_name=profile.get("name") or None,
                email=profile.get("email") or None,
                phone=profile.get("phone") or None,
            )
            db.add(candidate)
            db.flush()

        record = JobMatch(
            candidate_id=candidate.id,
            job_title=analysis["job_title"],
            company_name=None,
            job_description=data.text.strip(),
            match_score=analysis["job_compatibility_percentage"],
            matching_skills=json.dumps(analysis["matched_skills"], ensure_ascii=False),
            missing_skills=json.dumps(analysis["missing_skills"], ensure_ascii=False),
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        record_id = record.id
    finally:
        db.close()

    return {
        "status": "success",
        "job_match_id": record_id,
        "analysis": analysis,
    }

@router.get("/matches")
def get_job_matches():

    if not REPORT_PATH.exists():
        raise HTTPException(
            status_code=404,
            detail="Job analysis report not found"
        )

    with open(REPORT_PATH, "r", encoding="utf-8") as file:
        report = json.load(file)

    return {
        "status": "success",
        "candidate": report.get("candidate_name", "Unknown"),
        "job_analysis": report
    }


@router.get("/history")
def get_job_history(limit: int = 20):
    limit = max(1, min(limit, 100))
    db = SessionLocal()
    try:
        records = (
            db.query(JobMatch)
            .order_by(JobMatch.created_at.desc())
            .limit(limit)
            .all()
        )
        return {
            "status": "success",
            "history": [
                {
                    "id": record.id,
                    "job_title": record.job_title,
                    "company_name": record.company_name,
                    "match_score": record.match_score,
                    "created_at": record.created_at.isoformat() if record.created_at else None,
                }
                for record in reversed(records)
            ],
            "total": len(records),
        }
    finally:
        db.close()