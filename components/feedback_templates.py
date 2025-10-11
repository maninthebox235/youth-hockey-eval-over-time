import streamlit as st
from database.models import db, FeedbackTemplate


def delete_template(template_id):
    """Delete a feedback template"""
    try:
        template = FeedbackTemplate.query.get(template_id)
        if template:
            db.session.delete(template)
            db.session.commit()
            return True
    except Exception as e:
        print(f"Error deleting template: {e}")
        db.session.rollback()
        return False
    return False


def create_template_form():
    """Display form for creating a new feedback template"""
    st.subheader("Create Feedback Template")

    with st.form("create_template_form"):
        name = st.text_input("Template Name")
        description = st.text_area("Template Description")
        player_type = st.selectbox("Player Type", ["Skater", "Goalie"])

        st.subheader("Rating Categories")

        # Define category groups for better organization
        skating_categories = {
            "skating_speed_rating": "Skating Speed",
            "backward_skating_rating": "Backward Skating",
            "agility_rating": "Agility",
            "edge_control_rating": "Edge Control",
        }

        technical_categories = {
            "puck_control_rating": "Puck Control",
            "passing_accuracy_rating": "Passing Accuracy",
            "shooting_accuracy_rating": "Shooting Accuracy",
            "receiving_rating": "Receiving",
            "stick_protection_rating": "Stick Protection",
        }

        hockey_iq_categories = {
            "hockey_sense_rating": "Hockey Sense",
            "decision_making_rating": "Decision Making",
            "game_awareness_rating": "Game Awareness",
            "teamwork_rating": "Teamwork",
        }

        # Position-specific categories
        position_categories = {
            "compete_level_rating": "Compete Level",
            "offensive_ability_rating": "Offensive Ability",
            "defensive_ability_rating": "Defensive Ability",
            "net_front_rating": "Net Front Presence",
            "gap_control_rating": "Gap Control",
        }

        # Goalie-specific categories
        goalie_categories = {
            "save_technique_rating": "Save Technique",
            "positioning_rating": "Positioning",
            "rebound_control_rating": "Rebound Control",
            "recovery_rating": "Recovery",
            "puck_handling_rating": "Puck Handling",
            "communication_rating": "Communication",
        }

        # General categories
        general_categories = {
            "skating_rating": "Overall Skating",
            "shooting_rating": "Overall Shooting",
            "teamwork_rating": "Overall Teamwork",
        }

        # Common categories that apply to all players
        common_categories = {
            "effort_rating": "Effort",
            "improvement_rating": "Areas for Improvement",
            "strengths_rating": "Key Strengths",
        }

        # Initialize the categories dictionary
        categories = {}

        # Determine which categories to show based on player type
        if player_type == "Goalie":
            # For goalies, show goalie-specific categories and other relevant ones
            st.subheader("Goaltending Skills")
            cols = st.columns(3)
            items = list(goalie_categories.items())
            for i, (key, label) in enumerate(items):
                with cols[i % 3]:
                    categories[key] = st.checkbox(label, key=f"goalie_{key}")

            # Goalies still need some skating and hockey IQ skills
            st.subheader("Skating Skills")
            cols = st.columns(3)
            goalie_skating_keys = ["skating_speed_rating", "agility_rating"]
            for i, key in enumerate(goalie_skating_keys):
                with cols[i % 3]:
                    categories[key] = st.checkbox(
                        skating_categories[key], key=f"skating_{key}"
                    )

            st.subheader("Hockey IQ")
            cols = st.columns(3)
            goalie_iq_keys = ["decision_making_rating", "game_awareness_rating"]
            for i, key in enumerate(goalie_iq_keys):
                with cols[i % 3]:
                    categories[key] = st.checkbox(
                        hockey_iq_categories[key], key=f"iq_{key}"
                    )
        else:
            # For skaters, show all skill categories organized by group
            st.subheader("General Skills")
            cols = st.columns(3)
            for i, (key, label) in enumerate(general_categories.items()):
                with cols[i % 3]:
                    categories[key] = st.checkbox(label, key=f"general_{key}")

            st.subheader("Skating Skills")
            cols = st.columns(3)
            items = list(skating_categories.items())
            for i, (key, label) in enumerate(items):
                with cols[i % 3]:
                    categories[key] = st.checkbox(label, key=f"skating_{key}")

            st.subheader("Technical Skills")
            cols = st.columns(3)
            items = list(technical_categories.items())
            for i, (key, label) in enumerate(items):
                with cols[i % 3]:
                    categories[key] = st.checkbox(label, key=f"technical_{key}")

            st.subheader("Hockey IQ")
            cols = st.columns(3)
            items = list(hockey_iq_categories.items())
            for i, (key, label) in enumerate(items):
                with cols[i % 3]:
                    categories[key] = st.checkbox(label, key=f"iq_{key}")

            st.subheader("Position-Specific Skills")
            cols = st.columns(3)
            items = list(position_categories.items())
            for i, (key, label) in enumerate(items):
                # Show net_front only for forwards and gap_control only for defense
                show_item = True
                if key == "net_front_rating":
                    show_item = st.checkbox(
                        "Include Forward-specific skills",
                        value=True,
                        key="show_forward_skills",
                    )
                elif key == "gap_control_rating":
                    show_item = st.checkbox(
                        "Include Defense-specific skills",
                        value=True,
                        key="show_defense_skills",
                    )

                if show_item:
                    with cols[i % 3]:
                        categories[key] = st.checkbox(label, key=f"position_{key}")

        st.subheader("Common Categories")
        cols = st.columns(3)
        for i, (key, label) in enumerate(common_categories.items()):
            with cols[i % 3]:
                categories[key] = st.checkbox(label, key=f"common_{key}")

        # Custom categories
        st.subheader("Add Custom Categories")
        custom_categories = []

        col1, col2 = st.columns([3, 1])
        with col1:
            new_category = st.text_input("New Category Name", key="new_category")
        with col2:
            if st.button("Add Category", key="add_category") and new_category:
                custom_categories.append(new_category)
                st.session_state.custom_categories = custom_categories

        # Display and select custom categories
        if "custom_categories" in st.session_state:
            for category in st.session_state.custom_categories:
                category_key = f"{category.lower().replace(' ', '_')}_rating"
                categories[category_key] = st.checkbox(category)

        submitted = st.form_submit_button("Create Template")

        if submitted and name:
            # Combine selected categories - only include checkboxes that were checked (value is True)
            selected_categories = {k: v for k, v in categories.items() if v}

            if not selected_categories:
                st.error("Please select at least one category")
                return False

            template_structure = {
                "categories": list(selected_categories.keys()),
                "player_type": player_type,
            }

            try:
                template = FeedbackTemplate(
                    name=name,
                    description=description,
                    player_type=player_type,
                    template_structure=template_structure,
                )
                db.session.add(template)
                db.session.commit()
                st.success(f"Template '{name}' created successfully!")
                return True
            except Exception as e:
                st.error(f"Error creating template: {str(e)}")
                return False
    return False


def display_templates():
    """Display list of available feedback templates"""
    try:
        templates = FeedbackTemplate.query.order_by(
            FeedbackTemplate.created_date.desc()
        ).all()

        if not templates:
            st.info("No feedback templates available. Create one to get started!")
            return
    except Exception as e:
        st.error(f"Error loading templates: {str(e)}")
        print(f"Template display error: {str(e)}")
        return

    st.subheader("Available Templates")

    for template in templates:
        with st.expander(f"{template.name} ({template.player_type})", expanded=False):
            st.write(
                f"**Description:** {template.description or 'No description provided'}"
            )

            # Group template categories by skill type for better readability
            categories = template.template_structure.get("categories", [])

            # Define category groups
            skating_categories = [
                c
                for c in categories
                if c.startswith("skating")
                or c
                in ["backward_skating_rating", "agility_rating", "edge_control_rating"]
            ]

            technical_categories = [
                c
                for c in categories
                if c
                in [
                    "puck_control_rating",
                    "passing_accuracy_rating",
                    "shooting_accuracy_rating",
                    "receiving_rating",
                    "stick_protection_rating",
                ]
            ]

            hockey_iq_categories = [
                c
                for c in categories
                if c
                in [
                    "hockey_sense_rating",
                    "decision_making_rating",
                    "game_awareness_rating",
                    "teamwork_rating",
                ]
            ]

            position_categories = [
                c
                for c in categories
                if c
                in [
                    "compete_level_rating",
                    "offensive_ability_rating",
                    "defensive_ability_rating",
                    "net_front_rating",
                    "gap_control_rating",
                ]
            ]

            goalie_categories = [
                c
                for c in categories
                if c
                in [
                    "save_technique_rating",
                    "positioning_rating",
                    "rebound_control_rating",
                    "recovery_rating",
                    "puck_handling_rating",
                    "communication_rating",
                ]
            ]

            common_categories = [
                c
                for c in categories
                if c in ["effort_rating", "improvement_rating", "strengths_rating"]
            ]

            # Find categories that don't fit in any group
            other_categories = [
                c
                for c in categories
                if c
                not in skating_categories
                + technical_categories
                + hockey_iq_categories
                + position_categories
                + goalie_categories
                + common_categories
            ]

            # Display categories by group
            def display_category_group(title, category_list):
                if category_list:
                    st.write(f"**{title}:**")
                    for category in category_list:
                        st.write(
                            f"- {category.replace('_rating', '').replace('_', ' ').title()}"
                        )

            if skating_categories:
                display_category_group("Skating Skills", skating_categories)

            if technical_categories:
                display_category_group("Technical Skills", technical_categories)

            if hockey_iq_categories:
                display_category_group("Hockey IQ", hockey_iq_categories)

            if position_categories:
                display_category_group("Position-Specific Skills", position_categories)

            if goalie_categories:
                display_category_group("Goaltending Skills", goalie_categories)

            if common_categories:
                display_category_group("Common Skills", common_categories)

            if other_categories:
                display_category_group("Other Skills", other_categories)

            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                st.metric("Times Used", template.times_used or 0)
            with col2:
                last_used = (
                    template.last_used.strftime("%Y-%m-%d")
                    if template.last_used
                    else "Never"
                )
                st.metric("Last Used", last_used)
            with col3:
                if st.button("Delete Template", key=f"delete_{template.id}"):
                    if delete_template(template.id):
                        st.success(f"Template '{template.name}' deleted successfully!")
                        st.rerun()
                    else:
                        st.error("Error deleting template")


def manage_feedback_templates():
    """Interface for managing feedback templates"""
    st.subheader("Feedback Templates")

    # Create tabs for template management
    template_tabs = st.tabs(["Create Template", "View/Edit Templates"])

    with template_tabs[0]:
        with st.form("new_template_form"):
            template_name = st.text_input("Template Name", key="new_template_name")
            template_description = st.text_area("Description", key="new_template_desc")
            player_type = st.selectbox(
                "Player Type", ["Skater", "Goalie"], key="new_template_type"
            )

            # Template content
            st.subheader("Template Content")
            st.markdown("Use `{player_name}` as a placeholder for the player's name.")
            template_content = st.text_area(
                "Feedback Text", height=200, key="new_template_content"
            )

            # Submit button
            submit = st.form_submit_button("Create Template")

        # Move the logic outside the form
        if submit:
            if not template_name or not template_content:
                st.error("Template name and content are required.")
            else:
                try:
                    # Create template
                    new_template = FeedbackTemplate(
                        name=template_name,
                        description=template_description,
                        player_type=player_type,
                        template_structure={"content": template_content},
                    )
                    db.session.add(new_template)
                    db.session.commit()
                    st.success(f"Template '{template_name}' created successfully!")
                except Exception as e:
                    st.error(f"Error creating template: {str(e)}")
                    db.session_rollback()

    with template_tabs[1]:
        templates = FeedbackTemplate.query.all()

        if not templates:
            st.info("No templates found. Create one using the 'Create Template' tab.")
        else:
            # Create a selectbox for template selection
            template_names = [f"{t.name} ({t.player_type})" for t in templates]
            selected_template_idx = st.selectbox(
                "Select Template",
                range(len(templates)),
                format_func=lambda x: template_names[x],
            )

            selected_template = templates[selected_template_idx]

            # Display template details
            st.markdown(f"### {selected_template.name}")
            st.markdown(
                f"**Description:** {selected_template.description or 'No description'}"
            )
            st.markdown(f"**Player Type:** {selected_template.player_type}")
            st.markdown(
                f"**Created:** {selected_template.created_date.strftime('%Y-%m-%d')}"
            )
            st.markdown(f"**Times Used:** {selected_template.times_used}")

            # Edit form
            with st.form("edit_template_form"):
                edit_content = st.text_area(
                    "Template Content",
                    value=selected_template.template_structure.get("content", ""),
                    height=200,
                )

                update = st.form_submit_button("Update Template")

            # Delete functionality outside of form
            if st.button(
                "Delete Template", type="primary", help="This action cannot be undone"
            ):
                if "confirm_delete" not in st.session_state:
                    st.session_state.confirm_delete = False

                st.session_state.confirm_delete = True
                st.warning("Are you sure you want to delete this template?")

            if st.session_state.get("confirm_delete", False):
                if st.button("Confirm Delete", help="Click to confirm deletion"):
                    db.session.delete(selected_template)
                    db.session.commit()
                    st.success("Template deleted successfully!")
                    st.session_state.confirm_delete = False
                    st.rerun()

                if st.button("Cancel"):
                    st.session_state.confirm_delete = False
                    st.rerun()

            # Update functionality outside of form
            if update:
                selected_template.template_structure["content"] = edit_content
                db.session.commit()
                st.success("Template updated successfully!")
