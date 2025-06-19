#!/usr/bin/env python3
"""
Simple Gmail SMTP test script
"""
import smtplib
import ssl

def test_gmail_connection():
    # Gmail SMTP settings
    smtp_server = "smtp.gmail.com"
    port = 587
    sender_email = "broker.pagetest@gmail.com"
    password = "102572"  # This should be your 16-character app password
    
    # Create a secure SSL context
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    
    try:
        # Create SMTP session
        server = smtplib.SMTP(smtp_server, port)
        server.starttls(context=context)
        
        # Login
        print(f"Attempting to login with email: {sender_email}")
        print(f"Password length: {len(password)} characters")
        server.login(sender_email, password)
        print("✅ Login successful!")
        
        # Send test email
        receiver_email = "broker.pagetest@gmail.com"
        message = """Subject: Test Email from Broker.Page

This is a test email to verify Gmail SMTP configuration.
"""
        
        server.sendmail(sender_email, receiver_email, message)
        print(f"✅ Test email sent successfully to {receiver_email}")
        
        server.quit()
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ Authentication failed: {e}")
        print("\nPossible solutions:")
        print("1. Enable 2-Factor Authentication on your Gmail account")
        print("2. Generate a new App Password:")
        print("   - Go to Google Account settings")
        print("   - Security → 2-Step Verification → App passwords")
        print("   - Generate a new app password for 'Mail'")
        print("   - Use the 16-character password (without spaces)")
        return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("Testing Gmail SMTP connection...")
    test_gmail_connection() 