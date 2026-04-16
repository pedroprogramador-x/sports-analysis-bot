from sqlalchemy import Column, Integer, String, Float, DateTime, func
from app.database import Base


class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    team_a = Column(String(100), nullable=False)
    team_b = Column(String(100), nullable=False)
    goals_avg_a = Column(Float, nullable=False)
    goals_avg_b = Column(Float, nullable=False)
    corners_avg_a = Column(Float, nullable=False)
    corners_avg_b = Column(Float, nullable=False)
    goals_line = Column(Float, nullable=False)
    corners_line = Column(Float, nullable=False)
    created_at = Column(DateTime, server_default=func.now())