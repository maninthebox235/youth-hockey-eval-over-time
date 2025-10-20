from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean, LargeBinary
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    players = relationship("Player", back_populates="coach")
    evaluations = relationship("Evaluation", back_populates="evaluator_user")
    teams = relationship("Team", back_populates="coach")
    
    def verify_password(self, password: str) -> bool:
        return pwd_context.verify(password, self.hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        return pwd_context.hash(password)


class Team(Base):
    __tablename__ = "teams"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    age_group = Column(String)
    season = Column(String)
    coach_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    coach = relationship("User", back_populates="teams")
    players = relationship("Player", back_populates="team")


class Player(Base):
    __tablename__ = "players"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    jersey_number = Column(Integer)
    position = Column(String)
    age_group = Column(String)
    team_id = Column(Integer, ForeignKey("teams.id"))
    coach_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    photo_url = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    coach = relationship("User", back_populates="players")
    team = relationship("Team", back_populates="players")
    evaluations = relationship("Evaluation", back_populates="player")


class Evaluation(Base):
    __tablename__ = "evaluations"
    
    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    evaluator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    evaluator_name = Column(String, nullable=False)
    date = Column(DateTime, default=datetime.utcnow, index=True)
    evaluation_type = Column(String, nullable=False)
    
    skating = Column(Integer, nullable=False)
    shooting = Column(Integer, nullable=False)
    passing = Column(Integer, nullable=False)
    puck_handling = Column(Integer, nullable=False)
    hockey_iq = Column(Integer, nullable=False)
    physicality = Column(Integer, nullable=False)
    
    notes = Column(Text)
    strengths = Column(Text)
    areas_for_improvement = Column(Text)
    
    player = relationship("Player", back_populates="evaluations")
    evaluator_user = relationship("User", back_populates="evaluations")


class FeedbackTemplate(Base):
    __tablename__ = "feedback_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    coach_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category = Column(String)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    times_used = Column(Integer, default=0)
