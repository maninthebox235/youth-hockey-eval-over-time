"""
Email notification service for automated player updates and alerts.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from flask_mail import Message
import logging
from database.models import (
    Player,
    User,
    CoachFeedback,
    PlayerHistory,
    Team,
    TeamMembership,
    db,
)
from utils.type_converter import to_int, to_float, to_str

logger = logging.getLogger(__name__)


class NotificationService:
    """Service for managing email notifications."""

    def __init__(self, mail):
        """Initialize notification service.

        Args:
            mail: Flask-Mail instance
        """
        self.mail = mail

    def send_feedback_notification(
        self, player_id: int, feedback_id: int, recipient_email: str
    ) -> bool:
        """
        Send notification when new coach feedback is submitted.

        Args:
            player_id: ID of the player who received feedback
            feedback_id: ID of the feedback record
            recipient_email: Email address of the recipient (parent/player)

        Returns:
            bool: True if email sent successfully
        """
        try:
            player = Player.query.get(player_id)
            feedback = CoachFeedback.query.get(feedback_id)

            if not player or not feedback:
                logger.error(
                    f"Player or feedback not found: player_id={player_id}, feedback_id={feedback_id}"
                )
                return False

            subject = f"New Coach Feedback for {player.name}"

            feedback_date = feedback.date.strftime("%B %d, %Y")
            coach_name = feedback.coach_name or "Coach"

            body = f"""
Hello,

New feedback has been submitted for {player.name} by {coach_name} on {feedback_date}.

Key Highlights:
- Overall Rating: {self._get_overall_rating(feedback)}/5
- Strengths: {self._extract_strengths(feedback)}
- Areas for Improvement: {self._extract_weaknesses(feedback)}

{f'Coach Comments: {feedback.notes}' if feedback.notes else ''}

View the full feedback details by logging into your account at the Youth Hockey Development Tracker.

Best regards,
Youth Hockey Development Team
"""

            html = self._create_feedback_html(player, feedback, coach_name, feedback_date)

            msg = Message(
                subject=subject, recipients=[recipient_email], body=body, html=html
            )

            self.mail.send(msg)
            logger.info(
                f"Feedback notification sent to {recipient_email} for player {player.name}"
            )
            return True

        except Exception as e:
            logger.error(f"Error sending feedback notification: {str(e)}")
            return False

    def send_weekly_progress_report(
        self, player_id: int, recipient_email: str
    ) -> bool:
        """
        Send weekly progress report for a player.

        Args:
            player_id: ID of the player
            recipient_email: Email address of the recipient

        Returns:
            bool: True if email sent successfully
        """
        try:
            player = Player.query.get(player_id)
            if not player:
                logger.error(f"Player not found: player_id={player_id}")
                return False

            week_ago = datetime.now() - timedelta(days=7)
            recent_history = (
                PlayerHistory.query.filter_by(player_id=player_id)
                .filter(PlayerHistory.date >= week_ago)
                .order_by(PlayerHistory.date.desc())
                .all()
            )

            recent_feedback = (
                CoachFeedback.query.filter_by(player_id=player_id)
                .filter(CoachFeedback.date >= week_ago)
                .order_by(CoachFeedback.date.desc())
                .all()
            )

            subject = f"Weekly Progress Report for {player.name}"

            body = f"""
Hello,

Here's the weekly progress report for {player.name}:

Current Stats:
- Age: {player.age} ({player.age_group})
- Position: {player.position}
{self._format_position_stats(player)}

This Week's Activity:
- Assessments: {len(recent_history)}
- Coach Feedback Received: {len(recent_feedback)}

{self._format_progress_summary(player, recent_history)}

Keep up the great work!

Best regards,
Youth Hockey Development Team
"""

            html = self._create_progress_report_html(
                player, recent_history, recent_feedback
            )

            msg = Message(
                subject=subject, recipients=[recipient_email], body=body, html=html
            )

            self.mail.send(msg)
            logger.info(
                f"Weekly progress report sent to {recipient_email} for player {player.name}"
            )
            return True

        except Exception as e:
            logger.error(f"Error sending progress report: {str(e)}")
            return False

    def send_assessment_reminder(
        self, player_id: int, recipient_email: str, days_since_last: int
    ) -> bool:
        """
        Send reminder to assess player performance.

        Args:
            player_id: ID of the player
            recipient_email: Email address of the recipient
            days_since_last: Number of days since last assessment

        Returns:
            bool: True if email sent successfully
        """
        try:
            player = Player.query.get(player_id)
            if not player:
                logger.error(f"Player not found: player_id={player_id}")
                return False

            subject = f"Time to Assess {player.name}'s Progress"

            body = f"""
Hello,

It's been {days_since_last} days since the last assessment for {player.name}.

Regular assessments help track progress and identify areas for improvement. 
Consider scheduling a skills assessment soon to keep their development on track.

Log in to the Youth Hockey Development Tracker to add a new assessment.

Best regards,
Youth Hockey Development Team
"""

            html = self._create_reminder_html(player, days_since_last)

            msg = Message(
                subject=subject, recipients=[recipient_email], body=body, html=html
            )

            self.mail.send(msg)
            logger.info(
                f"Assessment reminder sent to {recipient_email} for player {player.name}"
            )
            return True

        except Exception as e:
            logger.error(f"Error sending assessment reminder: {str(e)}")
            return False

    def send_team_announcement(
        self, team_id: int, subject: str, message: str, sender_name: str
    ) -> int:
        """
        Send announcement to all team members.

        Args:
            team_id: ID of the team
            subject: Email subject
            message: Announcement message
            sender_name: Name of the person sending the announcement

        Returns:
            int: Number of emails sent successfully
        """
        try:
            team = Team.query.get(team_id)
            if not team:
                logger.error(f"Team not found: team_id={team_id}")
                return 0

            memberships = TeamMembership.query.filter_by(
                team_id=team_id, is_active=True
            ).all()

            sent_count = 0
            for membership in memberships:
                player = Player.query.get(membership.player_id)
                if player and player.user:
                    user = User.query.get(player.user_id)
                    if user and user.email:
                        body = f"""
Hello,

{sender_name} has sent an announcement for {team.name}:

{message}

Best regards,
{sender_name}
Youth Hockey Development Team
"""

                        html = self._create_announcement_html(
                            team, message, sender_name
                        )

                        msg = Message(
                            subject=f"[{team.name}] {subject}",
                            recipients=[user.email],
                            body=body,
                            html=html,
                        )

                        try:
                            self.mail.send(msg)
                            sent_count += 1
                        except Exception as e:
                            logger.error(
                                f"Error sending announcement to {user.email}: {str(e)}"
                            )

            logger.info(
                f"Team announcement sent to {sent_count} recipients for team {team.name}"
            )
            return sent_count

        except Exception as e:
            logger.error(f"Error sending team announcement: {str(e)}")
            return 0


    def _get_overall_rating(self, feedback: CoachFeedback) -> float:
        """Calculate overall rating from feedback."""
        ratings = []
        for attr in [
            "skating_stride",
            "skating_speed",
            "edge_control",
            "shooting_power",
            "shooting_accuracy",
        ]:
            value = getattr(feedback, attr, None)
            if value is not None:
                ratings.append(value)

        return round(sum(ratings) / len(ratings), 1) if ratings else 0.0

    def _extract_strengths(self, feedback: CoachFeedback) -> str:
        """Extract top strengths from feedback."""
        strengths = []
        attributes = {
            "skating_speed": "Skating Speed",
            "shooting_accuracy": "Shooting Accuracy",
            "passing_accuracy": "Passing",
            "hockey_sense": "Hockey Sense",
        }

        for attr, name in attributes.items():
            value = getattr(feedback, attr, None)
            if value and value >= 4:
                strengths.append(name)

        return ", ".join(strengths[:3]) if strengths else "Various areas"

    def _extract_weaknesses(self, feedback: CoachFeedback) -> str:
        """Extract areas needing improvement from feedback."""
        weaknesses = []
        attributes = {
            "skating_speed": "Skating Speed",
            "shooting_accuracy": "Shooting Accuracy",
            "passing_accuracy": "Passing",
            "hockey_sense": "Hockey Sense",
        }

        for attr, name in attributes.items():
            value = getattr(feedback, attr, None)
            if value and value <= 2:
                weaknesses.append(name)

        return ", ".join(weaknesses[:3]) if weaknesses else "Continue current development"

    def _format_position_stats(self, player: Player) -> str:
        """Format position-specific stats for email."""
        if player.position == "Goalie":
            return f"- Save Percentage: {player.save_percentage or 'N/A'}%\n- Reaction Time: {player.reaction_time or 'N/A'}/100"
        else:
            return f"- Skating Speed: {player.skating_speed or 'N/A'}/100\n- Shooting Accuracy: {player.shooting_accuracy or 'N/A'}/100"

    def _format_progress_summary(
        self, player: Player, recent_history: List[PlayerHistory]
    ) -> str:
        """Format progress summary from recent history."""
        if not recent_history or len(recent_history) < 2:
            return "Not enough data to show trends yet."

        latest = recent_history[0]
        previous = recent_history[-1]

        improvements = []
        if player.position != "Goalie":
            if (
                latest.skating_speed
                and previous.skating_speed
                and latest.skating_speed > previous.skating_speed
            ):
                improvements.append("Skating Speed")
            if (
                latest.shooting_accuracy
                and previous.shooting_accuracy
                and latest.shooting_accuracy > previous.shooting_accuracy
            ):
                improvements.append("Shooting Accuracy")

        if improvements:
            return f"Improvements: {', '.join(improvements)}"
        return "Keep working on fundamentals"

    def _create_feedback_html(
        self, player: Player, feedback: CoachFeedback, coach_name: str, date: str
    ) -> str:
        """Create HTML email template for feedback notification."""
        return f"""
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd;">
        <h2 style="color: #1a5490;">New Coach Feedback</h2>
        <p><strong>Player:</strong> {player.name}</p>
        <p><strong>Coach:</strong> {coach_name}</p>
        <p><strong>Date:</strong> {date}</p>
        <p><strong>Overall Rating:</strong> {self._get_overall_rating(feedback)}/5</p>
        
        <h3 style="color: #1a5490;">Highlights</h3>
        <p><strong>Strengths:</strong> {self._extract_strengths(feedback)}</p>
        <p><strong>Focus Areas:</strong> {self._extract_weaknesses(feedback)}</p>
        
        {f'<p><strong>Coach Notes:</strong> {feedback.notes}</p>' if feedback.notes else ''}
        
        <p style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd;">
            <a href="#" style="background-color: #1a5490; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                View Full Feedback
            </a>
        </p>
    </div>
</body>
</html>
"""

    def _create_progress_report_html(
        self,
        player: Player,
        recent_history: List[PlayerHistory],
        recent_feedback: List[CoachFeedback],
    ) -> str:
        """Create HTML email template for progress report."""
        return f"""
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd;">
        <h2 style="color: #1a5490;">Weekly Progress Report</h2>
        <p><strong>Player:</strong> {player.name}</p>
        <p><strong>Age/Position:</strong> {player.age} years old, {player.position}</p>
        
        <h3 style="color: #1a5490;">This Week's Activity</h3>
        <p>Assessments: {len(recent_history)}</p>
        <p>Coach Feedback: {len(recent_feedback)}</p>
        
        <h3 style="color: #1a5490;">Progress Summary</h3>
        <p>{self._format_progress_summary(player, recent_history)}</p>
        
        <p style="margin-top: 30px; font-style: italic;">Keep up the great work!</p>
    </div>
</body>
</html>
"""

    def _create_reminder_html(self, player: Player, days_since: int) -> str:
        """Create HTML email template for assessment reminder."""
        return f"""
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd;">
        <h2 style="color: #f39c12;">Assessment Reminder</h2>
        <p><strong>Player:</strong> {player.name}</p>
        <p>It's been <strong>{days_since} days</strong> since the last assessment.</p>
        
        <p>Regular assessments help track progress and identify areas for improvement. 
        Consider scheduling a skills assessment soon to keep development on track.</p>
        
        <p style="margin-top: 30px;">
            <a href="#" style="background-color: #f39c12; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                Add Assessment Now
            </a>
        </p>
    </div>
</body>
</html>
"""

    def _create_announcement_html(
        self, team: Team, message: str, sender_name: str
    ) -> str:
        """Create HTML email template for team announcement."""
        return f"""
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd;">
        <h2 style="color: #1a5490;">{team.name} Announcement</h2>
        <p><strong>From:</strong> {sender_name}</p>
        
        <div style="margin: 20px 0; padding: 15px; background-color: #f9f9f9; border-left: 4px solid #1a5490;">
            {message.replace(chr(10), '<br>')}
        </div>
        
        <p style="margin-top: 30px; font-size: 0.9em; color: #666;">
            This announcement was sent to all active members of {team.name}.
        </p>
    </div>
</body>
</html>
"""



def send_weekly_reports_batch(mail, app_context):
    """
    Send weekly progress reports to all active players.
    This should be run as a scheduled task (e.g., every Monday morning).
    
    Args:
        mail: Flask-Mail instance
        app_context: Flask application context
    """
    with app_context:
        notification_service = NotificationService(mail)
        
        week_ago = datetime.now() - timedelta(days=7)
        players = Player.query.all()
        
        sent_count = 0
        for player in players:
            if player.user and player.user.email:
                try:
                    notification_service.send_weekly_progress_report(
                        player.id, player.user.email
                    )
                    sent_count += 1
                except Exception as e:
                    logger.error(f"Error sending report for player {player.id}: {str(e)}")
        
        logger.info(f"Sent {sent_count} weekly progress reports")
        return sent_count


def send_assessment_reminders_batch(mail, app_context, days_threshold=30):
    """
    Send reminders for players who haven't been assessed recently.
    
    Args:
        mail: Flask-Mail instance
        app_context: Flask application context
        days_threshold: Number of days without assessment to trigger reminder
    """
    with app_context:
        notification_service = NotificationService(mail)
        threshold_date = datetime.now() - timedelta(days=days_threshold)
        
        sent_count = 0
        players = Player.query.all()
        
        for player in players:
            last_history = (
                PlayerHistory.query.filter_by(player_id=player.id)
                .order_by(PlayerHistory.date.desc())
                .first()
            )
            
            if not last_history or last_history.date < threshold_date:
                if player.user and player.user.email:
                    days_since = (
                        (datetime.now() - last_history.date).days
                        if last_history
                        else days_threshold
                    )
                    try:
                        notification_service.send_assessment_reminder(
                            player.id, player.user.email, days_since
                        )
                        sent_count += 1
                    except Exception as e:
                        logger.error(
                            f"Error sending reminder for player {player.id}: {str(e)}"
                        )
        
        logger.info(f"Sent {sent_count} assessment reminders")
        return sent_count
