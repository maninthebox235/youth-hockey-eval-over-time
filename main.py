import streamlit as st
import time
import logging

from database import init_app
from database.models import Player, User
from utils.data_generator import get_players_df, get_player_history, seed_database
from components.player_profile import display_player_profile
from components.development_charts import display_development_charts
from components.team_management import display_team_management
from components.stats_dashboard import display_age_group_stats, display_player_rankings
from components.auth_interface import display_auth_interface
from components.landing_page import display_landing_page
from components.age_benchmarks import (
    display_age_benchmarks,
    display_all_benchmarks_by_age,
)
from components.off_ice_training import display_off_ice_interface
from components.team_dashboard import display_team_dashboard
from components.peer_comparison import display_peer_comparison_interface
from components.training_plans import display_training_plan_interface
from components.video_analysis import display_video_analysis_interface
from components.onboarding import display_onboarding
from components.admin_dashboard import display_admin_dashboard
from components.drill_recommendations import display_contextual_drill_recommendations


# Function to load and inject custom CSS
def load_css(css_file):
    with open(css_file, "r") as f:
        css_content = f.read()

    # Inject CSS with Streamlit
    st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)


# Page configuration with improved styling
st.set_page_config(
    page_title="Youth Hockey Development Tracker", page_icon="🏒", layout="wide"
)

# Load custom CSS
try:
    load_css("styles/custom.css")
except Exception as e:
    st.warning(f"Could not load custom styles: {str(e)}")

# Initialize Flask app and context
app = init_app()
if app is not None:
    app_ctx = app.app_context()
    app_ctx.push()
else:
    app_ctx = None
    logging.error("Failed to initialize Flask app")

# Initialize basic session state
if "user" not in st.session_state:
    # Set user to None to show landing page
    st.session_state.user = None
else:
    # Keep existing user if already logged in
    pass

if "is_admin" not in st.session_state:
    st.session_state.is_admin = False
if "is_premium" not in st.session_state:
    st.session_state.is_premium = False
if "authentication_token" not in st.session_state:
    st.session_state.authentication_token = None

# Check for authentication token in URL params or session state
token = st.query_params.get("auth_token") or st.session_state.get(
    "authentication_token"
)

# Try to verify token and log in user if token is valid
if token and not st.session_state.user:
    user = User.verify_auth_token(token)
    if user:
        # Token is valid, set session state
        st.session_state.authentication_token = token

        # ALWAYS update query params for current session - this is the key change
        # This makes the token persist in the URL across refreshes
        st.query_params["auth_token"] = token

        # Set remember_me flag if it's not in session state
        # (This happens if the page is refreshed and we only have the token)
        if "remember_me" not in st.session_state:
            # Assume remember_me is true if token came from URL params
            # This ensures the proper UI indicator shows
            st.session_state.remember_me = True

        # Set user info in session
        st.session_state.user = {
            "id": user.id,
            "username": user.username,
            "name": user.name,
            "is_admin": user.is_admin,
        }
        st.session_state.is_admin = user.is_admin

# Display content
show_landing = display_landing_page()

if not show_landing:
    if not st.session_state.user:
        display_auth_interface()
    else:
        st.sidebar.image(
            "https://images.unsplash.com/photo-1547223431-cc59f141f389",
            caption="Player Development Platform",
        )

        # Check if we should show onboarding
        if "show_onboarding" not in st.session_state:
            st.session_state.show_onboarding = False

        # Show onboarding for new users before player profiles
        if st.session_state.show_onboarding:
            display_onboarding()
            # Add a button to exit onboarding mode
            if st.button("Continue to Dashboard", key="continue_to_dashboard"):
                st.session_state.show_onboarding = False
                st.rerun()
        else:
            # Initialize database if needed
            if "db_initialized" not in st.session_state:
                try:
                    if not Player.query.first():
                        st.info("Initializing database with sample data...")
                        if seed_database(
                            n_players=0
                        ):  # Don't add sample data for new users
                            st.session_state.db_initialized = True
                            st.success("Database initialized successfully!")
                            time.sleep(1)
                    else:
                        st.session_state.db_initialized = True
                except Exception as e:
                    st.error(f"Error initializing database: {str(e)}")

            try:
                # Add a prominent logout button in the header
                header_col1, header_col2 = st.columns([6, 1])
                with header_col2:
                    if st.button("🚪 Logout", type="primary", use_container_width=True):
                        # Clear session state
                        st.session_state.clear()
                        # Clear URL parameters to remove the token
                        st.query_params.clear()
                        st.info("Logging out...")
                        st.rerun()

                # Display main content - filter players by current user
                user_id = (
                    st.session_state.user["id"] if "user" in st.session_state else None
                )
                players_df = get_players_df(user_id=user_id)

                if players_df.empty:
                    # If no players, redirect to onboarding
                    st.warning("No player data available.")
                    st.info("Let's get started by adding players to your account.")
                    if st.button("Set Up Your Account", key="setup_account"):
                        st.session_state.show_onboarding = True
                        st.rerun()
                else:
                    # Enhanced navigation menu
                    # Check if user is admin
                    is_admin = st.session_state.user.get("is_admin", False)

                    # Admin users get access to the admin dashboard
                    if is_admin:
                        menu_options = [
                            "Team Dashboard",
                            "Player Profiles",
                            "Training & Development",
                            "Skill Analysis",
                            "Benchmarks & References",
                            "Team Management",
                            "Admin Dashboard",  # Added Admin Dashboard for admins
                        ]
                    else:
                        menu_options = [
                            "Team Dashboard",
                            "Player Profiles",
                            "Training & Development",
                            "Skill Analysis",
                            "Benchmarks & References",
                            "Team Management",
                        ]

                    menu = st.sidebar.selectbox("Navigation", menu_options)

                    # Display admin badge for admin users
                    if is_admin:
                        st.sidebar.success("Admin Access Enabled")

                    if menu == "Player Profiles":
                        st.subheader("Player Profiles")
                        selected_player = st.selectbox(
                            "Select Player", players_df["name"].tolist()
                        )
                        if selected_player:
                            player_data = players_df[
                                players_df["name"] == selected_player
                            ].iloc[0]
                            player_history = get_player_history(
                                player_data["player_id"]
                            )
                            display_player_profile(player_data, player_history)

                            # Add sub-navigation for additional player features
                            player_submenu = st.radio(
                                "Player Development Tools",
                                [
                                    "Development Charts",
                                    "Peer Comparison",
                                    "Off-Ice Training",
                                    "Training Plans",
                                    "Drill Recommendations",
                                    "Video Analysis",
                                ],
                                horizontal=True,
                            )

                            if player_submenu == "Development Charts":
                                display_development_charts(player_data, player_history)
                            elif player_submenu == "Peer Comparison":
                                display_peer_comparison_interface(
                                    player_data["player_id"], player_data
                                )
                            elif player_submenu == "Off-Ice Training":
                                display_off_ice_interface(
                                    player_data["player_id"], player_data
                                )
                            elif player_submenu == "Training Plans":
                                display_training_plan_interface(
                                    player_data["player_id"], player_data
                                )
                            elif player_submenu == "Drill Recommendations":
                                display_contextual_drill_recommendations(
                                    player_data["player_id"], player_data
                                )
                            elif player_submenu == "Video Analysis":
                                display_video_analysis_interface(
                                    player_data["player_id"], player_data
                                )

                    elif menu == "Training & Development":
                        st.subheader("Training & Development")

                        # Sub-navigation for training features
                        training_submenu = st.radio(
                            "Training Resources",
                            ["Training Plans", "Off-Ice Development", "Video Analysis"],
                            horizontal=True,
                        )

                        # Select player first
                        selected_player = st.selectbox(
                            "Select Player", players_df["name"].tolist()
                        )

                        if selected_player:
                            player_data = players_df[
                                players_df["name"] == selected_player
                            ].iloc[0]

                            if training_submenu == "Training Plans":
                                display_training_plan_interface(
                                    player_data["player_id"], player_data
                                )
                            elif training_submenu == "Off-Ice Development":
                                display_off_ice_interface(
                                    player_data["player_id"], player_data
                                )
                            elif training_submenu == "Video Analysis":
                                display_video_analysis_interface(
                                    player_data["player_id"], player_data
                                )

                    elif menu == "Team Dashboard":
                        # Show the enhanced team dashboard
                        display_team_dashboard()

                    elif menu == "Skill Analysis":
                        st.subheader("Skill Analysis")

                        # Sub-navigation for analysis features
                        analysis_submenu = st.radio(
                            "Analysis Tools",
                            [
                                "Development Analytics",
                                "Peer Comparison",
                                "Team Statistics",
                            ],
                            horizontal=True,
                        )

                        if analysis_submenu == "Development Analytics":
                            age_groups = sorted(players_df["age_group"].unique())
                            if age_groups:
                                age_group = st.selectbox("Select Age Group", age_groups)
                                filtered_df = players_df[
                                    players_df["age_group"] == age_group
                                ]
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.write("Player Distribution")
                                    st.dataframe(
                                        filtered_df[
                                            [
                                                "name",
                                                "position",
                                                "skating_speed",
                                                "shooting_accuracy",
                                            ]
                                        ]
                                    )
                                with col2:
                                    st.write("Performance Summary")
                                    st.dataframe(filtered_df.describe())

                        elif analysis_submenu == "Peer Comparison":
                            # Select player first
                            selected_player = st.selectbox(
                                "Select Player for Comparison",
                                players_df["name"].tolist(),
                            )

                            if selected_player:
                                player_data = players_df[
                                    players_df["name"] == selected_player
                                ].iloc[0]
                                display_peer_comparison_interface(
                                    player_data["player_id"], player_data
                                )

                        elif analysis_submenu == "Team Statistics":
                            display_age_group_stats(players_df)
                            display_player_rankings(players_df)

                    elif menu == "Benchmarks & References":
                        st.subheader("Age-Appropriate Benchmarks")

                        benchmark_submenu = st.radio(
                            "Benchmark Tools",
                            ["Player Benchmark Comparison", "All Benchmarks Reference"],
                            horizontal=True,
                        )

                        if benchmark_submenu == "Player Benchmark Comparison":
                            # Select player to see their benchmarks
                            selected_player = st.selectbox(
                                "Select Player", players_df["name"].tolist()
                            )

                            if selected_player:
                                player_data = players_df[
                                    players_df["name"] == selected_player
                                ].iloc[0]
                                display_age_benchmarks(player_data)

                        elif benchmark_submenu == "All Benchmarks Reference":
                            # Show all benchmarks by age
                            display_all_benchmarks_by_age()

                    elif menu == "Team Management":
                        # Show team management options
                        team_submenu = st.radio(
                            "Team Management Tools",
                            [
                                "Basic Team Management",
                                "Enhanced Team Dashboard",
                                "Tryout Evaluation",
                                "Game Evaluation",
                            ],
                            horizontal=True,
                        )

                        if team_submenu == "Basic Team Management":
                            display_team_management()
                        elif team_submenu == "Enhanced Team Dashboard":
                            display_team_dashboard()
                        elif team_submenu == "Tryout Evaluation":
                            # First select a team for tryout evaluation
                            from database.models import Team

                            teams = Team.query.all()
                            if teams:
                                team_options = [
                                    (t.id, f"{t.name} ({t.age_group})") for t in teams
                                ]
                                selected = st.selectbox(
                                    "Select Team for Tryout Evaluation",
                                    options=range(len(team_options)),
                                    format_func=lambda i: team_options[i][1],
                                )
                                team_id = team_options[selected][0]

                                # Display tryout evaluation mode for this team
                                # This requires a slightly different function signature
                                from components.team_dashboard import (
                                    display_tryout_evaluation_mode,
                                )

                                display_tryout_evaluation_mode(team_id)
                            else:
                                st.info(
                                    "No teams available. Please create a team first."
                                )
                        elif team_submenu == "Game Evaluation":
                            from database.models import Team
                            from components.game_evaluation import (
                                display_game_evaluation_interface,
                            )

                            teams = Team.query.all()
                            if teams:
                                team_options = [
                                    (t.id, f"{t.name} ({t.age_group})") for t in teams
                                ]
                                selected = st.selectbox(
                                    "Select Team for Game Evaluation",
                                    options=range(len(team_options)),
                                    format_func=lambda i: team_options[i][1],
                                )
                                team_id = team_options[selected][0]

                                display_game_evaluation_interface(team_id)
                            else:
                                st.info(
                                    "No teams available. Please create a team first."
                                )

                    elif menu == "Admin Dashboard":
                        # Show the admin dashboard
                        display_admin_dashboard()
            except Exception as e:
                st.error(f"Error: {str(e)}")

# Clean up context
if app_ctx is not None:
    app_ctx.pop()
