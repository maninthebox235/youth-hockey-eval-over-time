import streamlit as st
import json
from database.models import db, FeedbackTemplate
from datetime import datetime

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

        # Default categories based on player type
        if player_type == "Goalie":
            default_categories = {
                "save_technique_rating": "Save Technique",
                "positioning_rating": "Positioning",
                "rebound_control_rating": "Rebound Control",
                "communication_rating": "Communication",
                "mental_toughness_rating": "Mental Toughness"
            }
        else:
            default_categories = {
                "skating_rating": "Skating",
                "shooting_rating": "Shooting",
                "passing_rating": "Passing",
                "teamwork_rating": "Teamwork",
                "game_awareness_rating": "Game Awareness"
            }

        # Common categories
        common_categories = {
            "effort_rating": "Effort",
            "improvement_rating": "Areas for Improvement",
            "strengths_rating": "Key Strengths"
        }

        # Create checkboxes for default categories
        categories = {}
        st.subheader("Default Categories")
        for key, label in default_categories.items():
            categories[key] = st.checkbox(label, key=f"default_{key}")

        st.subheader("Common Categories")
        for key, label in common_categories.items():
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
            # Combine selected categories
            selected_categories = {k: v for k, v in {**categories, **common_categories}.items() if v}

            if not selected_categories:
                st.error("Please select at least one category")
                return False

            template_structure = {
                "categories": list(selected_categories.keys()),
                "player_type": player_type
            }

            try:
                template = FeedbackTemplate(
                    name=name,
                    description=description,
                    player_type=player_type,
                    template_structure=template_structure
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
    templates = FeedbackTemplate.query.order_by(FeedbackTemplate.created_date.desc()).all()

    if not templates:
        st.info("No feedback templates available. Create one to get started!")
        return

    st.subheader("Available Templates")

    for template in templates:
        with st.expander(f"{template.name} ({template.player_type})", expanded=False):
            st.write(f"**Description:** {template.description or 'No description provided'}")
            st.write("**Categories:**")
            for category in template.template_structure['categories']:
                st.write(f"- {category.replace('_rating', '').replace('_', ' ').title()}")

            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                st.metric("Times Used", template.times_used or 0)
            with col2:
                last_used = template.last_used.strftime("%Y-%m-%d") if template.last_used else "Never"
                st.metric("Last Used", last_used)
            with col3:
                if st.button("Delete Template", key=f"delete_{template.id}"):
                    if delete_template(template.id):
                        st.success(f"Template '{template.name}' deleted successfully!")
                        st.rerun()
                    else:
                        st.error("Error deleting template")

def manage_feedback_templates():
    """Main interface for managing feedback templates"""
    st.title("Feedback Templates")

    tab1, tab2 = st.tabs(["Available Templates", "Create Template"])

    with tab1:
        display_templates()

    with tab2:
        create_template_form()