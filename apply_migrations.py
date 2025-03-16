
import os
from flask import Flask
from flask_migrate import Migrate, upgrade
from sqlalchemy import inspect
from database.models import db

app = Flask(__name__)

# Database configuration
database_url = os.environ.get('DATABASE_URL')
if not database_url:
    database_url = input("Enter your database URL: ")
    
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)

# Initialize migrations
migrate = Migrate(app, db)

def check_columns_exist():
    """Check if required columns exist in the players table"""
    with app.app_context():
        inspector = inspect(db.engine)
        columns = inspector.get_columns('players')
        column_names = [col['name'] for col in columns]
        
        print("Existing columns in players table:")
        for name in column_names:
            print(f"- {name}")
            
        # Check for specific columns that were recently added
        needed_columns = [
            'edge_control', 'agility', 'backward_skating', 'puck_control', 
            'passing_accuracy', 'receiving', 'stick_protection', 'decision_making',
            'game_awareness', 'hockey_sense', 'wrist_shot', 'slap_shot',
            'one_timer', 'shot_accuracy', 'gap_control', 'physicality',
            'shot_blocking', 'breakout_passes', 'save_technique', 'rebound_control',
            'puck_handling', 'recovery', 'glove_saves', 'blocker_saves',
            'post_integration'
        ]
        
        missing_columns = [col for col in needed_columns if col not in column_names]
        
        if missing_columns:
            print("\nMISSING COLUMNS:")
            for col in missing_columns:
                print(f"- {col}")
            return False
        else:
            print("\nAll required columns exist in the players table.")
            return True

if __name__ == "__main__":
    with app.app_context():
        try:
            # Get user input for recovery mode
            import sys
            reset_db = False
            if len(sys.argv) > 1 and sys.argv[1] == '--reset':
                response = input("WARNING: This will reset ALL data. Continue? (y/n): ")
                if response.lower() == 'y':
                    reset_db = True
                    print("Resetting database...")
                    # Drop all tables
                    db.drop_all()
                    print("All tables dropped.")
            
            print("Rolling back any failed transactions...")
            db.session.rollback()
            
            print("\nRunning database migrations...")
            upgrade()
            print("Migrations completed.")
            
            print("\nChecking database schema...")
            columns_exist = check_columns_exist()
            
            print("\nCommitting session...")
            db.session.commit()
            
            if columns_exist:
                print("Migration successful! All required columns exist.")
            else:
                print("WARNING: Some required columns are missing. Check migration files.")
                print("You may need to run with --reset flag to completely rebuild the database.")
                
        except Exception as e:
            print(f"\nERROR: Migration failed: {str(e)}")
            db.session.rollback()
            import traceback
            print(traceback.format_exc())
            print("\nTry running with --reset flag to completely rebuild the database.")
            print("WARNING: This will delete all existing data.")
            print("Command: python apply_migrations.py --reset")
