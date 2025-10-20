from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Player(Base):
    __tablename__ = "players"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    jersey_number = Column(Integer, nullable=True)
    position = Column(String, nullable=True)
    age_group = Column(String, nullable=True)
    team = Column(String, nullable=True)
    
    evaluations = relationship("Evaluation", back_populates="player", cascade="all, delete-orphan")

class Evaluation(Base):
    __tablename__ = "evaluations"

    id = Column(String, primary_key=True, index=True)
    player_id = Column(String, ForeignKey("players.id"), nullable=False)
    player_name = Column(String, nullable=False)
    date = Column(DateTime, default=datetime.utcnow, nullable=False)
    evaluator = Column(String, nullable=False)
    evaluation_type = Column(String, nullable=False)
    
    skating = Column(Integer, nullable=False)
    shooting = Column(Integer, nullable=False)
    passing = Column(Integer, nullable=False)
    puck_handling = Column(Integer, nullable=False)
    hockey_iq = Column(Integer, nullable=False)
    physicality = Column(Integer, nullable=False)
    
    notes = Column(String, nullable=True)
    strengths = Column(String, nullable=True)
    areas_for_improvement = Column(String, nullable=True)
    
    player = relationship("Player", back_populates="evaluations")
