import streamlit as st
import pandas as pd
from database import db, init_app
from database.models import Player
from utils.data_generator import get_players_df, get_player_history, seed_database, clear_database
from components.player_profile import display_player_profile
from components.development_charts import display_development_charts
from components.team_management import display_team_management
from components.stats_dashboard import display_age_group_stats, display_player_rankings
from components.auth_interface import display_auth_interface
from components.landing_page import display_landing_page
import time

# Initialize Flask app
app = init_app()

# Ensure we have an application context
app_ctx = app.app_context()
app_ctx.push()

# Page configuration
st.set_page_config(
    page_title="Youth Hockey Development Tracker",
    page_icon="🏒",
    layout="wide"
)

# Display landing page for non-authenticated users
if 'user' not in st.session_state or not st.session_state.user:
    display_landing_page()
else:
    # Display authentication interface
    display_auth_interface()

    # Only show content if user is logged in
    if 'user' in st.session_state and st.session_state.user:
        st.sidebar.image("https://images.unsplash.com/photo-1547223431-cc59f141f389",
                         caption="Player Development Platform")

        # Initialize or clear database if requested
        if 'db_initialized' not in st.session_state:
            try:
                # Add a clear database button
                if st.sidebar.button("Clear Database"):
                    if clear_database():
                        st.success("Database cleared successfully!")
                        st.session_state.db_initialized = False
                        st.rerun()
                    else:
                        st.error("Error clearing database")

                # Check if database needs seeding
                if not Player.query.first():
                    st.info("Initializing database with sample data...")
                    if seed_database(n_players=20):
                        st.session_state.db_initialized = True
                        st.success("Database initialized successfully!")
                        # Add a small delay to ensure database is ready
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

# Clean up context when the app exits
app_ctx.pop()