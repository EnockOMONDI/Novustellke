#!/usr/bin/env python3
"""
CRITICAL PRODUCTION EMAIL FIX TEST
Test script to verify the email timeout and authentication fix
"""

import os
import sys
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Email configuration
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_TIMEOUT = 30  # 30 seconds timeout

# CORRECT production credentials
EMAIL_HOST_USER = 'novustellke@gmail.com'
EMAIL_HOST_PASSWORD = 'eoie dhrq cioh gxhz'  # Updated app password

def test_smtp_connection_with_timeout():
    """Test SMTP connection with timeout to prevent hanging"""
    print("🔧 Testing SMTP Connection with Timeout...")
    print("-" * 50)
    
    try:
        start_time = time.time()
        
        # Create SMTP connection with timeout
        print(f"📡 Connecting to {EMAIL_HOST}:{EMAIL_PORT} with {EMAIL_TIMEOUT}s timeout...")
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT, timeout=EMAIL_TIMEOUT)
        
        print("🔐 Starting TLS encryption...")
        server.starttls()
        
        print("🔑 Authenticating with Gmail...")
        server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
        
        connection_time = time.time() - start_time
        print(f"✅ SMTP connection successful in {connection_time:.2f} seconds")
        
        # Test sending a quick email
        print("📧 Sending test email...")
        msg = MIMEMultipart()
        msg['From'] = f"Novustell Travel <{EMAIL_HOST_USER}>"
        msg['To'] = EMAIL_HOST_USER
        msg['Subject'] = "🚨 CRITICAL FIX TEST - Email System Restored"
        
        body = f"""
CRITICAL PRODUCTION FIX VERIFICATION

✅ Email system has been restored!
✅ SMTP timeout fixed: {EMAIL_TIMEOUT} seconds
✅ Correct password configured: {EMAIL_HOST_PASSWORD[:4]}****
✅ Connection time: {connection_time:.2f} seconds

The newsletter subscription and all email functions should now work correctly.

Test completed at: {time.strftime('%Y-%m-%d %H:%M:%S')}

---
Novustell Travel Technical Team
"""
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Send the email
        text = msg.as_string()
        server.sendmail(EMAIL_HOST_USER, [EMAIL_HOST_USER], text)
        
        total_time = time.time() - start_time
        print(f"✅ Test email sent successfully in {total_time:.2f} seconds total")
        
        server.quit()
        print("🔌 SMTP connection closed")
        
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ SMTP Authentication Error: {e}")
        print("🔍 Check if the email password is correct")
        return False
        
    except smtplib.SMTPConnectError as e:
        print(f"❌ SMTP Connection Error: {e}")
        print("🔍 Check network connectivity and SMTP server")
        return False
        
    except smtplib.SMTPServerDisconnected as e:
        print(f"❌ SMTP Server Disconnected: {e}")
        print("🔍 Server may have closed the connection")
        return False
        
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"❌ Email test failed after {elapsed:.2f} seconds: {e}")
        print(f"🔍 Error type: {type(e).__name__}")
        return False

def test_django_email_backend():
    """Test Django email backend with the fixed configuration"""
    print("\n🐍 Testing Django Email Backend...")
    print("-" * 50)
    
    try:
        # Set up Django environment
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tours_travels.settings')
        
        import django
        from django.conf import settings
        from django.core.mail import send_mail
        
        # Configure Django if not already configured
        if not settings.configured:
            django.setup()
        
        print(f"📧 Email backend: {settings.EMAIL_BACKEND}")
        print(f"🏠 Email host: {settings.EMAIL_HOST}:{settings.EMAIL_PORT}")
        print(f"👤 Email user: {settings.EMAIL_HOST_USER}")
        print(f"⏱️ Email timeout: {getattr(settings, 'EMAIL_TIMEOUT', 'Not set')}")
        
        # Test Django send_mail function
        start_time = time.time()
        
        result = send_mail(
            subject='🐍 Django Email Test - CRITICAL FIX VERIFICATION',
            message=f'''
Django Email Backend Test - CRITICAL FIX

✅ Email timeout configured: {getattr(settings, 'EMAIL_TIMEOUT', 'Not set')} seconds
✅ Correct password in use: {settings.EMAIL_HOST_PASSWORD[:4]}****
✅ SMTP settings verified

This confirms the Django email system is working correctly after the fix.

Test timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}
            ''',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.EMAIL_HOST_USER],
            fail_silently=False,
        )
        
        send_time = time.time() - start_time
        
        if result == 1:
            print(f"✅ Django email sent successfully in {send_time:.2f} seconds")
            return True
        else:
            print(f"❌ Django email failed to send (result: {result})")
            return False
            
    except Exception as e:
        elapsed = time.time() - start_time if 'start_time' in locals() else 0
        print(f"❌ Django email test failed after {elapsed:.2f} seconds: {e}")
        return False

def main():
    """Run all email tests to verify the fix"""
    print("🚨 CRITICAL PRODUCTION EMAIL FIX VERIFICATION")
    print("=" * 60)
    print("Testing the fix for newsletter subscription timeout issue")
    print("=" * 60)
    
    # Test 1: Direct SMTP connection
    smtp_success = test_smtp_connection_with_timeout()
    
    # Test 2: Django email backend
    django_success = test_django_email_backend()
    
    # Summary
    print("\n📊 TEST RESULTS SUMMARY")
    print("=" * 30)
    print(f"SMTP Connection Test: {'✅ PASS' if smtp_success else '❌ FAIL'}")
    print(f"Django Email Test:    {'✅ PASS' if django_success else '❌ FAIL'}")
    
    if smtp_success and django_success:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Email system is working correctly")
        print("✅ Newsletter subscriptions should work now")
        print("✅ Production issue is RESOLVED")
        return 0
    else:
        print("\n⚠️ SOME TESTS FAILED!")
        print("❌ Email system may still have issues")
        print("❌ Further investigation required")
        return 1

if __name__ == "__main__":
    sys.exit(main())
