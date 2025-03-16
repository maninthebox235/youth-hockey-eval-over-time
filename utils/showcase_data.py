"""
Utility for generating showcase data for the landing page.
This module creates realistic demo data to demonstrate the app's features.
"""
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import streamlit as st
import base64
from io import BytesIO

def get_sample_player_data():
    """Return a sample player with realistic data"""
    player = {
        'player_id': 999,
        'name': 'Alex Johnson',
        'age': 12,
        'age_group': 'U12',
        'position': 'Forward',
        'skating_speed': 4.2,
        'shooting_accuracy': 3.8,
        'puck_control': 3.5,
        'passing_accuracy': 4.0,
        'hockey_sense': 4.1,
        'games_played': 24,
        'goals': 18,
        'assists': 12,
        'join_date': datetime.now() - timedelta(days=365)
    }
    return player

def get_sample_goalie_data():
    """Return a sample goalie with realistic data"""
    player = {
        'player_id': 998,
        'name': 'Sam Martinez',
        'age': 13,
        'age_group': 'U14',
        'position': 'Goalie',
        'save_percentage': 91.5,
        'reaction_time': 4.3,
        'positioning': 3.9,
        'save_technique': 4.1,
        'rebound_control': 3.7,
        'games_played': 20,
        'saves': 342,
        'goals_against': 32,
        'join_date': datetime.now() - timedelta(days=300)
    }
    return player

def get_sample_player_history():
    """Return sample player history data for charts"""
    # Create 12 months of data
    dates = pd.date_range(end=datetime.now(), periods=12, freq='ME')
    
    # Generate realistic progress data with improvement over time
    data = []
    for i, date in enumerate(dates):
        # Base values that improve over time with some variability
        skating_base = 3.0 + (i * 0.12)
        shooting_base = 2.8 + (i * 0.1)
        
        # Add some natural variation
        data.append({
            'date': date,
            'skating_speed': min(5.0, skating_base + np.random.normal(0, 0.2)),
            'shooting_accuracy': min(5.0, shooting_base + np.random.normal(0, 0.25)),
            'puck_control': min(5.0, 2.5 + (i * 0.15) + np.random.normal(0, 0.15)),
            'passing_accuracy': min(5.0, 3.0 + (i * 0.08) + np.random.normal(0, 0.2)),
            'games_played': np.random.randint(1, 4),
            'goals': np.random.randint(0, 3),
            'assists': np.random.randint(0, 4)
        })
    
    return pd.DataFrame(data)

def get_sample_goalie_history():
    """Return sample goalie history data for charts"""
    # Create 12 months of data
    dates = pd.date_range(end=datetime.now(), periods=12, freq='ME')
    
    # Generate realistic progress data with improvement over time
    data = []
    for i, date in enumerate(dates):
        # Base values that improve over time with some variability
        save_pct_base = 85.0 + (i * 0.5)
        
        # Add some natural variation
        data.append({
            'date': date,
            'save_percentage': min(95.0, save_pct_base + np.random.normal(0, 1.0)),
            'reaction_time': min(5.0, 3.5 + (i * 0.08) + np.random.normal(0, 0.15)),
            'positioning': min(5.0, 3.2 + (i * 0.1) + np.random.normal(0, 0.2)),
            'games_played': np.random.randint(1, 3),
            'saves': np.random.randint(20, 40),
            'goals_against': np.random.randint(1, 5)
        })
    
    return pd.DataFrame(data)

def get_sample_peer_data(player_data):
    """Return anonymized peer comparison data"""
    age = player_data['age']
    position = player_data['position']
    
    # Create 15 peers with similar age but varying skills
    peers = []
    for i in range(15):
        peer = {
            'peer_id': f'Player {i+1}',
            'age': age + np.random.randint(-1, 2),
            'position': position
        }
        
        # Generate skill metrics based on position
        if position == 'Goalie':
            peer.update({
                'save_percentage': np.random.uniform(85.0, 95.0),
                'reaction_time': np.random.uniform(3.0, 5.0),
                'positioning': np.random.uniform(3.0, 5.0),
                'save_technique': np.random.uniform(3.0, 5.0),
                'rebound_control': np.random.uniform(3.0, 5.0),
                'games_played': np.random.randint(15, 25)
            })
        else:
            peer.update({
                'skating_speed': np.random.uniform(3.0, 5.0),
                'shooting_accuracy': np.random.uniform(2.5, 5.0),
                'puck_control': np.random.uniform(2.8, 5.0),
                'passing_accuracy': np.random.uniform(2.5, 5.0),
                'hockey_sense': np.random.uniform(2.5, 5.0),
                'games_played': np.random.randint(15, 30),
                'goals': np.random.randint(0, 25),
                'assists': np.random.randint(0, 30)
            })
        
        peers.append(peer)
    
    return pd.DataFrame(peers)

def generate_skill_radar_chart(player_data):
    """Generate a skill radar chart for a player"""
    # Get metrics based on position
    if player_data['position'] == 'Goalie':
        metrics = [
            'reaction_time', 'positioning', 'save_technique', 
            'rebound_control', 'puck_handling'
        ]
        values = [
            player_data.get('reaction_time', 0),
            player_data.get('positioning', 0),
            player_data.get('save_technique', 0),
            player_data.get('rebound_control', 0),
            player_data.get('puck_handling', 3.7)  # Default if not provided
        ]
    else:
        metrics = [
            'skating_speed', 'shooting_accuracy', 'puck_control',
            'passing_accuracy', 'hockey_sense'
        ]
        values = [
            player_data.get('skating_speed', 0),
            player_data.get('shooting_accuracy', 0),
            player_data.get('puck_control', 0),
            player_data.get('passing_accuracy', 0),
            player_data.get('hockey_sense', 0)
        ]
    
    # Create radar chart
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=[m.replace('_', ' ').title() for m in metrics],
        fill='toself',
        name=player_data['name']
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 5]
            )
        ),
        showlegend=True,
        height=400,
        margin=dict(l=80, r=80, t=20, b=20)
    )
    
    return fig

def generate_progress_chart(player_history, metric='skating_speed'):
    """Generate a progress chart for a specific metric"""
    if metric not in player_history.columns:
        return None
        
    title = f"{metric.replace('_', ' ').title()} Progress Over Time"
    
    fig = px.line(
        player_history,
        x='date',
        y=metric,
        title=title,
        markers=True
    )
    
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title=metric.replace('_', ' ').title(),
        height=300,
        margin=dict(l=40, r=40, t=40, b=40)
    )
    
    return fig

def generate_peer_comparison_chart(player_value, peer_values, metric_name):
    """Generate a peer comparison histogram"""
    fig = px.histogram(
        pd.DataFrame({metric_name: peer_values}),
        x=metric_name,
        nbins=10,
        title=f"Distribution of {metric_name.replace('_', ' ').title()} Among Peers"
    )
    
    # Add vertical line for player's value
    fig.add_vline(
        x=player_value,
        line_dash="dash",
        line_color="red",
        annotation_text="Player's value",
        annotation_position="top"
    )
    
    fig.update_layout(
        height=300,
        margin=dict(l=40, r=40, t=60, b=40)
    )
    
    return fig

def display_feature_showcase():
    """Display feature showcase on the landing page"""
    st.subheader("App Features in Action")
    
    # Get sample data
    player = get_sample_player_data()
    player_history = get_sample_player_history()
    peer_data = get_sample_peer_data(player)
    
    # Create tabs for different features
    showcase_tabs = st.tabs([
        "Player Dashboard", 
        "Development Tracking", 
        "Peer Comparison", 
        "Position-Specific Analysis"
    ])
    
    # Tab 1: Player Dashboard
    with showcase_tabs[0]:
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.image("https://images.unsplash.com/photo-1547223431-cc59f141f389", caption=player['name'])
            
            st.markdown(f"""
            <div style="padding: 10px; border-radius: 5px; background-color: #f0f8ff; margin-top: 10px;">
                <strong>Age:</strong> {player['age']} ({player['age_group']})<br>
                <strong>Position:</strong> {player['position']}<br>
                <strong>Games:</strong> {player['games_played']}
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            # Create radar chart
            radar_fig = generate_skill_radar_chart(player)
            st.plotly_chart(radar_fig, use_container_width=True)
            
            # Show key stats
            st.markdown("### Key Statistics")
            stat_cols = st.columns(3)
            
            with stat_cols[0]:
                st.metric("Goals", player['goals'])
            with stat_cols[1]:
                st.metric("Assists", player['assists'])
            with stat_cols[2]:
                st.metric("Points", player['goals'] + player['assists'])
    
    # Tab 2: Development Tracking
    with showcase_tabs[1]:
        st.markdown("### Player Development Over Time")
        st.write("Track progress across multiple skills with detailed charts")
        
        dev_col1, dev_col2 = st.columns(2)
        
        with dev_col1:
            skating_chart = generate_progress_chart(player_history, 'skating_speed')
            st.plotly_chart(skating_chart, use_container_width=True)
        
        with dev_col2:
            shooting_chart = generate_progress_chart(player_history, 'shooting_accuracy')
            st.plotly_chart(shooting_chart, use_container_width=True)
            
        st.markdown("### Performance Metrics")
        st.write("Track game statistics to monitor on-ice performance")
        
        # Create synthetic game stats chart
        perf_data = player_history[['date', 'goals', 'assists']].copy()
        perf_data.loc[:, 'points'] = perf_data['goals'] + perf_data['assists']
        
        perf_fig = px.bar(
            perf_data,
            x='date',
            y=['goals', 'assists'],
            title="Goals and Assists by Month",
            labels={'value': 'Count', 'variable': 'Statistic'},
            barmode='group'
        )
        
        st.plotly_chart(perf_fig, use_container_width=True)
    
    # Tab 3: Peer Comparison
    with showcase_tabs[2]:
        st.markdown("### Peer Comparison Analytics")
        st.write("Compare player performance to peers in the same age group and position")
        
        # Create peer comparison widgets
        metric_options = ['skating_speed', 'shooting_accuracy', 'puck_control', 'passing_accuracy']
        selected_metric = 'skating_speed'
        
        player_value = player[selected_metric]
        peer_values = peer_data[selected_metric].values
        
        # Calculate percentile
        percentile = sum(1 for x in peer_values if x < player_value) / len(peer_values) * 100
        
        # Create percentile gauge
        gauge_col1, gauge_col2 = st.columns([1, 2])
        
        with gauge_col1:
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=percentile,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Percentile Rank"},
                gauge={
                    'axis': {'range': [0, 100]},
                    'bar': {'color': "royalblue"},
                    'steps': [
                        {'range': [0, 25], 'color': "lightgray"},
                        {'range': [25, 50], 'color': "lightgreen"},
                        {'range': [50, 75], 'color': "green"},
                        {'range': [75, 100], 'color': "darkgreen"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 50
                    }
                }
            ))
            
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        
        with gauge_col2:
            # Create histogram comparison
            hist_fig = generate_peer_comparison_chart(
                player_value, peer_values, selected_metric
            )
            st.plotly_chart(hist_fig, use_container_width=True)
            
        # Recommendations based on comparison
        st.markdown("### Development Recommendations")
        rec_col1, rec_col2 = st.columns(2)
        
        with rec_col1:
            st.markdown("""
            #### Areas for Improvement
            **Shooting Accuracy** (Percentile: 65%)
            - **Focus:** Shot repetition, proper weight transfer
            - **Drills:** Target practice, quick release drills
            """)
        
        with rec_col2:
            st.markdown("""
            #### Key Strengths
            **Skating Speed** (Percentile: 88%)
            - **Focus:** Continue to develop this elite skill
            - **Advanced:** Work on edge control at high speeds
            """)
    
    # Tab 4: Position-Specific Analysis
    with showcase_tabs[3]:
        st.markdown("### Position-Specific Analysis")
        st.write("Metrics and analytics tailored to each player's position")
        
        # Get goalie data
        goalie = get_sample_goalie_data()
        goalie_history = get_sample_goalie_history()
        
        pos_col1, pos_col2 = st.columns(2)
        
        with pos_col1:
            st.markdown("#### Forward Metrics")
            
            # Forward metrics radar chart
            forward_metrics = {
                'skating_speed': player['skating_speed'],
                'shooting_accuracy': player['shooting_accuracy'],
                'puck_control': player['puck_control'],
                'passing_accuracy': player['passing_accuracy'],
                'hockey_sense': player['hockey_sense']
            }
            
            forward_radar_fig = go.Figure()
            
            forward_radar_fig.add_trace(go.Scatterpolar(
                r=list(forward_metrics.values()),
                theta=[m.replace('_', ' ').title() for m in forward_metrics.keys()],
                fill='toself',
                name='Forward Skills'
            ))
            
            forward_radar_fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 5]
                    )
                ),
                showlegend=False,
                height=300,
                margin=dict(l=40, r=40, t=20, b=20)
            )
            
            st.plotly_chart(forward_radar_fig, use_container_width=True)
        
        with pos_col2:
            st.markdown("#### Goalie Metrics")
            
            # Goalie metrics radar chart
            goalie_metrics = {
                'reaction_time': goalie['reaction_time'],
                'positioning': goalie['positioning'],
                'save_technique': goalie['save_technique'],
                'rebound_control': goalie['rebound_control'],
                'save_percentage': goalie['save_percentage'] / 20  # Scale to 1-5 for radar chart
            }
            
            goalie_radar_fig = go.Figure()
            
            goalie_radar_fig.add_trace(go.Scatterpolar(
                r=list(goalie_metrics.values()),
                theta=[m.replace('_', ' ').title() for m in goalie_metrics.keys()],
                fill='toself',
                name='Goalie Skills'
            ))
            
            goalie_radar_fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 5]
                    )
                ),
                showlegend=False,
                height=300,
                margin=dict(l=40, r=40, t=20, b=20)
            )
            
            st.plotly_chart(goalie_radar_fig, use_container_width=True)
        
        # Save percentage chart for goalie
        st.markdown("#### Goalie Performance Tracking")
        
        save_pct_fig = px.line(
            goalie_history,
            x='date',
            y='save_percentage',
            title="Save Percentage Over Time",
            markers=True
        )
        
        save_pct_fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Save Percentage",
            height=300,
            margin=dict(l=40, r=40, t=40, b=40)
        )
        
        st.plotly_chart(save_pct_fig, use_container_width=True)
        
        # Show example data table
        st.markdown("#### Advanced Statistics")
        
        # Create a sample advanced stats dataframe - using all strings to avoid PyArrow conversion issues
        advanced_stats = pd.DataFrame([
            {'Metric': 'Goals per Game', 'Forward': '0.75', 'Defense': '0.35', 'Goalie': 'N/A'},
            {'Metric': 'Save Percentage', 'Forward': 'N/A', 'Defense': 'N/A', 'Goalie': '91.5%'},
            {'Metric': 'Shot Generation', 'Forward': '3.2', 'Defense': '1.8', 'Goalie': 'N/A'},
            {'Metric': 'Time on Ice', 'Forward': '18:45', 'Defense': '22:30', 'Goalie': '60:00'},
            {'Metric': 'Defensive Zone Starts', 'Forward': '42%', 'Defense': '65%', 'Goalie': 'N/A'}
        ])
        
        st.dataframe(advanced_stats, use_container_width=True)