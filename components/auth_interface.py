import streamlit as st
from database.models import User, db
from datetime import datetime
from werkzeug.security import generate_password_hash
import time

def init_session_state():
    """Initialize session state variables"""
    if 'user' not in st.session_state:
        # Try to load from existing token first
        if 'authentication_token' in st.session_state and st.session_state.authentication_token:
            try:
                # Import current app
                from app import app

                # Verify token with explicit app context
                with app.app_context():
                    user = User.verify_auth_token(st.session_state.authentication_token)

                if user and user.id:
                    st.session_state.user = {
                        'id': user.id,
                        'username': user.username,
                        'name': user.name,
                        'is_admin': user.is_admin
                    }
                    st.session_state.is_admin = user.is_admin
                    return
            except Exception as e:
                print(f"Session token verification error: {str(e)}")
        st.session_state.user = None

    if 'is_admin' not in st.session_state:
        st.session_state.is_admin = False
    if 'show_forgot_password' not in st.session_state:
        st.session_state.show_forgot_password = False
    if 'show_reset_confirmation' not in st.session_state:
        st.session_state.show_reset_confirmation = False
    if 'authentication_token' not in st.session_state:
        st.session_state.authentication_token = None
    if 'current_page' not in st.session_state:
        st.session_state.current_page = None

def login_user():
    """Handle user login"""
    st.header("Login")

    # Check for existing auth token first
    if 'authentication_token' in st.session_state and st.session_state.authentication_token:
        try:
            user = User.verify_auth_token(st.session_state.authentication_token)
            if user:
                st.session_state.user = {
                    'id': user.id,
                    'username': user.username,
                    'name': user.name,
                    'is_admin': user.is_admin
                }
                st.session_state.is_admin = user.is_admin
                st.success(f"Welcome back, {user.name}!")
                return
        except Exception:
            st.session_state.authentication_token = None

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        remember = st.checkbox("Remember me", value=True)
        submitted = st.form_submit_button("Login")

        if submitted:
            if not username or not password:
                st.error("Please enter both username and password")
                return

            try:
                # Get user from database
                user = User.query.filter_by(username=username).first()

                if not user:
                    st.error("Invalid username")
                    return

                if not user.check_password(password):
                    st.error("Invalid password")
                    return

                # Update last login time
                user.last_login = datetime.utcnow()
                db.session.commit()

                try:
                    # Import current app
                    from app import app

                    # Generate token with explicit app context
                    with app.app_context():
                        token = user.get_auth_token()

                    if token:
                        # Store token before user info
                        st.session_state.authentication_token = token

                        # Store user info in session state
                        st.session_state.user = {
                            'id': user.id,
                            'username': user.username,
                            'name': user.name,
                            'is_admin': user.is_admin
                        }
                        st.session_state.is_admin = user.is_admin

                        st.success(f"Welcome back, {user.name}!")
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error("Failed to generate auth token")
                        db.session.rollback()
                except Exception as e:
                    print(f"Token generation error: {str(e)}")
                    st.error("Authentication error, please try again")
                    db.session.rollback()

            except Exception as e:
                print(f"Login error: {str(e)}")
                st.error("Invalid login credentials. Please try again.")
                db.session.rollback()

def create_admin():
    """Create initial admin user"""
    st.header("Create Admin Account")
    with st.form("admin_form"):
        name = st.text_input("Full Name")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")

        submitted = st.form_submit_button("Create Admin")

        if submitted:
            if not all([name, username, password]):
                st.error("Please fill in all fields")
                return

            if password != confirm_password:
                st.error("Passwords do not match")
                return

            if User.query.filter_by(username=username).first():
                st.error("Username already taken")
                return

            try:
                admin = User(
                    username=username,
                    name=name,
                    is_admin=True
                )
                admin.set_password(password)
                db.session.add(admin)
                db.session.commit()
                st.success("Admin account created successfully!")
                st.session_state.user = admin
                st.session_state.is_admin = True
                st.rerun()
            except Exception as e:
                st.error(f"Error creating admin account: {str(e)}")

def display_admin_controls():
    """Display admin control panel"""
    if not st.session_state.is_admin:
        st.error("Access denied. Admin privileges required.")
        return

    st.header("Admin Control Panel")

    # Create tabs for different admin functions
    tab1, tab2 = st.tabs(["User Management", "Email Settings"])

    with tab1:
        # User Management tab
        st.subheader("User Management")
        users = User.query.all()

        for user in users:
            with st.expander(f"User: {user.name} ({user.username})"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"Admin: {'Yes' if user.is_admin else 'No'}")
                    st.write(f"Last Login: {user.last_login or 'Never'}")
                with col2:
                    if user.id != st.session_state.user['id']:  # Can't modify own account
                        if st.button(f"{'Remove' if user.is_admin else 'Make'} Admin", key=f"admin_{user.id}"):
                            user.is_admin = not user.is_admin
                            db.session.commit()
                            st.success(f"Updated admin status for {user.name}")
                            st.rerun()

                        if st.button("Delete User", key=f"delete_{user.id}"):
                            db.session.delete(user)
                            db.session.commit()
                            st.success(f"Deleted user {user.name}")
                            st.rerun()

    # Add New User
    st.subheader("Add New User")
    with st.form("add_user_form"):
        new_name = st.text_input("Full Name")
        new_username = st.text_input("Username")
        new_password = st.text_input("Password", type="password")
        is_admin = st.checkbox("Make Admin")

        if st.form_submit_button("Add User"):
            if not all([new_name, new_username, new_password]):
                st.error("Please fill in all fields")
                return

            if User.query.filter_by(username=new_username).first():
                st.error("Username already taken")
            else:
                try:
                    new_user = User(
                        username=new_username,
                        name=new_name,
                        is_admin=is_admin
                    )
                    new_user.set_password(new_password)
                    db.session.add(new_user)
                    db.session.commit()
                    st.success("User added successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error adding user: {str(e)}")

    with tab2:
        # Email Settings tab
        from components.email_settings import display_email_settings
        display_email_settings()

def request_password_reset():
    """Display password reset form to reset password directly on the website"""
    import logging

    st.header("Reset Your Password")
    st.write("Enter your username and verify your identity to reset your password.")

    with st.form("reset_request_form"):
        username = st.text_input("Username")
        name = st.text_input("Your Full Name (for verification)")
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm New Password", type="password")
        submitted = st.form_submit_button("Reset Password")

        if submitted:
            if not username or not name or not new_password or not confirm_password:
                st.error("Please fill in all fields")
                return

            if new_password != confirm_password:
                st.error("Passwords do not match")
                return

            # Find user and verify name matches
            user = User.query.filter_by(username=username).first()
            if not user:
                st.error("No account found with that username")
                return

            # Verify name as a simple identity check
            if user.name.lower() != name.lower():
                st.error("Name verification failed. Please try again with the correct information.")
                return

            try:
                # Update password
                user.set_password(new_password)
                db.session.commit()
                st.success("Password has been reset successfully!")

                # Show login button
                if st.button("Login with New Password"):
                    st.session_state.show_forgot_password = False
                    st.session_state.show_login = True
                    st.rerun()
            except Exception as e:
                st.error(f"Error resetting password: {str(e)}")
                db.session.rollback()
                logging.error(f"Error in password reset: {str(e)}")

    # Back to login link
    if st.button("Back to Login"):
        st.session_state.show_forgot_password = False
        st.session_state.show_login = True
        st.rerun()

def confirm_password_reset():
    """Handle password reset confirmation"""
    from utils.token_manager import verify_reset_token

    # Get token and username from query parameters
    query_params = st.query_params
    token = query_params.get("reset_token", "")
    username = query_params.get("username", "")

    if not token or not username:
        st.error("Invalid or missing reset token.")
        if st.button("Return to Login"):
            st.session_state.show_reset_confirmation = False
            st.session_state.show_login = True
            st.query_params.clear()
            st.rerun()
        return

    st.header("Set New Password")

    with st.form("reset_confirmation_form"):
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm New Password", type="password")
        submitted = st.form_submit_button("Reset Password")

        if submitted:
            if not new_password or not confirm_password:
                st.error("Please fill in all fields")
                return

            if new_password != confirm_password:
                st.error("Passwords do not match")
                return

            # Verify token and get user
            user = verify_reset_token(token, username)

            if not user:
                st.error("Invalid or expired reset token.")
                return

            try:
                # Update password
                user.set_password(new_password)

                # Clear reset token
                user.reset_token = None
                user.reset_token_expiry = None

                db.session.commit()
                st.success("Password has been reset successfully!")

                # Clear query parameters
                st.query_params.clear()

                # Show login button
                if st.button("Login with New Password"):
                    st.session_state.show_reset_confirmation = False
                    st.session_state.show_login = True
                    st.rerun()
            except Exception as e:
                st.error(f"Error resetting password: {str(e)}")
                db.session.rollback()

def display_auth_interface():
    """Main authentication interface"""
    init_session_state()

    # Try to authenticate using stored token
    if not st.session_state.user and 'authentication_token' in st.session_state and st.session_state.authentication_token:
        try:
            user = User.verify_auth_token(st.session_state.authentication_token)
            if user:
                st.session_state.user = {
                    'id': user.id,
                    'username': user.username,
                    'name': user.name,
                    'is_admin': user.is_admin
                }
                st.session_state.is_admin = user.is_admin
        except:
            # Clear invalid token
            st.session_state.authentication_token = None

    if not st.session_state.user:
        if not User.query.filter_by(is_admin=True).first():
            create_admin()
        elif st.session_state.show_forgot_password:
            request_password_reset()
        elif st.session_state.show_reset_confirmation:
            confirm_password_reset()
        else:
            login_user()
    else:
        # Display user info and navigation options
        with st.sidebar:
            st.write(f"Welcome, {st.session_state.user['name']}")

            # Navigation options
            if st.button("My Profile"):
                st.session_state.current_page = "profile"
            if st.session_state.is_admin and st.button("Admin Controls"):
                st.session_state.current_page = "admin"
            if st.button("Logout"):
                # Clear session state
                st.session_state.user = None
                st.session_state.is_admin = False
                st.session_state.authentication_token = None
                st.session_state.current_page = None
                st.rerun()

        # Display current page content
        if st.session_state.get('current_page') == "profile":
            from components.user_profile import display_user_profile
            display_user_profile()
        elif st.session_state.get('current_page') == "admin" and st.session_state.is_admin:
            display_admin_controls()