
import secrets
import hashlib
from datetime import datetime, timedelta
from database.models import db, User

def generate_reset_token(user):
    """Generate a secure reset token and store its hash in the database"""
    # Generate a secure random token
    token = secrets.token_hex(32)
    
    # Hash the token for secure storage
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    
    # Set expiration time (24 hours from now)
    expiry = datetime.utcnow() + timedelta(hours=24)
    
    # Store the hashed token in the user record
    user.reset_token = token_hash
    user.reset_token_expiry = expiry
    db.session.commit()
    
    return token

def verify_reset_token(token, username):
    """Verify if the reset token is valid for the given user"""
    if not token or not username:
        return None
    
    # Find the user by username
    user = User.query.filter_by(username=username).first()
    if not user or not user.reset_token or not user.reset_token_expiry:
        return None
    
    # Check if token has expired
    if datetime.utcnow() > user.reset_token_expiry:
        # Clear expired token
        user.reset_token = None
        user.reset_token_expiry = None
        db.session.commit()
        return None
    
    # Hash the provided token and compare with stored hash
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    if token_hash != user.reset_token:
        return None
    
    return user
