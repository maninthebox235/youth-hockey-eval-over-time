from flask import Flask
from database import init_app, db
from flask_migrate import Migrate

app = init_app()
migrate = Migrate(app, db)

if __name__ == '__main__':
    with app.app_context():
        try:
            # Initialize database
            db.create_all()
            print("Database initialized successfully")
        except Exception as e:
            print(f"Error initializing database: {e}")

        # Run Flask on port 5001 to avoid conflict with Streamlit
        app.run(host='0.0.0.0', port=5001, debug=True)