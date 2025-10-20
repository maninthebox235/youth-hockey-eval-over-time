from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid

app = FastAPI()

# Disable CORS. Do not remove this for full-stack development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

players_db = {}
evaluations_db = {}

class Player(BaseModel):
    id: Optional[str] = None
    name: str
    jersey_number: Optional[int] = None
    position: Optional[str] = None
    age_group: Optional[str] = None
    team: Optional[str] = None

class SkillRating(BaseModel):
    skating: int
    shooting: int
    passing: int
    puck_handling: int
    hockey_iq: int
    physicality: int

class Evaluation(BaseModel):
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

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

@app.get("/api/players", response_model=List[Player])
async def get_players():
    return list(players_db.values())

@app.post("/api/players", response_model=Player)
async def create_player(player: Player):
    player.id = str(uuid.uuid4())
    players_db[player.id] = player
    return player

@app.get("/api/players/{player_id}", response_model=Player)
async def get_player(player_id: str):
    if player_id not in players_db:
        raise HTTPException(status_code=404, detail="Player not found")
    return players_db[player_id]

@app.put("/api/players/{player_id}", response_model=Player)
async def update_player(player_id: str, player: Player):
    if player_id not in players_db:
        raise HTTPException(status_code=404, detail="Player not found")
    player.id = player_id
    players_db[player_id] = player
    return player

@app.delete("/api/players/{player_id}")
async def delete_player(player_id: str):
    if player_id not in players_db:
        raise HTTPException(status_code=404, detail="Player not found")
    del players_db[player_id]
    return {"message": "Player deleted"}

@app.get("/api/evaluations", response_model=List[Evaluation])
async def get_evaluations(player_id: Optional[str] = None):
    if player_id:
        return [e for e in evaluations_db.values() if e.player_id == player_id]
    return list(evaluations_db.values())

@app.post("/api/evaluations", response_model=Evaluation)
async def create_evaluation(evaluation: Evaluation):
    evaluation.id = str(uuid.uuid4())
    evaluation.date = datetime.now().isoformat()
    evaluations_db[evaluation.id] = evaluation
    return evaluation

@app.get("/api/evaluations/{evaluation_id}", response_model=Evaluation)
async def get_evaluation(evaluation_id: str):
    if evaluation_id not in evaluations_db:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    return evaluations_db[evaluation_id]

@app.put("/api/evaluations/{evaluation_id}", response_model=Evaluation)
async def update_evaluation(evaluation_id: str, evaluation: Evaluation):
    if evaluation_id not in evaluations_db:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    evaluation.id = evaluation_id
    evaluations_db[evaluation_id] = evaluation
    return evaluation

@app.delete("/api/evaluations/{evaluation_id}")
async def delete_evaluation(evaluation_id: str):
    if evaluation_id not in evaluations_db:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    del evaluations_db[evaluation_id]
    return {"message": "Evaluation deleted"}

@app.post("/api/sync")
async def sync_data(data: dict):
    if "players" in data:
        for player_data in data["players"]:
            player = Player(**player_data)
            if not player.id:
                player.id = str(uuid.uuid4())
            players_db[player.id] = player
    
    if "evaluations" in data:
        for eval_data in data["evaluations"]:
            evaluation = Evaluation(**eval_data)
            if not evaluation.id:
                evaluation.id = str(uuid.uuid4())
            evaluations_db[evaluation.id] = evaluation
    
    return {
        "players": list(players_db.values()),
        "evaluations": list(evaluations_db.values())
    }
