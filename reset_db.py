from app import app, db


def reset_database():
    """Reset the entire database and recreate all tables"""
    with app.app_context():
        # Drop all tables
        db.drop_all()

        # Recreate all tables
        db.create_all()

        print("Database reset successfully. All tables recreated.")


if __name__ == "__main__":
    reset_database()
