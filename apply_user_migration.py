from flask import Flask
from database import db
import psycopg2
import os
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def apply_migration():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URL", "postgresql://postgres:postgres@localhost/hockey_dev"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)

    with app.app_context():
        # Check if column already exists
        try:
            conn = psycopg2.connect(
                os.getenv(
                    "DATABASE_URL",
                    "postgresql://postgres:postgres@localhost/hockey_dev",
                )
            )
            cursor = conn.cursor()
            cursor.execute(
                "SELECT column_name FROM information_schema.columns WHERE table_name='players' AND column_name='user_id';"
            )
            column_exists = cursor.fetchone() is not None
            cursor.close()
            conn.close()

            if column_exists:
                logger.info("Column user_id already exists in players table")
            else:
                # Add column directly using SQL
                conn = psycopg2.connect(
                    os.getenv(
                        "DATABASE_URL",
                        "postgresql://postgres:postgres@localhost/hockey_dev",
                    )
                )
                cursor = conn.cursor()
                cursor.execute("ALTER TABLE players ADD COLUMN user_id INTEGER;")
                cursor.execute(
                    "ALTER TABLE players ADD CONSTRAINT players_user_id_fkey FOREIGN KEY (user_id) REFERENCES users (id);"
                )
                conn.commit()
                cursor.close()
                conn.close()
                logger.info("Successfully added user_id column to players table")

            return True
        except Exception as e:
            logger.error(f"Error applying migration: {e}")
            return False


if __name__ == "__main__":
    success = apply_migration()
    sys.exit(0 if success else 1)
