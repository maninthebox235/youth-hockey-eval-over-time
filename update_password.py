from app import app
from database.models import User, db
from werkzeug.security import generate_password_hash


def update_password(username, new_password):
    """Update a user's password directly in the database"""
    with app.app_context():
        # Find the user
        user = User.query.filter_by(username=username).first()

        if not user:
            print(f"No user found with username: {username}")
            # Check if there are any users in the database
            users = User.query.all()
            print("Available users:")
            for u in users:
                print(f"Username: {u.username}, Name: {u.name}")

            # Create the user if they don't exist
            print(f"Creating new user with username: {username}")
            user = User(username=username, name="Luke Boehrig", is_admin=True)
            user.set_password(new_password)
            db.session.add(user)
            db.session.commit()
            print(f"Created new user: {username} with provided password")
            return True

        # Update the password
        password_hash = generate_password_hash(new_password)
        user.password_hash = password_hash

        # Clear any reset tokens
        user.reset_token = None
        user.reset_token_expiry = None

        # Commit the changes
        db.session.commit()
        print(f"Password updated successfully for user: {user.username} ({user.name})")
        return True


if __name__ == "__main__":
    # Define the username and new password
    username = "lboehrig"
    new_password = "Hockey2025!"

    update_password(username, new_password)
