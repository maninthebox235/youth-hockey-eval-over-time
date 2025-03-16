"""
Script to run the coach feedback migration
"""
from database.models import db
from flask import Flask
import os
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

def run_migration():
    """Run the coach feedback rating migration"""
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    
    with app.app_context():
        try:
            # Add columns directly with SQL
            columns_to_add = [
                "skating_speed_rating INTEGER",
                "backward_skating_rating INTEGER",
                "agility_rating INTEGER",
                "edge_control_rating INTEGER",
                "puck_control_rating INTEGER",
                "passing_accuracy_rating INTEGER",
                "shooting_accuracy_rating INTEGER",
                "receiving_rating INTEGER",
                "stick_protection_rating INTEGER",
                "hockey_sense_rating INTEGER",
                "decision_making_rating INTEGER",
                "game_awareness_rating INTEGER",
                "compete_level_rating INTEGER",
                "offensive_ability_rating INTEGER",
                "defensive_ability_rating INTEGER",
                "net_front_rating INTEGER",
                "gap_control_rating INTEGER",
                "recovery_rating INTEGER",
                "puck_handling_rating INTEGER",
                "communication_rating INTEGER"
            ]
            
            for column in columns_to_add:
                col_name = column.split()[0]
                col_type = column.split()[1]
                
                # Check if column exists before adding
                check_column_query = text(f"""
                    SELECT EXISTS (
                        SELECT 1 
                        FROM information_schema.columns 
                        WHERE table_name='coach_feedback' AND column_name='{col_name}'
                    )
                """)
                column_exists = db.session.execute(check_column_query).scalar()
                
                if not column_exists:
                    print(f"Adding column {col_name}...")
                    add_column_query = text(f"ALTER TABLE coach_feedback ADD COLUMN IF NOT EXISTS {col_name} {col_type}")
                    db.session.execute(add_column_query)
                else:
                    print(f"Column {col_name} already exists.")
            
            # Make teamwork_rating nullable
            make_nullable_query = text("""
                ALTER TABLE coach_feedback 
                ALTER COLUMN teamwork_rating DROP NOT NULL
            """)
            db.session.execute(make_nullable_query)
            
            db.session.commit()
            print("Successfully applied coach feedback ratings migration")
            
        except SQLAlchemyError as e:
            print(f"Error during migration: {e}")
            db.session.rollback()
        except Exception as e:
            print(f"Unexpected error: {e}")
            db.session.rollback()

if __name__ == "__main__":
    run_migration()