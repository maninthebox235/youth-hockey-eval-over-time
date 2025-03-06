from flask import Flask
from database import init_app, db
from flask_migrate import Migrate
from utils.data_generator import seed_database

# Initialize Flask app and database
app = init_app()
migrate = Migrate(app, db)

if __name__ == '__main__':
    with app.app_context():
        try:
            # Check if database needs seeding
            from database.models import Player
            if not Player.query.first():
                print("No players found, seeding database...")
                if seed_database(n_players=20):
                    print("Database seeded successfully")
                else:
                    print("Error seeding database")
            else:
                print("Database already contains data")

        except Exception as e:
            print(f"Error initializing database: {e}")
            raise

        # Run Flask on port 5001 to avoid conflict with Streamlit
        app.run(host='0.0.0.0', port=5001, debug=True)