from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Player(db.Model):
    __tablename__ = 'players'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    age_group = db.Column(db.String(10), nullable=False)
    position = db.Column(db.String(20), nullable=False)
    join_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)

    # Latest metrics
    skating_speed = db.Column(db.Float)
    shooting_accuracy = db.Column(db.Float)
    games_played = db.Column(db.Integer, default=0)
    goals = db.Column(db.Integer, default=0)
    assists = db.Column(db.Integer, default=0)

    # Relationships
    history = db.relationship('PlayerHistory', backref='player', lazy=True)
    feedback = db.relationship('CoachFeedback', backref='player', lazy=True)

class PlayerHistory(db.Model):
    __tablename__ = 'player_history'

    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    skating_speed = db.Column(db.Float)
    shooting_accuracy = db.Column(db.Float)
    games_played = db.Column(db.Integer)
    goals = db.Column(db.Integer)
    assists = db.Column(db.Integer)

class CoachFeedback(db.Model):
    __tablename__ = 'coach_feedback'

    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'), nullable=False)
    coach_name = db.Column(db.String(100), nullable=False)
    feedback_text = db.Column(db.Text, nullable=False)
    skating_rating = db.Column(db.Integer)  # 1-5 rating
    shooting_rating = db.Column(db.Integer)  # 1-5 rating
    teamwork_rating = db.Column(db.Integer)  # 1-5 rating
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f'<CoachFeedback {self.id} for Player {self.player_id}>'