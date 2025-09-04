#!/usr/bin/env python3
"""
Quick Email Test - Update credentials and run
"""

import smtplib
from email.mime.text import MIMEText

# UPDATE THESE CREDENTIALS
EMAIL_HOST_USER = 'novustellke@gmail.com'
EMAIL_HOST_PASSWORD = 'iagt yans hoyd pavg'  # Replace with new app password

def quick_test():
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
        
        # Send test email
        msg = MIMEText('Test email from Novustell Travel')
        msg['Subject'] = 'Quick Email Test'
        msg['From'] = EMAIL_HOST_USER
        msg['To'] = EMAIL_HOST_USER
        
        server.send_message(msg)
        server.quit()
        
        print("✅ SUCCESS: Email credentials are working!")
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Quick Email Test")
    print(f"Testing: {EMAIL_HOST_USER}")
    print("-" * 40)
    quick_test()
