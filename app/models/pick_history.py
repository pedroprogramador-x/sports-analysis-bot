from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime
from app.database import Base


class PickHistory(Base):
    __tablename__ = "picks_history"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    home_team = Column(String, nullable=False)
    away_team = Column(String, nullable=False)
    league = Column(String, nullable=False)
    kickoff = Column(String, nullable=False)
    market = Column(String, nullable=False)
    odd = Column(Float, nullable=False)
    probability = Column(Float, nullable=False)
    value = Column(Float, nullable=False)
    pick_type = Column(String, nullable=False)   # "conservative", "bold", "acca_leg"
    bsd_event_id = Column(Integer, nullable=True)
    result = Column(String, nullable=True)        # "win", "loss", "void"
    result_updated_at = Column(DateTime, nullable=True)
