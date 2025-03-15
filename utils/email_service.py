
from flask_mail import Message
import logging

def send_welcome_email(mail, recipient_email, recipient_name):
    """
    Send a welcome email to new users
    
    Args:
        mail: Flask-Mail instance
        recipient_email: Email address of the recipient
        recipient_name: Name of the recipient
        
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    try:
        subject = "Welcome to the Youth Hockey Development Tracker"
        body = f"""
        Hello {recipient_name},
        
        Welcome to the Youth Hockey Development Tracker! 
        
        You can now track player development, manage teams, and provide feedback 
        to players all in one place.
        
        If you have any questions, please don't hesitate to reach out.
        
        Best regards,
        The Youth Hockey Development Team
        """
        
        msg = Message(
            subject=subject,
            recipients=[recipient_email],
            body=body
        )
        
        mail.send(msg)
        logging.info(f"Welcome email sent successfully to {recipient_email}")
        return True
    except Exception as e:
        logging.error(f"Error sending welcome email to {recipient_email}: {str(e)}")
        return False

def test_email_configuration(mail, test_email=None):
    """
    Test the email configuration by sending a test email
    
    Args:
        mail: Flask-Mail instance
        test_email: Email address to send test to (optional)
        
    Returns:
        dict: Result of the test with status and message
    """
    try:
        recipient = test_email or mail.default_sender
        if not recipient:
            return {
                "success": False,
                "message": "No recipient specified and no default sender configured"
            }
        
        msg = Message(
            subject="Email Configuration Test",
            recipients=[recipient],
            body="This is a test email to verify that the email configuration is working correctly."
        )
        
        mail.send(msg)
        
        return {
            "success": True,
            "message": f"Test email sent successfully to {recipient}"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error sending test email: {str(e)}"
        }
