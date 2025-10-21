from fastapi import FastAPI, HTTPException, Depends, File, UploadFile, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import timedelta
import base64
import os

from . import models, schemas, auth
from .database import engine, get_db
from .pdf_generator import generate_player_evaluation_pdf

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Hockey Evaluation API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

@app.post("/api/auth/register", response_model=schemas.User)
async def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already taken")
    
    hashed_password = models.User.get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/api/auth/login", response_model=schemas.Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not user.verify_password(form_data.password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/auth/me", response_model=schemas.User)
async def read_users_me(current_user: models.User = Depends(auth.get_current_active_user)):
    return current_user

@app.get("/api/teams", response_model=List[schemas.Team])
async def get_teams(
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    teams = db.query(models.Team).filter(models.Team.coach_id == current_user.id).all()
    return teams

@app.post("/api/teams", response_model=schemas.Team)
async def create_team(
    team: schemas.TeamCreate,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    db_team = models.Team(**team.dict(), coach_id=current_user.id)
    db.add(db_team)
    db.commit()
    db.refresh(db_team)
    return db_team

@app.get("/api/players", response_model=List[schemas.Player])
async def get_players(
    team_id: Optional[int] = None,
    search: Optional[str] = None,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    query = db.query(models.Player).filter(models.Player.coach_id == current_user.id)
    if team_id:
        query = query.filter(models.Player.team_id == team_id)
    if search:
        query = query.filter(models.Player.name.ilike(f"%{search}%"))
    players = query.all()
    return players

@app.post("/api/players", response_model=schemas.Player)
async def create_player(
    player: schemas.PlayerCreate,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    db_player = models.Player(**player.dict(), coach_id=current_user.id)
    db.add(db_player)
    db.commit()
    db.refresh(db_player)
    return db_player

@app.get("/api/players/{player_id}", response_model=schemas.PlayerWithEvaluations)
async def get_player(
    player_id: int,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    player = db.query(models.Player).filter(
        models.Player.id == player_id,
        models.Player.coach_id == current_user.id
    ).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    return player

@app.put("/api/players/{player_id}", response_model=schemas.Player)
async def update_player(
    player_id: int,
    player: schemas.PlayerUpdate,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    db_player = db.query(models.Player).filter(
        models.Player.id == player_id,
        models.Player.coach_id == current_user.id
    ).first()
    if not db_player:
        raise HTTPException(status_code=404, detail="Player not found")
    
    for key, value in player.dict(exclude_unset=True).items():
        setattr(db_player, key, value)
    
    db.commit()
    db.refresh(db_player)
    return db_player

@app.delete("/api/players/{player_id}")
async def delete_player(
    player_id: int,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    db_player = db.query(models.Player).filter(
        models.Player.id == player_id,
        models.Player.coach_id == current_user.id
    ).first()
    if not db_player:
        raise HTTPException(status_code=404, detail="Player not found")
    
    db.delete(db_player)
    db.commit()
    return {"message": "Player deleted"}

@app.post("/api/players/{player_id}/photo")
async def upload_player_photo(
    player_id: int,
    file: UploadFile = File(...),
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    db_player = db.query(models.Player).filter(
        models.Player.id == player_id,
        models.Player.coach_id == current_user.id
    ).first()
    if not db_player:
        raise HTTPException(status_code=404, detail="Player not found")

    # Maximum file size: 5MB
    MAX_FILE_SIZE = 5 * 1024 * 1024

    contents = await file.read()

    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large. Maximum size is 5MB")

    photo_data = base64.b64encode(contents).decode('utf-8')
    photo_url = f"data:{file.content_type};base64,{photo_data}"
    
    db_player.photo_url = photo_url
    db.commit()
    
    return {"photo_url": photo_url}

@app.get("/api/evaluations", response_model=List[schemas.Evaluation])
async def get_evaluations(
    player_id: Optional[int] = None,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    query = db.query(models.Evaluation).filter(models.Evaluation.evaluator_id == current_user.id)
    if player_id:
        query = query.filter(models.Evaluation.player_id == player_id)
    evaluations = query.order_by(models.Evaluation.date.desc()).all()
    return evaluations

@app.post("/api/evaluations", response_model=schemas.Evaluation)
async def create_evaluation(
    evaluation: schemas.EvaluationCreate,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    player = db.query(models.Player).filter(
        models.Player.id == evaluation.player_id,
        models.Player.coach_id == current_user.id
    ).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    
    db_evaluation = models.Evaluation(
        player_id=evaluation.player_id,
        evaluator_id=current_user.id,
        evaluator_name=evaluation.evaluator_name,
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
    return db_evaluation

@app.post("/api/evaluations/bulk", response_model=List[schemas.Evaluation])
async def create_bulk_evaluations(
    evaluations: List[schemas.EvaluationCreate],
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    created_evaluations = []
    for evaluation in evaluations:
        player = db.query(models.Player).filter(
            models.Player.id == evaluation.player_id,
            models.Player.coach_id == current_user.id
        ).first()
        if not player:
            continue
        
        db_evaluation = models.Evaluation(
            player_id=evaluation.player_id,
            evaluator_id=current_user.id,
            evaluator_name=evaluation.evaluator_name,
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
        created_evaluations.append(db_evaluation)
    
    db.commit()
    for eval in created_evaluations:
        db.refresh(eval)
    return created_evaluations

@app.get("/api/players/{player_id}/pdf")
async def get_player_pdf(
    player_id: int,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    player = db.query(models.Player).filter(
        models.Player.id == player_id,
        models.Player.coach_id == current_user.id
    ).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    
    evaluations = db.query(models.Evaluation).filter(
        models.Evaluation.player_id == player_id
    ).order_by(models.Evaluation.date.desc()).all()
    
    pdf_data = generate_player_evaluation_pdf(player, evaluations)
    
    return Response(
        content=pdf_data,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=player_{player_id}_evaluation.pdf"
        }
    )

@app.get("/api/feedback-templates", response_model=List[schemas.FeedbackTemplate])
async def get_feedback_templates(
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    templates = db.query(models.FeedbackTemplate).filter(
        models.FeedbackTemplate.coach_id == current_user.id
    ).all()
    return templates

@app.post("/api/feedback-templates", response_model=schemas.FeedbackTemplate)
async def create_feedback_template(
    template: schemas.FeedbackTemplateCreate,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    db_template = models.FeedbackTemplate(**template.dict(), coach_id=current_user.id)
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    return db_template

@app.delete("/api/feedback-templates/{template_id}")
async def delete_feedback_template(
    template_id: int,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    template = db.query(models.FeedbackTemplate).filter(
        models.FeedbackTemplate.id == template_id,
        models.FeedbackTemplate.coach_id == current_user.id
    ).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    db.delete(template)
    db.commit()
    return {"message": "Template deleted"}
