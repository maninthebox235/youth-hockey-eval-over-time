import streamlit as st
from database.models import User, db

def display_feature_preview():
    """Display feature preview for non-authenticated users"""
    st.title("🏒 Welcome to Hockey Development Tracker")

    st.markdown("""
    ### Transform Your Hockey Program with Advanced Analytics

    Track player development, manage teams, and make data-driven decisions with our comprehensive platform.
    """)

    # Feature Highlights
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📊 Player Development Tracking")
        st.markdown("""
        - Advanced metrics for both skaters and goalies
        - Customizable feedback templates
        - Progress visualization and reporting
        - Age-specific development milestones
        """)

        st.markdown("### 🎯 Performance Analytics")
        st.markdown("""
        - Detailed statistical analysis
        - Development trend visualization
        - Custom report generation
        - Compare against age group averages
        """)

    with col2:
        st.markdown("### 👥 Team Management")
        st.markdown("""
        - Roster management
        - Practice planning tools
        - Team performance tracking
        - Parent communication portal
        """)

        st.markdown("### 📝 Coach Feedback System")
        st.markdown("""
        - Structured evaluation templates
        - Real-time feedback submission
        - Development recommendations
        - Progress tracking
        """)

    # Call to Action
    st.markdown("---")
    col1, col2, col3 = st.columns([1,2,1])

    with col2:
        st.markdown("### Start Your Free Trial Today!")
        st.markdown("""
        ✅ No credit card required\n
        ✅ Full access to all features\n
        ✅ Unlimited player profiles\n
        ✅ Expert support
        """)

        if st.button("Create Account", type="primary"):
            st.session_state.show_signup = True
            st.rerun()
        if st.button("Already have an account? Login"):
            st.session_state.show_login = True
            st.rerun()

def display_signup_form():
    """Display the signup form for new users"""
    st.title("Create Your Account")

    with st.form("signup_form"):
        name = st.text_input("Full Name")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")

        col1, col2 = st.columns(2)
        with col1:
            role = st.selectbox("Role", ["Coach", "Team Manager", "Parent"])
        with col2:
            organization = st.text_input("Organization Name")

        submitted = st.form_submit_button("Create Account")

        if submitted:
            if not all([name, username, password, organization]):
                st.error("Please fill in all required fields")
                return

            if password != confirm_password:
                st.error("Passwords do not match")
                return

            if User.query.filter_by(username=username).first():
                st.error("Username already taken")
                return

            try:
                new_user = User(
                    username=username,
                    name=name,
                    is_admin=False
                )
                new_user.set_password(password)
                db.session.add(new_user)
                db.session.commit()

                # Set session state and clear signup flag
                st.session_state.user = new_user
                st.session_state.is_admin = new_user.is_admin
                st.session_state.show_signup = False
                st.success("Account created successfully! Redirecting to dashboard...")
                st.rerun()
            except Exception as e:
                st.error(f"Error creating account: {str(e)}")

def display_landing_page():
    """Main landing page handler"""
    # Initialize session state
    if 'show_signup' not in st.session_state:
        st.session_state.show_signup = False
    if 'show_login' not in st.session_state:
        st.session_state.show_login = False

    # Check if user is already logged in
    if 'user' in st.session_state and st.session_state.user:
        return False  # Skip landing page

    # Handle auth flow
    if st.session_state.show_signup:
        display_signup_form()
    elif st.session_state.get('show_login', False):
        from components.auth_interface import login_user
        login_user()
    else:
        display_feature_preview()

    return True  # Show landing page content