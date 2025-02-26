import streamlit as st
import pandas as pd
from database.models import db, CoachFeedback

def submit_coach_feedback(player_id, coach_name, feedback_text, skating_rating, shooting_rating, teamwork_rating):
    """Submit new coach feedback for a player"""
    try:
        feedback = CoachFeedback(
            player_id=int(player_id),  # Ensure integer conversion
            coach_name=coach_name,
            feedback_text=feedback_text,
            skating_rating=int(skating_rating),
            shooting_rating=int(shooting_rating),
            teamwork_rating=int(teamwork_rating)
        )
        db.session.add(feedback)
        db.session.commit()
        return True
    except Exception as e:
        print(f"Error submitting feedback: {e}")
        db.session.rollback()
        return False

def get_player_feedback(player_id):
    """Get all feedback for a specific player"""
    try:
        feedback = CoachFeedback.query.filter_by(player_id=int(player_id)).order_by(CoachFeedback.date.desc()).all()
        if not feedback:
            return pd.DataFrame()

        data = [{
            'date': f.date.strftime('%Y-%m-%d %H:%M'),
            'coach': f.coach_name,
            'feedback': f.feedback_text,
            'skating': f.skating_rating,
            'shooting': f.shooting_rating,
            'teamwork': f.teamwork_rating
        } for f in feedback]
        return pd.DataFrame(data)
    except Exception as e:
        print(f"Error getting feedback: {e}")
        return pd.DataFrame()

def display_feedback_form(player_id, player_name):
    """Display the coach feedback submission form"""
    st.subheader("Submit Coach Feedback")

    with st.form("coach_feedback_form"):
        coach_name = st.text_input("Coach Name")
        feedback_text = st.text_area("Feedback Comments")

        col1, col2, col3 = st.columns(3)
        with col1:
            skating_rating = st.slider("Skating Rating", 1, 5, 3)
        with col2:
            shooting_rating = st.slider("Shooting Rating", 1, 5, 3)
        with col3:
            teamwork_rating = st.slider("Teamwork Rating", 1, 5, 3)

        submitted = st.form_submit_button("Submit Feedback")

        if submitted:
            if not coach_name or not feedback_text:
                st.error("Please fill in all required fields")
            else:
                success = submit_coach_feedback(
                    player_id=player_id,
                    coach_name=coach_name,
                    feedback_text=feedback_text,
                    skating_rating=skating_rating,
                    shooting_rating=shooting_rating,
                    teamwork_rating=teamwork_rating
                )
                if success:
                    st.success(f"Feedback submitted for {player_name}")
                else:
                    st.error("Error submitting feedback. Please try again.")

def display_feedback_history(player_id):
    """Display the feedback history for a player"""
    feedback_df = get_player_feedback(player_id)

    if not feedback_df.empty:
        st.subheader("Previous Feedback")

        for _, row in feedback_df.iterrows():
            with st.expander(f"Feedback from {row['coach']} on {row['date']}"):
                st.write(row['feedback'])

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Skating", row['skating'])
                with col2:
                    st.metric("Shooting", row['shooting'])
                with col3:
                    st.metric("Teamwork", row['teamwork'])
    else:
        st.info("No feedback available yet.")