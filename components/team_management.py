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
    try:
        # Get team information
        team = Team.query.get(team_id)
        if not team:
            st.error("Team not found")
            return

        print(f"Processing team {team_id}: {team.name}")  # Debug log

        # Get available players in the same age group
        players = Player.query.filter_by(age_group=team.age_group).all()

        # Get current team memberships
        memberships = TeamMembership.query.filter_by(
            team_id=team_id,
            is_active=True
        ).all()
        current_player_ids = [m.player_id for m in memberships]

        # Filter out players already in the team
        available_players = [p for p in players if p.id not in current_player_ids]

        print(f"Found {len(available_players)} available players")  # Debug log

        if available_players:
            st.subheader(f"Add Players to {team.name}")

            with st.form(key=f"add_players_form_{team_id}"):
                # Create options list for multiselect
                player_options = [(str(p.id), p.name) for p in available_players]

                # Display player selection
                selected_players = st.multiselect(
                    "Select Players",
                    options=player_options,
                    format_func=lambda x: x[1]
                )

                if selected_players:
                    st.subheader("Assign Positions")
                    positions = {}
                    for player_id_str, player_name in selected_players:
                        positions[player_id_str] = st.selectbox(
                            f"Position for {player_name}",
                            options=['Forward', 'Defense', 'Goalie'],
                            key=f"pos_{player_id_str}"
                        )

                submitted = st.form_submit_button("Add Selected Players")

                if submitted and selected_players:
                    try:
                        for player_id_str, player_name in selected_players:
                            player_id = int(player_id_str)
                            print(f"Processing player {player_id}: {player_name}")  # Debug log

                            # Check if membership already exists
                            existing = TeamMembership.query.filter_by(
                                player_id=player_id,
                                team_id=team.id,
                                is_active=True
                            ).first()

                            if not existing:
                                position = positions[player_id_str]
                                membership = TeamMembership(
                                    player_id=player_id,
                                    team_id=team.id,
                                    position_in_team=position,
                                    is_active=True,
                                    join_date=datetime.utcnow()
                                )
                                db.session.add(membership)
                                print(f"Added membership: Player {player_id} to Team {team.id} as {position}")  # Debug log

                        db.session.commit()
                        st.success(f"Players added successfully to {team.name}!")
                        st.experimental_rerun()
                        return True

                    except Exception as e:
                        print(f"Error adding players: {str(e)}")  # Debug log
                        st.error(f"Error adding players: {str(e)}")
                        db.session.rollback()
                        return False
        else:
            st.info("No available players in this age group")

    except Exception as e:
        print(f"Error in assign_players_to_team: {str(e)}")  # Debug log
        st.error(f"Error managing team players: {str(e)}")
        return False

def display_team_list():
    """Display list of teams and their details"""
    try:
        teams = Team.query.all()

        if not teams:
            st.info("No teams created yet")
            return

        for team in teams:
            with st.expander(f"{team.name} - {team.age_group}", expanded=True):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Games Played", team.games_played)
                with col2:
                    st.metric("Wins", team.wins)
                with col3:
                    st.metric("Losses", team.losses)

                # Display team roster
                st.subheader("Team Roster")

                try:
                    # Get active memberships for this team
                    memberships = TeamMembership.query.filter_by(
                        team_id=team.id,
                        is_active=True
                    ).all()

                    print(f"Team {team.id}: Found {len(memberships)} memberships")  # Debug log

                    if memberships:
                        # Create roster dataframe
                        roster_data = []
                        for membership in memberships:
                            player = Player.query.get(membership.player_id)
                            if player:
                                roster_data.append({
                                    'Name': player.name,
                                    'Position': membership.position_in_team,
                                    'Age Group': player.age_group,
                                    'Goals': player.goals,
                                    'Assists': player.assists
                                })
                                print(f"Added player {player.id}: {player.name} to roster")  # Debug log

                        if roster_data:
                            st.dataframe(pd.DataFrame(roster_data))
                        else:
                            st.info("No active players in roster")
                    else:
                        st.info("No players assigned to this team")

                except Exception as e:
                    print(f"Error displaying roster: {str(e)}")  # Debug log
                    st.error("Error displaying team roster")

                # Add players button
                manage_players = st.button("Manage Players", key=f"manage_{team.id}")
                if manage_players:
                    st.markdown("---")
                    assign_players_to_team(team.id)

    except Exception as e:
        print(f"Error displaying team list: {str(e)}")  # Debug log
        st.error(f"Error displaying teams: {str(e)}")

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