"""
Admin dashboard component for viewing and managing all players and teams
"""
import streamlit as st
import pandas as pd
from database.models import Player, Team, TeamMembership, db, User, CoachFeedback

def get_all_players():
    """Get all players in the system"""
    players = Player.query.all()
    players_data = []
    
    for player in players:
        # Get coach name
        coach = User.query.filter_by(id=player.user_id).first()
        coach_name = coach.name if coach else "Unknown"
        
        # Add player data
        players_data.append({
            "ID": player.id,
            "Name": player.name,
            "Age": player.age,
            "Position": player.position,
            "Age Group": player.age_group,
            "Coach": coach_name,
            "Games": player.games_played or 0,
            "Goals": player.goals or 0,
            "Assists": player.assists or 0
        })
    
    return pd.DataFrame(players_data)

def get_all_teams():
    """Get all teams in the system"""
    teams = Team.query.all()
    teams_data = []
    
    for team in teams:
        # Get player count
        player_count = team.players.count()
        
        # Add team data
        teams_data.append({
            "ID": team.id,
            "Name": team.name,
            "Age Group": team.age_group,
            "Players": player_count,
            "Games": team.games_played or 0,
            "Wins": team.wins or 0,
            "Losses": team.losses or 0
        })
    
    return pd.DataFrame(teams_data)

def get_user_list():
    """Get all users in the system"""
    users = User.query.all()
    users_data = []
    
    for user in users:
        # Get player count
        player_count = Player.query.filter_by(user_id=user.id).count()
        
        # Add user data
        users_data.append({
            "ID": user.id,
            "Username": user.username,
            "Name": user.name,
            "Admin": "Yes" if user.is_admin else "No",
            "Players": player_count,
            "Last Login": user.last_login.strftime("%Y-%m-%d %H:%M") if user.last_login else "Never"
        })
    
    return pd.DataFrame(users_data)

def display_player_details(player_id):
    """Display detailed information about a player"""
    player = Player.query.get(player_id)
    
    if not player:
        st.error(f"Player with ID {player_id} not found.")
        return
    
    # Basic info
    col1, col2 = st.columns(2)
    with col1:
        st.subheader(player.name)
        st.write(f"Age: {player.age} ({player.age_group})")
        st.write(f"Position: {player.position}")
        
        # Get coach name
        coach = User.query.filter_by(id=player.user_id).first()
        st.write(f"Coach: {coach.name if coach else 'Unknown'}")
    
    with col2:
        st.write(f"Games Played: {player.games_played or 0}")
        st.write(f"Goals: {player.goals or 0}")
        st.write(f"Assists: {player.assists or 0}")
        
        # Get teams
        teams = player.teams.all()
        if teams:
            team_names = [team.name for team in teams]
            st.write(f"Teams: {', '.join(team_names)}")
        else:
            st.write("Not assigned to any teams")
    
    # Metrics tabs
    tab1, tab2, tab3 = st.tabs(["Skills", "History", "Feedback"])
    
    with tab1:
        st.write("### Skill Metrics")
        metrics = {}
        
        # Skating metrics
        metrics["Skating"] = {
            "Skating Speed": player.skating_speed,
            "Edge Control": player.edge_control,
            "Agility": player.agility,
            "Backward Skating": player.backward_skating
        }
        
        # Puck skills
        metrics["Puck Skills"] = {
            "Puck Control": player.puck_control,
            "Passing Accuracy": player.passing_accuracy,
            "Receiving": player.receiving,
            "Stick Protection": player.stick_protection
        }
        
        # Shooting skills
        metrics["Shooting"] = {
            "Wrist Shot": player.wrist_shot,
            "Slap Shot": player.slap_shot,
            "One Timer": player.one_timer,
            "Shot Accuracy": player.shot_accuracy
        }
        
        # Hockey sense
        metrics["Hockey Sense"] = {
            "Decision Making": player.decision_making,
            "Game Awareness": player.game_awareness,
            "Hockey Sense": player.hockey_sense
        }
        
        # For goalies
        if player.position == "Goalie":
            metrics["Goalie Skills"] = {
                "Save Percentage": player.save_percentage,
                "Reaction Time": player.reaction_time,
                "Positioning": player.positioning,
                "Save Technique": player.save_technique,
                "Rebound Control": player.rebound_control,
                "Puck Handling": player.puck_handling
            }
        
        # Display metrics
        for category, skills in metrics.items():
            st.write(f"**{category}**")
            data = []
            for skill, value in skills.items():
                if value is not None:
                    data.append({"Skill": skill, "Rating": value})
            
            if data:
                df = pd.DataFrame(data)
                st.bar_chart(df.set_index("Skill"))
            else:
                st.info(f"No {category.lower()} metrics recorded yet.")
    
    with tab2:
        st.write("### Player History")
        history = player.history
        
        if history:
            history_data = []
            for entry in history:
                history_data.append({
                    "Date": entry.date,
                    "Skating": entry.skating_speed,
                    "Shooting": entry.shooting_accuracy,
                    "Passing": entry.passing_accuracy,
                    "Notes": entry.notes
                })
            
            if history_data:
                st.dataframe(pd.DataFrame(history_data))
        else:
            st.info("No history records available.")
    
    with tab3:
        st.write("### Coach Feedback")
        feedback = CoachFeedback.query.filter_by(player_id=player.id).order_by(CoachFeedback.date.desc()).all()
        
        if feedback:
            for entry in feedback:
                with st.expander(f"{entry.date.strftime('%Y-%m-%d')} - {entry.coach_name}"):
                    st.write(entry.feedback_text)
                    
                    # Display ratings if available
                    ratings = {}
                    if entry.skating_rating:
                        ratings["Skating"] = entry.skating_rating
                    if entry.shooting_rating:
                        ratings["Shooting"] = entry.shooting_rating
                    if entry.teamwork_rating:
                        ratings["Teamwork"] = entry.teamwork_rating
                    
                    if ratings:
                        st.write("**Ratings:**")
                        for skill, rating in ratings.items():
                            st.write(f"{skill}: {rating}/5")
        else:
            st.info("No feedback records available.")

def display_team_details(team_id):
    """Display detailed information about a team"""
    team = Team.query.get(team_id)
    
    if not team:
        st.error(f"Team with ID {team_id} not found.")
        return
    
    # Basic info
    st.subheader(team.name)
    st.write(f"Age Group: {team.age_group}")
    st.write(f"Games: {team.games_played or 0} | Wins: {team.wins or 0} | Losses: {team.losses or 0}")
    
    # Players in the team
    st.write("### Players")
    players = team.players.all()
    
    if players:
        players_data = []
        for player in players:
            # Get membership info
            membership = TeamMembership.query.filter_by(
                player_id=player.id,
                team_id=team.id
            ).first()
            
            position = membership.position_in_team if membership else player.position
            active = "Yes" if (membership and membership.is_active) else "No"
            
            # Get coach name
            coach = User.query.filter_by(id=player.user_id).first()
            coach_name = coach.name if coach else "Unknown"
            
            players_data.append({
                "ID": player.id,
                "Name": player.name,
                "Age": player.age,
                "Position": position,
                "Active": active,
                "Coach": coach_name,
                "Games": player.games_played or 0,
                "Goals": player.goals or 0
            })
        
        st.dataframe(pd.DataFrame(players_data))
    else:
        st.info("No players in this team.")

def toggle_admin_status(user_id, make_admin):
    """Toggle admin status for a user"""
    user = User.query.get(user_id)
    if user:
        user.is_admin = make_admin
        db.session.commit()
        return True
    return False

def display_user_management():
    """Display user management interface"""
    st.write("### User Management")
    
    # Get all users
    users_df = get_user_list()
    
    # Display user list
    st.dataframe(users_df)
    
    # Form to change admin status
    with st.form("admin_status_form"):
        st.write("#### Change Admin Status")
        user_id = st.number_input("User ID", min_value=1)
        make_admin = st.checkbox("Make Admin")
        
        submitted = st.form_submit_button("Update")
        if submitted:
            success = toggle_admin_status(user_id, make_admin)
            if success:
                st.success(f"User {user_id} admin status updated to: {'Admin' if make_admin else 'Regular User'}")
                st.rerun()
            else:
                st.error(f"Failed to update user {user_id}")

def get_analytics_data():
    """Get website analytics data including user signups and traffic metrics"""
    from datetime import datetime, timedelta
    import pandas as pd
    import numpy as np
    import random  # For demo purposes only
    
    # Get current date and calculate time ranges
    now = datetime.now()
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)
    
    # Get user signup statistics from database
    users = User.query.all()
    
    # Calculate signup metrics
    total_users = len(users)
    users_last_month = sum(1 for user in users if user.created_at and user.created_at >= month_ago)
    users_last_week = sum(1 for user in users if user.created_at and user.created_at >= week_ago)
    
    # For demonstration purposes, generate traffic data
    # In a production environment, this would be replaced with actual analytics data
    days = [(now - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(30, 0, -1)]
    
    # Create a dataframe with traffic data (demo data)
    daily_visits = [int(np.clip(random.gauss(100, 30), 20, 200)) for _ in range(30)]
    daily_users = [int(daily * random.uniform(0.4, 0.7)) for daily in daily_visits]
    daily_signups = [int(daily * random.uniform(0.05, 0.15)) for daily in daily_users]
    
    traffic_df = pd.DataFrame({
        'Date': days,
        'Page Views': daily_visits,
        'Unique Visitors': daily_users,
        'New Signups': daily_signups
    })
    
    # Calculate totals for different time periods
    total_views = sum(daily_visits)
    month_views = sum(daily_visits[-30:])
    week_views = sum(daily_visits[-7:])
    
    return {
        'user_stats': {
            'total': total_users,
            'month': users_last_month,
            'week': users_last_week
        },
        'traffic_stats': {
            'total_views': total_views,
            'month_views': month_views,
            'week_views': week_views
        },
        'traffic_df': traffic_df
    }

def display_analytics_dashboard():
    """Display analytics dashboard with traffic and user statistics"""
    st.write("### Analytics Dashboard")
    
    # Get analytics data
    analytics = get_analytics_data()
    
    # Display key metrics in neat cards
    st.markdown("""
    <style>
    .metric-card {
        background-color: #f7f7f7;
        border-radius: 5px;
        padding: 15px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .metric-value {
        font-size: 24px;
        font-weight: bold;
        color: #2C3E50;
    }
    .metric-label {
        font-size: 14px;
        color: #7F8C8D;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # User Statistics Section
    st.write("#### User Statistics")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{analytics['user_stats']['total']}</div>
            <div class="metric-label">Total Users</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{analytics['user_stats']['month']}</div>
            <div class="metric-label">New Users (Last 30 Days)</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{analytics['user_stats']['week']}</div>
            <div class="metric-label">New Users (Last 7 Days)</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Traffic Statistics Section
    st.write("#### Website Traffic")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{analytics['traffic_stats']['total_views']}</div>
            <div class="metric-label">Total Page Views</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{analytics['traffic_stats']['month_views']}</div>
            <div class="metric-label">Page Views (Last 30 Days)</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{analytics['traffic_stats']['week_views']}</div>
            <div class="metric-label">Page Views (Last 7 Days)</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Traffic Chart
    st.write("#### Traffic Trends (Last 30 Days)")
    traffic_df = analytics['traffic_df']
    
    # Line chart for page views and unique visitors
    chart_data = traffic_df[['Date', 'Page Views', 'Unique Visitors']]
    chart_data = chart_data.melt('Date', var_name='Metric', value_name='Count')
    
    st.line_chart(traffic_df.set_index('Date')[['Page Views', 'Unique Visitors']])
    
    # Signups chart
    st.write("#### Signup Trends (Last 30 Days)")
    st.bar_chart(traffic_df.set_index('Date')['New Signups'])
    
    # Add note about demo data
    st.info("""
    Note: Currently showing simulated traffic data for demonstration purposes.
    In a production environment, this would be replaced with actual analytics data
    from services like Google Analytics or your server logs.
    """)

def display_admin_dashboard():
    """Main admin dashboard interface"""
    if 'user' not in st.session_state or not st.session_state.user.get('is_admin', False):
        st.warning("Admin access required. Please log in as an administrator.")
        return
    
    st.title("Admin Dashboard")
    st.write("Access and manage all players, teams, and users in the system.")
    
    # Create tabs for different sections
    tab1, tab2, tab3, tab4 = st.tabs(["Players", "Teams", "Users", "Analytics"])
    
    with tab1:
        st.write("### All Players")
        players_df = get_all_players()
        
        # Display the player list
        st.dataframe(players_df)
        
        # View player details
        player_id = st.number_input("Enter Player ID to view details", min_value=1)
        if st.button("View Player Details"):
            display_player_details(player_id)
    
    with tab2:
        st.write("### All Teams")
        teams_df = get_all_teams()
        
        # Display the team list
        st.dataframe(teams_df)
        
        # View team details
        team_id = st.number_input("Enter Team ID to view details", min_value=1)
        if st.button("View Team Details"):
            display_team_details(team_id)
    
    with tab3:
        display_user_management()
        
    with tab4:
        display_analytics_dashboard()