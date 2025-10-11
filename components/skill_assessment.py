import streamlit as st
import pandas as pd
from database.models import Player, PlayerHistory, db
from datetime import datetime
from utils.type_converter import to_int, to_float


def get_skill_metrics(position):
    """Get detailed skill metrics based on player position"""
    skating_metrics = {
        "skating_speed": "Straight-line skating speed",
        "edge_control": "Control and balance on edges",
        "agility": "Quick directional changes",
        "backward_skating": "Backward skating ability",
    }

    stickhandling_metrics = {
        "puck_control": "Puck control while moving",
        "passing_accuracy": "Accuracy of passes",
        "receiving": "Ability to receive passes",
        "stick_protection": "Protecting puck under pressure",
    }

    game_iq_metrics = {
        "positioning": "Proper positioning on ice",
        "decision_making": "Quick and effective decisions",
        "game_awareness": "Awareness of play development",
        "hockey_sense": "Understanding of game situations",
    }

    if position == "Forward":
        shooting_metrics = {
            "wrist_shot": "Wrist shot technique",
            "slap_shot": "Slap shot power and accuracy",
            "one_timer": "One-timer execution",
            "shot_accuracy": "Overall shooting accuracy",
        }
        return {
            **skating_metrics,
            **stickhandling_metrics,
            **shooting_metrics,
            **game_iq_metrics,
        }

    elif position == "Defense":
        defense_metrics = {
            "gap_control": "Maintaining proper defensive gaps",
            "physicality": "Physical play effectiveness",
            "shot_blocking": "Shot blocking technique",
            "breakout_passes": "Breakout pass execution",
        }
        return {
            **skating_metrics,
            **stickhandling_metrics,
            **defense_metrics,
            **game_iq_metrics,
        }

    else:  # Goalie
        goalie_metrics = {
            "positioning": "Net positioning",
            "save_technique": "Basic save techniques",
            "rebound_control": "Control of rebounds",
            "puck_handling": "Puck handling ability",
            "recovery": "Recovery after initial save",
            "glove_saves": "Glove save proficiency",
            "blocker_saves": "Blocker save proficiency",
            "post_integration": "Movement along posts",
        }
        return goalie_metrics


def get_benchmark_for_age(age, metric):
    """Get age-appropriate benchmark values for metrics"""
    benchmarks = {
        "skating_speed": {
            (6, 8): {"min": 2, "target": 3, "description": "Basic forward skating"},
            (9, 11): {"min": 2.5, "target": 3.5, "description": "Developing speed"},
            (12, 14): {"min": 3, "target": 4, "description": "Advanced speed"},
            (15, 18): {"min": 3.5, "target": 4.5, "description": "Elite speed"},
        },
        "puck_control": {
            (6, 8): {"min": 1.5, "target": 2.5, "description": "Basic puck handling"},
            (9, 11): {"min": 2, "target": 3, "description": "Controlled movements"},
            (12, 14): {"min": 2.5, "target": 3.5, "description": "Advanced control"},
            (15, 18): {"min": 3, "target": 4, "description": "Elite puck handling"},
        },
    }

    for (min_age, max_age), values in benchmarks.get(metric, {}).items():
        if min_age <= age <= max_age:
            return values
    return {"min": 1, "target": 3, "description": "Standard performance"}


def display_skill_assessment(player_id):
    """Display a tabbed view with current skills and add assessment form"""
    try:
        # Initialize session state for this player if not exists
        if "slider_range_fixed" not in st.session_state:
            st.session_state.slider_range_fixed = True

        # Convert player_id to integer safely
        player_id = to_int(player_id)
        if player_id is None:
            st.error("Invalid player ID")
            return False

        # Ensure we convert to native Python int for database compatibility
        try:
            player_id = int(player_id)  # Explicitly cast to native Python int
        except (TypeError, ValueError):
            st.error(f"Could not convert player ID {player_id} to integer")
            return False

        # Use a fresh session for this query to avoid transaction issues
        try:
            player = Player.query.get(player_id)
        except Exception as e:
            st.error(f"Error retrieving player: {str(e)}")
            # Reset session
            db.session.rollback()
            # Try again
            player = Player.query.get(player_id)

        if not player:
            st.error("Player not found")
            return False

        st.write(f"### Skill Assessment for {player.name}")
        st.write(f"Position: {player.position} | Age: {player.age}")

        # Check if we should show the Current Skills tab first
        tab_index = 0
        if "assessment_saved" in st.session_state and st.session_state.assessment_saved:
            tab_index = 0  # Default to Current Skills tab after saving
            st.session_state.assessment_saved = False  # Reset the flag

        # Create tabs for current skills and adding new assessment
        tab_names = ["Current Skills", "Add New Assessment"]
        current_tab, new_tab = st.tabs(tab_names)

        with current_tab:
            display_current_skills(player)

        with new_tab:
            assessment_saved = add_new_assessment(player)
            if assessment_saved:
                # This will be handled on the next rerun
                st.session_state.assessment_saved = True
                return True

        return False

    except Exception as e:
        st.error(f"Error in skill assessment: {str(e)}")
        return False


def display_current_skills(player):
    """Display the current skills of a player"""
    metrics = get_skill_metrics(player.position)

    st.subheader("Current Skill Ratings")
    st.write(
        "These are the player's current skill ratings. To update them, use the 'Add New Assessment' tab."
    )

    # Get recent assessments
    try:
        player_history = (
            PlayerHistory.query.filter_by(player_id=player.id)
            .order_by(PlayerHistory.date.desc())
            .first()
        )
    except Exception as e:
        st.error(f"Error retrieving player history: {str(e)}")
        db.session.rollback()
        player_history = None

    # Create a 3-column layout for better display of more metrics
    col1, col2, col3 = st.columns(3)
    metrics_list = list(metrics.items())
    section_size = len(metrics_list) // 3

    # First column
    with col1:
        for metric, description in metrics_list[:section_size]:
            if hasattr(player, metric):
                # Safely convert to float for display
                value = to_float(getattr(player, metric, None))
                if value is not None:
                    st.metric(
                        label=metric.replace("_", " ").title(),
                        value=f"{value:.1f}",
                        help=description,
                    )

    # Second column
    with col2:
        for metric, description in metrics_list[section_size : section_size * 2]:
            if hasattr(player, metric):
                # Safely convert to float for display
                value = to_float(getattr(player, metric, None))
                if value is not None:
                    st.metric(
                        label=metric.replace("_", " ").title(),
                        value=f"{value:.1f}",
                        help=description,
                    )

    # Third column
    with col3:
        for metric, description in metrics_list[section_size * 2 :]:
            if hasattr(player, metric):
                # Safely convert to float for display
                value = to_float(getattr(player, metric, None))
                if value is not None:
                    st.metric(
                        label=metric.replace("_", " ").title(),
                        value=f"{value:.1f}",
                        help=description,
                    )

    # Show recent assessment notes if available
    if player_history and player_history.notes:
        st.subheader("Latest Assessment Notes")
        st.write(f"*{player_history.date.strftime('%Y-%m-%d')}*")
        st.info(player_history.notes)


def add_new_assessment(player):
    """Add a new skill assessment for a player"""
    metrics = get_skill_metrics(player.position)

    st.subheader("Add New Assessment")

    # Create a unique form key with a timestamp to ensure fresh rendering
    form_key = f"skill_assessment_form_{int(datetime.utcnow().timestamp())}"

    with st.form(key=form_key):
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

                # Get current value with safe default and proper type conversion
                try:
                    # Get the attribute value and safely convert to integer
                    current_value = getattr(player, metric, None)
                    current_value = to_int(current_value)  # Use our custom converter

                    # Use default of 3 if None
                    if current_value is None:
                        current_value = 3
                    else:
                        # Ensure value is in valid range 1-5
                        current_value = min(max(current_value, 1), 5)
                except Exception:
                    # Default to middle value if any error occurs
                    current_value = 3

                # Create a unique key for each slider to avoid state conflicts
                slider_key = f"rating_{metric}_1_{form_key}"

                all_ratings[metric] = st.slider(
                    f"{metric.replace('_', ' ').title()} Rating",
                    min_value=1,
                    max_value=5,  # Ensure max is always 5
                    value=current_value,
                    key=slider_key,
                    step=1,
                )

        # Second column
        with col2:
            for metric, description in metrics_list[mid_point:]:
                st.write(f"**{metric.replace('_', ' ').title()}**")
                st.write(f"_{description}_")

                # Get current value with safe default and proper type conversion
                try:
                    # Get the attribute value and safely convert to integer
                    current_value = getattr(player, metric, None)
                    current_value = to_int(current_value)  # Use our custom converter

                    # Use default of 3 if None
                    if current_value is None:
                        current_value = 3
                    else:
                        # Ensure value is in valid range 1-5
                        current_value = min(max(current_value, 1), 5)
                except Exception:
                    # Default to middle value if any error occurs
                    current_value = 3

                # Create a unique key for each slider
                slider_key = f"rating_{metric}_2_{form_key}"

                all_ratings[metric] = st.slider(
                    f"{metric.replace('_', ' ').title()} Rating",
                    min_value=1,
                    max_value=5,  # Ensure max is always 5
                    value=current_value,
                    key=slider_key,
                    step=1,
                )

        # Assessment notes
        st.write("### Assessment Notes")
        notes = st.text_area(
            "Observations and Development Goals",
            placeholder="Add specific observations, areas for improvement, and development goals",
        )

        # Submit button
        submitted = st.form_submit_button("Save Assessment")

        if submitted:
            if not notes:
                st.error("Please add assessment notes")
                return False

            try:
                # Make sure we're not in a failed transaction state
                db.session.rollback()

                # Update player metrics that exist in the Player model
                for metric, value in all_ratings.items():
                    # Ensure value is in the valid 1-5 range and is integer
                    validated_value = min(max(to_int(value) or 3, 1), 5)
                    if hasattr(player, metric):
                        setattr(player, metric, validated_value)

                # Filter metrics to only include those that exist in PlayerHistory model
                valid_metrics = {}
                player_history_columns = [
                    column.key for column in PlayerHistory.__table__.columns
                ]

                for metric, value in all_ratings.items():
                    if metric in player_history_columns:
                        # Ensure value is in the valid 1-5 range and is integer
                        valid_metrics[metric] = min(max(to_int(value) or 3, 1), 5)

                # Create historical record with notes field
                history = PlayerHistory(
                    player_id=player.id, date=datetime.utcnow().date(), notes=notes
                )

                # Set the valid metrics individually
                for metric, value in valid_metrics.items():
                    setattr(history, metric, value)

                db.session.add(history)
                db.session.commit()

                # Clear the form by rerunning
                st.success("Assessment saved successfully!")

                # Set a session state flag to indicate we should switch tabs
                st.session_state.assessment_saved = True

                # Return True to trigger tab switch in the parent function
                return True

            except Exception as e:
                st.error(f"Error saving assessment: {str(e)}")
                db.session.rollback()
                return False

    return False


def rate_skill(label, key, description="", default_value=3):
    """Create a standardized rating slider for skills"""
    st.write(f"_{description}_")
    # Ensure default_value is an integer
    try:
        default_value = to_int(default_value)
        if default_value is None or default_value < 1 or default_value > 5:
            default_value = 3
    except:
        default_value = 3

    return st.slider(
        label,
        min_value=1,
        max_value=5,  # Ensure all sliders are 1-5 scale
        value=default_value,
        key=key,
        step=1,
    )
