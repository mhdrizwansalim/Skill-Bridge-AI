from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.database import Base

class InterviewHistory(Base):

    __tablename__ = "interview_history"

    id = Column(Integer, primary_key=True, index=True)

    candidate_id = Column(
        Integer,
        ForeignKey("candidates.id"),
        nullable=False
    )

    target_role = Column(String(200), nullable=False)
    difficulty = Column(String(50))
    total_questions = Column(Integer)
    total_answers = Column(Integer)
    average_score = Column(Float)
    performance_level = Column(String(100))
    questions_answers = Column(Text)
    feedback = Column(Text)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    candidate = relationship("Candidate", back_populates="interview_history")