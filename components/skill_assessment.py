import streamlit as st
import pandas as pd
from database.models import Player, PlayerHistory, db
from datetime import datetime

def get_skill_metrics(position):
    """Get detailed skill metrics based on player position"""
    skating_metrics = {
        'skating_speed': "Straight-line skating speed",
        'edge_control': "Control and balance on edges",
        'agility': "Quick directional changes",
        'backward_skating': "Backward skating ability"
    }

    stickhandling_metrics = {
        'puck_control': "Puck control while moving",
        'passing_accuracy': "Accuracy of passes",
        'receiving': "Ability to receive passes",
        'stick_protection': "Protecting puck under pressure"
    }

    game_iq_metrics = {
        'positioning': "Proper positioning on ice",
        'decision_making': "Quick and effective decisions",
        'game_awareness': "Awareness of play development",
        'hockey_sense': "Understanding of game situations"
    }

    if position == "Forward":
        shooting_metrics = {
            'wrist_shot': "Wrist shot technique",
            'slap_shot': "Slap shot power and accuracy",
            'one_timer': "One-timer execution",
            'shot_accuracy': "Overall shooting accuracy"
        }
        return {**skating_metrics, **stickhandling_metrics, **shooting_metrics, **game_iq_metrics}

    elif position == "Defense":
        defense_metrics = {
            'gap_control': "Maintaining proper defensive gaps",
            'physicality': "Physical play effectiveness",
            'shot_blocking': "Shot blocking technique",
            'breakout_passes': "Breakout pass execution"
        }
        return {**skating_metrics, **stickhandling_metrics, **defense_metrics, **game_iq_metrics}

    else:  # Goalie
        goalie_metrics = {
            'positioning': "Net positioning",
            'save_technique': "Basic save techniques",
            'rebound_control': "Control of rebounds",
            'puck_handling': "Puck handling ability",
            'recovery': "Recovery after initial save",
            'glove_saves': "Glove save proficiency",
            'blocker_saves': "Blocker save proficiency",
            'post_integration': "Movement along posts"
        }
        return goalie_metrics

def get_age_appropriate_benchmarks(age, metric):
    """Get age-appropriate benchmark values for metrics"""
    benchmarks = {
        'skating_speed': {
            (6, 8): {'min': 2, 'target': 3, 'description': "Basic forward skating"},
            (9, 11): {'min': 2.5, 'target': 3.5, 'description': "Developing speed"},
            (12, 14): {'min': 3, 'target': 4, 'description': "Advanced speed"},
            (15, 18): {'min': 3.5, 'target': 4.5, 'description': "Elite speed"}
        },
        'puck_control': {
            (6, 8): {'min': 1.5, 'target': 2.5, 'description': "Basic puck handling"},
            (9, 11): {'min': 2, 'target': 3, 'description': "Controlled movements"},
            (12, 14): {'min': 2.5, 'target': 3.5, 'description': "Advanced control"},
            (15, 18): {'min': 3, 'target': 4, 'description': "Elite puck handling"}
        }
    }

    for (min_age, max_age), values in benchmarks.get(metric, {}).items():
        if min_age <= age <= max_age:
            return values
    return {'min': 1, 'target': 3, 'description': "Standard performance"}

def display_skill_assessment(player_id):
    """Display and handle comprehensive skill assessment form"""
    try:
        player_id = int(player_id) if hasattr(player_id, 'item') else player_id
        player = Player.query.get(player_id)

        if not player:
            st.error("Player not found")
            return False

        st.write(f"### Skill Assessment for {player.name}")
        st.write(f"Position: {player.position} | Age: {player.age}")

        metrics = get_skill_metrics(player.position)

        with st.form(key="skill_assessment_form"):
            st.write("### Rate player's skills (1-5 scale)")
            st.write("1 = Needs significant improvement")
            st.write("3 = Meeting age-appropriate expectations")
            st.write("5 = Exceeding expectations significantly")

            all_ratings = {}

            # Split metrics into two columns
            col1, col2 = st.columns(2)
            metrics_list = list(metrics.items())
            mid_point = len(metrics_list) // 2

            # First column
            with col1:
                for metric, description in metrics_list[:mid_point]:
                    st.write(f"**{metric.replace('_', ' ').title()}**")
                    st.write(f"_{description}_")

                    # Get current value with safe default
                    try:
                        current_value = getattr(player, metric, None)
                        current_value = int(current_value) if current_value is not None else 3
                    except (ValueError, TypeError):
                        current_value = 3

                    all_ratings[metric] = st.slider(
                        f"{metric.replace('_', ' ').title()} Rating",
                        min_value=1,
                        max_value=5,
                        value=current_value,
                        key=f"rating_{metric}_1"
                    )

            # Second column
            with col2:
                for metric, description in metrics_list[mid_point:]:
                    st.write(f"**{metric.replace('_', ' ').title()}**")
                    st.write(f"_{description}_")

                    # Get current value with safe default
                    try:
                        current_value = getattr(player, metric, None)
                        current_value = int(current_value) if current_value is not None else 3
                    except (ValueError, TypeError):
                        current_value = 3

                    all_ratings[metric] = st.slider(
                        f"{metric.replace('_', ' ').title()} Rating",
                        min_value=1,
                        max_value=5,
                        value=current_value,
                        key=f"rating_{metric}_2"
                    )

            # Assessment notes
            st.write("### Assessment Notes")
            notes = st.text_area(
                "Observations and Development Goals",
                placeholder="Add specific observations, areas for improvement, and development goals"
            )

            # Submit button
            submitted = st.form_submit_button("Save Assessment")

            if submitted:
                if not notes:
                    st.error("Please add assessment notes")
                    return False

                try:
                    # Update player metrics
                    for metric, value in all_ratings.items():
                        setattr(player, metric, value)

                    # Create historical record
                    history = PlayerHistory(
                        player_id=player.id,
                        date=datetime.utcnow().date(),
                        assessment_notes=notes,
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

    except Exception as e:
        st.error(f"Error in skill assessment: {str(e)}")
        return False

def rate_skill(label, key, description="", default_value=3):
    """Create a standardized rating slider for skills"""
    st.write(f"_{description}_")
    return st.slider(
        label,
        min_value=1,
        max_value=5,
        value=default_value,
        key=key,
        step=1
    )

def get_age_appropriate_benchmarks(age, metric):
    """Get age-appropriate benchmark values for metrics"""
    benchmarks = {
        'skating_speed': {
            (6, 8): {'min': 2, 'target': 3, 'description': "Basic forward skating"},
            (9, 11): {'min': 2.5, 'target': 3.5, 'description': "Developing speed"},
            (12, 14): {'min': 3, 'target': 4, 'description': "Advanced speed"},
            (15, 18): {'min': 3.5, 'target': 4.5, 'description': "Elite speed"}
        },
        'puck_control': {
            (6, 8): {'min': 1.5, 'target': 2.5, 'description': "Basic puck handling"},
            (9, 11): {'min': 2, 'target': 3, 'description': "Controlled movements"},
            (12, 14): {'min': 2.5, 'target': 3.5, 'description': "Advanced control"},
            (15, 18): {'min': 3, 'target': 4, 'description': "Elite puck handling"}
        }
    }

    # Find appropriate age group
    for (min_age, max_age), values in benchmarks.get(metric, {}).items():
        if min_age <= age <= max_age:
            return values
    return {'min': 1, 'target': 3, 'description': "Standard performance"}