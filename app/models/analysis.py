from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.database import Base


class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=False)
    goals_suggestion = Column(String(10), nullable=False)
    goals_confidence = Column(String(10), nullable=False)
    goals_diff = Column(Float, nullable=False)
    corners_suggestion = Column(String(10), nullable=False)
    corners_confidence = Column(String(10), nullable=False)
    corners_diff = Column(Float, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    match = relationship("Match", backref="analyses")