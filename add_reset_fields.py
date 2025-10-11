from app import app
from database.models import db


def add_reset_fields():
    """Add password reset fields to users table"""
    with app.app_context():
        try:
            db.engine.execute(
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS reset_token VARCHAR(256)"
            )
            db.engine.execute(
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS reset_token_expiry TIMESTAMP"
            )
            print("Added reset token fields to users table")
        except Exception as e:
            print(f"Error adding reset token fields: {str(e)}")

            # Alternative approach using SQLAlchemy core
            from sqlalchemy import text

            try:
                db.session.execute(
                    text(
                        "ALTER TABLE users ADD COLUMN IF NOT EXISTS reset_token VARCHAR(256)"
                    )
                )
                db.session.execute(
                    text(
                        "ALTER TABLE users ADD COLUMN IF NOT EXISTS reset_token_expiry TIMESTAMP"
                    )
                )
                db.session.commit()
                print("Added reset token fields to users table using SQLAlchemy")
            except Exception as e:
                print(f"Error with SQLAlchemy approach: {str(e)}")
                db.session.rollback()


if __name__ == "__main__":
    add_reset_fields()
