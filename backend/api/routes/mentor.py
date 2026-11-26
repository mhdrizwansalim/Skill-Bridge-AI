from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.database import SessionLocal
from backend.models.candidate import Candidate
from backend.models.mentor_conversation import MentorConversation
from backend.services.mentor_service import generate_answer

router = APIRouter(
    prefix="/mentor",
    tags=["AI Career Mentor"]
)

class MentorQuestion(BaseModel):
    question: str = Field(min_length=3, max_length=2000)


@router.get("/history")
def get_mentor_history(limit: int = 20):
    limit = max(1, min(limit, 100))
    db = SessionLocal()
    try:
        records = (
            db.query(MentorConversation)
            .order_by(MentorConversation.created_at.desc())
            .limit(limit)
            .all()
        )
        return {
            "status": "success",
            "history": [
                {
                    "id": record.id,
                    "question": record.user_message,
                    "answer": record.ai_response,
                    "created_at": record.created_at.isoformat() if record.created_at else None,
                }
                for record in reversed(records)
            ],
            "total": len(records),
        }
    finally:
        db.close()

@router.post("/ask")
def ask_mentor(data: MentorQuestion):
    question = data.question.strip()
    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty"
        )

    try:
        answer, candidate_profile, context = generate_answer(question)
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except RuntimeError as error:
        raise HTTPException(
            status_code=503,
            detail=str(error),
        ) from error

    db = SessionLocal()
    try:
        candidate = db.query(Candidate).order_by(Candidate.id.desc()).first()
        if candidate is None:
            candidate = Candidate(
                full_name=candidate_profile.get("name"),
                email=candidate_profile.get("email") or None,
                phone=candidate_profile.get("phone"),
            )
            db.add(candidate)
            db.flush()

        record = MentorConversation(
            candidate_id=candidate.id,
            session_id="default",
            user_message=question,
            ai_response=answer,
            retrieved_context=(
                "\n\n".join(
                    f"{chunk.get('title', '')}: {chunk.get('text', '')}"
                    for chunk in context
                )
            ),
        )
        db.add(record)
        db.commit()
        db.refresh(record)
    finally:
        db.close()

    return {
        "status": "success",
        "question": question,
        "answer": answer,
        "sources": [
            {
                "title": chunk.get("title"),
                "category": chunk.get("category"),
            }
            for chunk in context
        ],
    }