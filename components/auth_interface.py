import streamlit as st
from database.models import User, db
from datetime import datetime
from werkzeug.security import generate_password_hash
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import ssl  # Add SSL support

def init_session_state():
    """Initialize session state variables"""
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'is_admin' not in st.session_state:
        st.session_state.is_admin = False

def send_welcome_email(user_email, user_name):
    """Send welcome email to new users"""
    try:
        # Add debug prints for environment variables
        print("Checking email configuration...")
        username = os.getenv('MAIL_USERNAME')
        password = os.getenv('MAIL_PASSWORD')
        sender = os.getenv('MAIL_DEFAULT_SENDER')

        if not all([username, password, sender]):
            print("Missing email configuration:")
            print(f"Username present: {bool(username)}")
            print(f"Password present: {bool(password)}")
            print(f"Sender present: {bool(sender)}")
            return False

        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = user_email
        msg['Subject'] = "Welcome to Hockey Development Tracker"

        body = f"""
        Hi {user_name},

        Welcome to the Hockey Development Tracker! Your account has been successfully created.

        You can now log in to access player profiles, track development progress, and manage feedback.

        Best regards,
        The Hockey Development Team
        """
        msg.attach(MIMEText(body, 'plain'))

        print(f"Attempting to send email to {user_email}")
        print(f"Using sender: {sender}")

        # Create SSL context
        context = ssl.create_default_context()

        # Connect to Gmail's SMTP server with SSL
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as server:
            print("Connected to SMTP server")
            server.login(username, password)
            print("Logged in successfully")
            server.send_message(msg)
            print(f"Email sent successfully to {user_email}")
            return True

    except Exception as e:
        print(f"Detailed error sending email: {str(e)}")
        if hasattr(e, 'smtp_error'):
            print(f"SMTP error: {e.smtp_error}")
        return False

def login_user():
    """Handle user login"""
    st.header("Login")
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

        if submitted:
            user = User.query.filter_by(email=email).first()
            if user and user.check_password(password):
                user.last_login = datetime.utcnow()
                db.session.commit()
                st.session_state.user = user
                st.session_state.is_admin = user.is_admin
                st.success(f"Welcome back, {user.name}!")
                st.rerun()
            else:
                st.error("Invalid email or password")

def create_admin():
    """Create initial admin user"""
    st.header("Create Admin Account")
    with st.form("admin_form"):
        name = st.text_input("Name")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")

        submitted = st.form_submit_button("Create Admin")

        if submitted:
            if password != confirm_password:
                st.error("Passwords do not match")
                return

            if User.query.filter_by(email=email).first():
                st.error("Email already registered")
                return

            admin = User(
                email=email,
                name=name,
                is_admin=True
            )
            admin.set_password(password)

            try:
                db.session.add(admin)
                db.session.commit()
                if send_welcome_email(email, name):
                    st.success("Admin account created successfully! Welcome email sent.")
                else:
                    st.warning("Admin account created but welcome email could not be sent.")
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

    # User Management
    st.subheader("User Management")
    users = User.query.all()

    for user in users:
        with st.expander(f"User: {user.name} ({user.email})"):
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
        new_name = st.text_input("Name")
        new_email = st.text_input("Email")
        new_password = st.text_input("Password", type="password")
        is_admin = st.checkbox("Make Admin")

        if st.form_submit_button("Add User"):
            if User.query.filter_by(email=new_email).first():
                st.error("Email already registered")
            else:
                new_user = User(
                    email=new_email,
                    name=new_name,
                    is_admin=is_admin
                )
                new_user.set_password(new_password)

                try:
                    db.session.add(new_user)
                    db.session.commit()
                    if send_welcome_email(new_email, new_name):
                        st.success("User added successfully! Welcome email sent.")
                    else:
                        st.warning("User added but welcome email could not be sent.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error adding user: {str(e)}")

def display_auth_interface():
    """Main authentication interface"""
    init_session_state()

    if not st.session_state.user:
        if not User.query.filter_by(is_admin=True).first():
            create_admin()
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