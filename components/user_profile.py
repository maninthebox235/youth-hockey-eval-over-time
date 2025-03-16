import streamlit as st
from database.models import User, db
from werkzeug.security import generate_password_hash
from datetime import datetime

def display_user_profile():
    """Display and manage user profile settings"""
    if not st.session_state.user:
        st.error("Please log in to view your profile")
        return

    st.header("My Profile")

    # Get current user data
    user = User.query.get(st.session_state.user['id'])
    if not user:
        st.error("Error loading user profile")
        return

    # Profile sections
    tabs = st.tabs(["Profile Information", "Change Password", "Activity Log"])

    with tabs[0]:
        st.subheader("Profile Information")

        profile_form = st.form(key="profile_form")
        with profile_form:
            new_name = st.text_input("Full Name", value=user.name)
            new_username = st.text_input("Username", value=user.username, disabled=True)

            # Role information
            st.info(f"Account Type: {'Administrator' if user.is_admin else 'Standard User'}")

            submit_profile = st.form_submit_button("Update Profile")

            if submit_profile:
                try:
                    if new_name != user.name:
                        user.name = new_name
                        db.session.commit()

                        # Update session state
                        st.session_state.user['name'] = new_name

                        st.success("Profile updated successfully!")
                        st.rerun()
                except Exception as e:
                    st.error(f"Error updating profile: {str(e)}")
                    db.session.rollback()

    with tabs[1]:
        st.subheader("Change Password")

        password_form = st.form(key="password_form")
        with password_form:
            current_password = st.text_input("Current Password", type="password")
            new_password = st.text_input("New Password", type="password")
            confirm_password = st.text_input("Confirm New Password", type="password")

            submit_password = st.form_submit_button("Change Password")

            if submit_password:
                if not all([current_password, new_password, confirm_password]):
                    st.error("Please fill in all password fields")
                elif new_password != confirm_password:
                    st.error("New passwords do not match")
                elif not user.check_password(current_password):
                    st.error("Current password is incorrect")
                else:
                    try:
                        user.set_password(new_password)
                        db.session.commit()
                        st.success("Password updated successfully!")
                    except Exception as e:
                        st.error(f"Error updating password: {str(e)}")
                        db.session.rollback()

    with tabs[2]:
        st.subheader("Recent Activity")

        # Display last login time
        if user.last_login:
            st.info(f"Last Login: {user.last_login.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            st.info("No recent login activity")

        # Account creation date
        st.info(f"Account Created: {user.created_at.strftime('%Y-%m-%d')}")