import streamlit as st
import plotly.express as px
from components.coach_feedback import display_feedback_form, display_feedback_history
from components.feedback_templates import manage_feedback_templates
from components.skill_assessment import display_skill_assessment
from utils.pdf_report import display_pdf_export_section
from utils.type_converter import to_int, to_float, to_str


def get_age_benchmark(age, skill_type):
    """Get benchmark data for a given age and skill"""
    benchmarks = {
        "skating_speed": {"6-8": 2.5, "9-11": 3.0, "12-14": 3.5, "15-18": 4.0},
        "shooting_accuracy": {"6-8": 2.0, "9-11": 2.8, "12-14": 3.3, "15-18": 3.8},
    }

    # Convert age to integer using our utility
    age_int = to_int(age)
    if age_int is None:
        # Default to middle age group if age is invalid
        return benchmarks.get(skill_type, {}).get("9-11", 3.0)

    # Determine age group with proper type handling
    if 6 <= age_int <= 8:
        age_group = "6-8"
    elif 9 <= age_int <= 11:
        age_group = "9-11"
    elif 12 <= age_int <= 14:
        age_group = "12-14"
    else:
        age_group = "15-18"

    return benchmarks.get(skill_type, {}).get(age_group, 3.0)


def display_player_profile(player_data, player_history):
    """Display comprehensive player profile with skill assessments"""

    # Styled header with player name
    st.markdown(
        f"""
    <div style="background: linear-gradient(90deg, var(--primary-color), var(--secondary-color)); 
         padding: 1.5rem; border-radius: 10px; color: white; margin-bottom: 1.5rem; box-shadow: var(--card-shadow);">
        <h2 style="margin:0; color: white; font-weight: 700;">{player_data['name']} Profile</h2>
        <p style="margin:0; opacity: 0.9;">Player Development Dashboard</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Profile Header with modern styling
    st.markdown('<div class="player-card">', unsafe_allow_html=True)
    col1, col2 = st.columns([1, 2])

    with col1:
        st.image(
            "https://images.unsplash.com/photo-1517177646641-83fe10f14633",
            caption=player_data["name"],
            use_container_width=True,
        )

        # Safe handling of join_date format
        join_date_str = ""
        if "join_date" in player_data and player_data["join_date"] is not None:
            try:
                join_date_str = player_data["join_date"].strftime("%Y-%m-%d")
            except (AttributeError, ValueError):
                join_date_str = str(player_data["join_date"])

    with col2:
        # Display player details with safe type handling and styled badges
        st.markdown(
            f"""
        <h3 style="color: var(--primary-color); margin-bottom: 1rem;">Player Details</h3>
        
        <div style="display: flex; flex-wrap: wrap; gap: 1rem; margin-bottom: 1rem;">
            <span class="badge badge-primary">Age: {to_int(player_data.get('age', 0)) or 'N/A'}</span>
            <span class="badge badge-secondary">Age Group: {player_data.get('age_group', 'N/A')}</span>
            <span class="badge badge-primary">Position: {player_data.get('position', 'N/A')}</span>
        </div>
        
        <p><strong>Join Date:</strong> {join_date_str or 'N/A'}</p>
        """,
            unsafe_allow_html=True,
        )

        # Add player stats preview
        position = to_str(player_data.get("position", ""))
        if position and position.lower() == "goalie":
            metrics = [
                {
                    "name": "Save %",
                    "value": f"{to_float(player_data.get('save_percentage', 0)) or 0:.1f}",
                },
                {
                    "name": "Games",
                    "value": f"{to_int(player_data.get('games_played', 0)) or 0}",
                },
            ]
        else:
            metrics = [
                {
                    "name": "Goals",
                    "value": f"{to_int(player_data.get('goals', 0)) or 0}",
                },
                {
                    "name": "Assists",
                    "value": f"{to_int(player_data.get('assists', 0)) or 0}",
                },
                {
                    "name": "Games",
                    "value": f"{to_int(player_data.get('games_played', 0)) or 0}",
                },
            ]

        st.markdown(
            """
        <div style="display: flex; gap: 1rem; margin-top: 1rem;">
        """,
            unsafe_allow_html=True,
        )

        for metric in metrics:
            st.markdown(
                f"""
            <div class="stat-box">
                <h4>{metric["name"]}</h4>
                <p class="value">{metric["value"]}</p>
            </div>
            """,
                unsafe_allow_html=True,
            )

        st.markdown(
            """
        </div>
        """,
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)

    # Create tabs for different sections
    tabs = st.tabs(
        [
            "Current Stats",
            "Skill Assessment",
            "Development Charts",
            "Feedback",
            "Export Report",
        ]
    )

    with tabs[0]:  # Current Stats
        st.subheader("Current Statistics")
        # Safely check player position with proper error handling
        position = to_str(player_data.get("position", ""))
        if position and position.lower() == "goalie":
            _display_goalie_stats(player_data)
        else:
            _display_skater_stats(player_data)

    with tabs[1]:  # Skill Assessment
        st.subheader("Skill Assessment")
        assessment_saved = display_skill_assessment(player_data["player_id"])

        # Check if assessment was just saved and we need to switch tabs
        if assessment_saved:
            # Rerun to show updated data and reset the form
            st.rerun()

    with tabs[2]:  # Development Charts
        st.subheader("Development Progress")
        if not player_history.empty:
            _display_development_charts(player_data, player_history)
        else:
            st.info("No performance history available yet.")

    with tabs[3]:  # Feedback
        feedback_tabs = st.tabs(["Submit Feedback", "Feedback History", "Templates"])

        with feedback_tabs[0]:
            display_feedback_form(
                player_data["player_id"], player_data["name"], player_data["position"]
            )

        with feedback_tabs[1]:
            display_feedback_history(player_data["player_id"])

        with feedback_tabs[2]:
            if "manage_templates" not in st.session_state:
                st.session_state.manage_templates = False

            if st.session_state.manage_templates:
                manage_feedback_templates()
            else:
                if st.button("Manage Templates"):
                    st.session_state.manage_templates = True
                    st.rerun()

    with tabs[4]:  # Export Report
        display_pdf_export_section(player_data["player_id"])


def _display_skater_stats(player_data):
    """Display statistics for skater players"""
    from utils.type_converter import to_float, to_int

    # Add a styled container for stats
    st.markdown('<div class="main-panel">', unsafe_allow_html=True)

    # Get benchmarks
    skating_benchmark = get_age_benchmark(player_data["age"], "skating_speed")
    shooting_benchmark = get_age_benchmark(player_data["age"], "shooting_accuracy")

    # Display primary stats with improved styling
    st.markdown(
        """
    <h3 style="color: var(--primary-color); margin-bottom: 1rem;">Key Performance Metrics</h3>
    <div style="display: flex; flex-wrap: wrap; gap: 1rem; margin-bottom: 1.5rem;">
    """,
        unsafe_allow_html=True,
    )

    # Skating Speed
    current_skating = to_float(player_data.get("skating_speed", 0)) or 0
    current_skating = min(max(current_skating, 1), 5) if current_skating else 0
    skating_diff = current_skating - skating_benchmark
    skating_diff_class = "text-success" if skating_diff >= 0 else "text-danger"

    st.markdown(
        f"""
    <div class="stat-box" style="flex: 1;">
        <h4>Skating Speed</h4>
        <p class="value">{current_skating:.1f}<span style="font-size: 0.8rem;">/5</span></p>
        <div class="rating-scale rating-level-{int(current_skating)}">
            <div class="rating-bar">
                <div class="fill"></div>
            </div>
        </div>
        <p class="{skating_diff_class}" style="font-size: 0.8rem; margin: 0;">
            {skating_diff:.1f} vs benchmark
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Shooting Accuracy
    current_shooting = to_float(player_data.get("shooting_accuracy", 0)) or 0
    current_shooting = min(max(current_shooting, 1), 5) if current_shooting else 0
    shooting_diff = current_shooting - shooting_benchmark
    shooting_diff_class = "text-success" if shooting_diff >= 0 else "text-danger"

    st.markdown(
        f"""
    <div class="stat-box" style="flex: 1;">
        <h4>Shooting Accuracy</h4>
        <p class="value">{current_shooting:.1f}<span style="font-size: 0.8rem;">/5</span></p>
        <div class="rating-scale rating-level-{int(current_shooting)}">
            <div class="rating-bar">
                <div class="fill"></div>
            </div>
        </div>
        <p class="{shooting_diff_class}" style="font-size: 0.8rem; margin: 0;">
            {shooting_diff:.1f} vs benchmark
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Games Played
    games = to_int(player_data.get("games_played", 0)) or 0

    st.markdown(
        f"""
    <div class="stat-box" style="flex: 1;">
        <h4>Games Played</h4>
        <p class="value">{games}</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown("</div>", unsafe_allow_html=True)

    # Game stats section
    goals = to_int(player_data.get("goals", 0)) or 0
    assists = to_int(player_data.get("assists", 0)) or 0

    st.markdown(
        """
    <h3 style="color: var(--primary-color); margin: 1rem 0;">Game Performance</h3>
    <div style="display: flex; gap: 1rem;">
    """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
    <div class="stat-box" style="flex: 1;">
        <h4>Goals</h4>
        <p class="value">{goals}</p>
    </div>
    
    <div class="stat-box" style="flex: 1;">
        <h4>Assists</h4>
        <p class="value">{assists}</p>
    </div>
    
    <div class="stat-box" style="flex: 1;">
        <h4>Points</h4>
        <p class="value">{goals + assists}</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)  # Close main-panel


def _display_goalie_stats(player_data):
    """Display statistics for goalie players"""
    from utils.type_converter import to_float, to_int

    # Add a styled container for stats
    st.markdown('<div class="main-panel">', unsafe_allow_html=True)

    # Use type conversion functions for consistent data handling
    save_pct = to_float(player_data.get("save_percentage", 0)) or 0
    reaction = to_float(player_data.get("reaction_time", 0)) or 0
    positioning = to_float(player_data.get("positioning", 0)) or 0

    # Ensure values are in 1-5 range
    reaction = min(max(reaction, 1), 5) if reaction else 0
    positioning = min(max(positioning, 1), 5) if positioning else 0

    # Display primary stats with improved styling
    st.markdown(
        """
    <h3 style="color: var(--primary-color); margin-bottom: 1rem;">Goalie Performance Metrics</h3>
    <div style="display: flex; flex-wrap: wrap; gap: 1rem; margin-bottom: 1.5rem;">
    """,
        unsafe_allow_html=True,
    )

    # Save Percentage
    st.markdown(
        f"""
    <div class="stat-box" style="flex: 1;">
        <h4>Save Percentage</h4>
        <p class="value">{save_pct:.1f}<span style="font-size: 0.8rem;">%</span></p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Reaction Time
    st.markdown(
        f"""
    <div class="stat-box" style="flex: 1;">
        <h4>Reaction Time</h4>
        <p class="value">{reaction:.1f}<span style="font-size: 0.8rem;">/5</span></p>
        <div class="rating-scale rating-level-{int(reaction)}">
            <div class="rating-bar">
                <div class="fill"></div>
            </div>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Positioning
    st.markdown(
        f"""
    <div class="stat-box" style="flex: 1;">
        <h4>Positioning</h4>
        <p class="value">{positioning:.1f}<span style="font-size: 0.8rem;">/5</span></p>
        <div class="rating-scale rating-level-{int(positioning)}">
            <div class="rating-bar">
                <div class="fill"></div>
            </div>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Close flex container
    st.markdown("</div>", unsafe_allow_html=True)

    # Get integer metrics with proper conversion
    games_played = to_int(player_data.get("games_played", 0)) or 0
    saves = to_int(player_data.get("saves", 0)) or 0
    goals_against = to_int(player_data.get("goals_against", 0)) or 0

    # Calculate save percentage
    total_shots = saves + goals_against
    save_percentage = (saves / total_shots * 100) if total_shots > 0 else 0

    # Game stats section
    st.markdown(
        """
    <h3 style="color: var(--primary-color); margin: 1rem 0;">Game Statistics</h3>
    <div style="display: flex; gap: 1rem;">
    """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
    <div class="stat-box" style="flex: 1;">
        <h4>Games Played</h4>
        <p class="value">{games_played}</p>
    </div>
    
    <div class="stat-box" style="flex: 1;">
        <h4>Saves</h4>
        <p class="value">{saves}</p>
    </div>
    
    <div class="stat-box" style="flex: 1;">
        <h4>Goals Against</h4>
        <p class="value">{goals_against}</p>
    </div>
    
    <div class="stat-box" style="flex: 1;">
        <h4>Game Save %</h4>
        <p class="value">{save_percentage:.1f}%</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)  # Close main-panel


def _display_development_charts(player_data, player_history):
    """Display development progress charts"""
    # Safely check player position with extra safeguard against None
    try:
        position = to_str(player_data.get("position", ""))
        is_goalie = position and position.lower() == "goalie"
    except (AttributeError, TypeError):
        is_goalie = False

    if is_goalie:
        # Check if required metrics exist in player_history
        required_metrics = ["save_percentage", "positioning", "reaction_time"]
        available_metrics = [m for m in required_metrics if m in player_history.columns]

        if not available_metrics:
            st.info("No goalie metrics available in player history.")
            return

        # Plot available goalie metrics
        fig = px.line(
            player_history,
            x="date",
            y=available_metrics,
            title="Goalie Performance Metrics Over Time",
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        # For skaters, check available metrics first
        skill_metrics = ["skating_speed", "shooting_accuracy"]
        available_skill_metrics = [
            m for m in skill_metrics if m in player_history.columns
        ]

        performance_metrics = ["goals", "assists"]
        available_perf_metrics = [
            m for m in performance_metrics if m in player_history.columns
        ]

        if available_skill_metrics:
            fig1 = px.line(
                player_history,
                x="date",
                y=available_skill_metrics,
                title="Skill Development Over Time",
            )
            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.info("No skill metrics available in player history.")

        if available_perf_metrics:
            fig2 = px.line(
                player_history,
                x="date",
                y=available_perf_metrics,
                title="Game Performance Over Time",
            )
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("No performance metrics available in player history.")


def get_player(player_id):
    """Get player by ID"""
    try:
        # Use our type_converter utility to handle any numeric type including numpy types
        from utils.type_converter import to_int

        player_id = to_int(player_id)

        if player_id is None:
            print("Invalid player ID: None after conversion")
            return None

        # Convert to native Python int to avoid numpy.int64 compatibility issues with psycopg2
        try:
            player_id = int(player_id)
        except (TypeError, ValueError):
            print(f"Could not convert player ID {player_id} to integer")
            return None

        from database.models import Player

        player = Player.query.get(player_id)
        if player:
            return player
        return None
    except Exception as e:
        print(f"Error getting player: {e}")
        return None
