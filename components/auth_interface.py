
import streamlit as st
from database.models import User, db
from datetime import datetime
import logging

def login_user():
    """Handle user login"""
    st.header("Login")
    
    # Initialize session state
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'is_admin' not in st.session_state:
        st.session_state.is_admin = False
    if 'authentication_token' not in st.session_state:
        st.session_state.authentication_token = None
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        
        if submitted:
            if not username or not password:
                st.error("Please enter both username and password")
                return
            
            try:
                # Find user by username
                user = User.query.filter_by(username=username).first()
                
                # Check if user exists and password is correct
                if not user:
                    st.error("User not found")
                    return
                    
                if not user.check_password(password):
                    st.error("Incorrect password")
                    return
                
                # Update last login time
                user.last_login = datetime.utcnow()
                db.session.commit()
                
                # Generate auth token
                token = user.get_auth_token()
                if not token:
                    st.error("Failed to generate authentication token")
                    return
                
                # Set session state
                st.session_state.authentication_token = token
                st.query_params["auth_token"] = token
                st.session_state.user = {
                    'id': user.id,
                    'username': user.username,
                    'name': user.name,
                    'is_admin': user.is_admin
                }
                st.session_state.is_admin = user.is_admin
                
                st.success("Login successful!")
                st.rerun()
            
            except Exception as e:
                logging.error(f"Login error: {str(e)}")
                st.error(f"Login failed: {str(e)}")
                db.session.rollback()
    
    # Add forgot password link
    st.markdown("[Forgot Password?](#)")
    
def request_password_reset():
    """Handle password reset requests"""
    st.header("Reset Password")
    
    with st.form("reset_password_form"):
        username = st.text_input("Username")
        submitted = st.form_submit_button("Send Reset Link")
        
        if submitted:
            if not username:
                st.error("Please enter your username")
                return
            
            try:
                user = User.query.filter_by(username=username).first()
                if user:
                    # In a real app, generate token and send email
                    st.success("If this account exists, a password reset link has been sent.")
                else:
                    # Don't reveal if account exists or not
                    st.success("If this account exists, a password reset link has been sent.")
            except Exception as e:
                logging.error(f"Password reset error: {str(e)}")
                st.error("An error occurred. Please try again later.")

def display_auth_interface():
    """Main authentication interface"""
    # Initialize user state if not present
    if 'user' not in st.session_state:
        st.session_state.user = None
        
    if not st.session_state.get('user'):
        login_user()
    else:
        with st.sidebar:
            st.write(f"Welcome, {st.session_state.user.get('name', 'User')}")
            if st.button("Logout"):
                st.session_state.clear()
                st.query_params.clear()
                st.rerun()
