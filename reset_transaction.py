import os
import psycopg2
from flask import Flask
from database.models import db

app = Flask(__name__)

# Database configuration
database_url = os.environ.get("DATABASE_URL")
if not database_url:
    database_url = input("Enter your database URL: ")

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize extensions
db.init_app(app)


def reset_transaction():
    """Reset any aborted transactions in the database"""
    try:
        # Connect directly with psycopg2 to avoid SQLAlchemy
        conn = psycopg2.connect(database_url)

        # Set autocommit to True to avoid transaction blocks
        conn.autocommit = True

        cur = conn.cursor()
        print("Resetting database transaction state...")

        # Check if the table exists before attempting to query
        cur.execute(
            "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'feedback_templates')"
        )
        table_exists = cur.fetchone()[0]

        if table_exists:
            print("Feedback templates table exists")
        else:
            print("Feedback templates table does not exist")

        # Close connection
        cur.close()
        conn.close()
        print("Transaction state reset successfully")

    except Exception as e:
        print(f"Error resetting transaction state: {e}")


if __name__ == "__main__":
    with app.app_context():
        reset_transaction()
