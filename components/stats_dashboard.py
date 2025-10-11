import streamlit as st
import plotly.express as px


def display_age_group_stats(players_df):
    st.subheader("Age Group Statistics")

    age_groups = (
        players_df.groupby("age_group")
        .agg(
            {
                "player_id": "count",
                "skating_speed": "mean",
                "shooting_accuracy": "mean",
                "games_played": "mean",
            }
        )
        .round(2)
    )

    age_groups.columns = [
        "Players",
        "Avg Skating Speed",
        "Avg Shooting Accuracy",
        "Avg Games Played",
    ]

    st.dataframe(age_groups)

    fig = px.bar(
        players_df,
        x="age_group",
        y=["skating_speed", "shooting_accuracy"],
        title="Average Skills by Age Group",
        barmode="group",
    )
    st.plotly_chart(fig, use_container_width=True)


def display_player_rankings(players_df):
    st.subheader("Top Performers")

    col1, col2 = st.columns(2)

    with col1:
        top_skating = players_df.nlargest(5, "skating_speed")[["name", "skating_speed"]]
        st.markdown("### Top Skating Speed")
        st.dataframe(top_skating)

    with col2:
        top_shooting = players_df.nlargest(5, "shooting_accuracy")[
            ["name", "shooting_accuracy"]
        ]
        st.markdown("### Top Shooting Accuracy")
        st.dataframe(top_shooting)
