
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
    import logging
    logging.info("Starting email test...")
    
    # Check mail configuration is valid
    if not hasattr(mail, 'send'):
        logging.error("Mail object doesn't have send method")
        return {
            "success": False,
            "message": "Invalid mail configuration. Mail object doesn't have send method."
        }
    
    try:
        # Validate mail settings
        if not mail.server or not mail.username or not mail.password:
            logging.error(f"Missing mail configuration: Server: {bool(mail.server)}, Username: {bool(mail.username)}, Password: {bool(mail.password)}")
            return {
                "success": False,
                "message": "Email configuration incomplete. Check MAIL_USERNAME, MAIL_PASSWORD and MAIL_SERVER settings."
            }
        
        recipient = test_email or mail.default_sender
        if not recipient:
            logging.error("No recipient specified and no default sender configured")
            return {
                "success": False,
                "message": "No recipient specified and no default sender configured"
            }
        
        logging.info(f"Attempting to send test email to: {recipient}")
        
        msg = Message(
            subject="Email Configuration Test",
            recipients=[recipient],
            body="This is a test email to verify that the email configuration is working correctly."
        )
        
        # Try sending with explicit debug information
        mail.send(msg)
        
        logging.info(f"Test email sent successfully to {recipient}")
        return {
            "success": True,
            "message": f"Test email sent successfully to {recipient}"
        }
    except Exception as e:
        logging.error(f"Error sending test email: {str(e)}", exc_info=True)
        
        # Provide more detailed error information
        error_details = str(e)
        suggestion = ""
        
        if "getaddrinfo failed" in error_details:
            suggestion = "There seems to be a network connectivity issue or DNS resolution problem."
        elif "Authentication" in error_details:
            suggestion = "Authentication failed. Ensure your MAIL_USERNAME and MAIL_PASSWORD are correct. If using Gmail, make sure you're using an App Password if 2FA is enabled."
        elif "SSLError" in error_details or "SSL" in error_details:
            suggestion = "SSL/TLS error. Your email provider may require different SSL settings."
        elif "Timeout" in error_details:
            suggestion = "Connection timed out. Check your network settings or try again later."
        
        return {
            "success": False,
            "message": f"Error sending test email: {str(e)}\n\nSuggestion: {suggestion if suggestion else 'Check your email configuration and network settings.'}"
        }
