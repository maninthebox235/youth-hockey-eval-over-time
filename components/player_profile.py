import streamlit as st
import plotly.express as px
from components.coach_feedback import display_feedback_form, display_feedback_history
from components.feedback_templates import manage_feedback_templates

def display_player_profile(player_data, player_history):
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

    with col2:
        st.subheader("Current Statistics")

        # Display different metrics based on position
        if player_data['position'] == 'Goalie':
            metrics_col1, metrics_col2, metrics_col3 = st.columns(3)

            # Handle potential None values
            save_pct = player_data.get('save_percentage', 0) or 0
            reaction = player_data.get('reaction_time', 0) or 0
            pos = player_data.get('positioning', 0) or 0

            with metrics_col1:
                st.metric("Save Percentage", f"{save_pct:.1f}%")
            with metrics_col2:
                st.metric("Reaction Time", f"{reaction:.1f}")
            with metrics_col3:
                st.metric("Positioning", f"{pos:.1f}")

            # Additional goalie stats
            stats_col1, stats_col2 = st.columns(2)
            with stats_col1:
                st.metric("Games Played", player_data.get('games_played', 0))
                st.metric("Saves", player_data.get('saves', 0))
            with stats_col2:
                st.metric("Goals Against", player_data.get('goals_against', 0))

                # Calculate save percentage from actual saves and goals against
                total_shots = player_data.get('saves', 0) + player_data.get('goals_against', 0)
                save_percentage = (player_data.get('saves', 0) / total_shots * 100) if total_shots > 0 else 0
                st.metric("Game Save Percentage", f"{save_percentage:.1f}%")
        else:
            metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
            with metrics_col1:
                st.metric("Skating Speed", f"{player_data.get('skating_speed', 0):.1f}")
            with metrics_col2:
                st.metric("Shooting Accuracy", f"{player_data.get('shooting_accuracy', 0):.1f}%")
            with metrics_col3:
                st.metric("Games Played", player_data.get('games_played', 0))

            # Additional skater stats
            stats_col1, stats_col2 = st.columns(2)
            with stats_col1:
                st.metric("Goals", player_data.get('goals', 0))
            with stats_col2:
                st.metric("Assists", player_data.get('assists', 0))

        st.subheader("Season Performance")
        if not player_history.empty:
            if player_data['position'] == 'Goalie':
                metrics_to_plot = ['save_percentage', 'positioning', 'reaction_time']
                fig = px.line(player_history, x='date', y=metrics_to_plot,
                            title="Goalie Performance Metrics Over Time")
            else:
                fig = px.line(player_history, x='date', y=['goals', 'assists'],
                            title="Goals and Assists Over Time")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No performance history available for this player.")

    # Add coach feedback section
    st.markdown("---")
    tab1, tab2, tab3 = st.tabs(["Submit Feedback", "Feedback History", "Manage Templates"])

    with tab1:
        display_feedback_form(
            player_data['player_id'], 
            player_data['name'],
            player_data['position']
        )

    with tab2:
        display_feedback_history(player_data['player_id'])

    with tab3:
        manage_feedback_templates()