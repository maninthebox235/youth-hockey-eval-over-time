import streamlit as st
import pandas as pd
from database.models import User, db


def display_auth_buttons():
    """Display authentication buttons in the top-right corner"""
    # Apply CSS for the auth container and buttons
    st.markdown(
        """
    <style>
    /* Hide default Streamlit container padding at the top to make room for our header */
    .main .block-container {
        padding-top: 0rem;
    }
    
    /* Style for auth buttons header */
    .auth-header {
        background-color: #f8f9fa;
        width: 100%;
        padding: 8px 20px;
        display: flex;
        justify-content: flex-end;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
    }
    
    /* Style for the button container */
    .auth-buttons {
        display: flex;
        gap: 10px;
        align-items: center;
    }
    
    /* Custom styling for the logo */
    .logo {
        font-weight: bold;
        font-size: 18px;
        color: #C8102E; /* Hockey red */
        margin-right: auto;
        display: flex;
        align-items: center;
    }
    
    /* Button container - to make sure hidden buttons are properly aligned */
    .stbutton-container {
        display: flex;
        justify-content: flex-end;
    }
    
    /* Make the default Streamlit buttons smaller */
    .stButton button {
        font-size: 13px !important;
        padding: 2px 12px !important;
        border-radius: 20px !important;
    }
    
    /* Login button style */
    .login-btn button {
        background-color: transparent !important;
        color: #333 !important;
        border: 1px solid #ddd !important;
    }
    
    /* Sign up button style */
    .signup-btn button {
        background-color: #C8102E !important; /* Hockey red */
        color: white !important;
        border: none !important;
    }
    </style>
    
    <div class="auth-header">
        <div class="logo">🏒 IceTracker</div>
        <div class="auth-buttons">
            <!-- The actual buttons will be injected by Streamlit -->
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Create a clean horizontal container for buttons at the top
    cols = st.columns([7, 1.2, 1])

    # Empty column to push buttons to the right
    cols[0].empty()

    # Sign Up button (first)
    with cols[1]:
        st.markdown('<div class="signup-btn">', unsafe_allow_html=True)
        if st.button("Sign Up", key="top_signup_button"):
            st.session_state.show_signup = True
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # Login button (second)
    with cols[2]:
        st.markdown('<div class="login-btn">', unsafe_allow_html=True)
        if st.button("Login", key="top_login_button"):
            st.session_state.show_login = True
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)


def display_feature_preview():
    """Display feature preview on landing page"""
    # Display authentication buttons at the top
    display_auth_buttons()

    # Display the title first, above the image
    st.title("🏒 IceTracker: Youth Hockey Player Development Platform")

    # Banner image - sized for optimal viewing without scrolling
    # Add custom CSS to limit image height and enhance appearance
    st.markdown(
        """
    <style>
        /* Control the height of the banner image */
        .banner-image img {
            max-height: 180px !important;
            object-fit: cover !important;
            border-radius: 8px !important;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1) !important;
        }
    </style>
    """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([2, 3, 2])
    with col2:
        st.markdown('<div class="banner-image">', unsafe_allow_html=True)
        st.image(
            "static/images/hockey/players/hockey_player_close_up.jpg",
            use_container_width=True,
            output_format="JPEG",
        )
        st.markdown("</div>", unsafe_allow_html=True)
    st.markdown(
        "##### Comprehensive skill tracking, personalized training, and advanced analytics for young players"
    )

    # Use a custom CSS style
    st.markdown(
        """
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
    }
    
    /* Make cards clickable */
    .clickable-card {
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .clickable-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 16px rgba(0,0,0,0.1);
    }
    
    /* Hide the actual buttons but keep them accessible */
    div[data-testid="column"] > div > div > div > div > button {
        background-color: transparent;
        color: transparent;
        border: none;
        padding: 0;
        width: 1px;
        height: 1px;
        position: absolute;
        overflow: hidden;
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
    .demo-banner {
        background-color: #A3CFF2;
        color: #1E3A8A;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
        text-align: center;
        font-weight: bold;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

    # Hero banner section
    st.markdown(
        """
    <div style="background-image: linear-gradient(to right, #1A2980, #26D0CE); color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
        <h2>Track, Analyze, Improve</h2>
        <p style="font-size: 18px;">The complete solution for youth hockey player development, trusted by coaches and parents nationwide.</p>
        <p>Designed for players age 6-18 • Position-specific metrics • Data-driven improvement</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Core Features Section
    st.subheader("Core Features")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            """
        <div class="feature-card">
            <div class="feature-icon">📊</div>
            <div class="feature-title">Skill Assessment & Tracking</div>
            <p>Comprehensive skill evaluations with position-specific metrics for skating, stickhandling, shooting, and hockey IQ.</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
        <div class="feature-card">
            <div class="feature-icon">📈</div>
            <div class="feature-title">Progress Visualization</div>
            <p>Dynamic charts showing player development over time with detailed historical data and trend analysis.</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
        <div class="feature-card">
            <div class="feature-icon">🏆</div>
            <div class="feature-title">Age-Appropriate Benchmarks</div>
            <p>Compare performance to age-specific benchmarks to identify strengths and areas for improvement.</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
        <div class="feature-card">
            <div class="feature-icon">👥</div>
            <div class="feature-title">Multi-Player Profiles</div>
            <p>Track multiple players under one account, perfect for families with siblings or coaches managing teams.</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    # Feature Showcase - Import and display interactive demo
    st.markdown(
        "<div class='demo-banner'>Try the interactive demo below 👇</div>",
        unsafe_allow_html=True,
    )
    from utils.showcase_data import display_feature_showcase

    display_feature_showcase()

    # Premium Features Section
    st.subheader("Premium Features")

    # Initialize session state for feature previews if not exists
    if "show_premium_preview" not in st.session_state:
        st.session_state.show_premium_preview = None

    # Add enhanced CSS for premium features
    st.markdown(
        """
    <style>
    .premium-card {
        border-radius: 10px;
        padding: 20px;
        margin: 10px 5px;
        height: 230px;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
        border: 1px solid #e0e0e0;
        box-shadow: 0 4px 8px rgba(0,0,0,0.05);
        background-color: white;
    }
    
    .premium-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 16px rgba(0,0,0,0.1);
    }
    
    .premium-card-1 {
        border-left: 5px solid #FFD700;
    }
    
    .premium-card-2 {
        border-left: 5px solid #FF7043;
    }
    
    .premium-card-3 {
        border-left: 5px solid #9C27B0;
    }
    
    .premium-badge {
        background-color: #FFD700;
        color: #333;
        padding: 3px 10px;
        border-radius: 15px;
        font-size: 12px;
        font-weight: bold;
        display: inline-block;
        margin-bottom: 10px;
    }
    
    .premium-card-title {
        font-size: 20px;
        font-weight: 600;
        margin-bottom: 15px;
        color: #2C3E50;
    }
    
    .premium-card-text {
        color: #555;
        font-size: 16px;
        line-height: 1.5;
    }
    
    .premium-link {
        position: absolute;
        bottom: 15px;
        text-align: center;
        width: 100%;
        left: 0;
        color: #FF7043;
        font-weight: 500;
        font-size: 15px;
        text-decoration: none;
        margin-top: 15px;
    }
    
    .premium-link:hover {
        text-decoration: underline;
        color: #E64A19;
    }
    
    /* Unify button styles for clickable areas */
    [data-testid="column"] button, .premium-button button, .team-button button {
        background-color: transparent !important;
        color: transparent !important;
        border: none !important;
        position: absolute !important;
        top: 0 !important;
        left: 0 !important;
        width: 100% !important;
        height: 100% !important;
        z-index: 10 !important;
        cursor: pointer !important;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

    premium_cols = st.columns(3)

    # Video Analysis Card
    with premium_cols[0]:
        # Add CSS to make cards clickable
        st.markdown(
            """
        <style>
        .clickable-card {
            cursor: pointer;
            position: relative;
            z-index: 1;
        }
        
        /* Make the premium card buttons visible and clickable */
        div[data-testid="column"] button {
            position: absolute !important;
            top: 0 !important;
            left: 0 !important;
            width: 100% !important;
            height: 100% !important;
            background: transparent !important;
            border: none !important;
            color: transparent !important;
            cursor: pointer !important;
            z-index: 10 !important;
        }
        </style>
        """,
            unsafe_allow_html=True,
        )

        # Create the card
        card_html = """
        <div class="premium-card premium-card-1 clickable-card">
            <div class="premium-badge">PREMIUM</div>
            <div class="premium-card-title">Video Analysis</div>
            <div class="premium-card-text">
                Upload practice or game footage for detailed technique analysis with actionable feedback.
            </div>
        </div>
        """

        # Simply display the card and use a normal button below it
        st.markdown(card_html, unsafe_allow_html=True)
        if st.button("View Feature", key="video-analysis-button"):
            st.session_state.show_premium_preview = "video_analysis"
            st.rerun()

    # Training Plans Card
    with premium_cols[1]:
        # Create the card
        card_html = """
        <div class="premium-card premium-card-2 clickable-card">
            <div class="premium-badge">PREMIUM</div>
            <div class="premium-card-title">Training Plans</div>
            <div class="premium-card-text">
                Personalized development plans based on player metrics with targeted drills and exercises.
            </div>
        </div>
        """

        # Simply display the card and use a normal button below it
        st.markdown(card_html, unsafe_allow_html=True)
        if st.button("View Feature", key="training-plans-button"):
            st.session_state.show_premium_preview = "training_plans"
            st.rerun()

    # Peer Comparison Card
    with premium_cols[2]:
        # Create the card
        card_html = """
        <div class="premium-card premium-card-3 clickable-card">
            <div class="premium-badge">PREMIUM</div>
            <div class="premium-card-title">Peer Comparison</div>
            <div class="premium-card-text">
                Anonymous benchmarking against other players in the same age group and position.
            </div>
        </div>
        """

        # Simply display the card and use a normal button below it
        st.markdown(card_html, unsafe_allow_html=True)
        if st.button("View Feature", key="peer-comparison-button"):
            st.session_state.show_premium_preview = "peer_comparison"
            st.rerun()

    # Show premium feature preview if one is selected
    if st.session_state.show_premium_preview == "video_analysis":
        st.markdown(
            """
        <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px; margin-top: 20px; border-left: 5px solid #FFD700;">
            <h3>Video Analysis Preview</h3>
        </div>
        """,
            unsafe_allow_html=True,
        )

        video_col1, video_col2 = st.columns([1, 1])

        with video_col1:
            st.image(
                "static/images/hockey/players/shooting.jpg",
                caption="Video Analysis Interface",
            )
            st.markdown(
                """
            <div style="margin-top: 10px;">
                <h4>Technique Assessment</h4>
                <p>Upload videos of practice sessions or games for detailed technical analysis</p>
                <ul>
                    <li>Skating technique analysis</li>
                    <li>Shooting form assessment</li>
                    <li>Automated technique scoring</li>
                </ul>
            </div>
            """,
                unsafe_allow_html=True,
            )

        with video_col2:
            # Create sample technique analysis
            st.markdown("#### Sample Analysis Results")

            # Add sample feedback
            st.info(
                "**Skating Analysis**: Good knee bend and stride length. Work on edge control during crossovers."
            )
            st.info(
                "**Shooting Analysis**: Proper weight transfer. Aim for quicker release and follow-through."
            )

            # Add sample metrics
            metrics = {
                "Technique Score": 82,
                "Efficiency Rating": 78,
                "Form Quality": 85,
            }

            for metric, value in metrics.items():
                st.metric(metric, f"{value}/100")

        # Add custom styling for close button
        st.markdown(
            """
        <style>
        div[data-testid="stButton"] > button[kind="secondaryFormSubmit"] {
            background-color: #f0f0f0;
            color: #505050;
            border: 1px solid #d0d0d0;
            padding: 0.25rem 1rem;
            font-size: 0.8em;
            margin-top: 10px;
        }
        div[data-testid="stButton"] > button[kind="secondaryFormSubmit"]:hover {
            background-color: #e0e0e0;
            border-color: #a0a0a0;
        }
        </style>
        """,
            unsafe_allow_html=True,
        )

        # Smaller centered close button
        col1, col2, col3 = st.columns([3, 2, 3])
        with col2:
            if st.button("Close Preview", key="close_video_preview", type="secondary"):
                st.session_state.show_premium_preview = None
                st.rerun()

    elif st.session_state.show_premium_preview == "training_plans":
        st.markdown(
            """
        <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px; margin-top: 20px; border-left: 5px solid #FFD700;">
            <h3>Training Plans Preview</h3>
        </div>
        """,
            unsafe_allow_html=True,
        )

        plan_col1, plan_col2 = st.columns([1, 1])

        with plan_col1:
            st.image(
                "static/images/hockey/players/player-stance.jpg",
                caption="Personalized Hockey Training",
            )
            st.markdown(
                """
            <div style="margin-top: 10px;">
                <h4>Personalized Development</h4>
                <p>Get custom training plans based on player's specific needs and metrics</p>
                <ul>
                    <li>Age-appropriate drills</li>
                    <li>Position-specific exercises</li>
                    <li>Targeted skills improvement</li>
                    <li>Progress tracking and adjustments</li>
                </ul>
            </div>
            """,
                unsafe_allow_html=True,
            )

        with plan_col2:
            # Create sample training plan
            st.markdown("#### Weekly Training Schedule")

            # Create sample schedule
            schedule = [
                {"Day": "Monday", "Focus": "Skating & Edges", "Duration": "45 min"},
                {"Day": "Tuesday", "Focus": "Stickhandling", "Duration": "30 min"},
                {"Day": "Wednesday", "Focus": "Rest Day", "Duration": "—"},
                {
                    "Day": "Thursday",
                    "Focus": "Shooting Technique",
                    "Duration": "40 min",
                },
                {"Day": "Friday", "Focus": "Game Situations", "Duration": "45 min"},
                {"Day": "Saturday", "Focus": "Team Practice", "Duration": "90 min"},
                {"Day": "Sunday", "Focus": "Light Skills Work", "Duration": "30 min"},
            ]

            # Display schedule
            st.dataframe(pd.DataFrame(schedule), use_container_width=True)

            st.markdown("#### Recommended Drills")
            st.success(
                "**Edge Control Drill**: Figure 8s around cones focusing on inside and outside edges"
            )
            st.success(
                "**Quick Release**: Rapid fire shooting from different angles with minimal setup time"
            )

        # Smaller centered close button
        col1, col2, col3 = st.columns([3, 2, 3])
        with col2:
            if st.button("Close Preview", key="close_plan_preview", type="secondary"):
                st.session_state.show_premium_preview = None
                st.rerun()

    elif st.session_state.show_premium_preview == "peer_comparison":
        st.markdown(
            """
        <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px; margin-top: 20px; border-left: 5px solid #FFD700;">
            <h3>Peer Comparison Preview</h3>
        </div>
        """,
            unsafe_allow_html=True,
        )

        from utils.showcase_data import (
            get_sample_player_data,
            get_sample_peer_data,
            generate_peer_comparison_chart,
        )

        # Get sample data
        player = get_sample_player_data()
        peer_data = get_sample_peer_data(player)

        peer_col1, peer_col2 = st.columns([1, 1])

        with peer_col1:
            # Create percentile gauges
            import plotly.graph_objects as go

            # Calculate percentile for skating speed
            player_value = player["skating_speed"]
            peer_values = peer_data["skating_speed"].values
            percentile = (
                sum(1 for x in peer_values if x < player_value) / len(peer_values) * 100
            )

            fig = go.Figure(
                go.Indicator(
                    mode="gauge+number",
                    value=percentile,
                    domain={"x": [0, 1], "y": [0, 1]},
                    title={"text": "Skating Speed Percentile"},
                    gauge={
                        "axis": {"range": [0, 100]},
                        "bar": {"color": "royalblue"},
                        "steps": [
                            {"range": [0, 25], "color": "lightgray"},
                            {"range": [25, 50], "color": "lightgreen"},
                            {"range": [50, 75], "color": "green"},
                            {"range": [75, 100], "color": "darkgreen"},
                        ],
                        "threshold": {
                            "line": {"color": "red", "width": 4},
                            "thickness": 0.75,
                            "value": 50,
                        },
                    },
                )
            )

            fig.update_layout(height=250)
            st.plotly_chart(fig, use_container_width=True)

            st.markdown(
                """
            <div style="margin-top: 10px;">
                <h4>Anonymous Benchmarking</h4>
                <p>Compare your player's performance against peers in the same age group and position</p>
                <ul>
                    <li>Percentile rankings for key metrics</li>
                    <li>Age-appropriate comparisons</li>
                    <li>Position-specific metrics</li>
                </ul>
            </div>
            """,
                unsafe_allow_html=True,
            )

        with peer_col2:
            # Create histogram comparison
            st.markdown("#### Skill Distribution Comparison")

            hist_fig = generate_peer_comparison_chart(
                player_value=player["skating_speed"],
                peer_values=peer_data["skating_speed"].values,
                metric_name="Skating Speed",
            )
            st.plotly_chart(hist_fig, use_container_width=True)

            st.markdown("#### Peer Competition Insights")
            st.info("**Top 15%** in skating speed among peers")
            st.info("**Above average** in shooting accuracy (65th percentile)")
            st.warning("**Development needed** in puck control (32nd percentile)")

        # Smaller centered close button
        col1, col2, col3 = st.columns([3, 2, 3])
        with col2:
            if st.button("Close Preview", key="close_peer_preview", type="secondary"):
                st.session_state.show_premium_preview = None
                st.rerun()

    # Team Features Section
    st.subheader("Team & Organization Features")

    # Initialize session state for team feature previews if not exists
    if "show_team_preview" not in st.session_state:
        st.session_state.show_team_preview = None

    # Add enhanced CSS for team features
    st.markdown(
        """
    <style>
    .team-card {
        border-radius: 10px;
        padding: 20px;
        margin: 10px 5px;
        height: 230px;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
        border: 1px solid #e0e0e0;
        box-shadow: 0 4px 8px rgba(0,0,0,0.05);
        background-color: white;
    }
    
    .team-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 16px rgba(0,0,0,0.1);
    }
    
    .team-card-1 {
        border-left: 5px solid #A3CFF2;
    }
    
    .team-card-2 {
        border-left: 5px solid #4169E1;
    }
    
    .team-card-3 {
        border-left: 5px solid #C8102E;
    }
    
    .team-badge {
        background-color: #4169E1;
        color: white;
        padding: 3px 10px;
        border-radius: 15px;
        font-size: 12px;
        font-weight: bold;
        display: inline-block;
        margin-bottom: 10px;
    }
    
    .team-card-title {
        font-size: 20px;
        font-weight: 600;
        margin-bottom: 15px;
        color: #2C3E50;
    }
    
    .team-card-text {
        color: #555;
        font-size: 16px;
        line-height: 1.5;
    }
    
    .preview-link {
        position: absolute;
        bottom: 15px;
        text-align: center;
        width: 100%;
        left: 0;
        color: #4169E1;
        font-weight: 500;
        font-size: 15px;
        text-decoration: none;
        margin-top: 15px;
    }
    
    .preview-link:hover {
        text-decoration: underline;
        color: #1E3A8A;
    }
    
    /* Hide the actual buttons but keep them clickable */
    .team-button button {
        background-color: transparent !important;
        color: transparent !important;
        border: none !important;
        position: absolute !important;
        top: 0 !important;
        left: 0 !important;
        width: 100% !important;
        height: 100% !important;
        z-index: 10 !important;
        cursor: pointer !important;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

    team_cols = st.columns(3)

    # Team Dashboard Card
    with team_cols[0]:
        # Create the card
        st.markdown(
            """
        <div class="team-card team-card-1 clickable-card">
            <div class="team-badge">TEAM</div>
            <div class="team-card-title">Team Dashboard</div>
            <div class="team-card-text">
                Comprehensive team overview with skill heatmaps, performance metrics, and development tracking.
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Add a normal button below it
        if st.button("View Feature", key="team-dashboard-button"):
            st.session_state.show_team_preview = "team_dashboard"
            st.rerun()

    # Tryout Evaluation Card
    with team_cols[1]:
        # Create the card
        st.markdown(
            """
        <div class="team-card team-card-2 clickable-card">
            <div class="team-badge">TEAM</div>
            <div class="team-card-title">Tryout Evaluation</div>
            <div class="team-card-text">
                Streamlined assessment system for player tryouts with customizable evaluation criteria.
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Add a normal button below it
        if st.button("View Feature", key="tryout-evaluation-button"):
            st.session_state.show_team_preview = "tryout_evaluation"
            st.rerun()

    # Custom Reports Card
    with team_cols[2]:
        # Create the card
        st.markdown(
            """
        <div class="team-card team-card-3 clickable-card">
            <div class="team-badge">TEAM</div>
            <div class="team-card-title">Custom Reports</div>
            <div class="team-card-text">
                Generate detailed team and player reports for season reviews and development planning.
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Add a normal button below it
        if st.button("View Feature", key="custom-reports-button"):
            st.session_state.show_team_preview = "custom_reports"
            st.rerun()

    # Show team feature preview if one is selected
    if st.session_state.show_team_preview == "team_dashboard":
        st.markdown(
            """
        <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px; margin-top: 20px; border-left: 5px solid #4169E1;">
            <h3>Team Dashboard Preview</h3>
        </div>
        """,
            unsafe_allow_html=True,
        )

        import plotly.express as px
        import numpy as np

        # Create sample team data for heatmap
        players = [
            "Player 1",
            "Player 2",
            "Player 3",
            "Player 4",
            "Player 5",
            "Player 6",
            "Player 7",
            "Player 8",
            "Player 9",
            "Player 10",
        ]

        skills = ["Skating", "Shooting", "Passing", "Puck Control", "Hockey IQ"]

        # Generate random skill values (1-5 scale)
        data = np.random.uniform(2.5, 4.8, size=(len(players), len(skills)))

        # Create heatmap
        fig = px.imshow(
            data,
            x=skills,
            y=players,
            color_continuous_scale="RdBu_r",
            aspect="auto",
            labels=dict(x="Skill", y="Player", color="Rating"),
            title="Team Skills Heatmap",
            zmin=1,
            zmax=5,
        )

        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

        metrics_col1, metrics_col2, metrics_col3, metrics_col4 = st.columns(4)

        with metrics_col1:
            st.metric("Team Size", "18 players")
        with metrics_col2:
            st.metric("Games Played", "24")
        with metrics_col3:
            st.metric("Win Rate", "62%")
        with metrics_col4:
            st.metric("Avg. Goals/Game", "3.7")

        st.markdown(
            """
        <div style="margin-top: 15px;">
            <h4>Team Dashboard Features</h4>
            <ul>
                <li>Visual skill distribution across the team</li>
                <li>Identify team strengths and weaknesses</li>
                <li>Track team performance metrics over time</li>
                <li>Position-based analysis and recommendations</li>
            </ul>
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Smaller centered close button
        col1, col2, col3 = st.columns([3, 2, 3])
        with col2:
            if st.button("Close Preview", key="close_team_dashboard", type="secondary"):
                st.session_state.show_team_preview = None
                st.rerun()

    elif st.session_state.show_team_preview == "tryout_evaluation":
        st.markdown(
            """
        <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px; margin-top: 20px; border-left: 5px solid #4169E1;">
            <h3>Tryout Evaluation Preview</h3>
        </div>
        """,
            unsafe_allow_html=True,
        )

        tryout_col1, tryout_col2 = st.columns([1, 1])

        with tryout_col1:
            st.image(
                "static/images/hockey/players/face-off.jpg",
                caption="Hockey Tryout Evaluation",
            )

            st.markdown(
                """
            <div style="margin-top: 15px;">
                <h4>Streamlined Evaluation Process</h4>
                <ul>
                    <li>Real-time player scoring during tryouts</li>
                    <li>Customizable evaluation criteria by age/level</li>
                    <li>Multiple evaluator input with automatic averaging</li>
                    <li>Easy-to-use mobile interface for on-ice use</li>
                </ul>
            </div>
            """,
                unsafe_allow_html=True,
            )

        with tryout_col2:
            # Create sample evaluation form
            st.markdown("#### Sample Tryout Evaluation Form")

            player_name = st.text_input("Player Name", value="Tryout Player #42")
            st.selectbox("Position", ["Forward", "Defense", "Goalie"])

            st.markdown("##### Skill Ratings")

            # Sample sliders
            st.slider("Skating", 1, 5, 3)
            st.slider("Shooting", 1, 5, 4)
            st.slider("Passing", 1, 5, 3)

            st.text_area(
                "Notes", "Good speed and first step. Needs work on backwards skating."
            )

            st.button(
                "Submit Evaluation (Demo)",
                key="demo_submit",
                type="primary",
                use_container_width=True,
            )

        # Smaller centered close button
        col1, col2, col3 = st.columns([3, 2, 3])
        with col2:
            if st.button("Close Preview", key="close_tryout_preview", type="secondary"):
                st.session_state.show_team_preview = None
                st.rerun()

    elif st.session_state.show_team_preview == "custom_reports":
        st.markdown(
            """
        <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px; margin-top: 20px; border-left: 5px solid #4169E1;">
            <h3>Custom Reports Preview</h3>
        </div>
        """,
            unsafe_allow_html=True,
        )

        reports_col1, reports_col2 = st.columns([1, 1])

        with reports_col1:
            st.markdown("#### Report Templates")

            # Display report types
            report_types = [
                "Team Performance Summary",
                "Individual Player Assessment",
                "Season Development Progress",
                "Game-by-Game Analysis",
                "Position Group Comparison",
            ]

            st.selectbox("Select Report Type", report_types)

            st.markdown(
                """
            <div style="margin-top: 15px;">
                <h4>Professional Report Generation</h4>
                <ul>
                    <li>Customizable report templates</li>
                    <li>Export to PDF, Excel, or printable formats</li>
                    <li>Data-driven insights and visualizations</li>
                    <li>Coach recommendations and notes inclusion</li>
                </ul>
            </div>
            """,
                unsafe_allow_html=True,
            )

            if st.button("Generate Sample Report", key="demo_report", type="primary"):
                st.success("Sample report generated! See preview on the right.")

        with reports_col2:
            st.image(
                "static/images/hockey/players/goalie-crouching.jpg",
                caption="Hockey Team Performance Report",
            )

            # Sample report sections
            st.markdown(
                """
            #### Report Sections
            - **Team Overview**: Season statistics and standings
            - **Performance Trends**: Charts showing improvement over time
            - **Strengths & Weaknesses**: Team skill assessment
            - **Player Highlights**: Top performers in key metrics
            - **Development Recommendations**: Focus areas for team improvement
            """
            )

        # Smaller centered close button
        col1, col2, col3 = st.columns([3, 2, 3])
        with col2:
            if st.button(
                "Close Preview", key="close_reports_preview", type="secondary"
            ):
                st.session_state.show_team_preview = None
                st.rerun()

    # Pricing Banner
    st.markdown(
        """
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
    """,
        unsafe_allow_html=True,
    )

    # Space before call to action
    st.markdown("<div style='margin: 20px 0;'></div>", unsafe_allow_html=True)

    # Call to action
    st.markdown(
        """
    <div style="text-align: center; margin: 30px 0;">
        <h2>Ready to elevate your hockey development?</h2>
    </div>
    """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        col1, col2 = st.columns(2)
        with col1:
            if st.button(
                "Sign Up Now",
                type="primary",
                key="signup_button",
                use_container_width=True,
            ):
                st.session_state.show_signup = True
                st.rerun()
        with col2:
            if st.button(
                "Login", key="login_button", type="secondary", use_container_width=True
            ):
                st.session_state.show_login = True
                st.rerun()

        # Reset password option
        forgot_col1, forgot_col2, forgot_col3 = st.columns([1, 2, 1])
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
            st.selectbox("Role", ["Coach", "Team Manager", "Parent"])
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
                new_user = User(username=username, name=name, is_admin=False)
                new_user.set_password(password)
                db.session.add(new_user)
                db.session.commit()

                # Set session state and clear signup flag
                st.session_state.user = {
                    "id": new_user.id,
                    "username": new_user.username,
                    "name": new_user.name,
                    "is_admin": new_user.is_admin,
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
    if "show_signup" not in st.session_state:
        st.session_state.show_signup = False
    if "show_login" not in st.session_state:
        st.session_state.show_login = False
    if "show_forgot_password" not in st.session_state:
        st.session_state.show_forgot_password = False
    if "show_reset_confirmation" not in st.session_state:
        st.session_state.show_reset_confirmation = False

    # Check if user is already logged in
    if "user" in st.session_state and st.session_state.user:
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
    elif st.session_state.get("show_login", False):
        from components.auth_interface import login_user

        login_user()
    elif st.session_state.get("show_forgot_password", False):
        from components.auth_interface import request_password_reset

        request_password_reset()
    else:
        display_feature_preview()

    return True  # Show landing pageing page
