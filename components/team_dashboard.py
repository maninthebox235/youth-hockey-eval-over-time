import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from database.models import db, Team, Player, TeamMembership, CoachFeedback
import numpy as np
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from components.age_benchmarks import get_age_appropriate_benchmark
from utils.type_converter import to_int, to_float, to_str

def get_team_data(team_id):
    """Get comprehensive team data including player metrics"""
    try:
        # Get user ID from session
        user_id = st.session_state.user['id'] if 'user' in st.session_state else None

        team = Team.query.get(team_id)
        if not team:
            return None, pd.DataFrame()

        # Get active team members
        memberships = TeamMembership.query.filter_by(team_id=team_id, is_active=True).all()

        if not memberships:
            return team, pd.DataFrame()

        # Collect player data
        players_data = []
        player_ids = [m.player_id for m in memberships]

        # Filter players by user_id if available
        if user_id:
            players = Player.query.filter(Player.id.in_(player_ids), Player.user_id == user_id).all()
        else:
            players = Player.query.filter(Player.id.in_(player_ids)).all()

        for player in players:
            # Find matching membership
            membership = next((m for m in memberships if m.player_id == player.id), None)
            if not membership:
                continue

            # Collect all metrics that we can find for this player
            player_data = {
                'player_id': to_int(player.id),
                'name': player.name,
                'age': to_int(player.age),
                'position': player.position,
                'team_position': membership.position_in_team,
                'games_played': to_int(player.games_played) or 0
            }

            # Add all numeric attributes
            for attr in dir(player):
                if attr.startswith('_') or callable(getattr(player, attr)):
                    continue

                value = getattr(player, attr)
                if isinstance(value, (int, float, np.integer, np.floating)) and not isinstance(value, bool):
                    # Convert numpy types to Python native types
                    if hasattr(value, 'item'):
                        player_data[attr] = value.item()
                    else:
                        player_data[attr] = value

            players_data.append(player_data)

        return team, pd.DataFrame(players_data)

    except Exception as e:
        st.error(f"Error getting team data: {str(e)}")
        return None, pd.DataFrame()

def display_team_overview(team, players_df):
    """Display team overview with key metrics"""
    if team is None:
        st.error("Team not found")
        return

    st.title(f"{team.name} - {team.age_group}")

    # Team statistics row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Players", len(players_df))
    with col2:
        st.metric("Games Played", team.games_played or 0)
    with col3:
        st.metric("Wins", team.wins or 0)
    with col4:
        win_pct = round((team.wins / team.games_played) * 100, 1) if team.games_played else 0
        st.metric("Win %", f"{win_pct}%")

    # Player distribution by position
    if not players_df.empty:
        position_counts = players_df['team_position'].value_counts().reset_index()
        position_counts.columns = ['Position', 'Count']

        fig = px.pie(position_counts, values='Count', names='Position', 
                     title='Team Composition by Position')
        st.plotly_chart(fig, use_container_width=True, key="team_composition_pie")
        
        # Add Team Skills Distribution Heatmap
        st.subheader("Team Skills Distribution")
        heatmap = create_team_skill_heatmap(players_df)
        if heatmap:
            st.plotly_chart(heatmap, use_container_width=True, key="team_skills_heatmap_overview")
        else:
            st.info("Not enough skill data available to generate team skills heatmap.")

        # Add age distribution
        age_counts = players_df['age'].value_counts().reset_index()
        age_counts.columns = ['Age', 'Count']
        age_counts = age_counts.sort_values('Age')

        fig2 = px.bar(age_counts, x='Age', y='Count', 
                      title='Age Distribution',
                      labels={'Count': 'Number of Players', 'Age': 'Age (years)'})
        st.plotly_chart(fig2, use_container_width=True, key="age_distribution_bar")

def create_team_skill_heatmap(players_df):
    """Create a team skills heatmap to identify strengths and weaknesses"""
    if players_df.empty:
        return None

    # Define columns to exclude from skill metrics (including ID columns)
    excluded_columns = [
        'player_id', 'user_id', 'id', 'name', 'age', 'position', 'team_position', 
        'games_played', 'goals', 'assists', 'goals_against', 'saves',
        'join_date', 'created_at', 'last_login'
    ]
    
    # Get all skill columns (only numeric columns that aren't in excluded list)
    skill_cols = []
    for col in players_df.columns:
        if col not in excluded_columns:
            if players_df[col].dtype in [np.float64, np.int64, float, int] and not players_df[col].isnull().all():
                skill_cols.append(col)

    if not skill_cols:
        return None

    # Prepare data for heatmap
    skill_data = []

    for _, player in players_df.iterrows():
        player_skills = {'Player': to_str(player['name']), 'Position': to_str(player['team_position'])}

        for skill in skill_cols:
            if pd.notna(player[skill]):
                # Convert to a 1-5 scale if needed (ensuring native Python float)
                try:
                    val = to_float(player[skill])
                    if val is None:
                        continue
                        
                    if val > 5:  # Percentage values
                        val = val / 20  # Convert percentage to rough 0-5 scale
                    player_skills[skill.replace('_', ' ').title()] = val
                except (TypeError, ValueError):
                    # Skip skills with invalid values
                    continue

        skill_data.append(player_skills)

    skill_df = pd.DataFrame(skill_data)

    # If we have data, create a heatmap
    if not skill_df.empty and len(skill_df.columns) > 2:
        # Melt the dataframe for heatmap format
        skill_df_melted = pd.melt(
            skill_df, 
            id_vars=['Player', 'Position'], 
            var_name='Skill', 
            value_name='Rating'
        )

        # Create heatmap
        fig = px.density_heatmap(
            skill_df_melted,
            x='Skill',
            y='Player',
            z='Rating',
            color_continuous_scale='YlGnBu',
            title='Team Skills Distribution',
            labels={'Rating': 'Skill Rating (1-5)'}
        )

        # Customize layout
        fig.update_layout(
            height=400 + (len(skill_df) * 20),  # Adjust height based on player count
            xaxis={'categoryorder': 'total descending'},
            yaxis={'categoryorder': 'category ascending'}
        )

        return fig

    return None

def identify_team_strengths_weaknesses(players_df):
    """Identify team strengths and weaknesses based on player metrics"""
    if players_df.empty:
        return [], []

    # Define columns to exclude from skill metrics
    excluded_columns = [
        'player_id', 'user_id', 'id', 'name', 'age', 'position', 'team_position', 
        'games_played', 'goals', 'assists', 'goals_against', 'saves',
        'join_date', 'created_at', 'last_login'
    ]
    
    # Get all skill columns (only numeric columns that aren't in excluded list)
    skill_cols = []
    for col in players_df.columns:
        if col not in excluded_columns:
            if players_df[col].dtype in [np.float64, np.int64, float, int] and not players_df[col].isnull().all():
                skill_cols.append(col)

    if not skill_cols:
        return [], []

    # Calculate average for each skill
    skill_averages = {}
    for skill in skill_cols:
        valid_values = players_df[skill].dropna()
        if not valid_values.empty:
            # Convert to Python float to ensure we don't have numpy types
            avg_value = float(valid_values.mean())
            skill_averages[skill] = avg_value

    # Sort skills by average
    sorted_skills = sorted(skill_averages.items(), key=lambda x: x[1], reverse=True)

    # Identify top 3 strengths and weaknesses if we have enough skills
    top_count = min(3, len(sorted_skills))
    strengths = sorted_skills[:top_count] 
    weaknesses = sorted_skills[-top_count:] if len(sorted_skills) >= top_count else []

    return strengths, weaknesses

def display_team_analysis(team, players_df):
    """Display detailed team analysis with visualizations"""
    if team is None or players_df.empty:
        st.info("No data available for team analysis")
        return

    st.subheader("Team Analysis")

    # Team Strengths and Weaknesses
    strengths, weaknesses = identify_team_strengths_weaknesses(players_df)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Team Strengths")
        for skill, avg in strengths:
            formatted_skill = skill.replace('_', ' ').title()
            st.metric(formatted_skill, f"{avg:.1f}")

    with col2:
        st.markdown("### Areas for Improvement")
        for skill, avg in weaknesses:
            formatted_skill = skill.replace('_', ' ').title()
            st.metric(formatted_skill, f"{avg:.1f}")

    # Add a note about skills distribution now being in the Overview tab
    st.info("Team Skills Distribution visualization is now available in the Team Overview tab.")

    # Performance by position
    if 'goals' in players_df.columns and not players_df['goals'].isnull().all():
        # Filter for forwards and defense
        skaters_df = players_df[players_df['position'].isin(['Forward', 'Defense'])].copy()

        if not skaters_df.empty:
            # Offensive productivity
            skaters_df.loc[:, 'points'] = skaters_df['goals'].fillna(0) + skaters_df['assists'].fillna(0)
            skaters_df.loc[:, 'games_played'] = skaters_df['games_played'].fillna(0)
            skaters_df.loc[:, 'points_per_game'] = skaters_df.apply(
                lambda x: x['points'] / x['games_played'] if x['games_played'] > 0 else 0, 
                axis=1
            )

            # Create performance comparison
            fig = px.scatter(
                skaters_df,
                x='points',
                y='points_per_game',
                color='position',
                size='games_played',
                hover_name='name',
                title='Player Offensive Production',
                labels={
                    'points': 'Total Points (Goals + Assists)',
                    'points_per_game': 'Points per Game',
                    'position': 'Position'
                }
            )
            st.plotly_chart(fig, use_container_width=True, key="offensive_production_scatter")

    # Goalie performance if we have goalies
    goalies_df = players_df[players_df['position'] == 'Goalie']
    if not goalies_df.empty and 'save_percentage' in goalies_df.columns:
        st.subheader("Goaltending")

        for _, goalie in goalies_df.iterrows():
            save_pct = goalie.get('save_percentage', 0)
            if isinstance(save_pct, str):
                try:
                    save_pct = float(save_pct.strip('%'))
                except:
                    save_pct = 0

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Goalie", goalie['name'])
            with col2:
                st.metric("Save %", f"{save_pct:.1f}%")
            with col3:
                saves = goalie.get('saves', 0) or 0
                goals_against = goalie.get('goals_against', 0) or 0
                games = goalie.get('games_played', 0) or 0
                gaa = goals_against / games if games > 0 else 0
                st.metric("GAA", f"{gaa:.2f}")

def display_player_comparison_tool(players_df):
    """Tool to compare selected players side by side"""
    if players_df.empty:
        st.info("No players available for comparison")
        return

    st.subheader("Player Comparison Tool")

    # Select 2-3 players to compare
    selected_players = st.multiselect(
        "Select Players to Compare (2-3 players recommended)",
        options=players_df['name'].tolist(),
        default=players_df['name'].tolist()[:2] if len(players_df) >= 2 else None
    )

    if not selected_players or len(selected_players) < 2:
        st.info("Please select at least 2 players to compare")
        return

    # Filter dataframe to selected players
    compare_df = players_df[players_df['name'].isin(selected_players)]

    # Get common skill metrics
    excluded_columns = [
        'player_id', 'user_id', 'id', 'name', 'age', 'position', 'team_position', 
        'games_played', 'goals', 'assists', 'goals_against', 'saves',
        'join_date', 'created_at', 'last_login'
    ]
    skill_metrics = [col for col in compare_df.columns 
                    if col not in excluded_columns
                    and compare_df[col].dtype in [np.float64, np.int64, float, int]
                    and not compare_df[col].isnull().all()]

    if not skill_metrics:
        st.warning("No comparable metrics found for these players")
        return

    # Create a radar chart for skill comparison
    fig = go.Figure()

    for _, player in compare_df.iterrows():
        player_skills = []
        for metric in skill_metrics:
            if pd.notna(player[metric]):
                # Safely convert to Python float (handles numpy types)
                try:
                    val = to_float(player[metric])
                    if val is None:
                        player_skills.append(0)
                        continue
                        
                    if val > 5:  # Percentage values
                        val = val / 20  # Convert to 0-5 scale
                    player_skills.append(val)
                except (TypeError, ValueError):
                    player_skills.append(0)
            else:
                player_skills.append(0)

        fig.add_trace(go.Scatterpolar(
            r=player_skills,
            theta=[m.replace('_', ' ').title() for m in skill_metrics],
            fill='toself',
            name=to_str(player['name'])
        ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 5]
            )
        ),
        title="Player Skills Comparison",
        showlegend=True
    )

    st.plotly_chart(fig, use_container_width=True, key="player_skills_radar")

    # Show side-by-side metric comparison
    st.subheader("Detailed Comparison")

    # Create a comparison table
    comparison_data = []

    for metric in ['age', 'position', 'games_played'] + skill_metrics:
        row = {'Metric': metric.replace('_', ' ').title()}

        for _, player in compare_df.iterrows():
            player_name = to_str(player['name'])
            value = player.get(metric, 'N/A')

            if pd.notna(value):
                if isinstance(value, (int, float, np.integer, np.floating)):
                    # Handle numpy numeric types
                    if hasattr(value, 'item'):
                        value = value.item()
                    
                    # Format the value
                    if isinstance(value, float):
                        row[player_name] = f"{value:.1f}" 
                    else:
                        row[player_name] = str(value)
                else:
                    row[player_name] = to_str(value)
            else:
                row[player_name] = 'N/A'

        comparison_data.append(row)

    # Display the comparison table
    comparison_df = pd.DataFrame(comparison_data)
    st.dataframe(comparison_df, use_container_width=True)

def display_tryout_evaluation_mode(team_id):
    """Streamlined assessment mode for player tryouts"""
    st.subheader("Tryout Evaluation Mode")

    # Get team data for context
    team = Team.query.get(team_id)
    if not team:
        st.error("Team not found")
        return

    # Get current user info from session
    user_id = st.session_state.user['id'] if 'user' in st.session_state else 1  # Default to 1 if not logged in
    user_name = st.session_state.user['name'] if 'user' in st.session_state else "Coach"

    st.write(f"Evaluating players for: **{team.name} ({team.age_group})**")

    # Create tab for new evaluation vs. reviewing evaluations
    eval_tabs = st.tabs(["New Evaluation", "Review Evaluations"])

    with eval_tabs[0]:
        with st.form("tryout_evaluation_form"):
            # Player information
            st.subheader("Player Information")
            
            # Get players on this team for the dropdown
            team_players = []
            try:
                # Get players from memberships
                memberships = TeamMembership.query.filter_by(team_id=team.id).all()
                if memberships:
                    player_ids = [m.player_id for m in memberships]
                    players = Player.query.filter(Player.id.in_(player_ids)).all()
                    team_players = [(p.id, f"{p.name} - {p.position}") for p in players]
                
                # Add option to add a new player
                team_players.append((-1, "-- Add New Player --"))
                
                # Create a unique key for this form
                form_key = f"tryout_form_{team.id}"
                
                # Simpler, direct player selection approach
                player_option = st.selectbox(
                    "Select Player", 
                    options=range(len(team_players)),
                    format_func=lambda i: team_players[i][1],
                    key=f"{form_key}_player_select"
                )
                
                # Get the selected player ID
                selected_player_id = team_players[player_option][0]
                
                # For existing player, fetch fresh data directly from database
                if selected_player_id > 0:
                    # This is an existing player - get fresh data from database
                    selected_player = Player.query.get(selected_player_id)
                    if selected_player:
                        # Display player info from database
                        st.write(f"**Name:** {selected_player.name}")
                        st.write(f"**Age:** {selected_player.age}")
                        st.write(f"**Position:** {selected_player.position}")
                        
                        # Store player info for form submission
                        player_name = selected_player.name
                        player_age = selected_player.age
                        player_position = selected_player.position
                        
                        # Set the display position directly based on database info
                        display_position = selected_player.position
                    else:
                        st.error("Player not found in database")
                        player_name = ""
                        player_age = int(team.age_group.replace('U', ''))
                        player_position = "Forward"
                        display_position = "Forward"
                else:
                    # This is a new player
                    st.write("**Adding a new player**")
                    player_name = st.text_input("Player Name", key="tryout_player_name")
                    player_age = st.number_input("Age", min_value=6, max_value=18, 
                                                value=int(team.age_group.replace('U', '')), 
                                                key="tryout_player_age")
                    player_position = st.selectbox("Position", ["Forward", "Defense", "Goalie"], 
                                                  key="tryout_player_position")
                    display_position = player_position
            except Exception as e:
                st.error(f"Error loading team players: {str(e)}")
                player_name = st.text_input("Player Name", key="tryout_player_name")
                player_age = st.number_input("Age", min_value=6, max_value=18, value=int(team.age_group.replace('U', '')), key="tryout_player_age")
                player_position = st.selectbox("Position", ["Forward", "Defense", "Goalie"], key="tryout_player_position")
                selected_player_id = None
                display_position = player_position  # Set display position directly based on selected position

            # Evaluation scale explanation
            st.write("### Evaluation Scale")
            st.write("1 = Significantly below expectations")
            st.write("3 = Meeting expectations")
            st.write("5 = Significantly exceeding expectations")

            # Create skill evaluation sliders based on position
            st.subheader("Skills Assessment")
            
            # display_position is already set when we fetch player data above
            # No additional position handling needed here
            
            if display_position == "Goalie":
                # Goalie skills
                col1, col2 = st.columns(2)
                with col1:
                    positioning = st.slider("Positioning", 1, 5, 3)
                    rebound_control = st.slider("Rebound Control", 1, 5, 3)
                    recovery = st.slider("Recovery", 1, 5, 3)
                with col2:
                    save_technique = st.slider("Save Technique", 1, 5, 3)
                    puck_handling = st.slider("Puck Handling", 1, 5, 3)
                    communication = st.slider("Communication", 1, 5, 3)

                skill_ratings = {
                    'positioning': positioning,
                    'rebound_control': rebound_control,
                    'recovery': recovery,
                    'save_technique': save_technique,
                    'puck_handling': puck_handling,
                    'communication_rating': communication
                }
            else:
                # Skater skills (common for Forward and Defense)
                col1, col2 = st.columns(2)
                with col1:
                    skating = st.slider("Skating", 1, 5, 3)
                    puck_control = st.slider("Puck Control", 1, 5, 3)
                    passing = st.slider("Passing", 1, 5, 3)
                with col2:
                    shooting = st.slider("Shooting", 1, 5, 3)
                    hockey_sense = st.slider("Hockey Sense", 1, 5, 3)
                    compete_level = st.slider("Compete Level", 1, 5, 3)

                # Add position-specific skills
                if display_position == "Defense":
                    defensive_ability = st.slider("Defensive Ability", 1, 5, 3)
                    gap_control = st.slider("Gap Control", 1, 5, 3)

                    skill_ratings = {
                        'skating_speed': skating,
                        'puck_control': puck_control,
                        'passing_accuracy': passing,
                        'shooting_accuracy': shooting,
                        'hockey_sense': hockey_sense,
                        'compete_level_rating': compete_level,
                        'defensive_ability_rating': defensive_ability,
                        'gap_control': gap_control
                    }
                else:  # Forward
                    offensive_ability = st.slider("Offensive Ability", 1, 5, 3)
                    net_front = st.slider("Net Front Presence", 1, 5, 3)

                    skill_ratings = {
                        'skating_speed': skating,
                        'puck_control': puck_control,
                        'passing_accuracy': passing,
                        'shooting_accuracy': shooting,
                        'hockey_sense': hockey_sense,
                        'compete_level_rating': compete_level,
                        'offensive_ability_rating': offensive_ability,
                        'net_front_rating': net_front
                    }

            # Comments and recommendation
            st.subheader("Evaluation Notes")
            strengths = st.text_area("Strengths", key="tryout_strengths")
            weaknesses = st.text_area("Areas for Improvement", key="tryout_weaknesses")

            recommendation = st.radio(
                "Recommendation",
                ["Highly Recommend", "Recommend", "Neutral", "Do Not Recommend"]
            )

            # Pre-fill with current user's name if available
            evaluator_name = st.text_input("Evaluator Name", value=user_name)

            submitted = st.form_submit_button("Save Evaluation")

            if submitted:
                # Use session state values if available (for selected player), otherwise use form values
                eval_player_name = st.session_state.get('current_player_name', player_name)
                eval_player_age = st.session_state.get('current_player_age', player_age)
                eval_player_position = st.session_state.get('current_player_position', player_position)
                
                if not eval_player_name or not evaluator_name:
                    st.error("Player name and evaluator name are required")
                else:
                    # Combine comments
                    comments = f"""
                    **Strengths:**
                    {strengths}

                    **Areas for Improvement:**
                    {weaknesses}

                    **Recommendation:** {recommendation}
                    """

                    # For an existing player, use the player_id directly
                    player = None
                    if selected_player_id and selected_player_id > 0:
                        player = Player.query.get(selected_player_id)
                    else:
                        # Check if player exists, otherwise create new player
                        player = Player.query.filter_by(name=eval_player_name, age_group=team.age_group).first()

                    if not player:
                        # Create new player
                        try:
                            player = Player(
                                name=eval_player_name,
                                age=eval_player_age,
                                age_group=team.age_group,
                                position=eval_player_position,
                                join_date=datetime.utcnow()
                            )

                            # Add skill ratings to player
                            for skill, rating in skill_ratings.items():
                                if hasattr(player, skill):
                                    setattr(player, skill, rating)

                            db.session.add(player)
                            db.session.flush()  # Get ID without committing

                        except Exception as e:
                            st.error(f"Error creating player: {str(e)}")
                            return

                    # Create feedback entry for the tryout
                    try:
                        # Use the current user ID from session if available, otherwise default to 1
                        feedback = CoachFeedback(
                            player_id=player.id,
                            coach_id=user_id,  # Use the user_id from session
                            coach_name=evaluator_name or user_name,  # Use name provided or session username
                            feedback_text=comments
                        )

                        # Add ratings to feedback
                        for skill, rating in skill_ratings.items():
                            rating_field = f"{skill}_rating" if not skill.endswith('_rating') else skill
                            if hasattr(feedback, rating_field):
                                setattr(feedback, rating_field, rating)

                        db.session.add(feedback)
                        db.session.commit()

                        st.success(f"Evaluation for {eval_player_name} saved successfully!")
                        
                        # Add redirect to team overview
                        st.session_state.show_tryout_mode = False  # Turn off tryout mode
                        st.session_state.redirect_to_overview = True  # Signal to redirect
                        st.rerun()  # Rerun to apply the state change
                    except Exception as e:
                        db.session.rollback()
                        st.error(f"Error saving evaluation: {str(e)}")

    with eval_tabs[1]:
        st.subheader("Tryout Evaluations")

        # Get recent evaluations for this team age group
        try:
            # Get players in this age group
            players = Player.query.filter_by(age_group=team.age_group).all()
            player_ids = [p.id for p in players]

            if player_ids:
                # Get recent feedback for these players
                feedback = CoachFeedback.query.filter(
                    CoachFeedback.player_id.in_(player_ids),
                    CoachFeedback.date >= (datetime.utcnow() - timedelta(days=14))
                ).order_by(CoachFeedback.date.desc()).all()

                if feedback:
                    for fb in feedback:
                        player = Player.query.get(fb.player_id)
                        if not player:
                            continue

                        with st.expander(f"{player.name} - {player.position} (Evaluated by {fb.coach_name})"):
                            st.write(f"**Date:** {fb.date.strftime('%Y-%m-%d %H:%M')}")
                            st.write(fb.feedback_text)

                            # Collect all ratings
                            ratings = {}
                            for col in CoachFeedback.__table__.columns:
                                if col.name.endswith('_rating'):
                                    val = getattr(fb, col.name)
                                    if val is not None:
                                        try:
                                            ratings[col.name] = int(float(val))
                                        except:
                                            pass

                            # Show all evaluated skills in a more organized way
                            if ratings:
                                st.markdown("### Evaluated Skills")
                                
                                # Group skills by category
                                goalie_skills = {}
                                skating_skills = {}
                                technical_skills = {}
                                hockey_iq_skills = {}
                                other_skills = {}
                                
                                for metric, value in ratings.items():
                                    metric_name = metric.replace('_rating', '').replace('_', ' ').title()
                                    
                                    # Categorize skills
                                    if metric in ['save_technique_rating', 'positioning_rating', 'rebound_control_rating', 
                                                 'recovery_rating', 'puck_handling_rating']:
                                        goalie_skills[metric_name] = value
                                    elif metric in ['skating_speed_rating', 'backward_skating_rating', 'agility_rating', 
                                                   'edge_control_rating']:
                                        skating_skills[metric_name] = value
                                    elif metric in ['puck_control_rating', 'passing_accuracy_rating', 'shooting_accuracy_rating',
                                                   'receiving_rating', 'stick_protection_rating']:
                                        technical_skills[metric_name] = value
                                    elif metric in ['hockey_sense_rating', 'decision_making_rating', 'game_awareness_rating']:
                                        hockey_iq_skills[metric_name] = value
                                    else:
                                        other_skills[metric_name] = value
                                
                                # Function to display skill category
                                def display_skill_section(title, skills_dict):
                                    if skills_dict:
                                        st.markdown(f"#### {title}")
                                        cols = st.columns(3)
                                        for i, (name, val) in enumerate(skills_dict.items()):
                                            with cols[i % 3]:
                                                st.metric(name, val, help="Rating scale: 1-5")
                                
                                # Display skill sections
                                if goalie_skills:
                                    display_skill_section("Goaltending Skills", goalie_skills)
                                if skating_skills:
                                    display_skill_section("Skating Skills", skating_skills)
                                if technical_skills:
                                    display_skill_section("Technical Skills", technical_skills) 
                                if hockey_iq_skills:
                                    display_skill_section("Hockey IQ Skills", hockey_iq_skills)
                                if other_skills:
                                    display_skill_section("Other Skills", other_skills)
                                
                                # Alternative view: show all skills in a unified visualization
                                if len(ratings) > 3:  # Only show chart if we have multiple ratings
                                    st.markdown("#### Skills Radar Chart")
                                    
                                    # Prepare data for radar chart
                                    categories = [k.replace('_rating', '').replace('_', ' ').title() for k in ratings.keys()]
                                    values = list(ratings.values())
                                    
                                    # Create radar chart
                                    fig = go.Figure()
                                    
                                    fig.add_trace(go.Scatterpolar(
                                        r=values,
                                        theta=categories,
                                        fill='toself',
                                        name='Skills Rating'
                                    ))
                                    
                                    fig.update_layout(
                                        polar=dict(
                                            radialaxis=dict(
                                                visible=True,
                                                range=[0, 5]
                                            )
                                        ),
                                        showlegend=False
                                    )
                                    
                                    st.plotly_chart(fig, use_container_width=True)
                            else:
                                st.info("No skill ratings were recorded for this evaluation.")
                else:
                    st.info("No recent evaluations found for this team age group")
            else:
                st.info("No players found in this age group")

        except Exception as e:
            st.error(f"Error loading evaluations: {str(e)}")

def create_custom_report(team, players_df):
    """Generate a detailed team performance report"""
    st.subheader("Custom Team Report")

    if team is None or players_df.empty:
        st.info("No data available for team reporting")
        return

    # Report customization options
    report_options = st.multiselect(
        "Select Report Sections",
        options=["Team Overview", "Player Performance", "Skill Assessment", "Development Tracking", "Coach Feedback"],
        default=["Team Overview", "Player Performance", "Skill Assessment"]
    )

    if not report_options:
        st.info("Please select at least one report section")
        return

    # Report period
    period = st.radio(
        "Report Period",
        options=["Current Status", "Season to Date", "Monthly Progress"],
        horizontal=True
    )

    # Report header
    st.markdown(f"""
    ## {team.name} - {team.age_group} Performance Report
    **Period:** {period}  
    **Generated:** {datetime.now().strftime('%Y-%m-%d')}
    """)

    # Report sections
    if "Team Overview" in report_options:
        st.markdown("### Team Overview")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Roster Size", len(players_df))
        with col2:
            st.metric("Games Played", team.games_played or 0)
        with col3:
            st.metric("Wins", team.wins or 0)
        with col4:
            win_pct = round((team.wins / team.games_played) * 100, 1) if team.games_played else 0
            st.metric("Win %", f"{win_pct}%")

        # Team composition
        position_counts = players_df['team_position'].value_counts().reset_index()
        position_counts.columns = ['Position', 'Count']

        fig = px.pie(position_counts, values='Count', names='Position', 
                    title='Team Composition by Position')
        st.plotly_chart(fig, use_container_width=True, key="report_team_composition_pie")

    if "Player Performance" in report_options:
        st.markdown("### Player Performance")

        # Filter skaters and goalies
        skaters_df = players_df[players_df['position'].isin(['Forward', 'Defense'])]
        goalies_df = players_df[players_df['position'] == 'Goalie']

        # Skater performance table
        if not skaters_df.empty:
            st.markdown("#### Skater Performance")

            # Create performance table
            skater_stats = []
            for _, player in skaters_df.iterrows():
                stats = {
                    'Name': player['name'],
                    'Position': player['team_position'],
                    'Games': player.get('games_played', 0) or 0,
                    'Goals': player.get('goals', 0) or 0,
                    'Assists': player.get('assists', 0) or 0,
                    'Points': (player.get('goals', 0) or 0) + (player.get('assists', 0) or 0)
                }

                # Add key skill metrics
                for skill in ['skating_speed', 'shooting_accuracy', 'puck_control']:
                    if skill in player and pd.notna(player[skill]):
                        stats[skill.replace('_', ' ').title()] = f"{float(player[skill]):.1f}"

                skater_stats.append(stats)

            # Sort by points
            skater_stats_df = pd.DataFrame(skater_stats).sort_values('Points', ascending=False)
            st.dataframe(skater_stats_df, use_container_width=True)

        # Goalie performance table
        if not goalies_df.empty:
            st.markdown("#### Goalie Performance")

            goalie_stats = []
            for _, goalie in goalies_df.iterrows():
                games = goalie.get('games_played', 0) or 0
                saves = goalie.get('saves', 0) or 0
                goals_against = goalie.get('goals_against', 0) or 0

                save_pct = (saves / (saves + goals_against)) * 100 if (saves + goals_against) > 0 else 0
                gaa = goals_against / games if games > 0 else 0

                stats = {
                    'Name': goalie['name'],
                    'Games': games,
                    'Save %': f"{save_pct:.1f}%",
                    'GAA': f"{gaa:.2f}",
                    'Saves': saves,
                    'Goals Against': goals_against
                }

                goalie_stats.append(stats)

            goalie_stats_df = pd.DataFrame(goalie_stats)
            st.dataframe(goalie_stats_df, use_container_width=True)

    if "Skill Assessment" in report_options:
        st.markdown("### Team Skill Assessment")

        # Team Skills Heatmap
        heatmap = create_team_skill_heatmap(players_df)
        if heatmap:
            st.plotly_chart(heatmap, use_container_width=True, key="report_skills_heatmap")

        # Team strengths and weaknesses
        strengths, weaknesses = identify_team_strengths_weaknesses(players_df)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Team Strengths")
            for skill, avg in strengths:
                formatted_skill = skill.replace('_', ' ').title()
                st.metric(formatted_skill, f"{avg:.1f}")

        with col2:
            st.markdown("#### Areas for Improvement")
            for skill, avg in weaknesses:
                formatted_skill = skill.replace('_', ' ').title()
                st.metric(formatted_skill, f"{avg:.1f}")

    # Export options
    st.markdown("### Export Options")
    export_format = st.radio("Export Format", ["PDF", "CSV"], horizontal=True)

    if st.button("Generate Report"):
        st.success(f"Report generated in {export_format} format! (Mock functionality)")
        # In a real implementation, we would generate and provide download link

def display_team_dashboard(team_id=None):
    """Main team dashboard interface"""
    st.title("Team Dashboard")
    st.write("Comprehensive team management and analysis tools")

    # Get user ID from session
    user_id = st.session_state.user['id'] if 'user' in st.session_state else None

    # Get list of teams with players added by current user
    if user_id:
        # First get players associated with the current user
        user_players = Player.query.filter_by(user_id=user_id).all()
        player_ids = [p.id for p in user_players]

        # Get team memberships for these players
        team_ids = []
        if player_ids:
            memberships = TeamMembership.query.filter(TeamMembership.player_id.in_(player_ids)).all()
            team_ids = [m.team_id for m in memberships]

        # Get teams that these players are part of
        if team_ids:
            teams = Team.query.filter(Team.id.in_(team_ids)).all()
        else:
            teams = []
    else:
        # If no user ID, show all teams (fallback for testing)
        teams = Team.query.all()

    if not teams:
        st.info("No teams available. Please create a team first.")
        return

    # If no team ID provided, ask user to select one
    if team_id is None:
        team_options = [(t.id, f"{t.name} ({t.age_group})") for t in teams]
        selected = st.selectbox(
            "Select Team",
            options=range(len(team_options)),
            format_func=lambda i: team_options[i][1]
        )
        team_id = team_options[selected][0]

    # Get team data
    team, players_df = get_team_data(team_id)

    if team is None:
        st.error("Failed to load team data")
        return

    # Create tabs for different dashboard views
    dashboard_tabs = st.tabs([
        "Team Overview", 
        "Team Analysis", 
        "Player Comparison", 
        "Tryout Evaluation", 
        "Custom Reports"
    ])
    
    # Initialize tab index in session state if not already set
    if 'active_tab' not in st.session_state:
        st.session_state.active_tab = 0
    
    # Check if we should redirect from tryout mode to overview
    if 'redirect_to_overview' in st.session_state and st.session_state.redirect_to_overview:
        st.session_state.active_tab = 0  # Set to team overview tab
        st.session_state.redirect_to_overview = False  # Reset the flag
        
    # Set the active tab index (Streamlit will show this tab first)
    st.session_state.active_tab_index = st.session_state.active_tab
    
    with dashboard_tabs[0]:
        display_team_overview(team, players_df)

    with dashboard_tabs[1]:
        display_team_analysis(team, players_df)

    with dashboard_tabs[2]:
        display_player_comparison_tool(players_df)

    with dashboard_tabs[3]:
        display_tryout_evaluation_mode(team_id)

    with dashboard_tabs[4]:
        create_custom_report(team, players_df)