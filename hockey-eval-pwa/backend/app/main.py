from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
import uuid

from app.database import engine, get_db, Base
from app import models

Base.metadata.create_all(bind=engine)

app = FastAPI()

# Disable CORS. Do not remove this for full-stack development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PlayerSchema(BaseModel):
    id: Optional[str] = None
    name: str
    jersey_number: Optional[int] = None
    position: Optional[str] = None
    age_group: Optional[str] = None
    team: Optional[str] = None

    class Config:
        from_attributes = True

class SkillRating(BaseModel):
    skating: int
    shooting: int
    passing: int
    puck_handling: int
    hockey_iq: int
    physicality: int

class EvaluationSchema(BaseModel):
    id: Optional[str] = None
    player_id: str
    player_name: str
    date: str
    evaluator: str
    evaluation_type: str
    skills: SkillRating
    notes: Optional[str] = None
    strengths: Optional[str] = None
    areas_for_improvement: Optional[str] = None

    class Config:
        from_attributes = True

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

@app.get("/api/players", response_model=List[PlayerSchema])
async def get_players(db: Session = Depends(get_db)):
    players = db.query(models.Player).all()
    return players

@app.post("/api/players", response_model=PlayerSchema)
async def create_player(player: PlayerSchema, db: Session = Depends(get_db)):
    db_player = models.Player(
        id=str(uuid.uuid4()),
        name=player.name,
        jersey_number=player.jersey_number,
        position=player.position,
        age_group=player.age_group,
        team=player.team
    )
    db.add(db_player)
    db.commit()
    db.refresh(db_player)
    return db_player

@app.get("/api/players/{player_id}", response_model=PlayerSchema)
async def get_player(player_id: str, db: Session = Depends(get_db)):
    player = db.query(models.Player).filter(models.Player.id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    return player

@app.put("/api/players/{player_id}", response_model=PlayerSchema)
async def update_player(player_id: str, player: PlayerSchema, db: Session = Depends(get_db)):
    db_player = db.query(models.Player).filter(models.Player.id == player_id).first()
    if not db_player:
        raise HTTPException(status_code=404, detail="Player not found")
    
    db_player.name = player.name
    db_player.jersey_number = player.jersey_number
    db_player.position = player.position
    db_player.age_group = player.age_group
    db_player.team = player.team
    
    db.commit()
    db.refresh(db_player)
    return db_player

@app.delete("/api/players/{player_id}")
async def delete_player(player_id: str, db: Session = Depends(get_db)):
    db_player = db.query(models.Player).filter(models.Player.id == player_id).first()
    if not db_player:
        raise HTTPException(status_code=404, detail="Player not found")
    db.delete(db_player)
    db.commit()
    return {"message": "Player deleted"}

@app.get("/api/evaluations", response_model=List[EvaluationSchema])
async def get_evaluations(player_id: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(models.Evaluation)
    if player_id:
        query = query.filter(models.Evaluation.player_id == player_id)
    evaluations = query.all()
    
    return [
        EvaluationSchema(
            id=e.id,
            player_id=e.player_id,
            player_name=e.player_name,
            date=e.date.isoformat(),
            evaluator=e.evaluator,
            evaluation_type=e.evaluation_type,
            skills=SkillRating(
                skating=e.skating,
                shooting=e.shooting,
                passing=e.passing,
                puck_handling=e.puck_handling,
                hockey_iq=e.hockey_iq,
                physicality=e.physicality
            ),
            notes=e.notes,
            strengths=e.strengths,
            areas_for_improvement=e.areas_for_improvement
        )
        for e in evaluations
    ]

@app.post("/api/evaluations", response_model=EvaluationSchema)
async def create_evaluation(evaluation: EvaluationSchema, db: Session = Depends(get_db)):
    db_evaluation = models.Evaluation(
        id=str(uuid.uuid4()),
        player_id=evaluation.player_id,
        player_name=evaluation.player_name,
        date=datetime.fromisoformat(evaluation.date.replace('Z', '+00:00')),
        evaluator=evaluation.evaluator,
        evaluation_type=evaluation.evaluation_type,
        skating=evaluation.skills.skating,
        shooting=evaluation.skills.shooting,
        passing=evaluation.skills.passing,
        puck_handling=evaluation.skills.puck_handling,
        hockey_iq=evaluation.skills.hockey_iq,
        physicality=evaluation.skills.physicality,
        notes=evaluation.notes,
        strengths=evaluation.strengths,
        areas_for_improvement=evaluation.areas_for_improvement
    )
    db.add(db_evaluation)
    db.commit()
    db.refresh(db_evaluation)
    
    return EvaluationSchema(
        id=db_evaluation.id,
        player_id=db_evaluation.player_id,
        player_name=db_evaluation.player_name,
        date=db_evaluation.date.isoformat(),
        evaluator=db_evaluation.evaluator,
        evaluation_type=db_evaluation.evaluation_type,
        skills=SkillRating(
            skating=db_evaluation.skating,
            shooting=db_evaluation.shooting,
            passing=db_evaluation.passing,
            puck_handling=db_evaluation.puck_handling,
            hockey_iq=db_evaluation.hockey_iq,
            physicality=db_evaluation.physicality
        ),
        notes=db_evaluation.notes,
        strengths=db_evaluation.strengths,
        areas_for_improvement=db_evaluation.areas_for_improvement
    )

@app.get("/api/evaluations/{evaluation_id}", response_model=EvaluationSchema)
async def get_evaluation(evaluation_id: str, db: Session = Depends(get_db)):
    evaluation = db.query(models.Evaluation).filter(models.Evaluation.id == evaluation_id).first()
    if not evaluation:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    
    return EvaluationSchema(
        id=evaluation.id,
        player_id=evaluation.player_id,
        player_name=evaluation.player_name,
        date=evaluation.date.isoformat(),
        evaluator=evaluation.evaluator,
        evaluation_type=evaluation.evaluation_type,
        skills=SkillRating(
            skating=evaluation.skating,
            shooting=evaluation.shooting,
            passing=evaluation.passing,
            puck_handling=evaluation.puck_handling,
            hockey_iq=evaluation.hockey_iq,
            physicality=evaluation.physicality
        ),
        notes=evaluation.notes,
        strengths=evaluation.strengths,
        areas_for_improvement=evaluation.areas_for_improvement
    )

@app.put("/api/evaluations/{evaluation_id}", response_model=EvaluationSchema)
async def update_evaluation(evaluation_id: str, evaluation: EvaluationSchema, db: Session = Depends(get_db)):
    db_evaluation = db.query(models.Evaluation).filter(models.Evaluation.id == evaluation_id).first()
    if not db_evaluation:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    
    db_evaluation.player_id = evaluation.player_id
    db_evaluation.player_name = evaluation.player_name
    db_evaluation.evaluator = evaluation.evaluator
    db_evaluation.evaluation_type = evaluation.evaluation_type
    db_evaluation.skating = evaluation.skills.skating
    db_evaluation.shooting = evaluation.skills.shooting
    db_evaluation.passing = evaluation.skills.passing
    db_evaluation.puck_handling = evaluation.skills.puck_handling
    db_evaluation.hockey_iq = evaluation.skills.hockey_iq
    db_evaluation.physicality = evaluation.skills.physicality
    db_evaluation.notes = evaluation.notes
    db_evaluation.strengths = evaluation.strengths
    db_evaluation.areas_for_improvement = evaluation.areas_for_improvement
    
    db.commit()
    db.refresh(db_evaluation)
    
    return EvaluationSchema(
        id=db_evaluation.id,
        player_id=db_evaluation.player_id,
        player_name=db_evaluation.player_name,
        date=db_evaluation.date.isoformat(),
        evaluator=db_evaluation.evaluator,
        evaluation_type=db_evaluation.evaluation_type,
        skills=SkillRating(
            skating=db_evaluation.skating,
            shooting=db_evaluation.shooting,
            passing=db_evaluation.passing,
            puck_handling=db_evaluation.puck_handling,
            hockey_iq=db_evaluation.hockey_iq,
            physicality=db_evaluation.physicality
        ),
        notes=db_evaluation.notes,
        strengths=db_evaluation.strengths,
        areas_for_improvement=db_evaluation.areas_for_improvement
    )

@app.delete("/api/evaluations/{evaluation_id}")
async def delete_evaluation(evaluation_id: str, db: Session = Depends(get_db)):
    db_evaluation = db.query(models.Evaluation).filter(models.Evaluation.id == evaluation_id).first()
    if not db_evaluation:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    db.delete(db_evaluation)
    db.commit()
    return {"message": "Evaluation deleted"}

@app.post("/api/sync")
async def sync_data(data: dict, db: Session = Depends(get_db)):
    if "players" in data:
        for player_data in data["players"]:
            existing = db.query(models.Player).filter(models.Player.id == player_data.get("id")).first()
            if existing:
                existing.name = player_data["name"]
                existing.jersey_number = player_data.get("jersey_number")
                existing.position = player_data.get("position")
                existing.age_group = player_data.get("age_group")
                existing.team = player_data.get("team")
            else:
                db_player = models.Player(
                    id=player_data.get("id") or str(uuid.uuid4()),
                    name=player_data["name"],
                    jersey_number=player_data.get("jersey_number"),
                    position=player_data.get("position"),
                    age_group=player_data.get("age_group"),
                    team=player_data.get("team")
                )
                db.add(db_player)
    
    if "evaluations" in data:
        for eval_data in data["evaluations"]:
            existing = db.query(models.Evaluation).filter(models.Evaluation.id == eval_data.get("id")).first()
            if not existing:
                db_evaluation = models.Evaluation(
                    id=eval_data.get("id") or str(uuid.uuid4()),
                    player_id=eval_data["player_id"],
                    player_name=eval_data["player_name"],
                    date=datetime.fromisoformat(eval_data["date"].replace('Z', '+00:00')),
                    evaluator=eval_data["evaluator"],
                    evaluation_type=eval_data["evaluation_type"],
                    skating=eval_data["skills"]["skating"],
                    shooting=eval_data["skills"]["shooting"],
                    passing=eval_data["skills"]["passing"],
                    puck_handling=eval_data["skills"]["puck_handling"],
                    hockey_iq=eval_data["skills"]["hockey_iq"],
                    physicality=eval_data["skills"]["physicality"],
                    notes=eval_data.get("notes"),
                    strengths=eval_data.get("strengths"),
                    areas_for_improvement=eval_data.get("areas_for_improvement")
                )
                db.add(db_evaluation)
    
    db.commit()
    
    players = db.query(models.Player).all()
    evaluations = db.query(models.Evaluation).all()
    
    return {
        "players": [PlayerSchema.from_orm(p) for p in players],
        "evaluations": [
            EvaluationSchema(
                id=e.id,
                player_id=e.player_id,
                player_name=e.player_name,
                date=e.date.isoformat(),
                evaluator=e.evaluator,
                evaluation_type=e.evaluation_type,
                skills=SkillRating(
                    skating=e.skating,
                    shooting=e.shooting,
                    passing=e.passing,
                    puck_handling=e.puck_handling,
                    hockey_iq=e.hockey_iq,
                    physicality=e.physicality
                ),
                notes=e.notes,
                strengths=e.strengths,
                areas_for_improvement=e.areas_for_improvement
            )
            for e in evaluations
        ]
    }
