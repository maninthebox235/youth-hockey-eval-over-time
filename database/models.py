from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class TeamMembership(db.Model):
    __tablename__ = 'team_membership'

    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    join_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    position_in_team = db.Column(db.String(20))
    is_active = db.Column(db.Boolean, default=True)

    # Add relationships to both sides
    player = db.relationship('Player', back_populates='memberships')
    team = db.relationship('Team', back_populates='memberships')

class Team(db.Model):
    __tablename__ = 'teams'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age_group = db.Column(db.String(10), nullable=False)
    created_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Team statistics
    games_played = db.Column(db.Integer, default=0)
    wins = db.Column(db.Integer, default=0)
    losses = db.Column(db.Integer, default=0)

    # Update relationships
    memberships = db.relationship('TeamMembership', back_populates='team', lazy='dynamic')
    players = db.relationship('Player', 
                            secondary='team_membership',
                            back_populates='teams',
                            lazy='dynamic')

class Player(db.Model):
    __tablename__ = 'players'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    age_group = db.Column(db.String(10), nullable=False)
    position = db.Column(db.String(20), nullable=False)
    join_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Latest metrics
    skating_speed = db.Column(db.Float)
    shooting_accuracy = db.Column(db.Float)
    games_played = db.Column(db.Integer, default=0)
    goals = db.Column(db.Integer, default=0)
    assists = db.Column(db.Integer, default=0)

    # Update relationships
    memberships = db.relationship('TeamMembership', back_populates='player', lazy='dynamic')
    teams = db.relationship('Team', 
                          secondary='team_membership',
                          back_populates='players',
                          lazy='dynamic')
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
    skating_rating = db.Column(db.Integer)
    shooting_rating = db.Column(db.Integer)
    teamwork_rating = db.Column(db.Integer)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

class TeamCoachFeedback(db.Model):
    __tablename__ = 'team_coach_feedback'

    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    coach_name = db.Column(db.String(100), nullable=False)
    feedback_text = db.Column(db.Text, nullable=False)
    teamwork_rating = db.Column(db.Integer)
    strategy_rating = db.Column(db.Integer)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f'<TeamCoachFeedback {self.id} for Team {self.team_id}>'