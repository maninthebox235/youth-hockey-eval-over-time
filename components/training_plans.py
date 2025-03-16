import streamlit as st
import pandas as pd
import numpy as np
from database.models import db, Player, PlayerHistory
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random

def fix_youtube_url(url):
    """Convert YouTube embed URL to watch URL for Streamlit compatibility"""
    if not url:
        return url
    if 'youtube.com/embed/' in url:
        video_id = url.split('/')[-1]
        return f"https://www.youtube.com/watch?v={video_id}"
    return url

class TrainingPlans:
    def __init__(self):
        # Training Library
        
        # Define the skill drills data
        self.skill_drills = {
            # Skating drills
            'skating_speed': [
                {
                    'name': 'Line Sprints',
                    'description': 'Sprint from goal line to blue line and back, then to center ice and back, then far blue line and back, then far goal line and back.',
                    'duration': '10 minutes',
                    'difficulty': 'Medium',
                    'resources': 'None',
                    'video_url': 'https://www.youtube.com/watch?v=ZsdRdPNUWcE'
                },
                {
                    'name': 'Explosive Starts',
                    'description': 'Practice explosive first 3 steps from standing start. Focus on powerful pushes and quick feet.',
                    'duration': '8 minutes',
                    'difficulty': 'Medium',
                    'resources': 'Cones',
                    'video_url': 'https://www.youtube.com/embed/Qt0X2-L-QKQ'
                },
                {
                    'name': 'Cornering Technique',
                    'description': 'Practice tight turns around circles maintaining speed and proper edge work.',
                    'duration': '12 minutes',
                    'difficulty': 'Medium',
                    'resources': 'Cones',
                    'video_url': 'https://www.youtube.com/embed/00wVVEqZ3cQ'
                }
            ],
            'edge_control': [
                {
                    'name': 'Figure 8s',
                    'description': 'Skate figure 8 patterns focusing on edge control and proper weight shifting.',
                    'duration': '10 minutes',
                    'difficulty': 'Medium',
                    'resources': 'None',
                    'video_url': 'https://www.youtube.com/embed/n6UMnCQn-Lc'
                },
                {
                    'name': 'Inside/Outside Edge Circles',
                    'description': 'Practice skating on inside and outside edges around circle. Keep inside foot up when using outside edge and vice versa.',
                    'duration': '15 minutes',
                    'difficulty': 'Hard',
                    'resources': 'None',
                    'video_url': 'https://www.youtube.com/embed/B5HxP9KzQf0'
                }
            ],
            'backward_skating': [
                {
                    'name': 'Backward C-Cuts',
                    'description': 'Practice C-cuts going backward in both directions, focusing on power and control.',
                    'duration': '8 minutes',
                    'difficulty': 'Medium',
                    'resources': 'None',
                    'video_url': 'https://www.youtube.com/embed/WgLrHFl8jWI'
                },
                {
                    'name': 'Backward Crossovers',
                    'description': 'Work on backward crossovers around circles, focusing on proper technique and edge control.',
                    'duration': '10 minutes',
                    'difficulty': 'Hard',
                    'resources': 'None',
                    'video_url': 'https://www.youtube.com/embed/a1_RrG0wnvE'
                }
            ],
            'agility': [
                {
                    'name': 'Cone Weaving',
                    'description': 'Set up cones in a zigzag pattern and weave through them forwards and backwards.',
                    'duration': '10 minutes',
                    'difficulty': 'Medium',
                    'resources': 'Cones',
                    'video_url': 'https://www.youtube.com/embed/zdLKnLkEOoU'
                },
                {
                    'name': 'Tight Turns',
                    'description': 'Practice tight turns around cones or objects, maintaining speed and control.',
                    'duration': '8 minutes',
                    'difficulty': 'Medium',
                    'resources': 'Cones',
                    'video_url': 'https://www.youtube.com/embed/00wVVEqZ3cQ'
                }
            ],
            
            # Puck control drills
            'puck_control': [
                {
                    'name': 'Stationary Stickhandling',
                    'description': 'Practice stickhandling in place with eyes up, focusing on various patterns (figure 8, side-to-side).',
                    'duration': '8 minutes',
                    'difficulty': 'Easy',
                    'resources': 'Puck or ball',
                    'video_url': 'https://www.youtube.com/embed/Fb0qmGOSZMc'
                },
                {
                    'name': 'Obstacle Stickhandling',
                    'description': 'Set up obstacles (cones, gloves) and practice stickhandling around them while skating.',
                    'duration': '10 minutes',
                    'difficulty': 'Medium',
                    'resources': 'Puck, cones',
                    'video_url': 'https://www.youtube.com/embed/Hl3PxUz00BE'
                },
                {
                    'name': 'Toe Drag Practice',
                    'description': 'Practice toe drag moves while stationary, then incorporate into skating patterns.',
                    'duration': '8 minutes',
                    'difficulty': 'Hard',
                    'resources': 'Puck',
                    'video_url': 'https://www.youtube.com/embed/gDfb0Yzh7Cs'
                }
            ],
            'passing_accuracy': [
                {
                    'name': 'Partner Passing',
                    'description': 'Pass back and forth with a partner, focusing on accuracy and proper technique.',
                    'duration': '10 minutes',
                    'difficulty': 'Easy',
                    'resources': 'Partner, pucks',
                    'video_url': 'https://www.youtube.com/embed/g_6E0IWO9KQ'
                },
                {
                    'name': 'Moving Target Passing',
                    'description': 'Practice passing to a moving target (partner skating) at different distances.',
                    'duration': '10 minutes',
                    'difficulty': 'Medium',
                    'resources': 'Partner, pucks',
                    'video_url': 'https://www.youtube.com/embed/C2uxYOZ6vEQ'
                },
                {
                    'name': 'Board Bank Passes',
                    'description': 'Practice using the boards to make passes to a teammate.',
                    'duration': '8 minutes',
                    'difficulty': 'Medium',
                    'resources': 'Partner, pucks',
                    'video_url': 'https://www.youtube.com/embed/KNh5fEA6O4Q'
                }
            ],
            
            # Shooting drills
            'shot_accuracy': [
                {
                    'name': 'Target Practice',
                    'description': 'Set up targets in the net and practice hitting them with wrist shots.',
                    'duration': '12 minutes',
                    'difficulty': 'Medium',
                    'resources': 'Pucks, targets',
                    'video_url': 'https://www.youtube.com/embed/iAqmIZgA8Os'
                },
                {
                    'name': 'Quick Release',
                    'description': 'Practice receiving a pass and shooting in one motion without stickhandling.',
                    'duration': '10 minutes',
                    'difficulty': 'Hard',
                    'resources': 'Partner, pucks',
                    'video_url': 'https://www.youtube.com/embed/Bpo9WrHnNSs'
                }
            ],
            'wrist_shot': [
                {
                    'name': 'Weight Transfer Shot',
                    'description': 'Focus on proper weight transfer from back to front foot during wrist shot.',
                    'duration': '10 minutes',
                    'difficulty': 'Medium',
                    'resources': 'Pucks',
                    'video_url': 'https://www.youtube.com/embed/9mKEgD0VUJ4'
                },
                {
                    'name': 'Wrist Shot From Motion',
                    'description': 'Practice wrist shots while skating at different speeds, focusing on accuracy.',
                    'duration': '12 minutes',
                    'difficulty': 'Medium',
                    'resources': 'Pucks',
                    'video_url': 'https://www.youtube.com/embed/UNDRsG23YmI'
                }
            ],
            'slap_shot': [
                {
                    'name': 'Stationary Slap Shot',
                    'description': 'Practice proper technique for slap shots from a stationary position.',
                    'duration': '10 minutes',
                    'difficulty': 'Hard',
                    'resources': 'Pucks',
                    'video_url': 'https://www.youtube.com/embed/MyRjT-ECesQ'
                },
                {
                    'name': 'One-Timer Practice',
                    'description': 'Set up for one-timers with a partner passing the puck.',
                    'duration': '15 minutes',
                    'difficulty': 'Hard',
                    'resources': 'Partner, pucks',
                    'video_url': 'https://www.youtube.com/embed/1E_YiODVQpE'
                }
            ],
            
            # Game IQ drills
            'hockey_sense': [
                {
                    'name': '3-on-2 Situations',
                    'description': 'Practice 3-on-2 offensive situations focusing on decision making and puck movement.',
                    'duration': '15 minutes',
                    'difficulty': 'Medium',
                    'resources': 'Teammates',
                    'video_url': 'https://www.youtube.com/embed/Wwo5aHnq8Eo'
                },
                {
                    'name': 'Small Area Games',
                    'description': 'Play 2-on-2 or 3-on-3 in a small area to practice quick decisions and puck movement.',
                    'duration': '20 minutes',
                    'difficulty': 'Medium',
                    'resources': 'Teammates, cones',
                    'video_url': 'https://www.youtube.com/embed/B-MqeZIib2U'
                }
            ],
            'decision_making': [
                {
                    'name': '2-on-1 Scenarios',
                    'description': 'Practice offensive 2-on-1 situations, focusing on when to pass vs. when to shoot.',
                    'duration': '15 minutes',
                    'difficulty': 'Medium',
                    'resources': 'Teammates, defender',
                    'video_url': 'https://www.youtube.com/embed/wIoVt00KqY4'
                },
                {
                    'name': 'Transition Drills',
                    'description': 'Practice quickly transitioning from defense to offense and making quick decisions.',
                    'duration': '12 minutes',
                    'difficulty': 'Hard',
                    'resources': 'Teammates',
                    'video_url': 'https://www.youtube.com/embed/BwWu3gVV1MM'
                }
            ],
            
            # Defense specific
            'gap_control': [
                {
                    'name': '1-on-1 Gap Control',
                    'description': 'Practice maintaining proper gap against an attacking forward.',
                    'duration': '15 minutes',
                    'difficulty': 'Medium',
                    'resources': 'Partner',
                    'video_url': 'https://www.youtube.com/embed/Z3sSA9D2T1s'
                },
                {
                    'name': 'Controlled Angling',
                    'description': 'Practice angling opponents to the boards, maintaining proper gap and body position.',
                    'duration': '12 minutes',
                    'difficulty': 'Medium',
                    'resources': 'Partner',
                    'video_url': 'https://www.youtube.com/embed/qsKgYRQR-Mk'
                }
            ],
            'shot_blocking': [
                {
                    'name': 'Shot Blocking Technique',
                    'description': 'Practice proper technique for blocking shots safely and effectively.',
                    'duration': '10 minutes',
                    'difficulty': 'Hard',
                    'resources': 'Shooter, tennis balls',
                    'video_url': 'https://www.youtube.com/embed/TAeNyjJXZLM'
                }
            ],
            
            # Goalie specific
            'positioning': [
                {
                    'name': 'Post Integration Drill',
                    'description': 'Practice proper positioning against the post and quick movements to cover angles.',
                    'duration': '10 minutes',
                    'difficulty': 'Medium',
                    'resources': 'Shooter',
                    'video_url': 'https://www.youtube.com/embed/kYiE1Q-_RKE'
                },
                {
                    'name': 'Angle Drill',
                    'description': 'Move quickly between different positions in the crease to maintain proper angles.',
                    'duration': '12 minutes',
                    'difficulty': 'Medium',
                    'resources': 'Shooter, cones',
                    'video_url': 'https://www.youtube.com/embed/KWzIMtmApdU'
                }
            ],
            'save_technique': [
                {
                    'name': 'Butterfly Slide Drill',
                    'description': 'Practice butterfly slides from post to post to cover the bottom of the net quickly.',
                    'duration': '10 minutes',
                    'difficulty': 'Medium',
                    'resources': 'None',
                    'video_url': 'https://www.youtube.com/embed/qF-9hCTBBYs'
                },
                {
                    'name': 'Reaction Save Drill',
                    'description': 'Shooter randomly aims high or low requiring quick reactions and proper save selection.',
                    'duration': '15 minutes',
                    'difficulty': 'Hard',
                    'resources': 'Shooter',
                    'video_url': 'https://www.youtube.com/embed/ZYj8NpBP7U8'
                }
            ],
            'rebound_control': [
                {
                    'name': 'Controlled Rebounds',
                    'description': 'Practice directing rebounds to corners or catching and freezing the puck.',
                    'duration': '12 minutes',
                    'difficulty': 'Hard',
                    'resources': 'Shooter',
                    'video_url': 'https://www.youtube.com/embed/xzDdOIeiPqI'
                }
            ],
            'recovery': [
                {
                    'name': 'Recovery Drill',
                    'description': 'Practice quickly recovering position after making an initial save.',
                    'duration': '10 minutes',
                    'difficulty': 'Hard',
                    'resources': 'Multiple shooters',
                    'video_url': 'https://www.youtube.com/embed/KJP-XHbsBaE'
                }
            ]
        }
        
        # Fix all video URLs to work with Streamlit
        self._fix_all_video_urls()
        
        # Age-appropriate training plans
        self.age_plans = {
            (6, 8): {
                'focus': 'Fundamental Skills & Fun',
                'sessions_per_week': 2,
                'session_duration': 30,
                'priority_skills': ['skating_speed', 'edge_control', 'puck_control'],
                'intensity': 'Low',
                'off_ice_focus': 'Basic coordination, fun activities'
            },
            (9, 11): {
                'focus': 'Skill Development',
                'sessions_per_week': 2,
                'session_duration': 45,
                'priority_skills': ['skating_speed', 'edge_control', 'puck_control', 'passing_accuracy'],
                'intensity': 'Medium',
                'off_ice_focus': 'Coordination, basic strength exercises'
            },
            (12, 14): {
                'focus': 'Skill Refinement & Position-Specific',
                'sessions_per_week': 3,
                'session_duration': 60,
                'priority_skills': ['skating_speed', 'edge_control', 'shot_accuracy', 'hockey_sense'],
                'intensity': 'Medium-High',
                'off_ice_focus': 'Sport-specific exercises, core strength'
            },
            (15, 18): {
                'focus': 'Performance & Specialization',
                'sessions_per_week': 4,
                'session_duration': 60,
                'priority_skills': ['skating_speed', 'decision_making', 'shot_accuracy', 'hockey_sense'],
                'intensity': 'High',
                'off_ice_focus': 'Strength training, explosive power, conditioning'
            }
        }
    
    def _fix_all_video_urls(self):
        """Convert all video URLs to use watch format instead of embed format"""
        for skill_category in self.skill_drills:
            for drill in self.skill_drills[skill_category]:
                if 'video_url' in drill and drill['video_url']:
                    drill['video_url'] = fix_youtube_url(drill['video_url'])
    
    def get_age_plan(self, age):
        """Get the appropriate training plan for a player's age"""
        for (min_age, max_age), plan in self.age_plans.items():
            if min_age <= age <= max_age:
                return plan
        # Default to oldest age group if no match found
        return self.age_plans[(15, 18)]
    
    def get_drills_for_skill(self, skill, count=2):
        """Get recommended drills for a specific skill"""
        if skill not in self.skill_drills:
            return []
            
        drills = self.skill_drills[skill]
        # Return requested number of drills or all available if fewer
        return drills[:min(count, len(drills))]
    
    def get_player_needs(self, player_data):
        """Identify a player's development needs based on metrics"""
        if player_data is None or len(player_data) == 0:
            return []
            
        # Identify skills with lowest ratings
        skills = {}
        for attr, value in player_data.items():
            # Make sure we're dealing with a scalar value, not a pandas Series
            if isinstance(value, pd.Series):
                continue
                
            # Check if the attribute is in skill_drills and is a numeric value
            if attr in self.skill_drills and isinstance(value, (int, float)) and not pd.isna(value):
                skills[attr] = value
                
        # Sort by value, lowest first
        sorted_skills = sorted(skills.items(), key=lambda x: x[1])
        
        # Return the lowest 3 skills or fewer if not enough data
        return sorted_skills[:min(3, len(sorted_skills))]
    
    def generate_personalized_plan(self, player_data):
        """Generate a personalized training plan for a player"""
        if player_data is None or len(player_data) == 0:
            return None
            
        # Get age and position
        # Handle case where player_data might be a DataFrame or Series
        if isinstance(player_data, pd.DataFrame) or isinstance(player_data, pd.Series):
            age = player_data.get('age', 12)
            if isinstance(age, pd.Series):
                age = age.iloc[0] if not age.empty else 12
            position = player_data.get('position', 'Forward')
            if isinstance(position, pd.Series):
                position = position.iloc[0] if not position.empty else 'Forward'
        else:
            age = player_data.get('age', 12)
            position = player_data.get('position', 'Forward')
        
        # Get age-appropriate plan
        base_plan = self.get_age_plan(age)
        
        # Identify player's development needs
        needs = self.get_player_needs(player_data)
        
        # Add position-specific skills if needed
        position_skills = {
            'Forward': ['shot_accuracy', 'wrist_shot', 'hockey_sense'],
            'Defense': ['gap_control', 'backward_skating', 'shot_blocking'],
            'Goalie': ['positioning', 'save_technique', 'rebound_control']
        }
        
        # Include position-specific skills if there aren't enough needs identified
        if len(needs) < 3 and position in position_skills:
            for skill in position_skills[position]:
                if skill not in [s for s, _ in needs]:
                    # Add with a default value
                    needs.append((skill, 3.0))
                    if len(needs) >= 3:
                        break
        
        # Create the training plan
        plan = {
            'age_group': f"{age} years old",
            'position': position,
            'sessions_per_week': base_plan['sessions_per_week'],
            'session_duration': base_plan['session_duration'],
            'focus_areas': [skill for skill, _ in needs],
            'drills': []
        }
        
        # Add specific drills for each focus area
        for skill, value in needs:
            skill_drills = self.get_drills_for_skill(skill, count=2)
            for drill in skill_drills:
                plan['drills'].append({
                    'skill': skill,
                    'skill_rating': value,
                    **drill
                })
                
        return plan

def display_drill_details(drill):
    """Display details for a specific training drill"""
    st.subheader(drill['name'])
    st.write(f"**Focus Area:** {drill['skill'].replace('_', ' ').title()}")
    
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Duration:** {drill['duration']}")
        st.write(f"**Difficulty:** {drill['difficulty']}")
        st.write(f"**Resources Needed:** {drill['resources']}")
    
    with col2:
        # Show video if available
        if 'video_url' in drill and drill['video_url']:
            # Convert embed URL to watch URL if needed
            video_url = fix_youtube_url(drill['video_url'])
            st.video(video_url)
    
    st.write("**Description:**")
    st.write(drill['description'])
    
    # Add to calendar button (mock functionality)
    if st.button("Add to Training Schedule", key=f"add_{drill['name'].replace(' ', '_')}"):
        st.success("Drill added to your training schedule!")

def display_player_weaknesses(player_data, trainer):
    """Display a player's weaknesses and recommended focus areas"""
    # Convert DataFrame to dict if needed
    if isinstance(player_data, pd.DataFrame):
        if len(player_data) > 0:
            player_dict = player_data.iloc[0].to_dict()
        else:
            player_dict = {}
    else:
        player_dict = player_data
        
    needs = trainer.get_player_needs(player_dict)
    
    if not needs:
        st.info("Not enough skill data available to identify specific needs.")
        return
        
    st.subheader("Development Focus Areas")
    
    # Create columns for each need
    cols = st.columns(len(needs))
    
    for i, (skill, value) in enumerate(needs):
        with cols[i]:
            # Format skill name
            skill_name = skill.replace('_', ' ').title()
            
            # Create gauge for current level
            fig = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = value,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': skill_name},
                gauge = {
                    'axis': {'range': [0, 5]},
                    'bar': {'color': "red" if value < 2.5 else "yellow" if value < 3.5 else "green"},
                    'steps': [
                        {'range': [0, 2], 'color': "lightgray"},
                        {'range': [2, 3], 'color': "lightyellow"},
                        {'range': [3, 5], 'color': "lightgreen"}
                    ],
                    'threshold': {
                        'line': {'color': "black", 'width': 2},
                        'thickness': 0.75,
                        'value': 3
                    }
                }
            ))
            
            fig.update_layout(height=200)
            st.plotly_chart(fig, use_container_width=True)
            
            # Add focus recommendation
            if value < 2.5:
                st.error(f"**Primary Focus Area** - Significant improvement needed")
            elif value < 3.5:
                st.warning(f"**Development Area** - Consistent practice needed")
            else:
                st.info(f"**Refinement Area** - Fine-tune this skill")

def display_training_schedule(player_data, plan):
    """Display a weekly training schedule based on the plan"""
    st.subheader("Weekly Training Schedule")
    
    # Get age-appropriate plan
    if isinstance(player_data, pd.DataFrame) or isinstance(player_data, pd.Series):
        age = player_data.get('age', 12)
        if isinstance(age, pd.Series):
            age = age.iloc[0] if not age.empty else 12
    else:
        age = player_data.get('age', 12)
        
    age_plan = plan['sessions_per_week']
    
    # Define days of the week
    days = ["Monday", "Wednesday", "Friday", "Sunday"]
    
    # Create tabs for each training day
    if age_plan <= len(days):
        schedule_days = days[:age_plan]
        day_tabs = st.tabs(schedule_days)
        
        # Distribute drills across days
        drills = plan['drills']
        drills_per_day = max(1, len(drills) // age_plan)
        
        for i, day in enumerate(schedule_days):
            with day_tabs[i]:
                start_idx = i * drills_per_day
                end_idx = min(start_idx + drills_per_day, len(drills))
                day_drills = drills[start_idx:end_idx]
                
                if day_drills:
                    st.write(f"**Session Duration:** {plan['session_duration']} minutes")
                    
                    for drill in day_drills:
                        with st.expander(f"{drill['name']} ({drill['duration']})"):
                            st.write(f"**Focus Area:** {drill['skill'].replace('_', ' ').title()}")
                            st.write(f"**Difficulty:** {drill['difficulty']}")
                            st.write(f"**Description:** {drill['description']}")
                            
                            if 'video_url' in drill and drill['video_url']:
                                # Use the fix_youtube_url function to ensure proper format
                                st.video(fix_youtube_url(drill['video_url']))
                else:
                    st.info("No specific drills scheduled for this day.")
    else:
        st.write("Too many sessions requested for standard schedule.")

def display_progress_tracking(player_id, focus_skills):
    """Display progress tracking interface for targeted skills"""
    st.subheader("Track Your Progress")
    
    # Get historical data if available
    try:
        history = PlayerHistory.query.filter_by(player_id=player_id).order_by(PlayerHistory.date).all()
        
        history_data = []
        for entry in history:
            data_point = {
                'date': entry.date
            }
            
            # Add focus skills
            for skill in focus_skills:
                if hasattr(entry, skill):
                    value = getattr(entry, skill)
                    if value is not None:
                        data_point[skill] = value
                        
            history_data.append(data_point)
            
        if history_data:
            history_df = pd.DataFrame(history_data)
            
            # Create progress chart for focus skills
            available_skills = [s for s in focus_skills if s in history_df.columns]
            
            if available_skills:
                fig = px.line(
                    history_df,
                    x='date',
                    y=available_skills,
                    title="Skill Progress Over Time",
                    labels={s: s.replace('_', ' ').title() for s in available_skills}
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No historical data available for focus skills.")
        else:
            st.info("No progress data available yet.")
            
    except Exception as e:
        st.error(f"Error retrieving progress data: {str(e)}")
    
    # Progress tracking form
    with st.form("track_progress_form"):
        st.write("Record your progress after completing training sessions:")
        
        progress_date = st.date_input("Date", value=datetime.now())
        
        # Create sliders for each focus skill
        skill_values = {}
        for skill in focus_skills:
            skill_name = skill.replace('_', ' ').title()
            skill_values[skill] = st.slider(
                f"{skill_name} Rating",
                min_value=1,
                max_value=5,
                value=3,
                help=f"Rate your current {skill_name.lower()} level"
            )
            
        notes = st.text_area(
            "Session Notes",
            placeholder="How did your training go? What improvements did you notice?"
        )
        
        submitted = st.form_submit_button("Record Progress")
        
        if submitted:
            try:
                # Create new player history entry
                history_entry = PlayerHistory(
                    player_id=player_id,
                    date=progress_date,
                    notes=f"TRAINING PROGRESS: {notes}"
                )
                
                # Set skill values
                for skill, value in skill_values.items():
                    if hasattr(history_entry, skill):
                        setattr(history_entry, skill, value)
                        
                db.session.add(history_entry)
                db.session.commit()
                
                st.success("Progress recorded successfully!")
                st.rerun()  # Update the progress chart
                
            except Exception as e:
                st.error(f"Error recording progress: {str(e)}")
                db.session.rollback()

def display_training_plan_interface(player_id, player_data):
    """Main interface for personalized training plans"""
    # Check for premium membership
    is_premium = st.session_state.get('is_premium', False)
    
    if not is_premium:
        st.title("Personalized Training Plans")
        st.warning("⭐ Training Plans is a premium feature")
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("""
            Unlock personalized training plans with a premium membership.
            This feature provides:
            - Custom practice plans based on player assessment
            - Position-specific training recommendations
            - Age-appropriate drills and exercises
            - Weekly practice schedules
            """)
        with col2:
            st.button("Upgrade to Premium", type="primary", use_container_width=True)
            
            # Add a sample image to show what they're missing
            st.image("static/images/hockey/players/player-stance.jpg", caption="Training Plans Preview", use_container_width=True)
        return
    
    st.title("Personalized Training Plans")
    
    # Initialize training plans system
    trainer = TrainingPlans()
    
    # Convert player_data to dictionary if it's a DataFrame
    if isinstance(player_data, pd.DataFrame):
        if len(player_data) > 0:
            player_dict = player_data.iloc[0].to_dict()
        else:
            player_dict = {}
    else:
        player_dict = player_data
    
    # Generate personalized plan
    plan = trainer.generate_personalized_plan(player_dict)
    
    if not plan:
        st.error("Could not generate training plan with available data")
        return
    
    # Get name safely
    player_name = "Player"
    if isinstance(player_data, pd.DataFrame) and 'name' in player_data.columns and not player_data.empty:
        player_name = player_data['name'].iloc[0]
    elif isinstance(player_dict, dict) and 'name' in player_dict:
        player_name = player_dict['name']
        
    # Display plan overview
    st.subheader(f"Training Plan Overview for {player_name}")
    st.write(f"**Age:** {plan['age_group']} | **Position:** {plan['position']}")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Sessions Per Week", plan['sessions_per_week'])
    with col2:
        st.metric("Minutes Per Session", plan['session_duration'])
    with col3:
        st.metric("Focus Areas", len(plan['focus_areas']))
    
    # Create tabs for different sections
    tabs = st.tabs(["Focus Areas", "Weekly Schedule", "Training Library", "Progress Tracking"])
    
    with tabs[0]:
        display_player_weaknesses(player_data, trainer)
        
        # Show focus area description
        st.subheader("Recommended Skills Focus")
        for skill in plan['focus_areas']:
            skill_name = skill.replace('_', ' ').title()
            st.write(f"**{skill_name}**")
            
            if skill == 'skating_speed':
                st.info("Focus on stride efficiency, power, and explosive starts")
            elif skill == 'edge_control':
                st.info("Develop confident inside and outside edge work for better control and agility")
            elif skill == 'shot_accuracy':
                st.info("Improve consistent shot placement and quick release")
            elif skill == 'puck_control':
                st.info("Enhance puck handling in tight spaces and while in motion")
            elif skill == 'hockey_sense':
                st.info("Develop better positional awareness and decision-making")
            else:
                st.info(f"Develop and refine {skill_name.lower()} technique")
        
    with tabs[1]:
        display_training_schedule(player_data, plan)
        
    with tabs[2]:
        # Display all drills available for the player's focus areas
        st.subheader("Training Drill Library")
        
        # Group drills by skill
        skill_groups = {}
        for skill in plan['focus_areas']:
            drills = trainer.get_drills_for_skill(skill, count=5)
            if drills:
                skill_groups[skill] = drills
        
        if skill_groups:
            # Create expandable sections for each skill
            for skill, drills in skill_groups.items():
                skill_name = skill.replace('_', ' ').title()
                with st.expander(f"{skill_name} Drills", expanded=True):
                    for i, drill in enumerate(drills):
                        st.markdown(f"### {i+1}. {drill['name']}")
                        
                        # Create columns for drill info and video
                        col1, col2 = st.columns([1, 1])
                        
                        with col1:
                            st.write(f"**Duration:** {drill['duration']}")
                            st.write(f"**Difficulty:** {drill['difficulty']}")
                            st.write(f"**Description:** {drill['description']}")
                            st.write(f"**Resources:** {drill['resources']}")
                        
                        with col2:
                            if 'video_url' in drill and drill['video_url']:
                                # Use the fix_youtube_url function to ensure proper format
                                st.video(fix_youtube_url(drill['video_url']))
                                
                        st.markdown("---")
        else:
            st.info("No specific drills found for focus areas.")
    
    with tabs[3]:
        # Progress tracking interface
        display_progress_tracking(player_id, plan['focus_areas'])