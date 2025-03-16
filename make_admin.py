"""
Script to make a user an administrator
"""
import os
import sys
from sqlalchemy.exc import SQLAlchemyError

# Import the app, db, and models from the main application
from app import create_app
from database.models import db, User

# Create the app
app = create_app()

def make_user_admin(username):
    """
    Make a user an administrator
    
    Args:
        username: Username of the user to make admin
        
    Returns:
        bool: True if successful, False otherwise
    """
    with app.app_context():
        try:
            # Find the user
            user = User.query.filter_by(username=username).first()
            
            if not user:
                print(f"Error: User '{username}' not found.")
                return False
                
            # Set the user as admin
            user.is_admin = True
            db.session.commit()
            
            print(f"User '{username}' is now an administrator.")
            return True
            
        except SQLAlchemyError as e:
            db.session.rollback()
            print(f"Database error: {str(e)}")
            return False
        except Exception as e:
            print(f"Error: {str(e)}")
            return False

if __name__ == "__main__":
    # Allow passing username as command line argument
    if len(sys.argv) > 1:
        username = sys.argv[1]
    else:
        username = "lboehrig"  # Default to making lboehrig an admin
        
    make_user_admin(username)