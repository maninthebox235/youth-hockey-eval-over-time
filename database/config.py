import os
from flask import Flask
from flask_migrate import Migrate
from .models import db

def init_app():
    app = Flask(__name__)

    # Database configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['FLASK_APP'] = 'app.py'

    # Initialize extensions
    db.init_app(app)

    with app.app_context():
        # Import migrations
        migrate = Migrate(app, db)

        try:
            # Initialize database tables
            db.create_all()
            print("Database tables created successfully")
        except Exception as e:
            print(f"Error creating database tables: {e}")

    return app