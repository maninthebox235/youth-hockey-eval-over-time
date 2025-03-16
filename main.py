import streamlit as st
import pandas as pd
from database import db, init_app
from database.models import Player, User
from utils.data_generator import get_players_df, get_player_history, seed_database
from components.player_profile import display_player_profile
from components.development_charts import display_development_charts
from components.team_management import display_team_management
from components.stats_dashboard import display_age_group_stats, display_player_rankings
from components.auth_interface import display_auth_interface
from components.landing_page import display_landing_page
import time

# Page configuration must be the first Streamlit command
st.set_page_config(
    page_title="Youth Hockey Development Tracker",
    page_icon="🏒",
    layout="wide"
)

# Initialize Flask app
app = init_app()

# Ensure we have an application context
app_ctx = app.app_context()
app_ctx.push()

# Initialize session state and verify authentication token
if 'initialized' not in st.session_state:
    st.session_state.initialized = True

# Initialize essential session state variables every time
if 'user' not in st.session_state:
    st.session_state.user = None
if 'is_admin' not in st.session_state:
    st.session_state.is_admin = False
if 'show_signup' not in st.session_state:
    st.session_state.show_signup = False
if 'show_login' not in st.session_state:
    st.session_state.show_login = False
if 'authentication_token' not in st.session_state:
    st.session_state.authentication_token = None

# Try to restore session from token in session state or URL query params
query_params = st.query_params
url_token = query_params.get("auth_token", None)

# Use URL token if available, otherwise use session token if it exists
token_to_verify = url_token or st.session_state.get("authentication_token")

if not st.session_state.user and token_to_verify:
    print(f"Attempting to restore session with token...")
    try:
        with app.app_context():
            try:
                user = User.verify_auth_token(token_to_verify)
                if user:
                    # If the token came from URL and not session, store it in session
                    if url_token and not st.session_state.authentication_token:
                        st.session_state.authentication_token = url_token

                    st.session_state.user = {
                        'id': user.id,
                        'username': user.username,
                        'name': user.name,
                        'is_admin': user.is_admin
                    }
                    st.session_state.is_admin = user.is_admin
                    print(f"Session successfully restored for user: {user.username}")
                else:
                    print("Token verification failed: no user found")
                    st.session_state.authentication_token = None
                    # Clear auth_token from URL if it's invalid
                    if url_token:
                        params = dict(query_params)
                        if "auth_token" in params:
                            del params["auth_token"]
                        st.query_params.update(**params)
            except Exception as token_verify_error:
                print(f"Internal token verification error: {str(token_verify_error)}")
                # Safe error handling for token verification
                st.session_state.authentication_token = None
                # Clear auth_token from URL if it's invalid
                if url_token:
                    try:
                        params = dict(query_params)
                        if "auth_token" in params:
                            del params["auth_token"]
                        st.query_params.update(**params)
                    except Exception as param_error:
                        print(f"Error clearing URL params: {str(param_error)}")
            else:
                print("No token provided for verification")
    except Exception as e:
        print(f"Token verification outer error: {str(e)}")
        st.session_state.authentication_token = None
        # Clear auth_token from URL if it's invalid
        if url_token:
            try:
                params = dict(query_params)
                if "auth_token" in params:
                    del params["auth_token"]
                st.query_params.update(**params)
            except Exception as param_error:
                print(f"Error clearing URL params: {str(param_error)}")
else:
    if st.session_state.user:
        print(f"User already in session: {st.session_state.user['username']}")
    elif not st.session_state.authentication_token:
        print("No authentication token found in session")

# Handle authentication and landing page
show_landing = display_landing_page()

# Only show main content if landing page is skipped (user is authenticated)
if not show_landing:
    # Display authentication interface
    display_auth_interface()

    # Main application content
    if st.session_state.user:  # Only show content if user is authenticated
        st.sidebar.image("https://images.unsplash.com/photo-1547223431-cc59f141f389",
                         caption="Player Development Platform")

        # Initialize database if needed
        if 'db_initialized' not in st.session_state:
            try:
                # Check if database needs seeding
                if not Player.query.first():
                    st.info("Initializing database with sample data...")
                    if seed_database(n_players=20):
                        st.session_state.db_initialized = True
                        st.success("Database initialized successfully!")
                        time.sleep(2)
                    else:
                        st.error("Error initializing database. Please check the logs.")
                else:
                    st.session_state.db_initialized = True
            except Exception as e:
                st.error(f"Database initialization error: {str(e)}")

        # Get current player data
        try:
            players_df = get_players_df()
            if players_df.empty:
                st.warning("No player data available. Please check the database connection.")
            else:
                menu = st.sidebar.selectbox(
                    "Navigation",
                    ["Player Profiles", "Development Analytics", "Team Statistics", "Team Management"]
                )

                if menu == "Player Profiles":
                    st.subheader("Player Profiles")
                    selected_player = st.selectbox(
                        "Select Player",
                        players_df['name'].tolist()
                    )

                    if selected_player:
                        player_data = players_df[players_df['name'] == selected_player].iloc[0]
                        player_history = get_player_history(player_data['player_id'])
                        display_player_profile(player_data, player_history)
                        display_development_charts(player_data, player_history)

                elif menu == "Development Analytics":
                    st.subheader("Development Analytics")
                    age_groups = sorted(players_df['age_group'].unique())
                    if age_groups:
                        age_group = st.selectbox("Select Age Group", age_groups)
                        filtered_df = players_df[players_df['age_group'] == age_group]

                        col1, col2 = st.columns(2)
                        with col1:
                            st.write("Player Distribution")
                            st.dataframe(filtered_df[['name', 'position', 'skating_speed', 'shooting_accuracy']])

                        with col2:
                            st.write("Performance Summary")
                            st.dataframe(filtered_df.describe())

                elif menu == "Team Management":
                    display_team_management()

                else:  # Team Statistics
                    st.subheader("Team Statistics")
                    display_age_group_stats(players_df)
                    display_player_rankings(players_df)

        except Exception as e:
            st.error(f"Application error: {str(e)}")
            st.info("Please ensure the database is properly initialized and connected.")

# Handle any uncaught errors
st.set_option('client.showErrorDetails', True)

# Clean up context when the app exits
app_ctx.pop()