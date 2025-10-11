import io
import base64
import os
import streamlit as st
from datetime import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
)
from reportlab.lib.units import inch
from reportlab.graphics.shapes import Drawing
from utils.data_generator import get_player_history
from database.models import Player, PlayerHistory, FeedbackTemplate, CoachFeedback
import plotly.graph_objects as go
from utils.type_converter import to_int, to_float, to_datetime, to_date


class PDFReportGenerator:
    """Generate PDF reports for player assessments"""

    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.custom_styles = {
            "Title": ParagraphStyle(
                "CustomTitle", parent=self.styles["Title"], fontSize=16, spaceAfter=12
            ),
            "Heading1": ParagraphStyle(
                "CustomHeading1",
                parent=self.styles["Heading1"],
                fontSize=14,
                spaceBefore=10,
                spaceAfter=8,
            ),
            "Heading2": ParagraphStyle(
                "CustomHeading2",
                parent=self.styles["Heading2"],
                fontSize=12,
                spaceBefore=8,
                spaceAfter=6,
            ),
            "BodyText": ParagraphStyle(
                "CustomBodyText",
                parent=self.styles["BodyText"],
                fontSize=10,
                spaceBefore=4,
                spaceAfter=4,
            ),
            "Note": ParagraphStyle(
                "Note",
                parent=self.styles["BodyText"],
                fontSize=9,
                textColor=colors.darkblue,
                spaceBefore=2,
                spaceAfter=2,
            ),
        }

    def generate_player_report(self, player_id):
        """Generate a complete player assessment report"""
        # Convert player_id to Python int using our utility function
        player_id = to_int(player_id)
        if player_id is None:
            return None

        player = Player.query.get(player_id)
        if not player:
            return None

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72,
        )

        # Build the report content
        report_elements = []

        # Title and Player Information
        report_elements.append(
            Paragraph(f"Player Assessment Report", self.custom_styles["Title"])
        )
        report_elements.append(Spacer(1, 0.1 * inch))
        report_elements.append(
            Paragraph(f"Player: {player.name}", self.custom_styles["Heading1"])
        )

        # Basic Info Table
        player_data = [
            ["Age:", f"{player.age} years"],
            ["Position:", player.position],
            ["Age Group:", player.age_group],
            ["Date Generated:", datetime.now().strftime("%Y-%m-%d")],
        ]

        info_table = Table(player_data, colWidths=[1.5 * inch, 3 * inch])
        info_table.setStyle(
            TableStyle(
                [
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("PADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )
        report_elements.append(info_table)
        report_elements.append(Spacer(1, 0.2 * inch))

        # Skill Assessment Section
        report_elements.append(
            Paragraph("Skill Assessment", self.custom_styles["Heading1"])
        )
        report_elements.append(Spacer(1, 0.1 * inch))

        # Get skill metrics based on position
        skill_sections = self._get_skill_sections(player)

        for section_name, metrics in skill_sections.items():
            report_elements.append(
                Paragraph(section_name, self.custom_styles["Heading2"])
            )

            # Create a table for each skill section
            # Check if this is a stats section
            is_stats_section = section_name.lower() == "stats"
            header_cols = [
                "Skill",
                "Value" if is_stats_section else "Rating",
                "Description",
            ]
            skill_data = [header_cols]

            for metric_name, metric_value in metrics.items():
                if metric_value is not None:
                    # Format value based on if it's a stat or rating
                    if is_stats_section and isinstance(metric_value, (int, float)):
                        value_text = str(int(metric_value))
                    else:
                        value_text = (
                            f"{metric_value:.1f}"
                            if isinstance(metric_value, (int, float))
                            else str(metric_value)
                        )

                    skill_data.append(
                        [
                            metric_name.replace("_", " ").title(),
                            value_text,
                            self._get_rating_description(metric_name, metric_value),
                        ]
                    )

            if len(skill_data) > 1:  # Only add table if there are skills
                skill_table = Table(
                    skill_data, colWidths=[1.5 * inch, 0.8 * inch, 3 * inch]
                )
                skill_table.setStyle(
                    TableStyle(
                        [
                            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                            ("PADDING", (0, 0), (-1, -1), 6),
                        ]
                    )
                )
                report_elements.append(skill_table)
                report_elements.append(Spacer(1, 0.1 * inch))

        # Add Coach Feedback
        feedback_list = (
            CoachFeedback.query.filter_by(player_id=player_id)
            .order_by(CoachFeedback.date.desc())
            .limit(3)
            .all()
        )
        if feedback_list:
            report_elements.append(
                Paragraph("Recent Coach Feedback", self.custom_styles["Heading1"])
            )
            report_elements.append(Spacer(1, 0.1 * inch))

            for i, feedback in enumerate(feedback_list):
                report_elements.append(
                    Paragraph(
                        f"Feedback from {feedback.coach_name} - {feedback.date.strftime('%Y-%m-%d')}",
                        self.custom_styles["Heading2"],
                    )
                )
                report_elements.append(
                    Paragraph(feedback.feedback_text, self.custom_styles["BodyText"])
                )

                # Only add spacer if not the last feedback
                if i < len(feedback_list) - 1:
                    report_elements.append(Spacer(1, 0.1 * inch))

        # Add Development Progress
        history = (
            PlayerHistory.query.filter_by(player_id=player_id)
            .order_by(PlayerHistory.date)
            .all()
        )
        if history and len(history) > 1:
            report_elements.append(
                Paragraph("Development Progress", self.custom_styles["Heading1"])
            )
            report_elements.append(Spacer(1, 0.1 * inch))

            # Get key metrics to track over time based on position
            key_metrics = self._get_key_metrics_for_position(player.position)
            progress_data = [
                ["Date"] + [m.replace("_", " ").title() for m in key_metrics]
            ]

            for h in history[-6:]:  # Show last 6 assessments
                row = [h.date.strftime("%Y-%m-%d")]
                for metric in key_metrics:
                    value = getattr(h, metric, None)
                    row.append(f"{value:.1f}" if value is not None else "N/A")
                progress_data.append(row)

            progress_table = Table(progress_data)
            progress_table.setStyle(
                TableStyle(
                    [
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                        ("PADDING", (0, 0), (-1, -1), 6),
                    ]
                )
            )
            report_elements.append(progress_table)

        # Notes section for additional comments
        report_elements.append(Spacer(1, 0.3 * inch))
        report_elements.append(Paragraph("Notes:", self.custom_styles["Heading2"]))
        report_elements.append(Spacer(1, 1 * inch))  # Space for handwritten notes

        # Footer with disclaimer
        report_elements.append(
            Paragraph(
                "This report is generated by the Youth Hockey Development Tracker system. "
                "Assessment values are on a scale of 1-5, where 1 represents 'Needs Improvement' "
                "and 5 represents 'Exceeding Expectations' for the player's age group.",
                self.custom_styles["Note"],
            )
        )

        # Build the PDF document
        doc.build(report_elements)
        pdf_data = buffer.getvalue()
        buffer.close()

        return pdf_data

    def _get_skill_sections(self, player):
        """Get skill sections and metrics based on player position"""
        # Common skills for all positions
        skill_sections = {
            "Skating": {
                "skating_speed": getattr(player, "skating_speed", None),
                "edge_control": getattr(player, "edge_control", None),
                "agility": getattr(player, "agility", None),
                "backward_skating": getattr(player, "backward_skating", None),
            },
            "Puck Skills": {
                "puck_control": getattr(player, "puck_control", None),
                "passing_accuracy": getattr(player, "passing_accuracy", None),
                "receiving": getattr(player, "receiving", None),
                "stick_protection": getattr(player, "stick_protection", None),
            },
            "Game Intelligence": {
                "decision_making": getattr(player, "decision_making", None),
                "game_awareness": getattr(player, "game_awareness", None),
                "hockey_sense": getattr(player, "hockey_sense", None),
            },
        }

        # Position-specific skills
        if player.position.lower() in [
            "forward",
            "center",
            "wing",
            "left wing",
            "right wing",
        ]:
            skill_sections["Shooting"] = {
                "wrist_shot": getattr(player, "wrist_shot", None),
                "slap_shot": getattr(player, "slap_shot", None),
                "one_timer": getattr(player, "one_timer", None),
                "shot_accuracy": getattr(player, "shot_accuracy", None),
            }
            skill_sections["Stats"] = {
                "games_played": getattr(player, "games_played", None),
                "goals": getattr(player, "goals", None),
                "assists": getattr(player, "assists", None),
            }

        elif player.position.lower() in ["defense", "defenseman", "defenceman"]:
            skill_sections["Defensive Skills"] = {
                "gap_control": getattr(player, "gap_control", None),
                "physicality": getattr(player, "physicality", None),
                "shot_blocking": getattr(player, "shot_blocking", None),
                "breakout_passes": getattr(player, "breakout_passes", None),
            }

        elif player.position.lower() in ["goalie", "goaltender"]:
            skill_sections["Goaltending Skills"] = {
                "save_percentage": getattr(player, "save_percentage", None),
                "reaction_time": getattr(player, "reaction_time", None),
                "positioning": getattr(player, "positioning", None),
                "save_technique": getattr(player, "save_technique", None),
                "rebound_control": getattr(player, "rebound_control", None),
            }
            skill_sections["Advanced Goalie Skills"] = {
                "puck_handling": getattr(player, "puck_handling", None),
                "recovery": getattr(player, "recovery", None),
                "glove_saves": getattr(player, "glove_saves", None),
                "blocker_saves": getattr(player, "blocker_saves", None),
                "post_integration": getattr(player, "post_integration", None),
            }
            skill_sections["Stats"] = {
                "games_played": getattr(player, "games_played", None),
                "saves": getattr(player, "saves", None),
                "goals_against": getattr(player, "goals_against", None),
            }

        return skill_sections

    def _get_key_metrics_for_position(self, position):
        """Get key metrics to track over time based on position"""
        common_metrics = ["skating_speed", "puck_control", "decision_making"]

        if position.lower() in ["forward", "center", "wing", "left wing", "right wing"]:
            return common_metrics + ["shot_accuracy", "one_timer"]
        elif position.lower() in ["defense", "defenseman", "defenceman"]:
            return common_metrics + ["gap_control", "breakout_passes"]
        elif position.lower() in ["goalie", "goaltender"]:
            return [
                "positioning",
                "save_technique",
                "rebound_control",
                "reaction_time",
                "recovery",
            ]

        return common_metrics

    def _get_rating_description(self, metric, value):
        """Get descriptive text for a metric rating"""
        # For statistics like games_played, goals, assists, etc., return factual description
        stat_metrics = ["games_played", "goals", "assists", "saves", "goals_against"]
        if metric.lower() in stat_metrics:
            if value is None or value == 0:
                return "No data recorded yet"
            elif metric == "games_played":
                return f"Player has participated in {int(value)} games"
            elif metric == "goals":
                return f"Player has scored {int(value)} goals"
            elif metric == "assists":
                return f"Player has made {int(value)} assists"
            elif metric == "saves":
                return f"Player has made {int(value)} saves"
            elif metric == "goals_against":
                return f"Player has conceded {int(value)} goals"
            else:
                return f"Current value: {int(value)}"

        # For skill ratings
        if value is None:
            return "Not assessed"

        value = float(value)
        if value >= 4.5:
            return "Exceptional - significantly above expectations for age group"
        elif value >= 4.0:
            return "Excellent - exceeding expectations for age group"
        elif value >= 3.5:
            return "Very good - above average for age group"
        elif value >= 3.0:
            return "Good - meeting expectations for age group"
        elif value >= 2.5:
            return "Developing - approaching expectations for age group"
        elif value >= 2.0:
            return "Fair - below expectations but showing progress"
        elif value >= 1.5:
            return "Needs improvement - significantly below expectations"
        else:
            return "Requires focused development - fundamental skill building needed"


def generate_player_pdf_report(player_id):
    """Generate a player PDF report and return as a downloadable link"""
    # Convert player_id to Python int using our utility function
    player_id = to_int(player_id)
    if player_id is None:
        return None

    generator = PDFReportGenerator()
    pdf_data = generator.generate_player_report(player_id)

    if pdf_data:
        # Create a download link
        b64_pdf = base64.b64encode(pdf_data).decode()
        return f'<a href="data:application/pdf;base64,{b64_pdf}" download="player_report_{player_id}.pdf">📄 Download Player Assessment Report (PDF)</a>'
    else:
        return None


def display_pdf_export_section(player_id):
    """Display PDF export options for player reports"""
    st.subheader("Export Player Report")

    # Convert player_id to Python int using our utility function
    player_id = to_int(player_id)
    if player_id is None:
        st.error("Invalid player ID format.")
        return

    player = Player.query.get(player_id)
    if not player:
        st.error("Player not found.")
        return

    st.write(f"Generate a comprehensive assessment report for {player.name}.")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.write("The report will include:")
        st.markdown("- Current skill assessments and ratings")
        st.markdown("- Recent coach feedback")
        st.markdown("- Development progress over time")
        st.markdown("- Statistical performance")

    with col2:
        if st.button("Generate PDF Report", type="primary"):
            with st.spinner("Generating PDF report..."):
                pdf_link = generate_player_pdf_report(player_id)
                if pdf_link:
                    st.markdown(pdf_link, unsafe_allow_html=True)
                    st.success("PDF report generated successfully!")
                else:
                    st.error("Failed to generate PDF report.")
