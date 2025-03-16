import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from database.models import db, Player, PlayerHistory
from utils.type_converter import to_int, to_float, to_datetime, to_date, to_str

def seed_database(n_players=20):
    """Seed the database with initial player data"""
    try:
        # Generate player data
        ages = np.random.randint(6, 19, n_players)
        names = [f"Player {i+1}" for i in range(n_players)]

        for i in range(n_players):
            # Use our conversion utilities for consistent type handling
            age = to_int(ages[i])
            player = Player(
                name=names[i],
                age=age,
                age_group=f"U{(age // 2) * 2}",  # Age group calculation with Python int
                position=to_str(np.random.choice(['Forward', 'Defense', 'Goalie'])),
                skating_speed=to_float(np.random.uniform(60, 100)),
                shooting_accuracy=to_float(np.random.uniform(50, 95)),
                games_played=to_int(np.random.randint(10, 50)),
                goals=to_int(np.random.randint(0, 30)),
                assists=to_int(np.random.randint(0, 40)),
                join_date=to_datetime(datetime.now() - timedelta(days=to_int(np.random.randint(30, 730))))
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

def generate_player_history(player, months=12):
    """Generate historical data for a player"""
    dates = pd.date_range(end=datetime.now(), periods=months, freq='ME')

    for i, date in enumerate(dates):
        history = PlayerHistory(
            player_id=to_int(player.id),
            date=to_date(date),
            skating_speed=to_float(70 + (20 * i/months) + np.random.normal(0, 2)),
            shooting_accuracy=to_float(60 + (25 * i/months) + np.random.normal(0, 3)),
            games_played=to_int(np.random.randint(2, 6)),
            goals=to_int(np.random.randint(0, 3)),
            assists=to_int(np.random.randint(0, 4))
        )
        db.session.add(history)

def get_players_df(user_id=None):
    """
    Get players as a pandas DataFrame, filtered by user_id if provided
    
    Args:
        user_id: Optional user ID to filter players by owner
        
    Returns:
        DataFrame containing player data
    """
    try:
        # Convert user_id if provided
        if user_id is not None:
            user_id = to_int(user_id)
            players = Player.query.filter_by(user_id=user_id).all()
        else:
            players = Player.query.all()
            
        if not players:
            return pd.DataFrame()  # Return empty DataFrame if no players

        data = [{
            'player_id': to_int(p.id),
            'name': p.name,
            'age': to_int(p.age),
            'age_group': p.age_group,
            'position': p.position,
            'skating_speed': to_float(p.skating_speed),
            'shooting_accuracy': to_float(p.shooting_accuracy),
            'save_percentage': to_float(p.save_percentage),
            'reaction_time': to_float(p.reaction_time),
            'positioning': to_float(p.positioning),
            'games_played': to_int(p.games_played) or 0,
            'goals': to_int(p.goals) or 0,
            'assists': to_int(p.assists) or 0,
            'goals_against': to_int(p.goals_against) or 0,
            'saves': to_int(p.saves) or 0,
            'join_date': to_datetime(p.join_date)
        } for p in players]

        return pd.DataFrame(data)
    except Exception as e:
        print(f"Error getting players data: {e}")
        return pd.DataFrame()

def get_player_history(player_id):
    """Get historical data for a specific player"""
    try:
        # Convert player_id to Python int using our utility function
        player_id = to_int(player_id)
        if player_id is None:
            print("Invalid player_id: None after conversion")
            return pd.DataFrame()

        # Query the player
        player = Player.query.get(player_id)
        if not player:
            print(f"Player not found for ID: {player_id}")
            return pd.DataFrame()

        # Get history records
        history = PlayerHistory.query.filter_by(player_id=player_id).order_by(PlayerHistory.date).all()
        if not history:
            print(f"No history found for player ID: {player_id}")
            return pd.DataFrame()

        data = [{
            'date': to_date(h.date),
            'skating_speed': to_float(h.skating_speed),
            'shooting_accuracy': to_float(h.shooting_accuracy),
            'save_percentage': to_float(h.save_percentage),
            'reaction_time': to_float(h.reaction_time),
            'positioning': to_float(h.positioning),
            'games_played': to_int(h.games_played) or 0,  # Use 0 as fallback
            'goals': to_int(h.goals) or 0,
            'assists': to_int(h.assists) or 0,
            'goals_against': to_int(h.goals_against) or 0,
            'saves': to_int(h.saves) or 0
        } for h in history]

        # Convert to DataFrame and ensure date column is datetime
        df = pd.DataFrame(data)
        if not df.empty:
            df['date'] = pd.to_datetime(df['date'])
        return df
    except Exception as e:
        print(f"Error getting player history: {e}")
        return pd.DataFrame()

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