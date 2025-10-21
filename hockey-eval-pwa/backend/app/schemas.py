from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class User(UserBase):
    id: int
    created_at: datetime
    is_active: bool
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class TeamBase(BaseModel):
    name: str
    age_group: Optional[str] = None
    season: Optional[str] = None

class TeamCreate(TeamBase):
    pass

class Team(TeamBase):
    id: int
    coach_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class PlayerBase(BaseModel):
    name: str
    jersey_number: Optional[int] = None
    position: Optional[str] = None
    age_group: Optional[str] = None
    team_id: Optional[int] = None

class PlayerCreate(PlayerBase):
    pass

class PlayerUpdate(PlayerBase):
    photo_url: Optional[str] = None

class Player(PlayerBase):
    id: int
    coach_id: int
    photo_url: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class SkillRating(BaseModel):
    skating: int = Field(..., ge=1, le=10, description="Skating skill rating (1-10)")
    shooting: int = Field(..., ge=1, le=10, description="Shooting skill rating (1-10)")
    passing: int = Field(..., ge=1, le=10, description="Passing skill rating (1-10)")
    puck_handling: int = Field(..., ge=1, le=10, description="Puck handling skill rating (1-10)")
    hockey_iq: int = Field(..., ge=1, le=10, description="Hockey IQ rating (1-10)")
    physicality: int = Field(..., ge=1, le=10, description="Physicality rating (1-10)")

class EvaluationBase(BaseModel):
    player_id: int
    evaluator_name: str
    evaluation_type: str
    skills: SkillRating
    notes: Optional[str] = None
    strengths: Optional[str] = None
    areas_for_improvement: Optional[str] = None

class EvaluationCreate(EvaluationBase):
    pass

class Evaluation(BaseModel):
    id: int
    player_id: int
    evaluator_id: int
    evaluator_name: str
    date: datetime
    evaluation_type: str
    skating: int
    shooting: int
    passing: int
    puck_handling: int
    hockey_iq: int
    physicality: int
    notes: Optional[str] = None
    strengths: Optional[str] = None
    areas_for_improvement: Optional[str] = None
    
    class Config:
        from_attributes = True

class FeedbackTemplateBase(BaseModel):
    name: str
    category: Optional[str] = None
    text: str

class FeedbackTemplateCreate(FeedbackTemplateBase):
    pass

class FeedbackTemplate(FeedbackTemplateBase):
    id: int
    coach_id: int
    created_at: datetime
    times_used: int
    
    class Config:
        from_attributes = True

class PlayerWithEvaluations(Player):
    evaluations: List[Evaluation] = []
    
    class Config:
        from_attributes = True
