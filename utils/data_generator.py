import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def generate_mock_players(n_players=20):
    ages = np.random.randint(6, 19, n_players)
    names = [f"Player {i+1}" for i in range(n_players)]
    
    data = {
        'player_id': range(1, n_players + 1),
        'name': names,
        'age': ages,
        'age_group': [f"U{(age // 2) * 2}" for age in ages],
        'position': np.random.choice(['Forward', 'Defense', 'Goalie'], n_players),
        'skating_speed': np.random.uniform(60, 100, n_players),
        'shooting_accuracy': np.random.uniform(50, 95, n_players),
        'games_played': np.random.randint(10, 50, n_players),
        'goals': np.random.randint(0, 30, n_players),
        'assists': np.random.randint(0, 40, n_players),
        'join_date': [
            (datetime.now() - timedelta(days=np.random.randint(30, 730))).strftime('%Y-%m-%d')
            for _ in range(n_players)
        ]
    }
    
    return pd.DataFrame(data)

def generate_player_history(player_id, months=12):
    dates = pd.date_range(end=datetime.now(), periods=months, freq='M')
    
    data = {
        'date': dates,
        'skating_speed': np.linspace(70, 90, months) + np.random.normal(0, 2, months),
        'shooting_accuracy': np.linspace(60, 85, months) + np.random.normal(0, 3, months),
        'games_played': np.cumsum(np.random.randint(2, 6, months)),
        'goals': np.cumsum(np.random.randint(0, 3, months)),
        'assists': np.cumsum(np.random.randint(0, 4, months))
    }
    
    return pd.DataFrame(data)
