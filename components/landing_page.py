import streamlit as st
from database.models import User, db
from datetime import datetime

def display_feature_preview():
    """Display feature preview on landing page"""
    st.title("🏒 IceTracker: Youth Hockey Player Development Platform")
    st.markdown("##### Comprehensive skill tracking, personalized training, and advanced analytics for young players")
    
    # Use a custom CSS style
    st.markdown("""
    <style>
    .feature-card {
        border-radius: 10px;
        border: 1px solid #ddd;
        padding: 20px;
        margin: 10px 0;
        background-color: white;
    }
    .feature-icon {
        font-size: 24px;
        margin-bottom: 10px;
    }
    .feature-title {
        font-weight: bold;
        margin-bottom: 10px;
    }
    .premium-badge {
        background-color: #FFD700;
        color: #000;
        padding: 2px 8px;
        border-radius: 10px;
        font-size: 12px;
        margin-left: 5px;
    }
    .team-badge {
        background-color: #4169E1;
        color: white;
        padding: 2px 8px;
        border-radius: 10px;
        font-size: 12px;
        margin-left: 5px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Hero banner section
    st.markdown("""
    <div style="background-image: linear-gradient(to right, #1A2980, #26D0CE); color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
        <h2>Track, Analyze, Improve</h2>
        <p style="font-size: 18px;">The complete solution for youth hockey player development, trusted by coaches and parents nationwide.</p>
        <p>Designed for players age 6-18 • Position-specific metrics • Data-driven improvement</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Core Features Section
    st.subheader("Core Features")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📊</div>
            <div class="feature-title">Skill Assessment & Tracking</div>
            <p>Comprehensive skill evaluations with position-specific metrics for skating, stickhandling, shooting, and hockey IQ.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📈</div>
            <div class="feature-title">Progress Visualization</div>
            <p>Dynamic charts showing player development over time with detailed historical data and trend analysis.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🏆</div>
            <div class="feature-title">Age-Appropriate Benchmarks</div>
            <p>Compare performance to age-specific benchmarks to identify strengths and areas for improvement.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">👥</div>
            <div class="feature-title">Multi-Player Profiles</div>
            <p>Track multiple players under one account, perfect for families with siblings or coaches managing teams.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Premium Features Section
    st.subheader("Premium Features")
    
    premium_cols = st.columns(3)
    
    with premium_cols[0]:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🎬</div>
            <div class="feature-title">Video Analysis <span class="premium-badge">PREMIUM</span></div>
            <p>Upload practice or game footage for detailed technique analysis with actionable feedback.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with premium_cols[1]:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🏋️</div>
            <div class="feature-title">Training Plans <span class="premium-badge">PREMIUM</span></div>
            <p>Personalized development plans based on player metrics with targeted drills and exercises.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with premium_cols[2]:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🔍</div>
            <div class="feature-title">Peer Comparison <span class="premium-badge">PREMIUM</span></div>
            <p>Anonymous benchmarking against other players in the same age group and position.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Team Features Section
    st.subheader("Team & Organization Features")
    
    team_cols = st.columns(3)
    
    with team_cols[0]:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📋</div>
            <div class="feature-title">Team Dashboard <span class="team-badge">TEAM</span></div>
            <p>Comprehensive team overview with skill heatmaps, performance metrics, and development tracking.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with team_cols[1]:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🏁</div>
            <div class="feature-title">Tryout Evaluation <span class="team-badge">TEAM</span></div>
            <p>Streamlined assessment system for player tryouts with customizable evaluation criteria.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with team_cols[2]:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📝</div>
            <div class="feature-title">Custom Reports <span class="team-badge">TEAM</span></div>
            <p>Generate detailed team and player reports for season reviews and development planning.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Pricing Banner
    st.markdown("""
    <div style="background-color: #f5f5f5; padding: 20px; border-radius: 10px; margin: 20px 0; text-align: center;">
        <h3>Simple, Flexible Pricing</h3>
        <div style="display: flex; justify-content: center; text-align: center; margin-top: 15px;">
            <div style="margin: 0 15px; background-color: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                <h4>Free</h4>
                <h2>$0</h2>
                <p>Core features<br>Up to 3 players<br>Basic statistics</p>
            </div>
            <div style="margin: 0 15px; background-color: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); border: 2px solid #FFD700;">
                <h4>Premium</h4>
                <h2>$4.99<small>/month</small></h2>
                <p>All core features<br>Unlimited players<br>All premium features</p>
            </div>
            <div style="margin: 0 15px; background-color: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                <h4>Team</h4>
                <h2>$99<small>/year</small></h2>
                <p>Everything in Premium<br>Team features<br>Custom branding</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Space before call to action
    st.markdown("<div style='margin: 20px 0;'></div>", unsafe_allow_html=True)
    
    # Call to action
    st.markdown("""
    <div style="text-align: center; margin: 30px 0;">
        <h2>Ready to elevate your hockey development?</h2>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    
    with col2:
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Sign Up Now", type="primary", key="signup_button", use_container_width=True):
                st.session_state.show_signup = True
                st.rerun()
        with col2:
            if st.button("Login", key="login_button", type="secondary", use_container_width=True):
                st.session_state.show_login = True
                st.rerun()
        
        # Reset password option
        forgot_col1, forgot_col2, forgot_col3 = st.columns([1,2,1])
        with forgot_col2:
            if st.button("Forgot Password?", key="forgot_pw_button"):
                st.session_state.show_login = False
                st.session_state.show_signup = False
                st.session_state.show_forgot_password = True
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
                st.session_state.user = {
                    'id': new_user.id,
                    'username': new_user.username,
                    'name': new_user.name,
                    'is_admin': new_user.is_admin
                }
                st.session_state.is_admin = new_user.is_admin
                st.session_state.show_signup = False
                
                # Set onboarding flag for new users
                st.session_state.show_onboarding = True
                
                st.success("Account created successfully! Redirecting to onboarding...")
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
    if 'show_forgot_password' not in st.session_state:
        st.session_state.show_forgot_password = False
    if 'show_reset_confirmation' not in st.session_state:
        st.session_state.show_reset_confirmation = False

    # Check if user is already logged in
    if 'user' in st.session_state and st.session_state.user:
        return False  # Skip landing page
        
    # Check for reset token in URL
    query_params = st.query_params
    if "reset_token" in query_params and "username" in query_params:
        st.session_state.show_reset_confirmation = True
        st.session_state.show_login = False
        st.session_state.show_signup = False
        st.session_state.show_forgot_password = False
        from components.auth_interface import confirm_password_reset
        confirm_password_reset()
        return True

    # Handle auth flow
    if st.session_state.user:
        # User is authenticated, don't show landing page
        return False
    
    if st.session_state.show_signup:
        display_signup_form()
    elif st.session_state.get('show_login', False):
        from components.auth_interface import login_user
        login_user()
    elif st.session_state.get('show_forgot_password', False):
        from components.auth_interface import request_password_reset
        request_password_reset()
    else:
        display_feature_preview()

    return True  # Show landing pageing page