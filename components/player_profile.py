import streamlit as st
import plotly.express as px

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
        metrics_col1, metrics_col2, metrics_col3 = st.columns(3)

        with metrics_col1:
            st.metric("Skating Speed", f"{player_data['skating_speed']:.1f}")
        with metrics_col2:
            st.metric("Shooting Accuracy", f"{player_data['shooting_accuracy']:.1f}%")
        with metrics_col3:
            st.metric("Games Played", player_data['games_played'])

        st.subheader("Season Performance")
        if not player_history.empty:
            fig = px.line(player_history, x='date', y=['goals', 'assists'],
                         title="Goals and Assists Over Time")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No performance history available for this player.")