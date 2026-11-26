from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.database import Base

class Candidate(Base):

    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)

    full_name = Column(String(150), nullable=True)
    email = Column(String(150), unique=True, index=True)
    phone = Column(String(30))

    education = Column(Text)
    experience = Column(Text)
    location = Column(String(150))

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        onupdate=func.now()
    )

    resumes = relationship("Resume", back_populates="candidate", cascade="all, delete-orphan")
    skills = relationship("Skill", back_populates="candidate", cascade="all, delete-orphan")
    career_recommendations = relationship("CareerRecommendation", back_populates="candidate")
    job_matches = relationship("JobMatch", back_populates="candidate")
    interview_history = relationship("InterviewHistory", back_populates="candidate")
    mentor_conversations = relationship("MentorConversation", back_populates="candidate")