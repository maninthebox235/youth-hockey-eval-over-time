import streamlit as st
import pandas as pd
from database.models import db, CoachFeedback, FeedbackTemplate, Player
from datetime import datetime


def get_templates_for_player(player_type):
    """Get available templates for the player type"""
    try:
        return FeedbackTemplate.query.filter_by(player_type=player_type).all()
    except Exception as e:
        st.error(f"Error loading templates: {str(e)}")
        print(f"Template query error: {str(e)}")
        # Return empty list as fallback
        return []


def submit_coach_feedback(
    player_id, coach_name, feedback_text, ratings, template_id=None
):
    """Submit new coach feedback for a player"""
    try:
        # Use type converter utility for consistent handling
        from utils.type_converter import to_int

        # Convert player_id to Python int
        player_id = to_int(player_id)
        if player_id is None:
            raise ValueError("Invalid player ID: None after conversion")

        # Ensure template_id is a regular Python int if provided
        if template_id is not None:
            template_id = to_int(template_id)

        # Ensure all rating values are integers and filter out None values
        validated_ratings = {}
        for key, value in ratings.items():
            if key.endswith("_rating") and value is not None:
                try:
                    validated_ratings[key] = to_int(value)
                    if validated_ratings[key] is None:
                        print(f"Warning: Rating {key} converted to None, skipping")
                        continue
                except Exception as e:
                    print(f"Error converting rating {key}: {value} - {str(e)}")
                    continue

        # Create feedback entry
        feedback = CoachFeedback(
            player_id=player_id,
            coach_name=coach_name,
            feedback_text=feedback_text,
            **validated_ratings,
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
        # Use type converter utility for consistent handling
        from utils.type_converter import to_int

        # Convert player_id to Python int
        player_id = to_int(player_id)
        if player_id is None:
            raise ValueError("Invalid player ID: None after conversion")

        feedback = (
            CoachFeedback.query.filter_by(player_id=player_id)
            .order_by(CoachFeedback.date.desc())
            .all()
        )
        if not feedback:
            return pd.DataFrame()

        data = []
        for f in feedback:
            feedback_data = {
                "date": f.date.strftime("%Y-%m-%d %H:%M"),
                "coach": f.coach_name,
                "feedback": f.feedback_text,
            }

            # Add all ratings that exist for this feedback
            for column in CoachFeedback.__table__.columns:
                if column.name.endswith("_rating"):
                    value = getattr(f, column.name)
                    if value is not None:
                        try:
                            # Use type converter for consistent handling
                            converted_value = to_int(value)
                            if converted_value is not None:
                                feedback_data[column.name] = converted_value
                        except Exception as e:
                            print(f"Error converting {column.name}: {value} - {str(e)}")
                            continue

            data.append(feedback_data)

        return pd.DataFrame(data)
    except Exception as e:
        print(f"Error getting feedback: {e}")
        return pd.DataFrame()


def display_feedback_form(player_id, player_name, position):
    """Display feedback form for a player"""
    try:
        # Use type converter utility for consistent handling
        from utils.type_converter import to_int

        # Convert player_id to Python int
        player_id = to_int(player_id)
        if player_id is None:
            raise ValueError("Invalid player ID: None after conversion")
    except ValueError as e:
        st.error(f"Invalid player ID: {e}")
        return

    st.subheader("Submit Coach Feedback")

    # Get available templates for this player type
    player_type = "Goalie" if position == "Goalie" else "Skater"
    templates = get_templates_for_player(player_type)

    # Template selection
    selected_template = None
    template_id = None
    if templates:
        template_names = ["Custom Feedback"] + [t.name for t in templates]
        template_choice = st.selectbox("Select Template", template_names)

        if template_choice != "Custom Feedback":
            selected_template = next(t for t in templates if t.name == template_choice)
            template_id = selected_template.id

    with st.form("coach_feedback_form"):
        coach_name = st.text_input("Coach Name")
        feedback_text = st.text_area("Feedback Comments")

        # Initialize ratings dictionary
        ratings = {}

        st.subheader("Rating Categories")

        # Get template structure if template selected
        categories_to_rate = []
        if selected_template:
            categories_to_rate = selected_template.template_structure.get(
                "categories", []
            )

            # Display ratings for each category
            for category in categories_to_rate:
                category_label = (
                    category.replace("_rating", "").replace("_", " ").title()
                )
                ratings[category] = st.slider(
                    category_label,
                    min_value=1,
                    max_value=5,
                    value=3,
                    help=f"Rate {category_label.lower()} from 1-5",
                )

        if selected_template:
            # Use template structure to create rating sliders
            categories = selected_template.template_structure["categories"]

            # Create sliders in columns, 3 per row
            for i in range(0, len(categories), 3):
                cols = st.columns(3)
                for j, col in enumerate(cols):
                    if i + j < len(categories):
                        category = categories[i + j]
                        category_name = (
                            category.replace("_rating", "").replace("_", " ").title()
                        )
                        with col:
                            ratings[category] = st.slider(
                                category_name,
                                min_value=1,
                                max_value=5,  # Explicitly set max to 5
                                value=3,
                                step=1,
                            )
        else:
            # Default rating fields organized by skill category
            if position == "Goalie":
                # Add goalie-specific skill categories
                st.markdown("### Goaltending Skills")
                col1, col2, col3 = st.columns(3)
                with col1:
                    ratings["save_technique_rating"] = st.slider(
                        "Save Technique", min_value=1, max_value=5, value=3, step=1
                    )
                with col2:
                    ratings["positioning_rating"] = st.slider(
                        "Positioning", min_value=1, max_value=5, value=3, step=1
                    )
                with col3:
                    ratings["rebound_control_rating"] = st.slider(
                        "Rebound Control", min_value=1, max_value=5, value=3, step=1
                    )

                col1, col2, col3 = st.columns(3)
                with col1:
                    ratings["recovery_rating"] = st.slider("Recovery", 1, 5, 3)
                with col2:
                    ratings["puck_handling_rating"] = st.slider(
                        "Puck Handling", 1, 5, 3
                    )
                with col3:
                    ratings["communication_rating"] = st.slider(
                        "Communication", 1, 5, 3
                    )

                # Add skating skills section
                st.markdown("### Skating Skills")
                col1, col2 = st.columns(2)
                with col1:
                    ratings["skating_speed_rating"] = st.slider(
                        "Skating Speed", 1, 5, 3
                    )
                with col2:
                    ratings["agility_rating"] = st.slider("Agility", 1, 5, 3)

                # Add Hockey IQ section
                st.markdown("### Hockey IQ")
                col1, col2 = st.columns(2)
                with col1:
                    ratings["game_awareness_rating"] = st.slider(
                        "Game Awareness", 1, 5, 3
                    )
                with col2:
                    ratings["decision_making_rating"] = st.slider(
                        "Decision Making", 1, 5, 3
                    )
            else:
                # Add general ratings
                st.markdown("### Overall Skills")
                col1, col2, col3 = st.columns(3)
                with col1:
                    ratings["skating_rating"] = st.slider("Skating", 1, 5, 3)
                with col2:
                    ratings["shooting_rating"] = st.slider("Shooting", 1, 5, 3)
                with col3:
                    ratings["teamwork_rating"] = st.slider("Teamwork", 1, 5, 3)

                # Add skating skills section
                st.markdown("### Skating Skills")
                col1, col2, col3 = st.columns(3)
                with col1:
                    ratings["skating_speed_rating"] = st.slider(
                        "Skating Speed", 1, 5, 3
                    )
                with col2:
                    ratings["backward_skating_rating"] = st.slider(
                        "Backward Skating", 1, 5, 3
                    )
                with col3:
                    ratings["agility_rating"] = st.slider("Agility", 1, 5, 3)

                col1, col2 = st.columns(2)
                with col1:
                    ratings["edge_control_rating"] = st.slider("Edge Control", 1, 5, 3)

                # Add technical skills section
                st.markdown("### Technical Skills")
                col1, col2, col3 = st.columns(3)
                with col1:
                    ratings["puck_control_rating"] = st.slider("Puck Control", 1, 5, 3)
                with col2:
                    ratings["passing_accuracy_rating"] = st.slider(
                        "Passing Accuracy", 1, 5, 3
                    )
                with col3:
                    ratings["shooting_accuracy_rating"] = st.slider(
                        "Shooting Accuracy", 1, 5, 3
                    )

                col1, col2 = st.columns(2)
                with col1:
                    ratings["receiving_rating"] = st.slider("Receiving", 1, 5, 3)
                with col2:
                    ratings["stick_protection_rating"] = st.slider(
                        "Stick Protection", 1, 5, 3
                    )

                # Add Hockey IQ section
                st.markdown("### Hockey IQ")
                col1, col2, col3 = st.columns(3)
                with col1:
                    ratings["hockey_sense_rating"] = st.slider("Hockey Sense", 1, 5, 3)
                with col2:
                    ratings["decision_making_rating"] = st.slider(
                        "Decision Making", 1, 5, 3
                    )
                with col3:
                    ratings["game_awareness_rating"] = st.slider(
                        "Game Awareness", 1, 5, 3
                    )

                # Add Position specific skills section
                st.markdown("### Position-Specific Skills")
                col1, col2, col3 = st.columns(3)
                with col1:
                    ratings["compete_level_rating"] = st.slider(
                        "Compete Level", 1, 5, 3
                    )
                with col2:
                    ratings["offensive_ability_rating"] = st.slider(
                        "Offensive Ability", 1, 5, 3
                    )
                with col3:
                    ratings["defensive_ability_rating"] = st.slider(
                        "Defensive Ability", 1, 5, 3
                    )

                if position == "Forward":
                    col1, col2 = st.columns(2)
                    with col1:
                        ratings["net_front_rating"] = st.slider(
                            "Net Front Presence", 1, 5, 3
                        )

                if position == "Defense":
                    col1, col2 = st.columns(2)
                    with col1:
                        ratings["gap_control_rating"] = st.slider(
                            "Gap Control", 1, 5, 3
                        )

        submitted = st.form_submit_button("Submit Feedback")

        if submitted:
            if not coach_name or not feedback_text:
                st.error("Please fill in all required fields")
            else:
                success = submit_coach_feedback(
                    player_id=player_id,
                    coach_name=coach_name,
                    feedback_text=feedback_text,
                    ratings=ratings,
                    template_id=template_id,
                )
                if success:
                    st.success(f"Feedback submitted for {player_name}")
                    st.rerun()
                else:
                    st.error("Error submitting feedback. Please try again.")


def display_feedback_history(player_id):
    """Display the feedback history for a player"""
    try:
        # Use type converter utility for consistent handling
        from utils.type_converter import to_int

        # Convert player_id to Python int
        player_id = to_int(player_id)
        if player_id is None:
            raise ValueError("Invalid player ID: None after conversion")
    except ValueError as e:
        st.error(f"Invalid player ID: {e}")
        return

    feedback_df = get_player_feedback(player_id)

    if not feedback_df.empty:
        st.subheader("Previous Feedback")

        for _, row in feedback_df.iterrows():
            with st.expander(
                f"Feedback from {row['coach']} on {row['date']}", expanded=True
            ):
                st.write(row["feedback"])

                # Get all ratings and organize by category
                from utils.type_converter import to_int

                ratings = {
                    k: v
                    for k, v in row.items()
                    if k.endswith("_rating") and pd.notna(v)
                }

                # Organize ratings by category for better display
                if ratings:
                    # Define rating categories
                    skating_ratings = [
                        "skating_rating",
                        "skating_speed_rating",
                        "backward_skating_rating",
                        "agility_rating",
                        "edge_control_rating",
                    ]

                    technical_ratings = [
                        "puck_control_rating",
                        "passing_accuracy_rating",
                        "shooting_rating",
                        "shooting_accuracy_rating",
                        "receiving_rating",
                        "stick_protection_rating",
                    ]

                    hockey_iq_ratings = [
                        "hockey_sense_rating",
                        "decision_making_rating",
                        "game_awareness_rating",
                        "teamwork_rating",
                    ]

                    position_ratings = [
                        "compete_level_rating",
                        "offensive_ability_rating",
                        "defensive_ability_rating",
                        "net_front_rating",
                        "gap_control_rating",
                    ]

                    goalie_ratings = [
                        "save_technique_rating",
                        "positioning_rating",
                        "rebound_control_rating",
                        "recovery_rating",
                        "puck_handling_rating",
                        "communication_rating",
                    ]

                    # Function to display a category of ratings
                    def display_rating_category(category_name, rating_keys):
                        category_ratings = {
                            k: v for k, v in ratings.items() if k in rating_keys
                        }
                        if category_ratings:
                            st.markdown(f"**{category_name}**")
                            cols = st.columns(3)
                            for i, (metric, value) in enumerate(
                                category_ratings.items()
                            ):
                                with cols[i % 3]:
                                    metric_name = (
                                        metric.replace("_rating", "")
                                        .replace("_", " ")
                                        .title()
                                    )
                                    st.metric(metric_name, to_int(value) or 0)

                    # Display ratings by category
                    display_rating_category(
                        "Overall Skills",
                        ["skating_rating", "shooting_rating", "teamwork_rating"],
                    )
                    display_rating_category("Skating Skills", skating_ratings)
                    display_rating_category("Technical Skills", technical_ratings)
                    display_rating_category("Hockey IQ", hockey_iq_ratings)
                    display_rating_category(
                        "Position-Specific Skills", position_ratings
                    )
                    display_rating_category("Goaltending Skills", goalie_ratings)
                else:
                    st.info("No ratings provided with this feedback.")
    else:
        st.info("No feedback available yet.")
