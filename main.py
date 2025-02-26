import streamlit as st
import pandas as pd
import plotly.express as px  # Add this import
from utils.data_generator import generate_mock_players, generate_player_history
from components.player_profile import display_player_profile
from components.development_charts import display_development_charts
from components.stats_dashboard import display_age_group_stats, display_player_rankings

st.set_page_config(page_title="Youth Hockey Development Tracker",
                   page_icon="🏒",
                   layout="wide")

# Load custom CSS
with open('styles/custom.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Initialize session state
if 'players_df' not in st.session_state:
    st.session_state.players_df = generate_mock_players()

# App header
st.title("🏒 Youth Hockey Development Tracker")

# Sidebar
st.sidebar.image("https://images.unsplash.com/photo-1547223431-cc59f141f389",
                 caption="Player Development Platform")

menu = st.sidebar.selectbox(
    "Navigation",
    ["Player Profiles", "Development Analytics", "Team Statistics"]
)

if menu == "Player Profiles":
    st.subheader("Player Profiles")
    
    # Player selection
    selected_player = st.selectbox(
        "Select Player",
        st.session_state.players_df['name'].tolist()
    )
    
    player_data = st.session_state.players_df[
        st.session_state.players_df['name'] == selected_player
    ].iloc[0]
    
    player_history = generate_player_history(player_data['player_id'])
    
    display_player_profile(player_data, player_history)
    display_development_charts(player_data, player_history)

elif menu == "Development Analytics":
    st.subheader("Development Analytics")
    
    # Age group filter
    age_group = st.selectbox(
        "Select Age Group",
        sorted(st.session_state.players_df['age_group'].unique())
    )
    
    filtered_df = st.session_state.players_df[
        st.session_state.players_df['age_group'] == age_group
    ]
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.scatter(filtered_df, x='skating_speed', y='shooting_accuracy',
                        color='position', hover_data=['name'],
                        title=f"Skill Distribution - {age_group}")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.box(filtered_df, y=['skating_speed', 'shooting_accuracy'],
                     title=f"Skill Ranges - {age_group}")
        st.plotly_chart(fig, use_container_width=True)

else:  # Team Statistics
    st.subheader("Team Statistics")
    
    display_age_group_stats(st.session_state.players_df)
    display_player_rankings(st.session_state.players_df)
    
    st.subheader("Equipment Resources")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.image("https://images.unsplash.com/photo-1547223431-cc59f141f389",
                 caption="Essential Equipment")
    with col2:
        st.image("https://images.unsplash.com/photo-1684907110935-dcb64eba6add",
                 caption="Training Gear")
    with col3:
        st.image("https://images.unsplash.com/photo-1725981408549-73467108cbf9",
                 caption="Safety Equipment")