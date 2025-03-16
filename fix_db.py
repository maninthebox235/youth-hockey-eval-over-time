
from app import app, db
from database.models import User
from sqlalchemy import text

def fix_database():
    """Fix database schema by recreating the users table"""
    with app.app_context():
        # Drop and recreate users table
        db.session.execute(text("DROP TABLE IF EXISTS users CASCADE"))
        
        # Create new users table with proper schema
        db.session.execute(text("""
        CREATE TABLE users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) NOT NULL UNIQUE,
            password_hash VARCHAR(256),
            name VARCHAR(100) NOT NULL,
            is_admin BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP,
            last_login TIMESTAMP
        )
        """))
        
        db.session.commit()
        print("Users table recreated successfully")

if __name__ == "__main__":
    fix_database()
