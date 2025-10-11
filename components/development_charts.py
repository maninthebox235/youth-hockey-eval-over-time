import streamlit as st
import plotly.express as px
import plotly.graph_objects as go


def plot_skill_radar(player_data):
    categories = ["Skating Speed", "Shooting Accuracy", "Game Experience"]
    values = [
        player_data["skating_speed"],
        player_data["shooting_accuracy"],
        min(100, player_data["games_played"] * 2),
    ]

    fig = go.Figure(data=go.Scatterpolar(r=values, theta=categories, fill="toself"))

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=False
    )

    return fig


def plot_progress_timeline(player_history):
    if player_history.empty:
        return None

    fig = px.line(
        player_history,
        x="date",
        y=["skating_speed", "shooting_accuracy"],
        title="Skill Development Over Time",
        labels={"value": "Score", "variable": "Metric"},
    )
    return fig


def display_development_charts(player_data, player_history):
    st.subheader("Player Development Overview")

    col1, col2 = st.columns(2)

    with col1:
        radar_fig = plot_skill_radar(player_data)
        st.plotly_chart(radar_fig, use_container_width=True)

    with col2:
        timeline_fig = plot_progress_timeline(player_history)
        if timeline_fig:
            st.plotly_chart(timeline_fig, use_container_width=True)
        else:
            st.info("No historical data available for this player.")
