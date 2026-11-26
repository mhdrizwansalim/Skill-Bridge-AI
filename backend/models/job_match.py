from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.database import Base

class JobMatch(Base):

    __tablename__ = "job_matches"

    id = Column(Integer, primary_key=True, index=True)

    candidate_id = Column(
        Integer,
        ForeignKey("candidates.id"),
        nullable=False
    )

    job_title = Column(String(200), nullable=False)
    company_name = Column(String(200))
    job_description = Column(Text)
    match_score = Column(Float)
    matching_skills = Column(Text)
    missing_skills = Column(Text)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    candidate = relationship("Candidate", back_populates="job_matches")