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