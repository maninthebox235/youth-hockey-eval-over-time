import streamlit as st
import pandas as pd
from database.models import Player, PlayerHistory, db
from datetime import datetime

def rate_skill(label, key, help_text="", default_value=3):
    """Create a standardized rating slider for skills"""
    return st.slider(
        label,
        min_value=1,
        max_value=5,
        value=default_value,
        help=help_text,
        key=key
    )

def get_position_specific_metrics(position):
    """Get position-specific metrics for assessment"""
    common_metrics = {
        'skating_speed': "Speed in straight-line skating",
        'agility': "Ability to change direction quickly",
        'puck_control': "Control over the puck while moving",
        'game_intelligence': "Decision making and positioning",
        'team_play': "Effectiveness in team situations"
    }

    if position == "Forward":
        return {
            **common_metrics,
            'shooting_accuracy': "Accuracy in shot placement",
            'shot_power': "Power behind shots",
            'offensive_awareness': "Ability to create scoring chances",
            'forechecking': "Effectiveness in offensive pressure"
        }
    elif position == "Defense":
        return {
            **common_metrics,
            'defensive_awareness': "Ability to read plays and position",
            'physicality': "Effectiveness in physical play",
            'first_pass': "Quality of first pass out of zone",
            'gap_control': "Maintaining proper defensive gaps"
        }
    else:  # Goalie
        return {
            'positioning': "Proper positioning relative to puck",
            'reaction_time': "Speed of reaction to shots",
            'rebound_control': "Control of rebounds",
            'save_technique': "Technical proficiency in saves",
            'puck_handling': "Ability to handle and move puck"
        }

def get_age_appropriate_benchmarks(age, metric):
    """Get age-appropriate benchmark values for metrics"""
    benchmarks = {
        'skating_speed': {
            (6, 8): 2.5,
            (9, 11): 3.0,
            (12, 14): 3.5,
            (15, 18): 4.0
        },
        'shooting_accuracy': {
            (6, 8): 2.0,
            (9, 11): 2.8,
            (12, 14): 3.3,
            (15, 18): 3.8
        },
        # Add more metrics with age-appropriate values
    }

    # Find appropriate age group
    for age_range, value in benchmarks.get(metric, {}).items():
        if age_range[0] <= age <= age_range[1]:
            return value
    return 3.0  # Default benchmark

def display_skill_assessment(player_id):
    """Display and handle comprehensive skill assessment form"""
    player = Player.query.get(player_id)
    if not player:
        st.error("Player not found")
        return False

    st.write(f"### Skill Assessment for {player.name}")
    st.write(f"Position: {player.position} | Age: {player.age}")

    metrics = get_position_specific_metrics(player.position)

    with st.form("skill_assessment_form"):
        all_ratings = {}

        # Create columns for metrics
        for i in range(0, len(metrics), 2):
            col1, col2 = st.columns(2)

            # First metric in the pair
            metric_name = list(metrics.keys())[i]
            benchmark = get_age_appropriate_benchmarks(player.age, metric_name)
            with col1:
                st.write(f"**{metric_name.replace('_', ' ').title()}**")
                st.write(f"_Benchmark for age {player.age}: {benchmark}_")
                all_ratings[metric_name] = rate_skill(
                    "Rating",
                    f"rating_{metric_name}",
                    metrics[metric_name],
                    default_value=int(getattr(player, metric_name, 3))
                )

            # Second metric in the pair (if exists)
            if i + 1 < len(metrics):
                metric_name = list(metrics.keys())[i + 1]
                benchmark = get_age_appropriate_benchmarks(player.age, metric_name)
                with col2:
                    st.write(f"**{metric_name.replace('_', ' ').title()}**")
                    st.write(f"_Benchmark for age {player.age}: {benchmark}_")
                    all_ratings[metric_name] = rate_skill(
                        "Rating",
                        f"rating_{metric_name}",
                        metrics[metric_name],
                        default_value=int(getattr(player, metric_name, 3))
                    )

        # Additional notes
        notes = st.text_area(
            "Assessment Notes",
            help="Add observations about player's performance, areas for improvement, or specific achievements"
        )

        submitted = st.form_submit_button("Save Assessment")

        if submitted:
            try:
                # Update player metrics
                for metric, value in all_ratings.items():
                    setattr(player, metric, value)

                # Create historical record
                history = PlayerHistory(
                    player_id=player.id,
                    date=datetime.utcnow().date(),
                    notes=notes,
                    **all_ratings
                )

                db.session.add(history)
                db.session.commit()

                st.success("Assessment saved successfully!")
                return True

            except Exception as e:
                st.error(f"Error saving assessment: {str(e)}")
                db.session.rollback()
                return False

    return False