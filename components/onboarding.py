import streamlit as st
import pandas as pd
import io
import base64
from database.models import Player, Team, TeamMembership, db
from datetime import datetime
import uuid

def display_welcome_message(user_name):
    """Display a welcome message for new users"""
    st.title(f"Welcome to IceTracker, {user_name}! 🏒")
    st.markdown("""
    Let's get you started with your hockey player development journey. Here's what you can do:
    
    - Add your players individually or upload a roster
    - Create teams and assign players
    - Begin tracking player development with assessments
    
    Follow the steps below to set up your account.
    """)

def get_download_link(df, filename, text):
    """Generate a download link for a DataFrame"""
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">📥 {text}</a>'
    return href

def create_roster_template():
    """Create a template for roster upload"""
    columns = [
        "name", "age", "age_group", "position", 
        "jersey_number", "team_name", "height", "weight"
    ]
    
    # Create example data
    data = [
        ["John Smith", 10, "U10", "Forward", 15, "Junior Bears", 140, 85],
        ["Emma Johnson", 12, "U12", "Defense", 22, "Junior Bears", 150, 95],
        ["Michael Brown", 14, "U14", "Goalie", 30, "Junior Bears", 160, 110]
    ]
    
    df = pd.DataFrame(data, columns=columns)
    return df

def validate_roster_data(df):
    """Validate uploaded roster data"""
    required_columns = ["name", "age", "age_group", "position"]
    errors = []
    
    # Check for required columns
    for col in required_columns:
        if col not in df.columns:
            errors.append(f"Missing required column: {col}")
    
    if errors:
        return False, errors
    
    # Validate data types and ranges
    if not errors and len(df) > 0:
        if not all(isinstance(age, (int, float)) for age in df['age'] if pd.notna(age)):
            errors.append("Age must be a number")
        
        valid_positions = ["Forward", "Defense", "Goalie"]
        invalid_pos = [pos for pos in df['position'] if pos not in valid_positions and pd.notna(pos)]
        if invalid_pos:
            errors.append(f"Invalid positions found: {', '.join(invalid_pos)}. Must be one of {', '.join(valid_positions)}")
        
        if 'jersey_number' in df.columns:
            if not all(isinstance(num, (int, float)) or pd.isna(num) for num in df['jersey_number']):
                errors.append("Jersey numbers must be numeric")
    
    return len(errors) == 0, errors

def process_roster_upload(df, user_id):
    """Process uploaded roster and add to database"""
    try:
        # Group by team if available
        if 'team_name' in df.columns and not all(pd.isna(df['team_name'])):
            team_groups = df.groupby('team_name', dropna=True)
            
            for team_name, players in team_groups:
                # Create the team if it doesn't exist
                if not Team.query.filter_by(name=team_name).first():
                    age_group = players['age_group'].iloc[0] if 'age_group' in players.columns else "Unknown"
                    new_team = Team(
                        name=team_name,
                        age_group=age_group,
                        created_date=datetime.utcnow()
                    )
                    db.session.add(new_team)
                    db.session.commit()
                    team = new_team
                else:
                    team = Team.query.filter_by(name=team_name).first()
                
                # Add each player
                for _, player_data in players.iterrows():
                    add_player_from_data(player_data, team.id, user_id)
        
        # Process players without teams
        no_team = df[df['team_name'].isna()] if 'team_name' in df.columns else df
        for _, player_data in no_team.iterrows():
            add_player_from_data(player_data, None, user_id)
            
        db.session.commit()
        return True, f"Successfully added {len(df)} players"
    except Exception as e:
        db.session.rollback()
        return False, f"Error adding players: {str(e)}"

def add_player_from_data(player_data, team_id=None, user_id=None):
    """Add a single player from data row"""
    new_player = Player(
        name=player_data['name'],
        age=int(player_data['age']),
        age_group=player_data['age_group'] if 'age_group' in player_data else get_age_group(int(player_data['age'])),
        position=player_data['position'],
        join_date=datetime.utcnow(),
        user_id=user_id  # Associate player with the user
    )
    
    # Add optional fields if available
    if 'jersey_number' in player_data and not pd.isna(player_data['jersey_number']):
        new_player.jersey_number = int(player_data['jersey_number'])
    
    if 'height' in player_data and not pd.isna(player_data['height']):
        new_player.height = float(player_data['height'])
    
    if 'weight' in player_data and not pd.isna(player_data['weight']):
        new_player.weight = float(player_data['weight'])
    
    db.session.add(new_player)
    db.session.flush()  # Get the ID without committing
    
    # Add to team if team_id is provided
    if team_id:
        team_membership = TeamMembership(
            player_id=new_player.id,
            team_id=team_id,
            join_date=datetime.utcnow(),
            position_in_team=player_data['position'],
            is_active=True
        )
        db.session.add(team_membership)

def get_age_group(age):
    """Get age group based on age"""
    if age <= 8:
        return "U8"
    elif age <= 10:
        return "U10"
    elif age <= 12:
        return "U12"
    elif age <= 14:
        return "U14"
    elif age <= 16:
        return "U16"
    else:
        return "U18"

def display_manual_add_form():
    """Display form for manually adding a player"""
    st.subheader("Add a Player")
    
    with st.form("add_player_form"):
        name = st.text_input("Player Name")
        col1, col2 = st.columns(2)
        
        with col1:
            age = st.number_input("Age", min_value=5, max_value=18, value=10)
            position = st.selectbox("Position", ["Forward", "Defense", "Goalie"])
        
        with col2:
            jersey_number = st.number_input("Jersey Number", min_value=0, max_value=99, value=0)
            # Get user ID from session for team filtering
            user_id = st.session_state.user['id'] if 'user' in st.session_state else None
            
            # Get teams that current user has access to
            if user_id:
                # Get the player IDs for this user
                user_players = Player.query.filter_by(user_id=user_id).all()
                player_ids = [p.id for p in user_players]
                
                # Get team memberships for these players
                team_ids = []
                if player_ids:
                    memberships = TeamMembership.query.filter(TeamMembership.player_id.in_(player_ids)).all()
                    team_ids = [m.team_id for m in memberships]
                
                # Get teams that contain these players
                if team_ids:
                    teams = Team.query.filter(Team.id.in_(team_ids)).all()
                else:
                    teams = []
            else:
                # If no user ID, show all teams (fallback for testing)
                teams = Team.query.all()
                
            team_id = st.selectbox(
                "Team",
                options=["No Team"] + [(t.id, t.name) for t in teams],
                format_func=lambda x: x[1] if isinstance(x, tuple) else x
            )
        
        submitted = st.form_submit_button("Add Player")
        
        if submitted and name:
            try:
                # Get user ID from session
                user_id = st.session_state.user['id'] if 'user' in st.session_state else None
                
                new_player = Player(
                    name=name,
                    age=age,
                    age_group=get_age_group(age),
                    position=position,
                    jersey_number=jersey_number if jersey_number > 0 else None,
                    join_date=datetime.utcnow(),
                    user_id=user_id  # Associate player with the user
                )
                
                db.session.add(new_player)
                db.session.flush()
                
                if team_id != "No Team":
                    team_membership = TeamMembership(
                        player_id=new_player.id,
                        team_id=team_id[0],
                        join_date=datetime.utcnow(),
                        position_in_team=position,
                        is_active=True
                    )
                    db.session.add(team_membership)
                
                db.session.commit()
                st.success(f"Added player: {name}")
                return True
            except Exception as e:
                db.session.rollback()
                st.error(f"Error adding player: {str(e)}")
                return False
    
    return False

def display_upload_roster_form():
    """Display form for uploading a roster"""
    st.subheader("Upload Roster")
    
    # Provide template for download
    template_df = create_roster_template()
    st.markdown("Download our template and fill it with your player data:")
    st.markdown(get_download_link(template_df, "player_roster_template.csv", "Download Roster Template"), unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("Upload your roster CSV file", type=["csv"])
    
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            
            # Show preview
            st.write("Preview of uploaded data:")
            st.dataframe(df.head())
            
            # Validate data
            is_valid, errors = validate_roster_data(df)
            
            if not is_valid:
                st.error("Errors in uploaded roster:")
                for error in errors:
                    st.error(f"- {error}")
            else:
                if st.button("Import Players"):
                    # Get user ID from session
                    user_id = st.session_state.user['id'] if 'user' in st.session_state else None
                    
                    # Process upload
                    success, message = process_roster_upload(df, user_id)
                    
                    if success:
                        st.success(message)
                        return True
                    else:
                        st.error(message)
        
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")
    
    return False

def display_create_team_form():
    """Display form for creating a new team"""
    st.subheader("Create a Team")
    
    with st.form("create_team_form"):
        team_name = st.text_input("Team Name")
        age_group = st.selectbox("Age Group", ["U8", "U10", "U12", "U14", "U16", "U18"])
        
        submitted = st.form_submit_button("Create Team")
        
        if submitted and team_name:
            try:
                new_team = Team(
                    name=team_name,
                    age_group=age_group,
                    created_date=datetime.utcnow()
                )
                
                db.session.add(new_team)
                db.session.commit()
                st.success(f"Team created: {team_name}")
                return True
            except Exception as e:
                db.session.rollback()
                st.error(f"Error creating team: {str(e)}")
                return False
    
    return False

def display_onboarding():
    """Main onboarding interface for new users"""
    user_name = st.session_state.user['name'] if 'user' in st.session_state else "Coach"
    
    # Display welcome message
    display_welcome_message(user_name)
    
    # Create tabs for different setup options
    tab1, tab2, tab3 = st.tabs(["Add Players", "Upload Roster", "Create Team"])
    
    with tab1:
        player_added = display_manual_add_form()
    
    with tab2:
        roster_uploaded = display_upload_roster_form()
    
    with tab3:
        team_created = display_create_team_form()
    
    # Display current rosters if any
    # Get user ID from session
    user_id = st.session_state.user['id'] if 'user' in st.session_state else None
    
    if user_id:
        # Get the player IDs for this user
        user_players = Player.query.filter_by(user_id=user_id).all()
        player_ids = [p.id for p in user_players]
        
        # Get team memberships for these players
        team_ids = []
        if player_ids:
            memberships = TeamMembership.query.filter(TeamMembership.player_id.in_(player_ids)).all()
            team_ids = [m.team_id for m in memberships]
        
        # Get teams that contain these players
        if team_ids:
            teams = Team.query.filter(Team.id.in_(team_ids)).all()
        else:
            teams = []
    else:
        # If no user ID, show all teams (fallback for testing)
        teams = Team.query.all()
        
    if teams:
        st.subheader("Your Teams")
        for team in teams:
            with st.expander(f"{team.name} ({team.age_group})"):
                # Filter players to show only those belonging to current user
                if user_id:
                    players = Player.query.join(TeamMembership).filter(
                        TeamMembership.team_id == team.id,
                        Player.user_id == user_id
                    ).all()
                else:
                    players = team.players.all()
                    
                if players:
                    data = []
                    for player in players:
                        memberships = player.memberships.filter_by(team_id=team.id).first()
                        position = memberships.position_in_team if memberships else player.position
                        
                        data.append({
                            "Name": player.name,
                            "Age": player.age,
                            "Position": position,
                            "Jersey": player.jersey_number if hasattr(player, 'jersey_number') else "-"
                        })
                    
                    if data:
                        st.dataframe(pd.DataFrame(data))
                else:
                    st.info("No players added to this team yet.")