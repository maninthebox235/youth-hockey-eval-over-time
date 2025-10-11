import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from database.models import db, Player, PlayerHistory
from sqlalchemy import func
from utils.type_converter import to_int, to_float
from datetime import datetime, timedelta
from components.age_benchmarks import get_age_appropriate_benchmark


def get_peer_group_data(player_age, position, attribute=None):
    """
    Get anonymized data for peers in the same age group and position

    Args:
        player_age: Age of the player
        position: Position of the player
        attribute: Optional specific attribute to query

    Returns:
        DataFrame with peer data
    """
    # Ensure player_age is properly converted to int
    player_age = to_int(player_age)
    if player_age is None:
        st.error("Invalid player age for peer comparison")
        return pd.DataFrame()  # Return empty dataframe if age is invalid

    try:
        # Ensure we're using native Python types for database operations
        # This explicitly converts from numpy.int64/int32 to Python int if necessary
        try:
            player_age = int(player_age)
            min_age = int(player_age - 1)
            max_age = int(player_age + 1)
        except (TypeError, ValueError) as e:
            st.error(f"Error converting player age to integer: {str(e)}")
            return pd.DataFrame()

        # Ensure position is a standard string, not a numpy string type
        if position is not None:
            try:
                position = str(position)
            except (TypeError, ValueError) as e:
                st.error(f"Error converting position to string: {str(e)}")
                return pd.DataFrame()
        else:
            st.error("Position cannot be None for peer comparison")
            return pd.DataFrame()

        # Query based on criteria with proper Python native types
        peer_query = Player.query.filter(
            Player.age.between(min_age, max_age), Player.position == position
        )

        # If specific attribute requested, ensure it's not null
        if attribute and hasattr(Player, attribute):
            # Create dynamic filter for non-null attribute
            peer_query = peer_query.filter(getattr(Player, attribute).isnot(None))

        peers = peer_query.all()

        if not peers:
            return pd.DataFrame()

        # Anonymize and collect data
        peer_data = []
        for i, peer in enumerate(peers):
            # Use a random ID instead of actual player name
            player_data = {
                "peer_id": f"Player {i+1}",
                "age": peer.age,
                "position": peer.position,
                "games_played": peer.games_played or 0,
            }

            # Add all numeric attributes with proper type conversion for database compatibility
            for attr in dir(peer):
                if attr.startswith("_") or callable(getattr(peer, attr)):
                    continue

                value = getattr(peer, attr)
                if isinstance(value, (int, float)) and not isinstance(value, bool):
                    # Convert numpy types to native Python types for database compatibility
                    if hasattr(value, "item"):
                        try:
                            # Extract native Python type from numpy type
                            # Use our utility functions for consistent conversion
                            if isinstance(value, (np.integer, int)):
                                player_data[attr] = to_int(value)
                            elif isinstance(value, (np.floating, float)):
                                player_data[attr] = to_float(value)
                            else:
                                player_data[attr] = value
                        except (TypeError, ValueError, AttributeError):
                            # Fallback if conversion fails
                            player_data[attr] = value
                    else:
                        player_data[attr] = value

            peer_data.append(player_data)

        return pd.DataFrame(peer_data)

    except Exception as e:
        st.error(f"Error retrieving peer data: {str(e)}")
        return pd.DataFrame()


def calculate_percentile(player_value, peer_values):
    """Calculate percentile of player among peers for a specific metric"""
    if peer_values is None or len(peer_values) == 0:
        return 0

    # Count how many peers have lower values
    lower_values = sum(1 for x in peer_values if x < player_value)

    # Calculate percentile
    percentile = (lower_values / len(peer_values)) * 100

    return percentile


def display_peer_comparison(player_data):
    """
    Display peer comparison analytics for a player

    Args:
        player_data: Dictionary containing player information
    """
    st.title("Peer Comparison Analytics")
    st.write("See how the player compares to peers in the same age group and position")

    # Get player information and safely convert types
    player_id = to_int(player_data.get("player_id"))
    player_age = to_int(player_data.get("age"))
    player_position = player_data.get("position")
    player_name = player_data.get("name")

    if not all(
        [player_id is not None, player_age is not None, player_position, player_name]
    ):
        st.error("Missing required player information")
        return

    # Get peer data
    peer_df = get_peer_group_data(player_age, player_position)

    if peer_df.empty:
        st.info(
            f"No peers found for comparison (Age: {player_age}, Position: {player_position})"
        )
        return

    # Number of peers for context
    num_peers = len(peer_df)
    # Safe calculation of age range with null checking
    min_age = f"{player_age-1}" if player_age is not None else "?"
    max_age = f"{player_age+1}" if player_age is not None else "?"
    st.write(
        f"Comparing against {num_peers} peers in age group {min_age}-{max_age}, position: {player_position}"
    )

    # Select metrics for comparison
    position_metrics = {
        "Forward": [
            "skating_speed",
            "shooting_accuracy",
            "puck_control",
            "passing_accuracy",
            "hockey_sense",
        ],
        "Defense": [
            "skating_speed",
            "backward_skating",
            "gap_control",
            "shot_blocking",
            "breakout_passes",
        ],
        "Goalie": [
            "save_percentage",
            "positioning",
            "rebound_control",
            "recovery",
            "save_technique",
        ],
    }

    default_metrics = position_metrics.get(
        player_position, ["skating_speed", "shooting_accuracy"]
    )
    available_metrics = [
        col
        for col in peer_df.columns
        if col not in ["peer_id", "age", "position", "games_played"]
    ]

    selected_metrics = st.multiselect(
        "Select metrics for comparison",
        options=available_metrics,
        default=[m for m in default_metrics if m in available_metrics],
    )

    if not selected_metrics:
        st.warning("Please select at least one metric for comparison")
        return

    # Calculate percentiles for selected metrics
    percentiles = {}
    for metric in selected_metrics:
        # Ensure metric exists in player data
        if metric not in player_data:
            continue

        player_value = player_data.get(metric)
        if player_value is None:
            continue

        # Get all peer values for this metric
        peer_values = peer_df[metric].dropna().values

        # Calculate percentile
        percentile = calculate_percentile(player_value, peer_values)
        percentiles[metric] = percentile

    # Display percentile ranks
    if percentiles:
        st.subheader("Percentile Rankings")

        # Create columns for percentile metrics
        cols = st.columns(min(3, len(percentiles)))

        for i, (metric, percentile) in enumerate(percentiles.items()):
            with cols[i % len(cols)]:
                # Format metric name
                metric_name = metric.replace("_", " ").title()

                # Create gauge chart for percentile
                fig = go.Figure(
                    go.Indicator(
                        mode="gauge+number",
                        value=percentile,
                        domain={"x": [0, 1], "y": [0, 1]},
                        title={"text": metric_name},
                        gauge={
                            "axis": {"range": [0, 100]},
                            "bar": {"color": "royalblue"},
                            "steps": [
                                {"range": [0, 25], "color": "lightgray"},
                                {"range": [25, 50], "color": "lightgreen"},
                                {"range": [50, 75], "color": "green"},
                                {"range": [75, 100], "color": "darkgreen"},
                            ],
                            "threshold": {
                                "line": {"color": "red", "width": 4},
                                "thickness": 0.75,
                                "value": 50,
                            },
                        },
                    )
                )

                fig.update_layout(height=200)
                st.plotly_chart(fig, use_container_width=True)

                # Interpret the percentile
                if percentile >= 90:
                    st.success(f"**ELITE:** In the top 10% among peers")
                elif percentile >= 75:
                    st.success(f"**EXCELLENT:** Better than 3/4 of peers")
                elif percentile >= 50:
                    st.info(f"**ABOVE AVERAGE:** Better than half of peers")
                elif percentile >= 25:
                    st.warning(f"**DEVELOPING:** In the lower half among peers")
                else:
                    st.error(f"**NEEDS FOCUS:** In the bottom 25% among peers")

        # Create radar chart comparison
        if len(selected_metrics) > 2:
            st.subheader("Skill Profile vs. Peer Average")

            # Prepare data for radar chart
            radar_metrics = []
            player_values = []
            peer_avg_values = []

            for metric in selected_metrics:
                if metric in player_data and metric in peer_df.columns:
                    player_value = player_data.get(metric, 0)
                    peer_avg = peer_df[metric].mean()

                    # Skip if either value is missing
                    if pd.isna(player_value) or pd.isna(peer_avg):
                        continue

                    radar_metrics.append(metric.replace("_", " ").title())
                    player_values.append(player_value)
                    peer_avg_values.append(peer_avg)

            if radar_metrics:
                # Create radar chart
                fig = go.Figure()

                fig.add_trace(
                    go.Scatterpolar(
                        r=player_values,
                        theta=radar_metrics,
                        fill="toself",
                        name=player_name,
                    )
                )

                fig.add_trace(
                    go.Scatterpolar(
                        r=peer_avg_values,
                        theta=radar_metrics,
                        fill="toself",
                        name="Peer Average",
                    )
                )

                fig.update_layout(
                    polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
                    showlegend=True,
                )

                st.plotly_chart(fig, use_container_width=True)

        # Distribution comparison for a selected metric
        st.subheader("Metric Distribution Comparison")

        # Let user select one metric to view distribution
        if selected_metrics:
            dist_metric = st.selectbox(
                "Select metric to view distribution",
                options=selected_metrics,
                format_func=lambda x: x.replace("_", " ").title(),
            )

            if dist_metric:
                # Create histogram with player's value marked
                player_value = player_data.get(dist_metric)

                if player_value is not None and dist_metric in peer_df.columns:
                    fig = px.histogram(
                        peer_df,
                        x=dist_metric,
                        nbins=10,
                        title=f"Distribution of {dist_metric.replace('_', ' ').title()} Among Peers",
                    )

                    # Add vertical line for player's value
                    fig.add_vline(
                        x=player_value,
                        line_dash="dash",
                        line_color="red",
                        annotation_text=f"{player_name}'s value",
                        annotation_position="top",
                    )

                    st.plotly_chart(fig, use_container_width=True)

                    # Calculate some statistics
                    peer_mean = peer_df[dist_metric].mean()
                    peer_median = peer_df[dist_metric].median()

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric(f"{player_name}'s Value", f"{player_value:.1f}")
                    with col2:
                        st.metric(
                            "Peer Average",
                            f"{peer_mean:.1f}",
                            delta=f"{player_value - peer_mean:.1f}",
                        )
                    with col3:
                        st.metric("Peer Median", f"{peer_median:.1f}")

        # Comparison table with all metrics
        st.subheader("Detailed Comparison Table")

        comparison_data = []

        for metric in selected_metrics:
            if metric in player_data and metric in peer_df.columns:
                player_value = player_data.get(metric)
                if player_value is None:
                    continue

                peer_avg = peer_df[metric].mean()
                peer_min = peer_df[metric].min()
                peer_max = peer_df[metric].max()
                percentile = percentiles.get(metric, 0)

                comparison_data.append(
                    {
                        "Metric": metric.replace("_", " ").title(),
                        f"{player_name}'s Value": f"{player_value:.1f}",
                        "Peer Average": f"{peer_avg:.1f}",
                        "Peer Range": f"{peer_min:.1f} - {peer_max:.1f}",
                        "Percentile": f"{percentile:.0f}%",
                    }
                )

        if comparison_data:
            st.dataframe(pd.DataFrame(comparison_data), use_container_width=True)
    else:
        st.warning("No comparable metrics found between player and peers")

    # Development recommendations
    st.subheader("Development Recommendations")

    # Find areas for improvement (lowest percentiles)
    if percentiles:
        weaknesses = sorted(percentiles.items(), key=lambda x: x[1])[:2]
        strengths = sorted(percentiles.items(), key=lambda x: x[1], reverse=True)[:2]

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Areas for Improvement")
            if weaknesses:
                for metric, percentile in weaknesses:
                    metric_name = metric.replace("_", " ").title()
                    st.write(f"**{metric_name}** (Percentile: {percentile:.0f}%)")

                    # Get age-appropriate training recommendation
                    if metric == "skating_speed":
                        st.info(
                            "**Training Focus:** Edge work, stride efficiency, and explosive starts"
                        )
                    elif metric == "shooting_accuracy":
                        st.info(
                            "**Training Focus:** Shot repetition, proper weight transfer, target practice"
                        )
                    elif metric == "puck_control":
                        st.info(
                            "**Training Focus:** Stickhandling drills, tight space control, head-up practice"
                        )
                    elif metric == "passing_accuracy":
                        st.info(
                            "**Training Focus:** Pass reception, proper technique, moving targets"
                        )
                    else:
                        st.info(
                            f"**Training Focus:** Consistent practice of {metric_name.lower()} fundamentals"
                        )

        with col2:
            st.markdown("#### Key Strengths")
            if strengths:
                for metric, percentile in strengths:
                    metric_name = metric.replace("_", " ").title()
                    st.write(f"**{metric_name}** (Percentile: {percentile:.0f}%)")

                    # Get strength-building recommendation
                    if percentile >= 90:
                        st.success(
                            "**Focus:** Continue to develop this elite skill and teach others"
                        )
                    elif percentile >= 75:
                        st.success(
                            "**Focus:** Refine this strength with advanced techniques"
                        )
                    else:
                        st.success(
                            "**Focus:** Build on this strength in game situations"
                        )


def display_historical_comparison(player_id, player_data):
    """Show how player compares to peers over time"""
    st.subheader("Historical Performance Trends")

    # Convert player_id to Python integer using our utility and ensure it's a native int type
    player_id_int = to_int(player_id)
    if player_id_int is None:
        st.error("Invalid player ID for historical comparison")
        return

    # Convert to native Python int to avoid numpy.int64 compatibility issues with psycopg2
    player_id_int = int(player_id_int)

    # Get player history
    try:
        player_history = (
            PlayerHistory.query.filter_by(player_id=player_id_int)
            .order_by(PlayerHistory.date)
            .all()
        )

        if not player_history:
            st.info("No historical data available for trend analysis")
            return

        # Process history into DataFrame
        history_data = []
        for entry in player_history:
            data_point = {"date": entry.date, "player_id": player_id_int}

            # Add all numeric attributes
            for attr in dir(entry):
                if attr.startswith("_") or callable(getattr(entry, attr)):
                    continue

                value = getattr(entry, attr)
                if isinstance(value, (int, float)) and not isinstance(value, bool):
                    data_point[attr] = value

            history_data.append(data_point)

        player_history_df = pd.DataFrame(history_data)

        # Get age-appropriate benchmarks for comparison
        player_age = player_data.get("age", 10)
        position = player_data.get("position", "Forward")

        # Select metrics based on position
        if position == "Goalie":
            metrics = ["positioning", "save_technique", "rebound_control"]
        elif position == "Defense":
            metrics = ["skating_speed", "backward_skating", "gap_control"]
        else:  # Forward
            metrics = ["skating_speed", "shooting_accuracy", "puck_control"]

        # Filter metrics to those actually in the history
        available_metrics = [m for m in metrics if m in player_history_df.columns]

        if not available_metrics:
            st.info("No relevant metrics found in historical data")
            return

        # Select one metric for historical comparison
        selected_metric = st.selectbox(
            "Select metric for historical comparison",
            options=available_metrics,
            format_func=lambda x: x.replace("_", " ").title(),
        )

        if selected_metric:
            # Get peer data for this metric over time
            dates = player_history_df["date"].unique()

            if len(dates) > 1:
                # Create a line chart showing player vs peer average over time
                fig = go.Figure()

                # Add player's progress line
                fig.add_trace(
                    go.Scatter(
                        x=player_history_df["date"],
                        y=player_history_df[selected_metric],
                        mode="lines+markers",
                        name=f"{player_data.get('name', 'Player')}",
                    )
                )

                # Add benchmark line if available
                metric_benchmark = get_age_appropriate_benchmark(
                    player_age, selected_metric
                )
                if metric_benchmark:
                    target_value = metric_benchmark.get("target", 3)

                    fig.add_trace(
                        go.Scatter(
                            x=player_history_df["date"],
                            y=[target_value] * len(player_history_df),
                            mode="lines",
                            line=dict(dash="dash"),
                            name=f"Age {player_age} Benchmark",
                        )
                    )

                # Add peer average for each date
                peer_averages = []
                for date in dates:
                    # Get peers at that time (could be simplified in this version)
                    peers_df = get_peer_group_data(
                        player_age, position, selected_metric
                    )
                    if not peers_df.empty and selected_metric in peers_df.columns:
                        peer_avg = peers_df[selected_metric].mean()
                        peer_averages.append((date, peer_avg))

                if peer_averages:
                    peer_dates, peer_values = zip(*peer_averages)
                    fig.add_trace(
                        go.Scatter(
                            x=peer_dates,
                            y=peer_values,
                            mode="lines",
                            line=dict(dash="dot"),
                            name="Peer Average",
                        )
                    )

                fig.update_layout(
                    title=f"{selected_metric.replace('_', ' ').title()} Progress Over Time",
                    xaxis_title="Date",
                    yaxis_title="Rating (1-5)",
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="center",
                        x=0.5,
                    ),
                )

                st.plotly_chart(fig, use_container_width=True)

                # Calculate improvement metrics
                if len(dates) >= 2:
                    first_value = player_history_df[selected_metric].iloc[0]
                    latest_value = player_history_df[selected_metric].iloc[-1]
                    improvement = latest_value - first_value

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Starting Value", f"{first_value:.1f}")
                    with col2:
                        st.metric(
                            "Current Value",
                            f"{latest_value:.1f}",
                            delta=f"{improvement:.1f}",
                        )
                    with col3:
                        # Calculate improvement percentage
                        if first_value > 0:
                            pct_improvement = (improvement / first_value) * 100
                            st.metric("Improvement", f"{pct_improvement:.1f}%")
                        else:
                            st.metric("Improvement", "N/A")
            else:
                st.info("Need multiple history points for trend analysis")

    except Exception as e:
        st.error(f"Error analyzing historical data: {str(e)}")


def display_peer_comparison_interface(player_id, player_data):
    """Main interface for peer comparison analytics"""
    # Check for premium membership
    is_premium = st.session_state.get("is_premium", False)

    if not is_premium:
        st.warning("⭐ Peer Comparison is a premium feature")
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(
                """
            Unlock peer comparison analytics with a premium membership.
            This feature allows you to:
            - Compare your player with others in the same age group
            - See percentile rankings for all key skills
            - Track relative performance over time
            - Identify areas where your player stands out
            """
            )
        with col2:
            st.button("Upgrade to Premium", type="primary", use_container_width=True)
        return

    # Ensure player_id is properly converted for database operations
    player_id_int = to_int(player_id)
    if player_id_int is None:
        st.error("Invalid player ID for peer comparison")
        return

    # Convert to native Python int to avoid numpy.int64 compatibility issues with psycopg2
    try:
        player_id_int = int(player_id_int)
    except (TypeError, ValueError):
        st.error("Could not convert player ID to integer")
        return

    # Create tabs for different views
    tabs = st.tabs(["Current Comparison", "Historical Trends"])

    with tabs[0]:
        display_peer_comparison(player_data)

    with tabs[1]:
        display_historical_comparison(player_id_int, player_data)
