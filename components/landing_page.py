import streamlit as st

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
        ✅ Full access to all features for 30 days\n
        ✅ Unlimited player profiles\n
        ✅ Expert support
        """)

        if st.button("Sign Up Now", type="primary", key="signup_button"):
            display_signup_form()

def display_signup_form():
    """Display the signup form for new users"""
    st.title("Create Your Account")

    with st.form("signup_form", clear_on_submit=True):
        name = st.text_input("Full Name")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")

        col1, col2 = st.columns(2)
        with col1:
            role = st.selectbox("Role", ["Coach", "Team Manager", "Parent"])
        with col2:
            organization = st.text_input("Organization Name")

        submitted = st.form_submit_button("Create Account")

        if submitted:
            if password != confirm_password:
                st.error("Passwords do not match")
            else:
                # Handle account creation here
                st.success("Account created! Please check your email for verification.")
                st.session_state.show_login = True

def display_landing_page():
    """Main landing page handler"""
    if 'show_signup' not in st.session_state:
        st.session_state.show_signup = False

    if st.session_state.get('show_login', False):
        from components.auth_interface import login_user
        login_user()
    else:
        display_feature_preview()