from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer as Serializer
import time
from flask import current_app
import os

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    name = db.Column(db.String(100), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    # Password reset fields
    reset_token = db.Column(db.String(256), nullable=True)
    reset_token_expiry = db.Column(db.DateTime, nullable=True)

    # Relationship with feedback
    feedback_given = db.relationship('CoachFeedback', backref='coach', lazy=True,
                                   foreign_keys='CoachFeedback.coach_id')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_auth_token(self, expiration=2592000):  # 30 days default
        s = Serializer(current_app.config['SECRET_KEY'])
        token = s.dumps({'user_id': self.id, 'exp': int(time.time()) + expiration})
        # Handle both string and bytes return types from dumps()
        if isinstance(token, bytes):
            return token.decode('utf-8')
        return token

    @staticmethod
    def verify_auth_token(token):
        """Verify the authentication token"""
        if not token:
            print("No token provided for verification")
            return None

        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            print(f"Attempting to verify token: {token[:10]}...") # Print first part of token for debugging
            data = s.loads(token)

            #Improved type checking and error handling
            if not isinstance(data, dict):
                print(f"Error: Invalid token data type: {type(data)}. Token: {token}")
                return None

            print(f"Token data loaded successfully: {list(data.keys())}")

            user_id = data.get('user_id')
            if user_id is None:
                print("Error: 'user_id' not found in token data. Token: {token}")
                return None

            user = User.query.get(user_id)
            if user:
                print(f"User found with ID {user_id}: {user.username}")
            else:
                print(f"No user found with ID {user_id}")
            return user
        except Exception as e:
            print(f"Token verification exception: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

class CoachFeedback(db.Model):
    __tablename__ = 'coach_feedback'

    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'), nullable=False)
    coach_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    coach_name = db.Column(db.String(100), nullable=False)
    feedback_text = db.Column(db.Text, nullable=False)

    # Position-specific ratings
    skating_rating = db.Column(db.Integer, nullable=True)
    shooting_rating = db.Column(db.Integer, nullable=True)
    teamwork_rating = db.Column(db.Integer)

    # Goalie-specific ratings
    save_technique_rating = db.Column(db.Integer, nullable=True)
    positioning_rating = db.Column(db.Integer, nullable=True)
    rebound_control_rating = db.Column(db.Integer, nullable=True)

    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

class TeamMembership(db.Model):
    __tablename__ = 'team_membership'

    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    join_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    position_in_team = db.Column(db.String(20))
    is_active = db.Column(db.Boolean, default=True)

    player = db.relationship('Player', back_populates='memberships')
    team = db.relationship('Team', back_populates='memberships')

class Team(db.Model):
    __tablename__ = 'teams'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age_group = db.Column(db.String(10), nullable=False)
    created_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    games_played = db.Column(db.Integer, default=0)
    wins = db.Column(db.Integer, default=0)
    losses = db.Column(db.Integer, default=0)

    memberships = db.relationship('TeamMembership', back_populates='team', lazy='dynamic')
    players = db.relationship('Player', 
                            secondary='team_membership',
                            back_populates='teams',
                            lazy='dynamic',
                            overlaps="memberships,team,player")

class Player(db.Model):
    __tablename__ = 'players'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    age_group = db.Column(db.String(10), nullable=False)
    position = db.Column(db.String(20), nullable=False)
    join_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Player metrics based on position
    # Skater metrics
    skating_speed = db.Column(db.Float, nullable=True)
    shooting_accuracy = db.Column(db.Float, nullable=True)

    # Goalie metrics
    save_percentage = db.Column(db.Float, nullable=True)
    reaction_time = db.Column(db.Float, nullable=True)
    positioning = db.Column(db.Float, nullable=True)

    # Common stats
    games_played = db.Column(db.Integer, default=0)
    goals = db.Column(db.Integer, default=0)
    assists = db.Column(db.Integer, default=0)

    # For goalies: goals against and saves
    goals_against = db.Column(db.Integer, default=0)
    saves = db.Column(db.Integer, default=0)

    memberships = db.relationship('TeamMembership', back_populates='player', lazy='dynamic')
    teams = db.relationship('Team', 
                          secondary='team_membership',
                          back_populates='players',
                          lazy='dynamic',
                          overlaps="memberships,player,team")
    history = db.relationship('PlayerHistory', backref='player', lazy=True)
    feedback = db.relationship('CoachFeedback', backref='player', lazy=True)

class PlayerHistory(db.Model):
    __tablename__ = 'player_history'

    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)

    # Skater metrics
    skating_speed = db.Column(db.Float, nullable=True)
    shooting_accuracy = db.Column(db.Float, nullable=True)

    # Goalie metrics
    save_percentage = db.Column(db.Float, nullable=True)
    reaction_time = db.Column(db.Float, nullable=True)
    positioning = db.Column(db.Float, nullable=True)

    # Common stats
    games_played = db.Column(db.Integer)
    goals = db.Column(db.Integer)
    assists = db.Column(db.Integer)

    # Goalie specific stats
    goals_against = db.Column(db.Integer, nullable=True)
    saves = db.Column(db.Integer, nullable=True)

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

class FeedbackTemplate(db.Model):
    __tablename__ = 'feedback_templates'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    player_type = db.Column(db.String(20), nullable=False)  # 'Goalie' or 'Skater'
    created_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Template structure stored as JSON
    template_structure = db.Column(db.JSON, nullable=False)

    # Track template usage
    times_used = db.Column(db.Integer, default=0)
    last_used = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f'<FeedbackTemplate {self.name} for {self.player_type}>'