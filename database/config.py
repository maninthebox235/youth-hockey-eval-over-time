import os
from flask import Flask
from flask_migrate import Migrate
from .models import db

def init_app():
    app = Flask(__name__)

    # Database configuration
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        raise ValueError("DATABASE_URL environment variable not set")

    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['FLASK_APP'] = 'app.py'

    # Initialize extensions
    db.init_app(app)

    return app