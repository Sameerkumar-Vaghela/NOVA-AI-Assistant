import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(sender_email, sender_password, recipient_email, subject, message):
    """
    Send an email using Gmail SMTP.
    
    Note: For Gmail, you need to use an App Password if 2FA is enabled.
    """
    try:
        # Create message container
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject

        # Add body to email
        body = f"""
        Nova Assistant Reminder:
        
        {message}
        
        Best regards,
        Nova AI Assistant
        """
        msg.attach(MIMEText(body, 'plain'))

        # Create SMTP session
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        
        # Login to the server
        server.login(sender_email, sender_password)
        
        # Send email
        text = msg.as_string()
        server.sendmail(sender_email, recipient_email, text)
        
        # Close the connection
        server.quit()
        
        return True, "Email sent successfully"
    except Exception as e:
        error_message = str(e)
        if "Authentication" in error_message:
            return False, "Email authentication failed. Please check the email credentials."
        return False, f"Failed to send email: {error_message}" 