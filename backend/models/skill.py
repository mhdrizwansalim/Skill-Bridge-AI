from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.database import Base

class Skill(Base):

    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)

    candidate_id = Column(
        Integer,
        ForeignKey("candidates.id"),
        nullable=False
    )

    skill_name = Column(String(150), nullable=False)
    proficiency_level = Column(String(50))
    years_of_experience = Column(Integer)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    candidate = relationship("Candidate", back_populates="skills")