"""
Admin interface for managing email notification settings and sending batch notifications.
"""

import streamlit as st
from datetime import datetime, timedelta
from database.models import Player, User, db
from app import mail, app
from utils.notification_service import (
    NotificationService,
    send_weekly_reports_batch,
    send_assessment_reminders_batch,
)


def display_notification_settings():
    """Display notification settings and controls for admins."""
    st.title("📧 Notification Management")

    tab1, tab2, tab3, tab4 = st.tabs([
        "Send Batch Notifications",
        "Scheduled Reports",
        "Test Notifications",
        "Notification Log"
    ])

    with tab1:
        display_batch_notifications()

    with tab2:
        display_scheduled_reports()

    with tab3:
        display_test_notifications()

    with tab4:
        display_notification_log()


def display_batch_notifications():
    """Interface for sending batch notifications."""
    st.subheader("Send Batch Notifications")

    notification_type = st.selectbox(
        "Notification Type",
        [
            "Weekly Progress Reports",
            "Assessment Reminders",
            "Custom Team Announcement"
        ]
    )

    if notification_type == "Weekly Progress Reports":
        st.info(
            "This will send weekly progress reports to all players who have activity in the last 7 days."
        )

        if st.button("Send Weekly Reports", type="primary"):
            with st.spinner("Sending weekly reports..."):
                try:
                    with app.app_context():
                        sent_count = send_weekly_reports_batch(mail, app.app_context())
                        st.success(
                            f"✅ Successfully sent {sent_count} weekly progress reports!"
                        )
                except Exception as e:
                    st.error(f"Error sending reports: {str(e)}")

    elif notification_type == "Assessment Reminders":
        st.info("Send reminders to players who haven't been assessed recently.")

        days_threshold = st.slider(
            "Days since last assessment",
            min_value=7,
            max_value=90,
            value=30,
            help="Send reminders to players not assessed in this many days"
        )

        if st.button("Send Reminders", type="primary"):
            with st.spinner("Sending assessment reminders..."):
                try:
                    with app.app_context():
                        sent_count = send_assessment_reminders_batch(
                            mail, app.app_context(), days_threshold
                        )
                        st.success(
                            f"✅ Successfully sent {sent_count} assessment reminders!"
                        )
                except Exception as e:
                    st.error(f"Error sending reminders: {str(e)}")

    elif notification_type == "Custom Team Announcement":
        st.info("Send a custom announcement to all members of a team.")

        from database.models import Team

        teams = Team.query.all()
        if teams:
            team_options = {f"{t.name} ({t.age_group})": t.id for t in teams}
            selected_team_name = st.selectbox("Select Team", list(team_options.keys()))
            team_id = team_options[selected_team_name]

            sender_name = st.text_input(
                "Your Name", value=st.session_state.user.get("name", "Coach")
            )
            subject = st.text_input("Subject", placeholder="Important Update")
            message = st.text_area(
                "Message",
                placeholder="Enter your announcement message here...",
                height=200
            )

            if st.button("Send Announcement", type="primary"):
                if not subject or not message:
                    st.error("Please provide both subject and message")
                else:
                    with st.spinner("Sending announcement..."):
                        try:
                            notification_service = NotificationService(mail)
                            sent_count = notification_service.send_team_announcement(
                                team_id, subject, message, sender_name
                            )
                            st.success(
                                f"✅ Announcement sent to {sent_count} team members!"
                            )
                        except Exception as e:
                            st.error(f"Error sending announcement: {str(e)}")
        else:
            st.warning("No teams found. Create a team first to send announcements.")


def display_scheduled_reports():
    """Display scheduled notification settings."""
    st.subheader("Scheduled Notifications")

    st.info(
        """
        **Automated Email Schedule (Future Feature)**
        
        Configure when automated emails should be sent:
        - Weekly Progress Reports: Every Monday at 9:00 AM
        - Assessment Reminders: Every 1st of the month
        - Team Announcements: As needed by coaches
        
        This feature requires a task scheduler (e.g., Celery, APScheduler) to be implemented.
        """
    )

    st.markdown("### Weekly Progress Reports")
    col1, col2 = st.columns(2)
    with col1:
        enabled = st.checkbox("Enable Weekly Reports", value=False, disabled=True)
    with col2:
        day_of_week = st.selectbox(
            "Send on", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
            disabled=True
        )

    st.markdown("### Assessment Reminders")
    col1, col2 = st.columns(2)
    with col1:
        reminder_enabled = st.checkbox(
            "Enable Reminders", value=False, disabled=True
        )
    with col2:
        reminder_frequency = st.selectbox(
            "Frequency", ["Weekly", "Bi-weekly", "Monthly"], disabled=True
        )

    if st.button("Save Schedule Settings", disabled=True):
        st.info("Scheduling feature coming soon!")


def display_test_notifications():
    """Interface for testing email notifications."""
    st.subheader("Test Notifications")

    test_email = st.text_input(
        "Test Email Address",
        placeholder="your-email@example.com",
        help="Enter an email address to receive test notifications"
    )

    notification_type = st.selectbox(
        "Test Notification Type",
        [
            "Feedback Notification",
            "Weekly Progress Report",
            "Assessment Reminder"
        ]
    )

    players = Player.query.limit(10).all()
    if players:
        player_options = {p.name: p.id for p in players}
        selected_player_name = st.selectbox("Select Player (for test)", list(player_options.keys()))
        player_id = player_options[selected_player_name]

        if st.button("Send Test Email", type="primary"):
            if not test_email:
                st.error("Please enter a test email address")
            else:
                with st.spinner("Sending test email..."):
                    try:
                        notification_service = NotificationService(mail)

                        if notification_type == "Feedback Notification":
                            from database.models import CoachFeedback

                            feedback = (
                                CoachFeedback.query.filter_by(player_id=player_id)
                                .order_by(CoachFeedback.date.desc())
                                .first()
                            )
                            if feedback:
                                success = notification_service.send_feedback_notification(
                                    player_id, feedback.id, test_email
                                )
                            else:
                                st.warning(
                                    "No feedback found for this player. Create feedback first."
                                )
                                success = False

                        elif notification_type == "Weekly Progress Report":
                            success = notification_service.send_weekly_progress_report(
                                player_id, test_email
                            )

                        elif notification_type == "Assessment Reminder":
                            success = notification_service.send_assessment_reminder(
                                player_id, test_email, days_since_last=30
                            )

                        if success:
                            st.success(f"✅ Test email sent to {test_email}!")
                        else:
                            st.error("Failed to send test email. Check logs for details.")

                    except Exception as e:
                        st.error(f"Error sending test email: {str(e)}")
    else:
        st.warning("No players found. Add players to test notifications.")


def display_notification_log():
    """Display notification history and statistics."""
    st.subheader("Notification Log")

    st.info(
        """
        **Email Notification History (Future Feature)**
        
        Track all sent notifications:
        - Delivery status
        - Open rates
        - Click-through rates
        - Bounce/failure logs
        
        This requires integration with email service provider API (SendGrid, Mailgun, etc.)
        """
    )

    st.markdown("### Recent Notifications (Sample Data)")

    import pandas as pd

    sample_data = pd.DataFrame({
        "Date": [
            datetime.now() - timedelta(days=i) for i in range(5)
        ],
        "Type": [
            "Weekly Report",
            "Feedback",
            "Reminder",
            "Announcement",
            "Weekly Report"
        ],
        "Recipient": [
            "parent1@example.com",
            "parent2@example.com",
            "coach@example.com",
            "team@example.com",
            "parent3@example.com"
        ],
        "Status": ["Delivered", "Delivered", "Delivered", "Delivered", "Failed"]
    })

    st.dataframe(sample_data, use_container_width=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Sent (7 days)", "234")
    with col2:
        st.metric("Delivery Rate", "98.5%")
    with col3:
        st.metric("Open Rate", "67.2%")


def display_notification_preferences():
    """User-facing notification preferences (for future implementation)."""
    st.subheader("Notification Preferences")

    st.info("Allow users to customize their email notification preferences.")

    st.checkbox("Weekly Progress Reports", value=True)
    st.checkbox("Coach Feedback Notifications", value=True)
    st.checkbox("Assessment Reminders", value=True)
    st.checkbox("Team Announcements", value=True)

    if st.button("Save Preferences"):
        st.success("Preferences saved!")
