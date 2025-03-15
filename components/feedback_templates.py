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

        # Different categories based on player type
        if player_type == "Goalie":
            categories = {
                "save_technique_rating": st.checkbox("Save Technique"),
                "positioning_rating": st.checkbox("Positioning"),
                "rebound_control_rating": st.checkbox("Rebound Control"),
                "communication_rating": st.checkbox("Communication"),
                "mental_toughness_rating": st.checkbox("Mental Toughness")
            }
        else:
            categories = {
                "skating_rating": st.checkbox("Skating"),
                "shooting_rating": st.checkbox("Shooting"),
                "passing_rating": st.checkbox("Passing"),
                "teamwork_rating": st.checkbox("Teamwork"),
                "game_awareness_rating": st.checkbox("Game Awareness")
            }

        # Common categories for all players
        common_categories = {
            "effort_rating": st.checkbox("Effort"),
            "improvement_rating": st.checkbox("Areas for Improvement"),
            "strengths_rating": st.checkbox("Key Strengths")
        }

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