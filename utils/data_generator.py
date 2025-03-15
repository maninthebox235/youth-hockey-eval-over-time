import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from database.models import db, Player, PlayerHistory

def seed_database(n_players=20):
    """Seed the database with initial player data"""
    try:
        # Generate player data
        ages = np.random.randint(6, 19, n_players)
        names = [f"Player {i+1}" for i in range(n_players)]

        for i in range(n_players):
            player = Player(
                name=names[i],
                age=int(ages[i]),  # Convert numpy int to Python int
                age_group=f"U{(ages[i] // 2) * 2}",
                position=np.random.choice(['Forward', 'Defense', 'Goalie']),  # String is already Python string
                skating_speed=float(np.random.uniform(60, 100)),  # Convert numpy float
                shooting_accuracy=float(np.random.uniform(50, 95)),
                games_played=int(np.random.randint(10, 50)),  # Convert numpy int
                goals=int(np.random.randint(0, 30)),
                assists=int(np.random.randint(0, 40)),
                join_date=datetime.now() - timedelta(days=int(np.random.randint(30, 730)))
            )
            db.session.add(player)
            db.session.flush()  # Get the player ID

            # Generate historical data
            generate_player_history(player)

        db.session.commit()
        return True
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.session.rollback()
        return False

def clear_database():
    """Clear all players and related data from the database"""
    try:
        # The cascade delete will handle related records
        Player.query.delete()
        db.session.commit()
        return True
    except Exception as e:
        print(f"Error clearing database: {e}")
        db.session.rollback()
        return False

def generate_player_history(player, months=12):
    """Generate historical data for a player"""
    dates = pd.date_range(end=datetime.now(), periods=months, freq='ME')

    for i, date in enumerate(dates):
        history = PlayerHistory(
            player_id=player.id,
            date=date.date(),
            skating_speed=float(70 + (20 * i/months) + np.random.normal(0, 2)),
            shooting_accuracy=float(60 + (25 * i/months) + np.random.normal(0, 3)),
            games_played=int(np.random.randint(2, 6)),
            goals=int(np.random.randint(0, 3)),
            assists=int(np.random.randint(0, 4))
        )
        db.session.add(history)

def get_players_df():
    """Get all players as a pandas DataFrame"""
    try:
        players = Player.query.all()
        if not players:
            return pd.DataFrame()  # Return empty DataFrame if no players

        data = [{
            'player_id': p.id,
            'name': p.name,
            'age': p.age,
            'age_group': p.age_group,
            'position': p.position,
            'skating_speed': float(p.skating_speed) if p.skating_speed is not None else None,
            'shooting_accuracy': float(p.shooting_accuracy) if p.shooting_accuracy is not None else None,
            'save_percentage': float(p.save_percentage) if p.save_percentage is not None else None,
            'reaction_time': float(p.reaction_time) if p.reaction_time is not None else None,
            'positioning': float(p.positioning) if p.positioning is not None else None,
            'games_played': int(p.games_played),
            'goals': int(p.goals) if p.goals is not None else 0,
            'assists': int(p.assists) if p.assists is not None else 0,
            'goals_against': int(p.goals_against) if p.goals_against is not None else 0,
            'saves': int(p.saves) if p.saves is not None else 0,
            'join_date': p.join_date
        } for p in players]
        return pd.DataFrame(data)
    except Exception as e:
        print(f"Error getting players data: {e}")
        return pd.DataFrame()

def get_player_history(player_id):
    """Get historical data for a specific player"""
    try:
        # Get player position first
        player = Player.query.get(int(player_id))
        if not player:
            return pd.DataFrame()

        history = PlayerHistory.query.filter_by(player_id=player_id).order_by(PlayerHistory.date).all()
        if not history:
            return pd.DataFrame()

        data = [{
            'date': h.date,
            'skating_speed': float(h.skating_speed) if h.skating_speed is not None else None,
            'shooting_accuracy': float(h.shooting_accuracy) if h.shooting_accuracy is not None else None,
            'save_percentage': float(h.save_percentage) if h.save_percentage is not None else None,
            'reaction_time': float(h.reaction_time) if h.reaction_time is not None else None,
            'positioning': float(h.positioning) if h.positioning is not None else None,
            'games_played': int(h.games_played),
            'goals': int(h.goals) if h.goals is not None else 0,
            'assists': int(h.assists) if h.assists is not None else 0,
            'goals_against': int(h.goals_against) if h.goals_against is not None else 0,
            'saves': int(h.saves) if h.saves is not None else 0
        } for h in history]

        # Convert to DataFrame and ensure date column is datetime
        df = pd.DataFrame(data)
        if not df.empty:
            df['date'] = pd.to_datetime(df['date'])
        return df
    except Exception as e:
        print(f"Error getting player history: {e}")
        return pd.DataFrame()