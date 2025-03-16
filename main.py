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
app_ctx = app.app_context()
app_ctx.push()

# Check URL parameters for auth token
query_params = st.query_params
url_token = query_params.get("auth_token", None)

# Initialize session state
if 'user' not in st.session_state:
    st.session_state.user = None
if 'is_admin' not in st.session_state:
    st.session_state.is_admin = False
if 'authentication_token' not in st.session_state:
    st.session_state.authentication_token = None

# Try to restore session from token in URL or session state
if not st.session_state.user:
    token_to_try = url_token or st.session_state.authentication_token
    if token_to_try:
        try:
            with app.app_context():
                user = User.verify_auth_token(token_to_try)
                if user:
                    # Store token in both session and URL
                    st.session_state.authentication_token = token_to_try
                    if not url_token:
                        st.query_params["auth_token"] = token_to_try

                    # Set user info
                    st.session_state.user = {
                        'id': user.id,
                        'username': user.username,
                        'name': user.name,
                        'is_admin': user.is_admin
                    }
                    st.session_state.is_admin = user.is_admin
                else:
                    st.session_state.authentication_token = None
                    st.query_params.clear()
        except Exception as e:
            print(f"Token verification error: {str(e)}")
            st.session_state.authentication_token = None
            st.query_params.clear()

# Display landing page or main content
show_landing = display_landing_page()

if not show_landing and st.session_state.user:
    st.sidebar.image("https://images.unsplash.com/photo-1547223431-cc59f141f389",
                     caption="Player Development Platform")

    # Initialize database if needed
    if 'db_initialized' not in st.session_state:
        try:
            if not Player.query.first():
                st.info("Initializing database with sample data...")
                if seed_database(n_players=20):
                    st.session_state.db_initialized = True
                    st.success("Database initialized successfully!")
                    time.sleep(2)
                else:
                    st.error("Error initializing database.")
            else:
                st.session_state.db_initialized = True
        except Exception as e:
            st.error(f"Database error: {str(e)}")

    # Get and display player data
    try:
        players_df = get_players_df()
        if not players_df.empty:
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

        else:
            st.warning("No player data available.")
    except Exception as e:
        st.error(f"Error: {str(e)}")

# Clean up context
app_ctx.pop()