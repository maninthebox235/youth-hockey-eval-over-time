import streamlit as st
import pandas as pd
from database.models import db, CoachFeedback, FeedbackTemplate, Player
from datetime import datetime

def get_templates_for_player(player_type):
    """Get available templates for the player type"""
    return FeedbackTemplate.query.filter_by(player_type=player_type).all()

def submit_coach_feedback(player_id, coach_name, feedback_text, ratings, template_id=None):
    """Submit new coach feedback for a player"""
    try:
        # Ensure player_id is a regular Python int
        player_id = int(player_id)

        # Ensure all rating values are integers and filter out None values
        validated_ratings = {}
        for key, value in ratings.items():
            if key.endswith('_rating') and value is not None:
                try:
                    validated_ratings[key] = int(float(value))
                except (ValueError, TypeError):
                    print(f"Error converting rating {key}: {value}")
                    continue

        # Create feedback entry
        feedback = CoachFeedback(
            player_id=player_id,
            coach_name=coach_name,
            feedback_text=feedback_text,
            **validated_ratings
        )
        db.session.add(feedback)

        # Update template usage if a template was used
        if template_id:
            try:
                template = FeedbackTemplate.query.get(template_id)
                if template:
                    template.times_used = (template.times_used or 0) + 1
                    template.last_used = datetime.utcnow()
            except Exception as e:
                print(f"Error updating template usage: {e}")

        db.session.commit()
        return True
    except Exception as e:
        print(f"Error submitting feedback: {e}")
        db.session.rollback()
        return False

def get_player_feedback(player_id):
    """Get all feedback for a specific player"""
    try:
        # Ensure player_id is a regular Python int
        player_id = int(player_id)

        feedback = CoachFeedback.query.filter_by(player_id=player_id).order_by(CoachFeedback.date.desc()).all()
        if not feedback:
            return pd.DataFrame()

        data = []
        for f in feedback:
            feedback_data = {
                'date': f.date.strftime('%Y-%m-%d %H:%M'),
                'coach': f.coach_name,
                'feedback': f.feedback_text
            }

            # Add all ratings that exist for this feedback
            for column in CoachFeedback.__table__.columns:
                if column.name.endswith('_rating'):
                    value = getattr(f, column.name)
                    if value is not None:
                        try:
                            feedback_data[column.name] = int(float(value))
                        except (ValueError, TypeError):
                            continue

            data.append(feedback_data)

        return pd.DataFrame(data)
    except Exception as e:
        print(f"Error getting feedback: {e}")
        return pd.DataFrame()

def display_feedback_form(player_id, player_name, player_position):
    """Display the coach feedback submission form"""
    st.subheader("Submit Coach Feedback")

    # Get available templates for this player type
    player_type = "Goalie" if player_position == "Goalie" else "Skater"
    templates = get_templates_for_player(player_type)

    # Template selection
    selected_template = None
    if templates:
        template_names = ["Custom Feedback"] + [t.name for t in templates]
        template_choice = st.selectbox("Select Template", template_names)

        if template_choice != "Custom Feedback":
            selected_template = next(t for t in templates if t.name == template_choice)

    with st.form("coach_feedback_form"):
        coach_name = st.text_input("Coach Name")
        feedback_text = st.text_area("Feedback Comments")

        # Initialize ratings dictionary
        ratings = {}

        st.subheader("Rating Categories")

        if selected_template:
            # Use template structure to create rating sliders
            categories = selected_template.template_structure['categories']

            # Create sliders in columns, 3 per row
            for i in range(0, len(categories), 3):
                cols = st.columns(3)
                for j, col in enumerate(cols):
                    if i + j < len(categories):
                        category = categories[i + j]
                        category_name = category.replace('_rating', '').replace('_', ' ').title()
                        with col:
                            ratings[category] = st.slider(category_name, 1, 5, 3)
        else:
            # Default rating fields based on position
            if player_position == "Goalie":
                col1, col2, col3 = st.columns(3)
                with col1:
                    ratings['save_technique_rating'] = st.slider("Save Technique", 1, 5, 3)
                with col2:
                    ratings['positioning_rating'] = st.slider("Positioning", 1, 5, 3)
                with col3:
                    ratings['rebound_control_rating'] = st.slider("Rebound Control", 1, 5, 3)

                col1, col2 = st.columns(2)
                with col1:
                    ratings['communication_rating'] = st.slider("Communication", 1, 5, 3)
                with col2:
                    ratings['mental_toughness_rating'] = st.slider("Mental Toughness", 1, 5, 3)
            else:
                col1, col2, col3 = st.columns(3)
                with col1:
                    ratings['skating_rating'] = st.slider("Skating", 1, 5, 3)
                with col2:
                    ratings['shooting_rating'] = st.slider("Shooting", 1, 5, 3)
                with col3:
                    ratings['teamwork_rating'] = st.slider("Teamwork", 1, 5, 3)

        submitted = st.form_submit_button("Submit Feedback")

        if submitted:
            if not coach_name or not feedback_text:
                st.error("Please fill in all required fields")
            else:
                template_id = selected_template.id if selected_template else None
                success = submit_coach_feedback(
                    player_id=player_id,
                    coach_name=coach_name,
                    feedback_text=feedback_text,
                    ratings=ratings,
                    template_id=template_id
                )
                if success:
                    st.success(f"Feedback submitted for {player_name}")
                    st.rerun()
                else:
                    st.error("Error submitting feedback. Please try again.")

def display_feedback_history(player_id):
    """Display the feedback history for a player"""
    feedback_df = get_player_feedback(player_id)

    if not feedback_df.empty:
        st.subheader("Previous Feedback")

        for _, row in feedback_df.iterrows():
            with st.expander(f"Feedback from {row['coach']} on {row['date']}", expanded=True):
                st.write(row['feedback'])

                # Display ratings in columns
                cols = st.columns(3)
                ratings = {k: v for k, v in row.items() if k.endswith('_rating') and pd.notna(v)}

                for i, (metric, value) in enumerate(ratings.items()):
                    with cols[i % 3]:
                        metric_name = metric.replace('_rating', '').replace('_', ' ').title()
                        st.metric(metric_name, int(value))
    else:
        st.info("No feedback available yet.")