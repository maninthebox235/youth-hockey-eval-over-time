import streamlit as st
import pandas as pd
from database.models import db, GameEvaluation, Team
from datetime import datetime, date
from utils.type_converter import to_int, to_float
import plotly.graph_objects as go


def display_game_evaluation_form(team_id):
    st.subheader("📹 New Game Evaluation")

    team = Team.query.get(team_id)
    if not team:
        st.error("Team not found")
        return

    st.write(f"**Team:** {team.name} ({team.age_group})")

    with st.expander("📊 Understanding the Rating Scale", expanded=False):
        st.markdown(
            """
        **10U Team Tactical Rating Scale (1-5)**
        
        - **1 - Needs Significant Work**: Concept not yet understood or executed
        - **2 - Developing**: Some understanding, inconsistent execution
        - **3 - Meeting Expectations**: Age-appropriate execution most of the time
        - **4 - Above Expectations**: Consistent execution with good decision-making
        - **5 - Excellent**: Advanced execution for age level, ready for next level
        
        **Key Team Tactics for 10U:**
        - **Spacing/Support**: Maintaining proper positioning to support teammates
        - **Forechecking**: Applying pressure when opponent has the puck
        - **Backchecking**: Quick transition back to defense
        - **Breakouts**: Moving the puck from defense to offense effectively
        """
        )

    with st.form("game_evaluation_form"):
        st.markdown("### 🏒 Game Information")
        col1, col2 = st.columns(2)

        with col1:
            game_date = st.date_input(
                "Game Date", value=date.today(), max_value=date.today()
            )
            opponent_name = st.text_input(
                "Opponent Team Name", placeholder="Enter opponent team name"
            )

        with col2:
            final_score = st.text_input(
                "Final Score (optional)",
                placeholder="e.g., W 4-2 or L 1-3",
                help="Include W/L and score if desired",
            )
            game_location = st.text_input(
                "Game Location (optional)", placeholder="Home, Away, or rink name"
            )

        st.markdown("### 🎥 Game Video")
        uploaded_file = st.file_uploader(
            "Upload Game Video (optional)",
            type=["mp4", "mov", "avi", "mkv"],
            help="Upload game footage for reference",
        )

        st.markdown("### 📋 Team Tactical Evaluation")
        st.write("Rate the team's performance in these key areas:")

        col1, col2 = st.columns(2)

        with col1:
            spacing_support_rating = st.select_slider(
                "Spacing & Support",
                options=[1, 2, 3, 4, 5],
                value=3,
                help="How well did players maintain positioning to support teammates?",
            )

            forechecking_rating = st.select_slider(
                "Forechecking",
                options=[1, 2, 3, 4, 5],
                value=3,
                help="How effective was the team at applying pressure on opponents?",
            )

        with col2:
            backchecking_rating = st.select_slider(
                "Backchecking",
                options=[1, 2, 3, 4, 5],
                value=3,
                help="How quickly did players transition back to defense?",
            )

            breakout_rating = st.select_slider(
                "Breakouts",
                options=[1, 2, 3, 4, 5],
                value=3,
                help="How well did the team execute breakouts from the defensive zone?",
            )

        st.markdown("### ⭐ Overall Team Performance")

        col1, col2 = st.columns(2)

        with col1:
            overall_effort_rating = st.select_slider(
                "Team Effort",
                options=[1, 2, 3, 4, 5],
                value=3,
                help="Overall team hustle and determination",
            )

        with col2:
            overall_execution_rating = st.select_slider(
                "Execution",
                options=[1, 2, 3, 4, 5],
                value=3,
                help="Overall skill execution and performance",
            )

        st.markdown("### 📝 Coaching Notes")

        strengths_notes = st.text_area(
            "Team Strengths Observed",
            placeholder="What did the team do well? (e.g., strong puck support, good communication, effective forecheck...)",
            height=100,
        )

        areas_for_improvement = st.text_area(
            "Areas for Improvement",
            placeholder="What should the team focus on in practice? (e.g., improving breakout timing, maintaining defensive gaps...)",
            height=100,
        )

        coaching_observations = st.text_area(
            "Additional Coaching Observations",
            placeholder="Any other notes, player highlights, or tactical observations...",
            height=100,
        )

        submitted = st.form_submit_button(
            "💾 Save Game Evaluation", use_container_width=True
        )

        if submitted:
            if not opponent_name:
                st.error("Please enter the opponent team name")
                return

            try:
                user_id = (
                    st.session_state.user["id"] if "user" in st.session_state else 1
                )
                evaluator_name = (
                    st.session_state.user["name"]
                    if "user" in st.session_state
                    else "Coach"
                )

                video_filename = None
                if uploaded_file is not None:
                    video_filename = uploaded_file.name

                evaluation = GameEvaluation(
                    team_id=to_int(team_id),
                    user_id=to_int(user_id),
                    evaluator_name=evaluator_name,
                    game_date=game_date,
                    opponent_name=opponent_name,
                    final_score=final_score if final_score else None,
                    game_location=game_location if game_location else None,
                    video_filename=video_filename,
                    spacing_support_rating=to_int(spacing_support_rating),
                    forechecking_rating=to_int(forechecking_rating),
                    backchecking_rating=to_int(backchecking_rating),
                    breakout_rating=to_int(breakout_rating),
                    overall_team_effort_rating=to_int(overall_effort_rating),
                    overall_execution_rating=to_int(overall_execution_rating),
                    strengths_notes=strengths_notes if strengths_notes else None,
                    areas_for_improvement=(
                        areas_for_improvement if areas_for_improvement else None
                    ),
                    coaching_observations=(
                        coaching_observations if coaching_observations else None
                    ),
                )

                db.session.add(evaluation)
                db.session.commit()

                st.success(
                    f"✅ Game evaluation saved successfully! ({opponent_name} on {game_date})"
                )
                st.rerun()

            except Exception as e:
                db.session.rollback()
                st.error(f"Error saving evaluation: {str(e)}")


def display_evaluation_history(team_id):
    st.subheader("📊 Evaluation History")

    team = Team.query.get(team_id)
    if not team:
        st.error("Team not found")
        return

    user_id = st.session_state.user["id"] if "user" in st.session_state else None

    try:
        if user_id:
            evaluations = (
                GameEvaluation.query.filter_by(team_id=team_id, user_id=user_id)
                .order_by(GameEvaluation.game_date.desc())
                .all()
            )
        else:
            evaluations = (
                GameEvaluation.query.filter_by(team_id=team_id)
                .order_by(GameEvaluation.game_date.desc())
                .all()
            )

        if not evaluations:
            st.info(
                "No game evaluations yet. Create your first evaluation using the 'New Evaluation' tab!"
            )
            return

        st.write(f"**Total Evaluations:** {len(evaluations)}")

        for eval in evaluations:
            with st.expander(
                f"🏒 vs {eval.opponent_name} - {eval.game_date.strftime('%B %d, %Y')} "
                f"({eval.final_score if eval.final_score else 'Score not recorded'})",
                expanded=False,
            ):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(f"**Date:** {eval.game_date.strftime('%m/%d/%Y')}")
                    st.write(f"**Opponent:** {eval.opponent_name}")
                with col2:
                    st.write(f"**Score:** {eval.final_score or 'Not recorded'}")
                    st.write(f"**Location:** {eval.game_location or 'Not recorded'}")
                with col3:
                    st.write(f"**Evaluator:** {eval.evaluator_name}")
                    st.write(
                        f"**Video:** {'✅ Yes' if eval.video_filename else '❌ No'}"
                    )

                st.markdown("---")

                st.markdown("**Team Tactical Ratings**")

                ratings_data = {
                    "Spacing/Support": eval.spacing_support_rating or 0,
                    "Forechecking": eval.forechecking_rating or 0,
                    "Backchecking": eval.backchecking_rating or 0,
                    "Breakouts": eval.breakout_rating or 0,
                    "Team Effort": eval.overall_team_effort_rating or 0,
                    "Execution": eval.overall_execution_rating or 0,
                }

                fig = go.Figure(
                    data=[
                        go.Bar(
                            x=list(ratings_data.keys()),
                            y=list(ratings_data.values()),
                            marker_color=[
                                "#1f77b4",
                                "#ff7f0e",
                                "#2ca02c",
                                "#d62728",
                                "#9467bd",
                                "#8c564b",
                            ],
                            text=list(ratings_data.values()),
                            textposition="auto",
                        )
                    ]
                )

                fig.update_layout(
                    yaxis=dict(range=[0, 5], title="Rating"),
                    xaxis=dict(title="Category"),
                    height=300,
                    showlegend=False,
                )

                st.plotly_chart(fig, use_container_width=True)

                if eval.strengths_notes:
                    st.markdown("**✅ Team Strengths:**")
                    st.info(eval.strengths_notes)

                if eval.areas_for_improvement:
                    st.markdown("**🎯 Areas for Improvement:**")
                    st.warning(eval.areas_for_improvement)

                if eval.coaching_observations:
                    st.markdown("**📝 Coaching Observations:**")
                    st.write(eval.coaching_observations)

    except Exception as e:
        st.error(f"Error loading evaluations: {str(e)}")


def display_game_evaluation_interface(team_id):
    st.title("🏒 Game Evaluation - Post-Game Analysis")

    team = Team.query.get(team_id)
    if not team:
        st.error("Team not found")
        return

    st.write(f"Evaluating games for: **{team.name} ({team.age_group})**")
    st.write("Analyze team performance in key tactical areas based on game video.")

    tabs = st.tabs(["📝 New Evaluation", "📊 View History"])

    with tabs[0]:
        display_game_evaluation_form(team_id)

    with tabs[1]:
        display_evaluation_history(team_id)
