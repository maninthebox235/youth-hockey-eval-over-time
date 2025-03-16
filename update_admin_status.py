"""
Quick script to update admin status for user lboehrig
"""
from app import create_app
from database.models import db, User

# Create Flask app with context
app = create_app()

with app.app_context():
    # Find the user
    username = "lboehrig"
    user = User.query.filter_by(username=username).first()
    
    if user:
        # Update admin status
        user.is_admin = True
        db.session.commit()
        print(f"User '{username}' is now an administrator.")
    else:
        print(f"User '{username}' not found.")