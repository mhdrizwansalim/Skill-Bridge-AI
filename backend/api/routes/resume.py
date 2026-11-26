from pathlib import Path
from uuid import uuid4
from fastapi import APIRouter, UploadFile, File, HTTPException
from backend.config import PROJECT_ROOT
from backend.database import SessionLocal
from backend.api.routes.resume_parser import parse_resume
from backend.models.candidate import Candidate
from backend.models.resume import Resume

router = APIRouter(
    prefix="/resume",
    tags=["Resume"]
)

UPLOAD_PATH = PROJECT_ROOT / "data" / "processed" / "uploaded_resumes"
UPLOAD_PATH.mkdir(parents=True, exist_ok=True)

@router.post("/upload")
async def upload_resume(file: UploadFile = File(...)):

    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed"
        )

    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Invalid PDF filename"
        )

    content = await file.read(10 * 1024 * 1024 + 1)

    if not content.startswith(b"%PDF-"):
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is not a valid PDF"
        )

    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail="File size exceeds 10 MB"
        )

    saved_name = f"{uuid4().hex}.pdf"
    save_path = UPLOAD_PATH / saved_name

    save_path.write_bytes(content)

    parsing = parse_resume(saved_name)
    candidate_profile = parsing.get("candidate", {})

    db = SessionLocal()
    try:
        candidate = None
        email = (candidate_profile.get("email") or "").strip().lower() or None
        if email:
            candidate = db.query(Candidate).filter(Candidate.email == email).first()

        if candidate is None:
            candidate = Candidate(
                full_name=candidate_profile.get("name"),
                email=email,
                phone=candidate_profile.get("phone"),
                education=candidate_profile.get("education"),
                experience=candidate_profile.get("experience"),
            )
            db.add(candidate)
            db.flush()

        resume_record = Resume(
            candidate_id=candidate.id,
            filename=file.filename,
            file_path=str(save_path),
            file_type="application/pdf",
            file_size=len(content),
        )
        db.add(resume_record)
        db.commit()
        db.refresh(resume_record)
    finally:
        db.close()

    return {
        "status": "success",
        "original_filename": file.filename,
        "saved_filename": saved_name,
        "size_bytes": len(content),
        "profile_id": parsing.get("profile_id"),
        "candidate": candidate_profile,
        "profile_saved": True,
        "message": "Resume uploaded and parsed successfully"
    }