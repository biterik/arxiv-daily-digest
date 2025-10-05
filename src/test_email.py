#!/usr/bin/env python3
"""
Simple email test script
Copyright (c) 2025 Erik Bitzek
Licensed under GNU AGPL v3

Test your email configuration before running the full digest.
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime


def test_email():
    """Test email sending with detailed debug output."""
    
    print("="*80)
    print("EMAIL CONFIGURATION TEST")
    print("="*80)
    print()
    
    # Get credentials
    smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.getenv('SMTP_PORT', '587'))
    smtp_user = os.getenv('SMTP_USER')
    smtp_password = os.getenv('SMTP_PASSWORD')
    recipient = "e.bitzek@mpie.de"
    
    # Display configuration
    print("Configuration:")
    print(f"  SMTP Server: {smtp_server}")
    print(f"  SMTP Port: {smtp_port}")
    print(f"  SMTP User: {smtp_user if smtp_user else '❌ NOT SET'}")
    print(f"  SMTP Password: {'✓ Set' if smtp_password else '❌ NOT SET'}")
    print(f"  Recipient: {recipient}")
    print()
    
    # Check for missing credentials
    if not smtp_user:
        print("❌ ERROR: SMTP_USER not set")
        print("\nSet it with:")
        print('  export SMTP_USER="your.email@gmail.com"')
        return False
    
    if not smtp_password:
        print("❌ ERROR: SMTP_PASSWORD not set")
        print("\nFor Gmail:")
        print("  1. Enable 2FA at: https://myaccount.google.com/security")
        print("  2. Generate App Password at: https://myaccount.google.com/apppasswords")
        print("  3. Set it with:")
        print('     export SMTP_PASSWORD="xxxx xxxx xxxx xxxx"')
        return False
    
    # Create test message
    msg = MIMEMultipart()
    msg['From'] = smtp_user
    msg['To'] = recipient
    msg['Subject'] = f"arXiv Digest Test - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    
    body = """This is a test email from your arXiv Daily Digest setup.

If you're reading this, your email configuration is working correctly! 🎉

Next steps:
1. Run the full digest: python main.py
2. Set up GitHub Actions for daily automation

--
arXiv Daily Digest
"""
    
    msg.attach(MIMEText(body, 'plain'))
    
    # Attempt to send
    print("="*80)
    print("SENDING TEST EMAIL")
    print("="*80)
    print()
    
    try:
        print(f"Step 1: Connecting to {smtp_server}:{smtp_port}...")
        server = smtplib.SMTP(smtp_server, smtp_port, timeout=30)
        server.set_debuglevel(1)  # Show detailed SMTP conversation
        print("  ✓ Connected\n")
        
        print("Step 2: Starting TLS encryption...")
        server.starttls()
        print("  ✓ TLS started\n")
        
        print(f"Step 3: Logging in as {smtp_user}...")
        server.login(smtp_user, smtp_password)
        print("  ✓ Login successful\n")
        
        print(f"Step 4: Sending message to {recipient}...")
        server.send_message(msg)
        print("  ✓ Message sent\n")
        
        print("Step 5: Closing connection...")
        server.quit()
        print("  ✓ Connection closed\n")
        
        print("="*80)
        print("✅ SUCCESS!")
        print("="*80)
        print(f"\nTest email sent to: {recipient}")
        print("Check your inbox (and spam folder)!")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print("\n" + "="*80)
        print("❌ AUTHENTICATION FAILED")
        print("="*80)
        print(f"\nError: {e}")
        print("\n🔧 How to fix:")
        print("\nFor Gmail:")
        print("  1. Make sure 2-Factor Authentication is enabled")
        print("  2. Go to: https://myaccount.google.com/apppasswords")
        print("  3. Create a new App Password for 'Mail' / 'Other'")
        print("  4. Use that 16-character password (not your regular password)")
        print('  5. Set it: export SMTP_PASSWORD="xxxx xxxx xxxx xxxx"')
        print("\nFor other email providers:")
        print("  - Check if SMTP access is enabled")
        print("  - Verify username and password are correct")
        print(f"  - Confirm SMTP server is: {smtp_server}")
        return False
        
    except smtplib.SMTPConnectError as e:
        print("\n" + "="*80)
        print("❌ CONNECTION FAILED")
        print("="*80)
        print(f"\nError: {e}")
        print("\n🔧 How to fix:")
        print(f"  - Verify SMTP server: {smtp_server}")
        print(f"  - Verify SMTP port: {smtp_port}")
        print("  - Check your internet connection")
        print("  - Check if firewall is blocking SMTP")
        return False
        
    except Exception as e:
        print("\n" + "="*80)
        print("❌ UNEXPECTED ERROR")
        print("="*80)
        print(f"\nError type: {type(e).__name__}")
        print(f"Error message: {e}")
        print("\nFull traceback:")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n")
    success = test_email()
    print("\n")
    
    if success:
        print("🎉 Email configuration is working!")
        print("\nYou can now run the full digest:")
        print("  cd src")
        print("  python main.py")
    else:
        print("❌ Email test failed. Fix the issues above and try again.")
        print("\nQuick checklist:")
        print("  ✓ SMTP_USER is set")
        print("  ✓ SMTP_PASSWORD is set (use App Password for Gmail)")
        print("  ✓ 2FA is enabled (for Gmail)")
        print("  ✓ SMTP_SERVER is correct")
    
    print("\n")