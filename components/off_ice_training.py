import streamlit as st
import pandas as pd
from database.models import db, Player, PlayerHistory
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

class OffIceTraining:
    def __init__(self):
        # Define off-ice training categories
        self.training_categories = {
            "Strength & Conditioning": {
                "Bodyweight Exercises": ["Push-ups", "Pull-ups", "Squats", "Lunges", "Planks"],
                "Resistance Training": ["Bands", "Weights", "Medicine Ball", "Kettlebells"],
                "Cardio": ["Running", "Sprints", "Jump Rope", "Agility Ladder"]
            },
            "Hockey-Specific": {
                "Stickhandling": ["Ball handling", "Stickhandling pad", "Mini sticks", "Hand-eye coordination"],
                "Shooting": ["Shot boards", "Shooting tarps", "Puck handling"],
                "Balance": ["Balance board", "Slide board", "Single-leg exercises"]
            },
            "Recovery": {
                "Flexibility": ["Stretching", "Yoga", "Foam Rolling"],
                "Mental": ["Visualization", "Game video", "Hockey IQ development"]
            }
        }
        
        # Define default training plans by age
        self.age_based_plans = {
            (6, 8): {
                "title": "Fun Development",
                "focus": "Basic movement skills, coordination",
                "schedule": ["15-20 min stickhandling", "15 min bodyweight activities", "15 min coordination games"],
                "frequency": "2-3 times per week"
            },
            (9, 11): {
                "title": "Skill Building",
                "focus": "Sport-specific skills, basic strength",
                "schedule": ["20 min stickhandling", "20 min bodyweight training", "20 min shooting or balance"],
                "frequency": "3 times per week"
            },
            (12, 14): {
                "title": "Athletic Development",
                "focus": "Speed, strength, position-specific",
                "schedule": ["25 min stickhandling/shooting", "25 min strength training", "15 min agility/speed"],
                "frequency": "3-4 times per week" 
            },
            (15, 18): {
                "title": "Performance Training",
                "focus": "Sport-specific conditioning, strength",
                "schedule": ["30 min skill work", "30-45 min strength training", "20 min conditioning"],
                "frequency": "4-5 times per week"
            }
        }
        
    def get_plan_for_age(self, age):
        """Get the appropriate training plan for a player's age"""
        for (min_age, max_age), plan in self.age_based_plans.items():
            if min_age <= age <= max_age:
                return plan
        # Default to oldest age group if no match
        return self.age_based_plans[(15, 18)]
    
    def record_training_session(self, player_id, training_date, training_type, 
                               duration, activities, notes):
        """
        Record an off-ice training session for a player
        
        Args:
            player_id: ID of the player
            training_date: Date of training
            training_type: Type of training (category)
            duration: Duration in minutes
            activities: List of specific activities performed
            notes: Additional notes
            
        Returns:
            bool: Success or failure of recording
        """
        try:
            # Find the player
            player = Player.query.get(player_id)
            if not player:
                return False
            
            # Convert NumPy types to Python native types
            if hasattr(player_id, 'item'):
                player_id = player_id.item()
            if hasattr(duration, 'item'):
                duration = duration.item()
                
            # Record as a player history entry
            history = PlayerHistory(
                player_id=int(player_id),
                date=training_date,
                notes=f"OFF-ICE TRAINING: {training_type}\n\nActivities: {', '.join(activities)}\n\nDuration: {int(duration)} minutes\n\n{notes}"
            )
            
            db.session.add(history)
            db.session.commit()
            return True
            
        except Exception as e:
            st.error(f"Error recording training: {str(e)}")
            db.session.rollback()
            return False
    
    def display_training_log(self, player_id):
        """Display a log of past off-ice training sessions"""
        try:
            # Convert NumPy types to Python native types
            if hasattr(player_id, 'item'):
                player_id = player_id.item()
            
            # Ensure player_id is an integer for database query
            player_id = int(player_id)
                
            # Fetch player history entries that contain off-ice training
            history_entries = PlayerHistory.query.filter_by(player_id=player_id)\
                             .order_by(PlayerHistory.date.desc()).all()
            
            off_ice_entries = []
            for entry in history_entries:
                if entry.notes and "OFF-ICE TRAINING:" in entry.notes:
                    training_type = entry.notes.split("OFF-ICE TRAINING:")[1].split("\n")[0].strip()
                    
                    # Extract activities and duration if present
                    activities = ""
                    duration = ""
                    if "Activities:" in entry.notes:
                        activities = entry.notes.split("Activities:")[1].split("\n")[0].strip()
                    if "Duration:" in entry.notes:
                        duration = entry.notes.split("Duration:")[1].split("\n")[0].strip()
                        
                    # Add to off-ice entries
                    off_ice_entries.append({
                        'date': entry.date,
                        'type': training_type,
                        'activities': activities,
                        'duration': duration.replace(" minutes", ""),
                        'notes': entry.notes
                    })
            
            if off_ice_entries:
                # Create a DataFrame for display
                df = pd.DataFrame(off_ice_entries)
                
                # Show summary metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Sessions", len(df))
                with col2:
                    try:
                        total_duration = sum([int(d.split(" ")[0]) for d in df['duration'] if d and d[0].isdigit()])
                        st.metric("Total Training Time", f"{total_duration} minutes")
                    except:
                        st.metric("Total Training Time", "N/A")
                with col3:
                    recent_date = df['date'].max()
                    days_since = (datetime.now().date() - recent_date).days
                    st.metric("Last Training", f"{days_since} days ago")
                
                # Show training log
                st.markdown("### Training History")
                
                for i, entry in enumerate(off_ice_entries):
                    with st.expander(f"{entry['date']} - {entry['type']}", expanded=i==0):
                        st.write(f"**Activities:** {entry['activities']}")
                        st.write(f"**Duration:** {entry['duration']}")
                        
                        # Show detailed notes without the structured part
                        detailed_notes = entry['notes']
                        if "OFF-ICE TRAINING:" in detailed_notes:
                            sections = detailed_notes.split("\n\n")
                            if len(sections) > 3:
                                detailed_notes = "\n\n".join(sections[3:])
                                if detailed_notes.strip():
                                    st.write("**Notes:**")
                                    st.info(detailed_notes)
                
                # Show training distribution chart
                training_types = df['type'].value_counts().reset_index()
                training_types.columns = ['Type', 'Sessions']
                
                fig = px.pie(training_types, values='Sessions', names='Type', 
                             title='Off-Ice Training Distribution')
                st.plotly_chart(fig, use_container_width=True)
                
                return True
            else:
                st.info("No off-ice training records found for this player.")
                return False
                
        except Exception as e:
            st.error(f"Error displaying training log: {str(e)}")
            return False
    
    def display_training_form(self, player_id, player_name):
        """Display a form for recording new off-ice training"""
        st.subheader(f"Record Off-Ice Training for {player_name}")
        
        with st.form("off_ice_training_form"):
            # Training date
            training_date = st.date_input("Training Date", value=datetime.now())
            
            # Training category
            category_options = list(self.training_categories.keys())
            training_category = st.selectbox("Training Category", category_options)
            
            # Subcategory based on main category
            if training_category:
                subcategories = list(self.training_categories[training_category].keys())
                training_subcategory = st.selectbox("Training Subcategory", subcategories)
                
                # Activities based on subcategory
                if training_subcategory:
                    activity_options = self.training_categories[training_category][training_subcategory]
                    selected_activities = st.multiselect("Activities", activity_options)
            
            # Duration
            duration = st.number_input("Duration (minutes)", min_value=5, max_value=180, value=30, step=5)
            
            # Exertion level
            exertion = st.slider("Effort Level", min_value=1, max_value=5, value=3,
                                help="1 = Light, 3 = Moderate, 5 = Maximum effort")
            
            # Notes
            notes = st.text_area("Training Notes", 
                                placeholder="Enter details about the training session...")
            
            # Submit button
            submitted = st.form_submit_button("Record Training")
            
            if submitted:
                if not training_category or not selected_activities:
                    st.error("Please select at least one activity")
                    return False
                    
                # Format the training type with category and subcategory
                training_type = f"{training_category} - {training_subcategory}"
                
                # Add exertion to notes
                full_notes = f"Effort Level: {exertion}/5\n\n{notes}"
                
                # Record the training
                success = self.record_training_session(
                    player_id=player_id,
                    training_date=training_date,
                    training_type=training_type,
                    duration=duration,
                    activities=selected_activities,
                    notes=full_notes
                )
                
                if success:
                    st.success("Training session recorded successfully!")
                    return True
                else:
                    st.error("Failed to record training session")
                    return False
        
        return False

    def display_age_appropriate_plan(self, player_age, player_position):
        """Display age-appropriate training recommendations"""
        plan = self.get_plan_for_age(player_age)
        
        st.subheader(f"Recommended Training Plan: {plan['title']}")
        st.markdown(f"**Focus Areas:** {plan['focus']}")
        st.markdown(f"**Recommended Frequency:** {plan['frequency']}")
        
        st.markdown("### Suggested Schedule")
        for item in plan['schedule']:
            st.markdown(f"- {item}")
            
        # Add position-specific recommendations
        st.markdown("### Position-Specific Focus")
        if player_position == "Forward":
            st.info("""
            **Forward Training Focus:**
            - Shooting accuracy and quick release drills
            - Stickhandling in tight spaces
            - Explosive first-step skating drills
            - Offensive zone positioning visualization
            """)
        elif player_position == "Defense":
            st.info("""
            **Defense Training Focus:**
            - Backwards skating and transitions
            - Gap control visualization exercises
            - Shot blocking techniques (without equipment)
            - Passing accuracy from defensive positions
            """)
        else:  # Goalie
            st.info("""
            **Goalie Training Focus:**
            - Hand-eye coordination drills
            - Lateral movement and recovery exercises
            - Flexibility and core strengthening
            - Visual tracking exercises
            """)
            
        # Add downloadable training plan option
        st.markdown("### Next Steps")
        st.markdown("1. Start with 2-3 exercises from each category")
        st.markdown("2. Record your training using the form on this page")
        st.markdown("3. Gradually increase difficulty as skills improve")

def display_off_ice_interface(player_id, player_data):
    """Main interface for off-ice training tracking"""
    off_ice = OffIceTraining()
    
    # Convert NumPy types to Python native types
    if hasattr(player_id, 'item'):
        player_id = int(player_id.item())
    else:
        player_id = int(player_id)
    
    # Convert other NumPy types in player_data if needed
    player_age = player_data['age']
    if hasattr(player_age, 'item'):
        player_age = int(player_age.item())
    else:
        player_age = int(player_age)
        
    player_name = player_data['name']
    player_position = player_data['position']
    
    st.title("Off-Ice Training Tracker")
    st.write("Track and monitor off-ice development activities")
    
    # Create tabs for different functions
    tabs = st.tabs(["Training Log", "Record Training", "Training Plan"])
    
    with tabs[0]:
        off_ice.display_training_log(player_id)
        
    with tabs[1]:
        off_ice.display_training_form(player_id, player_name)
        
    with tabs[2]:
        off_ice.display_age_appropriate_plan(player_age, player_position)