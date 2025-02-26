import streamlit as st
import pandas as pd
from database.models import db, Team, TeamMembership, Player
from datetime import datetime

def create_player_form():
    """Display form for creating a new player"""
    st.subheader("Create New Player")

    with st.form("create_player_form"):
        name = st.text_input("Player Name")
        age = st.number_input("Age", min_value=6, max_value=18, value=10)
        age_group = f"U{(age // 2) * 2}"
        position = st.selectbox("Position", ["Forward", "Defense", "Goalie"])

        submitted = st.form_submit_button("Create Player")

        if submitted and name:
            try:
                player = Player(
                    name=name,
                    age=age,
                    age_group=age_group,
                    position=position,
                    skating_speed=float(70),  # Default starting values
                    shooting_accuracy=float(70),
                    games_played=0,
                    goals=0,
                    assists=0,
                    join_date=datetime.utcnow()
                )
                db.session.add(player)
                db.session.commit()
                st.success(f"Player '{name}' created successfully!")
                return True
            except Exception as e:
                st.error(f"Error creating player: {str(e)}")
                return False
    return False

def create_team_form():
    """Display form for creating a new team"""
    st.subheader("Create New Team")

    with st.form("create_team_form"):
        team_name = st.text_input("Team Name")
        age_group = st.selectbox(
            "Age Group",
            options=['U8', 'U10', 'U12', 'U14', 'U16', 'U18']
        )

        submitted = st.form_submit_button("Create Team")

        if submitted and team_name:
            try:
                team = Team(
                    name=team_name,
                    age_group=age_group
                )
                db.session.add(team)
                db.session.commit()
                st.success(f"Team '{team_name}' created successfully!")
                return True
            except Exception as e:
                st.error(f"Error creating team: {str(e)}")
                return False
    return False

def assign_players_to_team(team_id):
    """Form for assigning players to a team"""
    team = Team.query.get(team_id)
    if not team:
        st.error("Team not found")
        return

    # Get available players in the same age group
    available_players = Player.query.filter_by(age_group=team.age_group).all()
    current_team_players = [p.id for p in team.players]

    # Filter out players already in the team
    available_players = [p for p in available_players if p.id not in current_team_players]

    if available_players:
        st.subheader(f"Add Players to {team.name}")

        selected_players = st.multiselect(
            "Select Players",
            options=[(p.id, p.name) for p in available_players],
            format_func=lambda x: x[1]
        )

        positions = {
            p_id: st.selectbox(
                f"Position for {next(p[1] for p in [(p.id, p.name) for p in available_players] if p[0] == p_id)}",
                options=['Forward', 'Defense', 'Goalie'],
                key=f"pos_{p_id}"
            ) for p_id, _ in selected_players
        }

        if st.button("Add Selected Players"):
            try:
                for player_id, _ in selected_players:
                    membership = TeamMembership(
                        player_id=player_id,
                        team_id=team.id,
                        position_in_team=positions[player_id]
                    )
                    db.session.add(membership)
                db.session.commit()
                st.success("Players added successfully!")
                return True
            except Exception as e:
                st.error(f"Error adding players: {str(e)}")
                return False
    else:
        st.info("No available players in this age group")
    return False

def display_team_list():
    """Display list of teams and their details"""
    teams = Team.query.all()

    if not teams:
        st.info("No teams created yet")
        return

    for team in teams:
        with st.expander(f"{team.name} - {team.age_group}"):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Games Played", team.games_played)
            with col2:
                st.metric("Wins", team.wins)
            with col3:
                st.metric("Losses", team.losses)

            # Display team roster
            st.subheader("Team Roster")
            if team.players:
                player_data = []
                for player in team.players:
                    membership = TeamMembership.query.filter_by(
                        team_id=team.id,
                        player_id=player.id,
                        is_active=True
                    ).first()

                    player_data.append({
                        'Name': player.name,
                        'Position': membership.position_in_team if membership else 'Unknown',
                        'Goals': player.goals,
                        'Assists': player.assists
                    })

                st.dataframe(pd.DataFrame(player_data))
            else:
                st.info("No players assigned to this team")

            # Add players button
            if st.button("Manage Players", key=f"manage_{team.id}"):
                assign_players_to_team(team.id)

def display_team_management():
    """Main team management interface"""
    st.title("Team Management")

    tab1, tab2, tab3 = st.tabs(["Team List", "Create Team", "Create Player"])

    with tab1:
        display_team_list()

    with tab2:
        create_team_form()

    with tab3:
        create_player_form()