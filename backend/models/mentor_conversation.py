from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.database import Base

class MentorConversation(Base):

    __tablename__ = "mentor_conversations"

    id = Column(Integer, primary_key=True, index=True)

    candidate_id = Column(
        Integer,
        ForeignKey("candidates.id"),
        nullable=False
    )

    session_id = Column(String(100), index=True)
    user_message = Column(Text, nullable=False)
    ai_response = Column(Text, nullable=False)
    retrieved_context = Column(Text)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    candidate = relationship("Candidate", back_populates="mentor_conversations")