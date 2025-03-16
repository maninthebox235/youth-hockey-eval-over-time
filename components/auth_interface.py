import streamlit as st
from database.models import User, db
from datetime import datetime
from werkzeug.security import generate_password_hash

def init_session_state():
    """Initialize session state variables"""
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'is_admin' not in st.session_state:
        st.session_state.is_admin = False
    if 'show_forgot_password' not in st.session_state:
        st.session_state.show_forgot_password = False
    if 'show_reset_confirmation' not in st.session_state:
        st.session_state.show_reset_confirmation = False

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
                if user and user.check_password(password):
                    user.last_login = datetime.utcnow()
                    db.session.commit()
                    st.session_state.user = user
                    st.session_state.is_admin = user.is_admin
                    st.success(f"Welcome back, {user.name}!")
                    st.rerun()
                else:
                    st.error("Invalid username or password")
            except Exception as e:
                st.error(f"Login error: {str(e)}")
                db.session.rollback()
    
    # Password reset link
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("Forgot Password?"):
            st.session_state.show_forgot_password = True
            st.session_state.show_login = False
            st.rerun()

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
                if user.id != st.session_state.user.id:  # Can't modify own account
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

def display_auth_interface():
    """Main authentication interface"""
    init_session_state()
    
    # Initialize password reset state if not present
    if 'show_forgot_password' not in st.session_state:
        st.session_state.show_forgot_password = False
    if 'show_reset_confirmation' not in st.session_state:
        st.session_state.show_reset_confirmation = False
    
    # Check for reset token in URL
    query_params = st.query_params
    if "reset_token" in query_params and "username" in query_params:
        st.session_state.show_reset_confirmation = True
        st.session_state.show_login = False
        st.session_state.show_forgot_password = False

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
        st.sidebar.write(f"Logged in as: {st.session_state.user.name}")
        if st.sidebar.button("Logout"):
            st.session_state.user = None
            st.session_state.is_admin = False
            st.rerun()

        if st.session_state.is_admin:
            if st.sidebar.button("Admin Controls"):
                display_admin_controls()