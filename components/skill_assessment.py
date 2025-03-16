import streamlit as st
import pandas as pd
from database.models import Player, PlayerHistory, db
from datetime import datetime

def rate_skill(label, key, help_text=""):
    """Create a standardized rating slider for skills"""
    return st.slider(
        label,
        min_value=1,
        max_value=5,
        value=3,
        help=help_text,
        key=key
    )

def display_skill_assessment(player_id):
    """Display and handle comprehensive skill assessment form"""
    player = Player.query.get(player_id)
    if not player:
        st.error("Player not found")
        return False

    with st.form("skill_assessment_form"):
        st.write(f"Assessing skills for: {player.name}")

        # Skating Skills Section
        st.subheader("Skating")
        skating_speed = rate_skill(
            "Skating Speed",
            "skating_speed",
            "Assess player's straight-line speed and acceleration (1=Beginner, 5=Elite)"
        )
        agility = rate_skill(
            "Agility",
            "agility",
            "Assess player's ability to change direction and maintain balance"
        )

        # Stickhandling Section
        st.subheader("Stickhandling")
        puck_control = rate_skill(
            "Puck Control",
            "puck_control",
            "Assess player's ability to maintain control while moving"
        )
        passing = rate_skill(
            "Passing Accuracy",
            "passing",
            "Assess player's ability to complete accurate passes"
        )

        # Shooting Skills
        st.subheader("Shooting")
        shooting_power = rate_skill(
            "Shot Power",
            "shooting_power",
            "Assess player's shot strength and velocity"
        )
        shooting_accuracy = rate_skill(
            "Shooting Accuracy",
            "shooting_accuracy",
            "Assess player's ability to hit targets and corners"
        )

        # Game Intelligence
        st.subheader("Game IQ")
        positioning = rate_skill(
            "Positioning",
            "positioning",
            "Assess player's ability to find open spaces and maintain proper position"
        )
        decision_making = rate_skill(
            "Decision Making",
            "decision_making",
            "Assess player's ability to make good choices with and without the puck"
        )

        # Additional Notes
        notes = st.text_area(
            "Assessment Notes",
            help="Add any additional observations or comments about the player's performance"
        )

        submitted = st.form_submit_button("Save Assessment")

        if submitted:
            try:
                # Update player metrics
                player.skating_speed = skating_speed
                player.shooting_accuracy = shooting_accuracy
                player.positioning = positioning

                # Create historical record
                history = PlayerHistory(
                    player_id=player.id,
                    date=datetime.utcnow().date(),
                    skating_speed=skating_speed,
                    shooting_accuracy=shooting_accuracy,
                    positioning=positioning,

                    # Additional metrics
                    agility=agility,
                    puck_control=puck_control,
                    passing=passing,
                    shooting_power=shooting_power,
                    decision_making=decision_making
                )

                # Add notes if provided
                if notes:
                    history.notes = notes

                db.session.add(history)
                db.session.commit()

                st.success("Assessment saved successfully!")
                return True

            except Exception as e:
                st.error(f"Error saving assessment: {str(e)}")
                return False

    return False