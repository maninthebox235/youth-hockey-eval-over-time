from flask import Flask
from flask_migrate import Migrate
from database.models import db
import os

app = Flask(__name__)

# Database configuration
database_url = os.environ.get("DATABASE_URL")
if not database_url:
    database_url = input("Enter your database URL: ")

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize extensions
db.init_app(app)

# Initialize migrations
migrate = Migrate(app, db)

if __name__ == "__main__":
    with app.app_context():
        print("Running database migrations...")
        from flask_migrate import upgrade

        upgrade()
        print("Migrations completed successfully.")
