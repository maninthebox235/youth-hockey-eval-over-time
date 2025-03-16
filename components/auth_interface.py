
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
        col1, col2 = st.columns([1, 2])
        with col1:
            remember_me = st.checkbox("Remember Me", value=True, 
                                     help="Keep me logged in for 30 days")
        with col2:
            submitted = st.form_submit_button("Login", use_container_width=True)
        
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
                try:
                    # Set token expiration based on "Remember Me"
                    expiration = 30 * 24 * 3600 if remember_me else 24 * 3600  # 30 days or 1 day
                    token = user.get_auth_token(expiration=expiration)
                    if not token:
                        st.error("Failed to generate authentication token")
                        return
                    
                    # Set session state
                    st.session_state.authentication_token = token
                    st.session_state.remember_me = remember_me
                    st.query_params["auth_token"] = token
                except Exception as e:
                    logging.error(f"Token generation error: {str(e)}")
                    # Continue without token - at least allow session-based auth
                    token = None
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
            # Check if user is a dictionary (expected) or use safe access
            user_name = st.session_state.user.get('name', 'User') if isinstance(st.session_state.user, dict) else 'User'
            is_admin = st.session_state.user.get('is_admin', False) if isinstance(st.session_state.user, dict) else False
            
            # User profile container
            with st.container():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"👤 Welcome, **{user_name}**")
                    
                    # Display status icons
                    status_icons = []
                    if is_admin:
                        status_icons.append("🔑 **Admin Access**")
                    
                    # Show session type
                    if 'remember_me' in st.session_state and st.session_state.remember_me:
                        status_icons.append("📌 **Extended Session** (30 days)")
                    else:
                        status_icons.append("⏱️ **Standard Session** (24 hours)")
                    
                    # Display all status icons
                    for icon in status_icons:
                        st.write(icon)
                
                with col2:
                    if st.button("Logout", use_container_width=True):
                        # Clear session state
                        st.session_state.clear()
                        # Clear URL parameters
                        st.query_params.clear()
                        # Redirect to login page
                        st.info("Logging out...")
                        st.rerun()
            
            # Add a horizontal rule for visual separation
            st.markdown("---")
