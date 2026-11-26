from backend.database import SessionLocal
from backend.models.candidate import Candidate


def create_candidate(full_name, email, phone=None,
                     education=None, experience=None, location=None):

    db = SessionLocal()

    try:
        candidate = Candidate(
            full_name=full_name,
            email=email,
            phone=phone,
            education=education,
            experience=experience,
            location=location
        )

        db.add(candidate)
        db.commit()
        db.refresh(candidate)

        return candidate

    finally:
        db.close()


def get_candidate(candidate_id):

    db = SessionLocal()

    try:
        return db.query(Candidate).filter(
            Candidate.id == candidate_id
        ).first()

    finally:
        db.close()


def get_all_candidates():

    db = SessionLocal()

    try:
        return db.query(Candidate).all()

    finally:
        db.close()


def update_candidate(candidate_id, **updates):

    allowed_fields = {
        "full_name", "email", "phone",
        "education", "experience", "location"
    }

    db = SessionLocal()

    try:
        candidate = db.query(Candidate).filter(
            Candidate.id == candidate_id
        ).first()

        if candidate is None:
            return None

        for field, value in updates.items():
            if field in allowed_fields:
                setattr(candidate, field, value)

        db.commit()
        db.refresh(candidate)

        return candidate

    finally:
        db.close()


def delete_candidate(candidate_id):

    db = SessionLocal()

    try:
        candidate = db.query(Candidate).filter(
            Candidate.id == candidate_id
        ).first()

        if candidate is None:
            return False

        db.delete(candidate)
        db.commit()

        return True

    finally:
        db.close()