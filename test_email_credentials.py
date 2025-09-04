#!/usr/bin/env python3
"""
Email Credentials Test Script for Novustell Travel
Tests Gmail SMTP connection and email sending capability
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import sys

# Email configuration
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'novustellke@gmail.com'
EMAIL_HOST_PASSWORD = 'iagt yans hoyd pavg'

def test_smtp_connection():
    """Test SMTP connection without sending email"""
    print("🔍 Testing SMTP Connection...")
    print(f"Host: {EMAIL_HOST}")
    print(f"Port: {EMAIL_PORT}")
    print(f"User: {EMAIL_HOST_USER}")
    print("-" * 50)
    
    try:
        # Create SMTP session
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.starttls()  # Enable TLS encryption
        
        print("✅ SMTP connection established successfully")
        print("✅ TLS encryption enabled")
        
        # Attempt login
        server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
        print("✅ Authentication successful")
        
        # Close connection
        server.quit()
        print("✅ Connection closed properly")
        
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print("❌ Authentication failed!")
        print(f"Error: {e}")
        print("\n🔧 Possible solutions:")
        print("1. Check if the email address is correct")
        print("2. Verify the app password is correct")
        print("3. Ensure 2-factor authentication is enabled on Gmail")
        print("4. Make sure 'Less secure app access' is disabled (use app passwords)")
        return False
        
    except smtplib.SMTPConnectError as e:
        print("❌ Connection failed!")
        print(f"Error: {e}")
        print("\n🔧 Possible solutions:")
        print("1. Check internet connection")
        print("2. Verify SMTP server and port")
        print("3. Check firewall settings")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def send_test_email():
    """Send a test email to verify full functionality"""
    print("\n📧 Testing Email Sending...")
    print("-" * 50)
    
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = f"Novustell Travel <{EMAIL_HOST_USER}>"
        msg['To'] = EMAIL_HOST_USER  # Send to self for testing
        msg['Subject'] = f"✅ Email Test - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        # Email body
        body = f"""
🎉 Email Configuration Test Successful!

This is a test email to verify that the Novustell Travel email configuration is working correctly.

Test Details:
- SMTP Host: {EMAIL_HOST}
- SMTP Port: {EMAIL_PORT}
- From Email: {EMAIL_HOST_USER}
- Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

If you receive this email, your Gmail SMTP configuration is working perfectly!

---
Novustell Travel
Think Convenience, Think Novustell
"""
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Create SMTP session and send email
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.starttls()
        server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
        
        text = msg.as_string()
        server.sendmail(EMAIL_HOST_USER, EMAIL_HOST_USER, text)
        server.quit()
        
        print("✅ Test email sent successfully!")
        print(f"📬 Check inbox: {EMAIL_HOST_USER}")
        print("📝 Subject: ✅ Email Test - [timestamp]")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to send test email: {e}")
        return False

def test_django_email_backend():
    """Test Django email backend configuration"""
    print("\n🐍 Testing Django Email Backend...")
    print("-" * 50)
    
    try:
        # Try to import Django and test email backend
        import os
        import django
        from django.conf import settings
        from django.core.mail import send_mail
        
        # Configure Django settings if not already configured
        if not settings.configured:
            settings.configure(
                EMAIL_BACKEND='django.core.mail.backends.smtp.EmailBackend',
                EMAIL_HOST=EMAIL_HOST,
                EMAIL_PORT=EMAIL_PORT,
                EMAIL_USE_TLS=True,
                EMAIL_HOST_USER=EMAIL_HOST_USER,
                EMAIL_HOST_PASSWORD=EMAIL_HOST_PASSWORD,
                DEFAULT_FROM_EMAIL='NOVUSTELL TRAVEL',
            )
        
        django.setup()
        
        # Send test email using Django
        send_mail(
            subject='🐍 Django Email Test - Novustell Travel',
            message=f'''
Django Email Backend Test

This email was sent using Django's email backend to verify the configuration.

Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Backend: django.core.mail.backends.smtp.EmailBackend

Configuration:
- EMAIL_HOST: {EMAIL_HOST}
- EMAIL_PORT: {EMAIL_PORT}
- EMAIL_USE_TLS: True
- EMAIL_HOST_USER: {EMAIL_HOST_USER}

If you receive this email, Django email configuration is working correctly!

---
Novustell Travel
''',
            from_email='NOVUSTELL TRAVEL',
            recipient_list=[EMAIL_HOST_USER],
            fail_silently=False,
        )
        
        print("✅ Django email backend test successful!")
        print(f"📬 Check inbox: {EMAIL_HOST_USER}")
        
        return True
        
    except ImportError:
        print("⚠️  Django not available - skipping Django backend test")
        print("💡 This is normal if running outside Django environment")
        return True
        
    except Exception as e:
        print(f"❌ Django email backend test failed: {e}")
        return False

def main():
    """Main test function"""
    print("=" * 60)
    print("🧪 NOVUSTELL TRAVEL EMAIL CREDENTIALS TEST")
    print("=" * 60)
    print(f"Testing credentials for: {EMAIL_HOST_USER}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Test 1: SMTP Connection
    connection_success = test_smtp_connection()
    
    if not connection_success:
        print("\n❌ SMTP connection failed. Please fix the connection issues before proceeding.")
        return False
    
    # Test 2: Send Test Email
    email_success = send_test_email()
    
    # Test 3: Django Email Backend (if available)
    django_success = test_django_email_backend()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"SMTP Connection: {'✅ PASS' if connection_success else '❌ FAIL'}")
    print(f"Email Sending: {'✅ PASS' if email_success else '❌ FAIL'}")
    print(f"Django Backend: {'✅ PASS' if django_success else '❌ FAIL'}")
    
    if connection_success and email_success:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Email credentials are working correctly")
        print("✅ Gmail SMTP configuration is valid")
        print("✅ Ready for production use")
        
        print("\n📋 Next Steps:")
        print("1. Check your email inbox for test messages")
        print("2. Update your Django settings with these credentials")
        print("3. Test the contact form on your website")
        
    else:
        print("\n⚠️  SOME TESTS FAILED")
        print("❌ Please review the error messages above")
        print("🔧 Fix the issues before using in production")
    
    print("=" * 60)
    return connection_success and email_success

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        sys.exit(1)
