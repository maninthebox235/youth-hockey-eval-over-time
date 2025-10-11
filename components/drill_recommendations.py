"""
Contextual Hockey Drill Recommendations module.

This module provides intelligent drill recommendations based on a player's:
1. Position (Forward, Defense, Goalie)
2. Age and skill level
3. Recent performance trends
4. Team context (where available)
5. Specific weaknesses identified in assessments
"""

import streamlit as st
import numpy as np
from database.models import Player, PlayerHistory, Team, TeamMembership
from datetime import datetime, timedelta
import random
from utils.type_converter import to_int, to_float
from components.training_plans import (
    TrainingPlans,
)


class DrillRecommendationEngine:
    """
    Engine for generating contextual hockey drill recommendations based on
    player profile, performance history, and team context.
    """

    def __init__(self):
        """Initialize the recommendation engine with training plans data"""
        self.training_plans = TrainingPlans()
        self.skill_drills = self.training_plans.skill_drills

    def get_recent_performance_trends(self, player_id, lookback_months=3):
        """
        Analyze recent performance metrics to identify trends

        Args:
            player_id: ID of the player
            lookback_months: Number of months to look back for trend analysis

        Returns:
            Dictionary with skills as keys and trend values (1=improving, 0=stable, -1=declining)
        """
        # Ensure player_id is a Python native int
        player_id = to_int(player_id)
        if player_id is None:
            return {}

        # Get history for this player with date filter
        cutoff_date = datetime.now() - timedelta(days=lookback_months * 30)
        history = (
            PlayerHistory.query.filter(
                PlayerHistory.player_id == player_id, PlayerHistory.date >= cutoff_date
            )
            .order_by(PlayerHistory.date)
            .all()
        )

        if not history or len(history) < 2:
            # Not enough data for trend analysis
            return {}

        # Track metrics that can show trends
        metrics = [
            "skating_speed",
            "shooting_accuracy",
            "puck_control",
            "passing_accuracy",
            "edge_control",
            "agility",
            "backward_skating",
            "decision_making",
            "game_awareness",
            "hockey_sense",
            "wrist_shot",
            "slap_shot",
            "gap_control",
            "physicality",
            "shot_blocking",
            "positioning",
            "save_technique",
            "rebound_control",
        ]

        # Calculate trends for each metric
        trends = {}

        for metric in metrics:
            # Get values for this metric
            values = []
            for entry in history:
                if hasattr(entry, metric) and getattr(entry, metric) is not None:
                    values.append(to_float(getattr(entry, metric)))

            if len(values) >= 2:
                # Simple trend calculation: compare first and last values
                if values[-1] > values[0] + 0.3:  # Meaningful improvement
                    trends[metric] = 1  # Improving
                elif values[-1] < values[0] - 0.3:  # Meaningful decline
                    trends[metric] = -1  # Declining
                else:
                    trends[metric] = 0  # Stable

        return trends

    def get_team_context(self, player_id):
        """
        Get team context information for recommendation purposes

        Args:
            player_id: ID of the player

        Returns:
            Dictionary with team context data
        """
        # Ensure player_id is a Python native int
        player_id = to_int(player_id)
        if player_id is None:
            return None

        # Get player's current team
        membership = TeamMembership.query.filter(
            TeamMembership.player_id == player_id, TeamMembership.is_active == True
        ).first()

        if not membership:
            return None

        team = Team.query.get(membership.team_id)
        if not team:
            return None

        # Get teammates in same team
        teammates = (
            Player.query.join(TeamMembership, Player.id == TeamMembership.player_id)
            .filter(
                TeamMembership.team_id == team.id,
                TeamMembership.is_active == True,
                Player.id != player_id,  # Exclude the current player
            )
            .all()
        )

        # Calculate team averages for key metrics
        team_averages = {}
        player_count = len(teammates) + 1  # Include current player in count

        # Add current player to the list for calculations
        current_player = Player.query.get(player_id)
        if current_player:
            teammates.append(current_player)

        # Calculate averages for relevant metrics
        metrics = [
            "skating_speed",
            "shooting_accuracy",
            "puck_control",
            "passing_accuracy",
            "hockey_sense",
            "decision_making",
        ]

        for metric in metrics:
            values = []
            for teammate in teammates:
                if hasattr(teammate, metric) and getattr(teammate, metric) is not None:
                    values.append(to_float(getattr(teammate, metric)))

            if values:
                team_averages[metric] = sum(values) / len(values)

        return {
            "team_name": team.name,
            "age_group": team.age_group,
            "team_averages": team_averages,
            "team_size": player_count,
        }

    def get_contextual_recommendations(self, player_id, limit=5):
        """
        Generate contextual drill recommendations based on player data

        Args:
            player_id: ID of the player
            limit: Maximum number of recommendations to return

        Returns:
            List of recommended drills with context explanation
        """
        # Ensure we have a standard Python integer for player_id
        player_id = to_int(player_id)
        if player_id is None:
            return []

        # Get player data
        player = Player.query.get(player_id)
        if not player:
            return []

        # Convert player to dictionary and ensure all values are Python native types
        player_dict = {}
        for c in player.__table__.columns:
            value = getattr(player, c.name)

            # Convert value based on its type
            if isinstance(value, (int, np.integer)):
                player_dict[c.name] = to_int(value)
            elif isinstance(value, (float, np.floating)):
                player_dict[c.name] = to_float(value)
            else:
                player_dict[c.name] = value

        # Get player needs (weaknesses) from training plans
        needs = self.training_plans.get_player_needs(player_dict)

        # Get recent performance trends
        trends = self.get_recent_performance_trends(player_id)

        # Get team context
        team_context = self.get_team_context(player_id)

        # Define different contexts for recommendations
        recommendation_contexts = []

        # 1. Priority skills (from weaknesses)
        for skill, value in needs:
            reason = f"This is one of your lowest rated skills ({value:.1f}/5)"
            recommendation_contexts.append(
                {
                    "skill": skill,
                    "reason": reason,
                    "priority": 10,  # Higher priority for weakness-based recommendations
                }
            )

        # 2. Declining skills (from trends)
        for skill, trend in trends.items():
            if trend == -1 and skill in self.skill_drills:
                reason = f"This skill has been declining in recent assessments"
                # Check if not already added as a weakness
                if not any(rc["skill"] == skill for rc in recommendation_contexts):
                    recommendation_contexts.append(
                        {
                            "skill": skill,
                            "reason": reason,
                            "priority": 8,  # High priority for declining skills
                        }
                    )

        # 3. Team context - skills where player is below team average
        if team_context and "team_averages" in team_context:
            for skill, team_avg in team_context["team_averages"].items():
                if hasattr(player, skill) and getattr(player, skill) is not None:
                    player_value = to_float(getattr(player, skill))
                    if player_value < team_avg - 0.5 and skill in self.skill_drills:
                        reason = f"This skill is below your team's average ({player_value:.1f} vs {team_avg:.1f})"
                        # Check if not already added
                        if not any(
                            rc["skill"] == skill for rc in recommendation_contexts
                        ):
                            recommendation_contexts.append(
                                {
                                    "skill": skill,
                                    "reason": reason,
                                    "priority": 7,  # Medium-high priority
                                }
                            )

        # 4. Position-specific important skills
        position_skills = {
            "Forward": ["shot_accuracy", "wrist_shot", "hockey_sense", "puck_control"],
            "Defense": [
                "gap_control",
                "backward_skating",
                "shot_blocking",
                "breakout_passes",
            ],
            "Goalie": ["positioning", "save_technique", "rebound_control", "recovery"],
        }

        # Get the position and normalize it for the position_skills dictionary
        position = player_dict.get("position", "Forward")

        # Convert the position to a standard form (Forward, Defense, Goalie)
        if "goalie" in position.lower():
            normalized_position = "Goalie"
        elif "defense" in position.lower():
            normalized_position = "Defense"
        else:
            normalized_position = "Forward"

        # For debugging purposes - can be commented out in production
        # st.write(f"Position from DB: '{position}', normalized to '{normalized_position}'")

        if normalized_position in position_skills:
            for skill in position_skills[normalized_position]:
                if skill in self.skill_drills:
                    # Check if not already added
                    if not any(rc["skill"] == skill for rc in recommendation_contexts):
                        reason = (
                            f"This is a critical skill for your position ({position})"
                        )
                        recommendation_contexts.append(
                            {
                                "skill": skill,
                                "reason": reason,
                                "priority": 6,  # Medium priority
                            }
                        )

        # 5. Add age-appropriate general skills if we still need more recommendations
        if len(recommendation_contexts) < limit:
            age = player_dict.get("age", 12)
            age_skills = {
                (6, 10): [
                    "skating_speed",
                    "edge_control",
                    "puck_control",
                ],  # Younger players
                (11, 14): [
                    "passing_accuracy",
                    "agility",
                    "shooting_accuracy",
                ],  # Middle age
                (15, 18): [
                    "decision_making",
                    "hockey_sense",
                    "position-specific",
                ],  # Older players
            }

            # Find appropriate age group
            age_group = None
            for min_age, max_age in age_skills.keys():
                if min_age <= age <= max_age:
                    age_group = (min_age, max_age)
                    break

            if age_group and age_group in age_skills:
                skills_to_add = age_skills[age_group]
                # For position-specific, use the appropriate position skills
                if (
                    "position-specific" in skills_to_add
                    and normalized_position in position_skills
                ):
                    skills_to_add.remove("position-specific")
                    skills_to_add.extend(position_skills[normalized_position])

                for skill in skills_to_add:
                    if skill in self.skill_drills:
                        # Check if not already added
                        if not any(
                            rc["skill"] == skill for rc in recommendation_contexts
                        ):
                            reason = f"This is an important skill for your age group ({age} years old)"
                            recommendation_contexts.append(
                                {
                                    "skill": skill,
                                    "reason": reason,
                                    "priority": 5,  # Lower priority
                                }
                            )

        # Sort by priority and take the top recommendations
        recommendation_contexts.sort(key=lambda x: x["priority"], reverse=True)
        top_contexts = recommendation_contexts[:limit]

        # For each context, get a recommended drill
        recommendations = []
        for context in top_contexts:
            skill = context["skill"]
            reason = context["reason"]

            # Get drills for this skill and select one, using the player's position
            available_drills = self.training_plans.get_drills_for_skill(
                skill, count=3, position=normalized_position
            )
            if available_drills:
                # Select a drill (randomly for variety)
                selected_drill = random.choice(available_drills)

                # Add context information
                # For goalies, we need to track both the original skill and the substituted skill
                original_skill = skill

                # If this is a goalie, the drill might be for a different skill than requested
                # We need to identify which goalie skill was actually used
                if normalized_position == "Goalie":
                    goalie_skills = [
                        "positioning",
                        "save_technique",
                        "rebound_control",
                        "recovery",
                        "puck_handling",
                        "glove_saves",
                        "blocker_saves",
                        "post_integration",
                    ]

                    goalie_substitutes = {
                        "decision_making": "positioning",
                        "hockey_sense": "positioning",
                        "skating_speed": "recovery",
                        "agility": "recovery",
                        "shooting_accuracy": "save_technique",
                        "passing_accuracy": "save_technique",
                    }

                    # If original skill is not a goalie skill, get the substituted skill for display
                    if (
                        original_skill not in goalie_skills
                        and original_skill in goalie_substitutes
                    ):
                        display_skill = goalie_substitutes[original_skill]
                    else:
                        display_skill = original_skill
                else:
                    display_skill = original_skill

                selected_drill["skill"] = original_skill
                selected_drill["recommendation_reason"] = reason
                selected_drill["formatted_skill"] = display_skill.replace(
                    "_", " "
                ).title()

                recommendations.append(selected_drill)

        return recommendations


def display_recommendation_header():
    """Display header for drill recommendations section"""
    st.subheader("🏒 Personalized Drill Recommendations")
    st.write(
        """
    These drill recommendations are tailored specifically for you based on your 
    position, skill assessments, recent performance trends, and team context.
    """
    )


def display_contextual_drill_recommendations(player_id, player_data=None):
    """
    Display contextual drill recommendations for a player

    Args:
        player_id: ID of the player
        player_data: Optional player data (saves a database query)
    """
    # Check for premium membership
    is_premium = st.session_state.get("is_premium", False)

    if not is_premium:
        st.warning("⭐ Drill Recommendations is a premium feature")
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(
                """
            Unlock personalized drill recommendations with a premium membership. 
            Get custom drills based on:
            - Player position and age
            - Current skill assessment
            - Recent performance trends
            - Team context and peer comparison
            """
            )
        with col2:
            st.button("Upgrade to Premium", type="primary", use_container_width=True)
        return

    # Ensure player_id is a Python native int
    player_id = to_int(player_id)
    if player_id is None:
        st.error("Invalid player ID")
        return

    # Initialize recommendation engine
    engine = DrillRecommendationEngine()

    # Get recommendations
    recommendations = engine.get_contextual_recommendations(player_id)

    if not recommendations:
        st.info(
            "We don't have enough data yet to provide personalized drill recommendations. Complete a skills assessment first."
        )
        return

    # Display recommendations
    display_recommendation_header()

    # Create tabs for each recommendation
    if len(recommendations) > 0:
        tab_titles = [f"{drill['formatted_skill']}" for drill in recommendations]
        tabs = st.tabs(tab_titles)

        for i, tab in enumerate(tabs):
            drill = recommendations[i]
            with tab:
                col1, col2 = st.columns([2, 1])

                with col1:
                    st.markdown(f"### {drill['name']}")
                    st.markdown(f"**Why this drill?** {drill['recommendation_reason']}")
                    st.markdown(f"**Description:** {drill['description']}")
                    st.markdown(f"**Duration:** {drill['duration']}")
                    st.markdown(f"**Difficulty:** {drill['difficulty']}")

                    if "resources" in drill and drill["resources"]:
                        st.markdown(f"**Resources needed:** {drill['resources']}")

                with col2:
                    # Display video if available
                    if "video_url" in drill and drill["video_url"]:
                        video_url = drill["video_url"]
                        st.video(video_url)

                    # Add a "Try this drill" button
                    if st.button(f"I'll try this drill!", key=f"try_drill_{i}"):
                        st.balloons()
                        st.success(
                            "Great choice! This drill will help improve your "
                            + drill["formatted_skill"]
                            + "."
                        )


def integrate_with_training_plans(player_id, player_data=None):
    """
    Integration point to include contextual recommendations in the training plans interface

    Args:
        player_id: ID of the player
        player_data: Optional player data (saves a database query)
    """
    # Ensure player_id is a Python native int
    player_id = to_int(player_id)
    if player_id is None:
        st.error("Invalid player ID")
        return

    # Add personalized drill recommendations section
    st.markdown("## Daily Drill Recommendations")

    display_contextual_drill_recommendations(player_id, player_data)
