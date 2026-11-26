from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.database import Base

class CareerRecommendation(Base):

    __tablename__ = "career_recommendations"

    id = Column(Integer, primary_key=True, index=True)

    candidate_id = Column(
        Integer,
        ForeignKey("candidates.id"),
        nullable=False
    )

    career_title = Column(String(200), nullable=False)
    similarity_score = Column(Float)
    matching_skills = Column(Text)
    missing_skills = Column(Text)
    explanation = Column(Text)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    candidate = relationship("Candidate", back_populates="career_recommendations")