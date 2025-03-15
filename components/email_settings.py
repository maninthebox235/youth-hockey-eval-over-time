
import streamlit as st
import os
from app import mail
from utils.email_service import test_email_configuration
import logging

def display_email_settings():
    """Display and manage email settings"""
    st.header("Email Settings")
    
    # Display current configuration
    with st.expander("Current Email Configuration", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**SMTP Settings**")
            st.write(f"Mail Server: {mail.server}")
            st.write(f"Mail Port: {mail.port}")
            st.write(f"Use TLS: {mail.use_tls}")
        
        with col2:
            st.write("**Authentication**")
            st.write(f"Username: {os.getenv('MAIL_USERNAME') or 'Not configured'}")
            st.write(f"Password: {'Configured' if os.getenv('MAIL_PASSWORD') else 'Not configured'}")
            st.write(f"Default Sender: {os.getenv('MAIL_DEFAULT_SENDER') or 'Not configured'}")
    
    # Test email functionality
    st.subheader("Test Email Configuration")
    test_email = st.text_input("Test email address", 
                              placeholder="Enter an email to receive the test message")
    
    if st.button("Send Test Email"):
        with st.spinner("Sending test email..."):
            if not test_email:
                st.error("Please enter a valid email address")
            else:
                result = test_email_configuration(mail, test_email)
                if result['success']:
                    st.success(result['message'])
                else:
                    st.error(result['message'])
                    # Show troubleshooting information
                    with st.expander("Troubleshooting Information"):
                        st.write("""
                        ### Common Email Issues:
                        
                        1. **Gmail Security Settings**: If using Gmail, you need to:
                           - Enable "Less secure app access" OR
                           - Use an App Password (recommended for 2FA accounts)
                        
                        2. **SMTP Credentials**: Ensure MAIL_USERNAME and MAIL_PASSWORD are correctly set in your environment variables
                        
                        3. **Network Restrictions**: Some cloud environments restrict outbound SMTP traffic
                        
                        4. **Rate Limiting**: Email providers might limit the number of emails you can send
                        """)
                        
                        st.write("#### Gmail App Password Setup:")
                        st.write("""
                        1. Go to your Google Account
                        2. Select Security
                        3. Under "Signing in to Google," select App Passwords (you may need to enable 2-Step Verification first)
                        4. Select the app (Other) and device you want to generate the app password for
                        5. Follow the instructions to generate the App Password
                        6. Use this password in your MAIL_PASSWORD environment variable
                        """)
                        
    # Update email settings (redirects to Secrets)
    st.subheader("Update Email Settings")
    st.write("To update your email configuration, you need to set the following environment variables:")
    
    st.code("""
    MAIL_USERNAME=your-email@gmail.com
    MAIL_PASSWORD=your-app-password
    MAIL_DEFAULT_SENDER=your-email@gmail.com
    """)
    
    if st.button("Update Email Settings"):
        st.info("To update email settings, you need to configure environment variables in the Secrets tool.")
        st.markdown("<a href='#' id='open-secrets' style='font-weight: bold;'>Click here to open Secrets Tool</a>", unsafe_allow_html=True)
        st.markdown("""
        <script>
        document.getElementById('open-secrets').addEventListener('click', function() {
            parent.postMessage({ type: 'openTool', tool: 'envEditor' }, '*');
        });
        </script>
        """, unsafe_allow_html=True)

def send_email_interface():
    """Interface for sending emails manually"""
    st.header("Send Email")
    
    recipient = st.text_input("Recipient Email")
    subject = st.text_input("Subject")
    body = st.text_area("Message Body", height=200)
    
    if st.button("Send Email"):
        if not recipient or not subject or not body:
            st.error("All fields are required")
            return
            
        from flask_mail import Message
        
        try:
            msg = Message(
                subject=subject,
                recipients=[recipient],
                body=body
            )
            
            mail.send(msg)
            st.success(f"Email sent successfully to {recipient}")
        except Exception as e:
            logging.error(f"Error sending email: {str(e)}")
            st.error(f"Error sending email: {str(e)}")
