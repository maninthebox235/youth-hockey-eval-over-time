import streamlit as st
from database.models import User, db
from datetime import datetime

def login_user():
    """Handle user login"""
    st.header("Login")

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

        if submitted:
            if not username or not password:
                st.error("Please enter both username and password")
                return

            try:
                user = User.query.filter_by(username=username).first()
                if not user or not user.check_password(password):
                    st.error("Invalid username or password")
                    return

                # Update last login time
                user.last_login = datetime.utcnow()
                db.session.commit()

                # Generate authentication token
                from app import app
                with app.app_context():
                    token = user.get_auth_token()

                if token:
                    # Store token in both session state and URL
                    st.session_state.authentication_token = token
                    st.query_params["auth_token"] = token

                    # Set user info in session state
                    st.session_state.user = {
                        'id': user.id,
                        'username': user.username,
                        'name': user.name,
                        'is_admin': user.is_admin
                    }
                    st.session_state.is_admin = user.is_admin
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Authentication failed")

            except Exception as e:
                print(f"Login error: {str(e)}")
                st.error("Login failed. Please try again.")
                db.session.rollback()

def display_auth_interface():
    """Main authentication interface"""
    # Display login form if not authenticated
    if not st.session_state.user:
        login_user()
    else:
        # Show user info and logout button in sidebar
        with st.sidebar:
            st.write(f"Welcome, {st.session_state.user['name']}")
            if st.button("Logout"):
                # Clear all session state and URL parameters
                st.session_state.user = None
                st.session_state.is_admin = None
                st.session_state.authentication_token = None
                st.query_params.clear()
                st.rerun()