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
                position=np.random.choice(['Forward', 'Defense', 'Goalie']).item(),  # Convert numpy string
                skating_speed=float(np.random.uniform(60, 100)),  # Convert numpy float
                shooting_accuracy=float(np.random.uniform(50, 95)),
                games_played=int(np.random.randint(10, 50)),
                goals=int(np.random.randint(0, 30)),
                assists=int(np.random.randint(0, 40)),
                join_date=datetime.now() - timedelta(days=np.random.randint(30, 730))
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
            player_id=int(player.id),  # Ensure Python int
            date=date.date(),  # Convert to date object
            skating_speed=float(70 + (20 * i/months) + float(np.random.normal(0, 2))),
            shooting_accuracy=float(60 + (25 * i/months) + float(np.random.normal(0, 3))),
            games_played=int(np.random.randint(2, 6).item()),
            goals=int(np.random.randint(0, 3).item()),
            assists=int(np.random.randint(0, 4).item())
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
            'skating_speed': float(p.skating_speed),
            'shooting_accuracy': float(p.shooting_accuracy),
            'games_played': int(p.games_played),
            'goals': int(p.goals),
            'assists': int(p.assists),
            'join_date': p.join_date
        } for p in players]
        return pd.DataFrame(data)
    except Exception as e:
        print(f"Error getting players data: {e}")
        return pd.DataFrame()

def get_player_history(player_id):
    """Get historical data for a specific player"""
    try:
        # Convert numpy.int64 to Python int
        player_id = int(player_id)
        history = PlayerHistory.query.filter_by(player_id=player_id).order_by(PlayerHistory.date).all()
        if not history:
            return pd.DataFrame()

        data = [{
            'date': h.date,
            'skating_speed': float(h.skating_speed),
            'shooting_accuracy': float(h.shooting_accuracy),
            'games_played': int(h.games_played),
            'goals': int(h.goals),
            'assists': int(h.assists)
        } for h in history]

        # Convert to DataFrame and ensure date column is datetime
        df = pd.DataFrame(data)
        if not df.empty:
            df['date'] = pd.to_datetime(df['date'])
        return df
    except Exception as e:
        print(f"Error getting player history: {e}")
        return pd.DataFrame()