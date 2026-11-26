import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from backend.config import PROJECT_ROOT
from backend.database import SessionLocal
from backend.models.candidate import Candidate
from backend.models.interview_history import InterviewHistory
from backend.services.cv_service import load_profile
from backend.services.interview_service import evaluate_answer, select_question_set

router = APIRouter(
    prefix="/interview",
    tags=["Mock Interview"]
)

REPORT_PATH = (
    PROJECT_ROOT / "data" / "processed" /
    "mock_interview" / "complete_interview_report.json"
)


class InterviewStartRequest(BaseModel):
    target_role: str = Field(min_length=2, max_length=200)


class InterviewAnswer(BaseModel):
    question: str = Field(min_length=3, max_length=1000)
    answer: str = Field(min_length=3, max_length=5000)


class InterviewSubmitRequest(BaseModel):
    target_role: str = Field(min_length=2, max_length=200)
    answers: list[InterviewAnswer] = Field(min_length=1, max_length=20)


@router.post("/start")
def start_interview(data: InterviewStartRequest):
    profile = load_profile()
    questions = select_question_set(data.target_role)
    return {
        "status": "success",
        "target_role": data.target_role,
        "candidate_skills": profile.get("skills", []),
        "questions": [
            {"id": index + 1, "question": question}
            for index, question in enumerate(questions)
        ],
        "evaluation_method": (
            "Local transparent scoring based on relevance, specificity, structure, "
            "answer length, and clarity."
        ),
    }


@router.post("/submit")
def submit_interview(data: InterviewSubmitRequest):
    profile = load_profile()
    skills = profile.get("skills", [])
    evaluations = [
        {
            "question": item.question,
            "answer": item.answer,
            "evaluation": evaluate_answer(item.answer, data.target_role, skills),
        }
        for item in data.answers
    ]
    average_score = round(
        sum(item["evaluation"]["score"] for item in evaluations) / len(evaluations),
        2,
    )
    if average_score >= 80:
        performance_level = "Strong"
    elif average_score >= 60:
        performance_level = "Developing"
    else:
        performance_level = "Needs focused practice"

    feedback = sorted(
        {
            suggestion
            for item in evaluations
            for suggestion in item["evaluation"]["feedback"]
        }
    )

    db = SessionLocal()
    try:
        candidate = db.query(Candidate).order_by(Candidate.id.desc()).first()
        if candidate is None:
            candidate = Candidate(
                full_name=profile.get("name") or None,
                email=profile.get("email") or None,
                phone=profile.get("phone") or None,
                education=profile.get("education"),
                experience=profile.get("experience"),
            )
            db.add(candidate)
            db.flush()

        record = InterviewHistory(
            candidate_id=candidate.id,
            target_role=data.target_role,
            difficulty="General",
            total_questions=len(data.answers),
            total_answers=len(data.answers),
            average_score=average_score,
            performance_level=performance_level,
            questions_answers=json.dumps(evaluations, ensure_ascii=False),
            feedback=json.dumps(feedback, ensure_ascii=False),
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        record_id = record.id
    finally:
        db.close()

    return {
        "status": "success",
        "interview_id": record_id,
        "target_role": data.target_role,
        "average_score": average_score,
        "performance_level": performance_level,
        "evaluations": evaluations,
        "feedback": feedback,
    }

@router.get("/report")
def get_interview_report():

    if not REPORT_PATH.exists():
        raise HTTPException(
            status_code=404,
            detail="Interview report not found"
        )

    with open(REPORT_PATH, "r", encoding="utf-8") as file:
        report = json.load(file)

    return {
        "status": "success",
        "interview_report": report
    }


@router.get("/history")
def get_interview_history(limit: int = 20):
    limit = max(1, min(limit, 100))
    db = SessionLocal()
    try:
        records = (
            db.query(InterviewHistory)
            .order_by(InterviewHistory.created_at.desc())
            .limit(limit)
            .all()
        )
        return {
            "status": "success",
            "history": [
                {
                    "id": record.id,
                    "target_role": record.target_role,
                    "average_score": record.average_score,
                    "performance_level": record.performance_level,
                    "created_at": record.created_at.isoformat() if record.created_at else None,
                }
                for record in reversed(records)
            ],
            "total": len(records),
        }
    finally:
        db.close()


@router.get("/{interview_id}")
def get_saved_interview(interview_id: int):
    db = SessionLocal()
    try:
        record = db.query(InterviewHistory).filter(
            InterviewHistory.id == interview_id
        ).first()
        if record is None:
            raise HTTPException(status_code=404, detail="Interview report not found")

        try:
            evaluations = json.loads(record.questions_answers or "[]")
            feedback = json.loads(record.feedback or "[]")
        except json.JSONDecodeError:
            evaluations = []
            feedback = []

        return {
            "status": "success",
            "interview": {
                "id": record.id,
                "target_role": record.target_role,
                "average_score": record.average_score,
                "performance_level": record.performance_level,
                "evaluations": evaluations,
                "feedback": feedback,
            },
        }
    finally:
        db.close()