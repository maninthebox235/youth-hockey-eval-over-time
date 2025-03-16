import streamlit as st
import plotly.express as px
from components.coach_feedback import display_feedback_form, display_feedback_history
from components.feedback_templates import manage_feedback_templates
from components.skill_assessment import display_skill_assessment
import pandas as pd
from utils.pdf_report import display_pdf_export_section

def get_age_benchmark(age, skill_type):
    """Get benchmark data for a given age and skill"""
    benchmarks = {
        'skating_speed': {
            '6-8': 2.5,
            '9-11': 3.0,
            '12-14': 3.5,
            '15-18': 4.0
        },
        'shooting_accuracy': {
            '6-8': 2.0,
            '9-11': 2.8,
            '12-14': 3.3,
            '15-18': 3.8
        }
    }

    # Determine age group
    if 6 <= age <= 8:
        age_group = '6-8'
    elif 9 <= age <= 11:
        age_group = '9-11'
    elif 12 <= age <= 14:
        age_group = '12-14'
    else:
        age_group = '15-18'

    return benchmarks.get(skill_type, {}).get(age_group, 3.0)

def display_player_profile(player_data, player_history):
    """Display comprehensive player profile with skill assessments"""

    # Profile Header
    col1, col2 = st.columns([1, 2])

    with col1:
        st.image("https://images.unsplash.com/photo-1517177646641-83fe10f14633", 
                caption=player_data['name'])

        st.markdown(f"""
        ### Player Details
        - **Age:** {player_data['age']}
        - **Age Group:** {player_data['age_group']}
        - **Position:** {player_data['position']}
        - **Join Date:** {player_data['join_date'].strftime('%Y-%m-%d')}
        """)

    # Create tabs for different sections
    tabs = st.tabs(["Current Stats", "Skill Assessment", "Development Charts", "Feedback", "Export Report"])

    with tabs[0]:  # Current Stats
        st.subheader("Current Statistics")
        if player_data['position'] == 'Goalie':
            _display_goalie_stats(player_data)
        else:
            _display_skater_stats(player_data)

    with tabs[1]:  # Skill Assessment
        st.subheader("Skill Assessment")
        assessment_saved = display_skill_assessment(player_data['player_id'])
        
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
                player_data['player_id'],
                player_data['name'],
                player_data['position']
            )

        with feedback_tabs[1]:
            display_feedback_history(player_data['player_id'])

        with feedback_tabs[2]:
            if 'manage_templates' not in st.session_state:
                st.session_state.manage_templates = False

            if st.session_state.manage_templates:
                manage_feedback_templates()
            else:
                if st.button("Manage Templates"):
                    st.session_state.manage_templates = True
                    st.rerun()
                    
    with tabs[4]:  # Export Report
        display_pdf_export_section(player_data['player_id'])

def _display_skater_stats(player_data):
    """Display statistics for skater players"""
    from utils.type_converter import to_float, to_int
    
    metrics_col1, metrics_col2, metrics_col3 = st.columns(3)

    # Get benchmarks
    skating_benchmark = get_age_benchmark(player_data['age'], 'skating_speed')
    shooting_benchmark = get_age_benchmark(player_data['age'], 'shooting_accuracy')

    with metrics_col1:
        # Use type converter to handle various numeric types consistently
        current = to_float(player_data.get('skating_speed', 0)) or 0
        # Ensure value is in 1-5 range
        current = min(max(current, 1), 5) if current else 0
        st.metric(
            "Skating Speed",
            f"{current:.1f}/5",
            f"{(current - skating_benchmark):.1f} vs benchmark"
        )

    with metrics_col2:
        # Use type converter to handle various numeric types consistently
        current = to_float(player_data.get('shooting_accuracy', 0)) or 0
        # Ensure value is in 1-5 range
        current = min(max(current, 1), 5) if current else 0
        st.metric(
            "Shooting Accuracy",
            f"{current:.1f}/5",
            f"{(current - shooting_benchmark):.1f} vs benchmark"
        )

    with metrics_col3:
        st.metric("Games Played", to_int(player_data.get('games_played', 0)) or 0)

    # Additional stats
    stats_col1, stats_col2 = st.columns(2)
    with stats_col1:
        st.metric("Goals", to_int(player_data.get('goals', 0)) or 0)
    with stats_col2:
        st.metric("Assists", to_int(player_data.get('assists', 0)) or 0)

def _display_goalie_stats(player_data):
    """Display statistics for goalie players"""
    from utils.type_converter import to_float, to_int
    
    metrics_col1, metrics_col2, metrics_col3 = st.columns(3)

    # Use type conversion functions for consistent data handling
    save_pct = to_float(player_data.get('save_percentage', 0)) or 0
    reaction = to_float(player_data.get('reaction_time', 0)) or 0
    positioning = to_float(player_data.get('positioning', 0)) or 0
    
    # Ensure values are in 1-5 range
    reaction = min(max(reaction, 1), 5) if reaction else 0
    positioning = min(max(positioning, 1), 5) if positioning else 0

    with metrics_col1:
        st.metric("Save Percentage", f"{save_pct:.1f}%")
    with metrics_col2:
        st.metric("Reaction Time", f"{reaction:.1f}/5")
    with metrics_col3:
        st.metric("Positioning", f"{positioning:.1f}/5")

    # Additional goalie stats
    stats_col1, stats_col2 = st.columns(2)
    
    # Get integer metrics with proper conversion
    games_played = to_int(player_data.get('games_played', 0)) or 0
    saves = to_int(player_data.get('saves', 0)) or 0
    goals_against = to_int(player_data.get('goals_against', 0)) or 0
    
    with stats_col1:
        st.metric("Games Played", games_played)
        st.metric("Saves", saves)
    with stats_col2:
        st.metric("Goals Against", goals_against)

        # Calculate save percentage
        total_shots = saves + goals_against
        save_percentage = (saves / total_shots * 100) if total_shots > 0 else 0
        st.metric("Game Save Percentage", f"{save_percentage:.1f}%")

def _display_development_charts(player_data, player_history):
    """Display development progress charts"""
    if player_data['position'] == 'Goalie':
        metrics_to_plot = ['save_percentage', 'positioning', 'reaction_time']
        fig = px.line(
            player_history,
            x='date',
            y=metrics_to_plot,
            title="Goalie Performance Metrics Over Time"
        )
    else:
        # For skaters, show both performance metrics and game statistics
        fig1 = px.line(
            player_history,
            x='date',
            y=['skating_speed', 'shooting_accuracy'],
            title="Skill Development Over Time"
        )

        fig2 = px.line(
            player_history,
            x='date',
            y=['goals', 'assists'],
            title="Game Performance Over Time"
        )

        st.plotly_chart(fig1, use_container_width=True)
        st.plotly_chart(fig2, use_container_width=True)
        return

    st.plotly_chart(fig, use_container_width=True)

def get_player(player_id):
    """Get player by ID"""
    try:
        # Use our type_converter utility to handle any numeric type including numpy types
        from utils.type_converter import to_int
        player_id = to_int(player_id)
        
        if player_id is None:
            print("Invalid player ID: None after conversion")
            return None

        from database.models import Player
        player = Player.query.get(player_id)
        if player:
            return player
        return None
    except Exception as e:
        print(f"Error getting player: {e}")
        return None