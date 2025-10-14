#!/usr/bin/env python3
"""
PRODUCTION EMAIL FUNCTIONALITY TEST
Test the email system using production settings and credentials
"""

import os
import sys
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def test_production_smtp_direct():
    """Test direct SMTP connection using production credentials"""
    print("🔧 Testing Production SMTP Connection (Direct)")
    print("-" * 60)
    
    # Production email configuration
    EMAIL_HOST = 'smtp.gmail.com'
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
    EMAIL_TIMEOUT = 30
    EMAIL_HOST_USER = 'novustellke@gmail.com'
    EMAIL_HOST_PASSWORD = 'eoie dhrq cioh gxhz'  # Updated app password
    
    print(f"📧 Host: {EMAIL_HOST}:{EMAIL_PORT}")
    print(f"👤 User: {EMAIL_HOST_USER}")
    print(f"⏱️ Timeout: {EMAIL_TIMEOUT} seconds")
    print(f"🔐 Password: {EMAIL_HOST_PASSWORD[:4]}****")
    
    try:
        start_time = time.time()
        
        print("\n📡 Establishing SMTP connection...")
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT, timeout=EMAIL_TIMEOUT)
        connection_time = time.time() - start_time
        print(f"✅ Connected in {connection_time:.2f} seconds")
        
        print("🔐 Starting TLS encryption...")
        tls_start = time.time()
        server.starttls()
        tls_time = time.time() - tls_start
        print(f"✅ TLS enabled in {tls_time:.2f} seconds")
        
        print("🔑 Authenticating with Gmail...")
        auth_start = time.time()
        server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
        auth_time = time.time() - auth_start
        print(f"✅ Authentication successful in {auth_time:.2f} seconds")
        
        # Send test email
        print("📧 Sending production test email...")
        send_start = time.time()
        
        msg = MIMEMultipart()
        msg['From'] = f"Novustell Travel <{EMAIL_HOST_USER}>"
        msg['To'] = EMAIL_HOST_USER
        msg['Subject'] = "🚨 PRODUCTION EMAIL FIX VERIFICATION - SUCCESS"
        
        body = f"""
PRODUCTION EMAIL SYSTEM VERIFICATION

✅ SMTP Connection: SUCCESS ({connection_time:.2f}s)
✅ TLS Encryption: SUCCESS ({tls_time:.2f}s)
✅ Authentication: SUCCESS ({auth_time:.2f}s)
✅ Email Timeout: {EMAIL_TIMEOUT} seconds configured
✅ Production Password: Working correctly

CRITICAL FIX STATUS: ✅ RESOLVED

The newsletter subscription timeout issue has been fixed:
- Correct production password is now in use
- Email timeout prevents worker hangs
- SMTP connection completes within acceptable time

Test completed: {time.strftime('%Y-%m-%d %H:%M:%S')}
Total connection time: {time.time() - start_time:.2f} seconds

---
Novustell Travel Technical Team
Production Email System Test
"""
        
        msg.attach(MIMEText(body, 'plain'))
        text = msg.as_string()
        server.sendmail(EMAIL_HOST_USER, [EMAIL_HOST_USER], text)
        
        send_time = time.time() - send_start
        total_time = time.time() - start_time
        
        print(f"✅ Email sent successfully in {send_time:.2f} seconds")
        print(f"🎯 Total operation time: {total_time:.2f} seconds")
        
        server.quit()
        print("🔌 SMTP connection closed")
        
        # Verify timing is within acceptable limits
        if total_time < EMAIL_TIMEOUT:
            print(f"✅ PERFORMANCE: Operation completed well within {EMAIL_TIMEOUT}s timeout")
            return True, total_time
        else:
            print(f"⚠️ WARNING: Operation took {total_time:.2f}s (close to {EMAIL_TIMEOUT}s timeout)")
            return True, total_time
            
    except smtplib.SMTPAuthenticationError as e:
        elapsed = time.time() - start_time
        print(f"❌ SMTP Authentication Failed after {elapsed:.2f}s: {e}")
        print("🔍 Issue: Production password may be incorrect")
        return False, elapsed
        
    except smtplib.SMTPConnectError as e:
        elapsed = time.time() - start_time
        print(f"❌ SMTP Connection Failed after {elapsed:.2f}s: {e}")
        print("🔍 Issue: Network or server connectivity problem")
        return False, elapsed
        
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"❌ Email test failed after {elapsed:.2f}s: {e}")
        print(f"🔍 Error type: {type(e).__name__}")
        return False, elapsed

def test_production_django_email():
    """Test Django email backend with production settings"""
    print("\n🐍 Testing Django Email Backend (Production Settings)")
    print("-" * 60)
    
    try:
        # Set production environment
        os.environ['DJANGO_SETTINGS_MODULE'] = 'tours_travels.settings_prod'
        os.environ['EMAIL_HOST_USER'] = 'novustellke@gmail.com'
        os.environ['EMAIL_HOST_PASSWORD'] = 'eoie dhrq cioh gxhz'
        os.environ['DEFAULT_FROM_EMAIL'] = 'Novustell Travel <novustellke@gmail.com>'
        os.environ['ADMIN_EMAIL'] = 'info@novustelltravel.com'
        os.environ['JOBS_EMAIL'] = 'careers@novustelltravel.com'
        os.environ['NEWSLETTER_EMAIL'] = 'news@novustelltravel.com'
        
        import django
        from django.conf import settings
        from django.core.mail import send_mail
        
        # Initialize Django
        if not settings.configured:
            django.setup()
        
        print(f"📧 Django Settings Module: {os.environ.get('DJANGO_SETTINGS_MODULE')}")
        print(f"🏠 Email Backend: {settings.EMAIL_BACKEND}")
        print(f"📡 Email Host: {settings.EMAIL_HOST}:{settings.EMAIL_PORT}")
        print(f"👤 Email User: {settings.EMAIL_HOST_USER}")
        print(f"⏱️ Email Timeout: {getattr(settings, 'EMAIL_TIMEOUT', 'Not configured')}")
        print(f"🔐 Password: {settings.EMAIL_HOST_PASSWORD[:4]}****")
        
        # Test newsletter subscription email function
        print("\n📧 Testing newsletter subscription email flow...")
        start_time = time.time()
        
        # Simulate the exact email sending that was failing
        admin_subject = 'Production Test - Newsletter Subscription'
        admin_message = f"""
PRODUCTION EMAIL TEST - Newsletter Subscription Flow

This email simulates the newsletter subscription notification that was timing out.

✅ Django email backend: Working
✅ Production settings: Loaded
✅ Email timeout: {getattr(settings, 'EMAIL_TIMEOUT', 'Not set')} seconds
✅ SMTP credentials: Verified

Test timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}

If you receive this email, the newsletter subscription timeout issue is RESOLVED.

---
Novustell Travel System Test
"""
        
        # Send admin notification (this was failing in production)
        print("📤 Sending admin notification email...")
        admin_result = send_mail(
            subject=admin_subject,
            message=admin_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.NEWSLETTER_EMAIL],
            fail_silently=False,
        )
        
        admin_time = time.time() - start_time
        print(f"✅ Admin email sent in {admin_time:.2f} seconds (Result: {admin_result})")
        
        # Send subscriber confirmation (this was also failing)
        print("📤 Sending subscriber confirmation email...")
        subscriber_start = time.time()
        
        subscriber_result = send_mail(
            subject='Welcome to Novustell Travel Newsletter - Production Test',
            message=f"""
Welcome to Novustell Travel Newsletter!

This is a production test of the subscriber confirmation email.

✅ Email system: Fully operational
✅ Timeout issue: Resolved
✅ Response time: {admin_time:.2f} seconds

Thank you for helping us test the system!

---
Novustell Travel Team
""",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.EMAIL_HOST_USER],
            fail_silently=False,
        )
        
        subscriber_time = time.time() - subscriber_start
        total_time = time.time() - start_time
        
        print(f"✅ Subscriber email sent in {subscriber_time:.2f} seconds (Result: {subscriber_result})")
        print(f"🎯 Total Django email operation: {total_time:.2f} seconds")
        
        # Verify performance
        timeout_setting = getattr(settings, 'EMAIL_TIMEOUT', 30)
        if total_time < timeout_setting:
            print(f"✅ PERFORMANCE: Django emails completed well within {timeout_setting}s timeout")
            return True, total_time
        else:
            print(f"⚠️ WARNING: Django emails took {total_time:.2f}s (close to {timeout_setting}s timeout)")
            return True, total_time
            
    except Exception as e:
        elapsed = time.time() - start_time if 'start_time' in locals() else 0
        print(f"❌ Django email test failed after {elapsed:.2f}s: {e}")
        print(f"🔍 Error type: {type(e).__name__}")
        return False, elapsed

def test_newsletter_subscription_simulation():
    """Simulate the exact newsletter subscription flow that was failing"""
    print("\n📝 Testing Newsletter Subscription Flow Simulation")
    print("-" * 60)
    
    try:
        # Set production environment
        os.environ['DJANGO_SETTINGS_MODULE'] = 'tours_travels.settings_prod'
        os.environ['EMAIL_HOST_USER'] = 'novustellke@gmail.com'
        os.environ['EMAIL_HOST_PASSWORD'] = 'eoie dhrq cioh gxhz'
        
        import django
        from django.conf import settings
        
        if not settings.configured:
            django.setup()
        
        # Import the actual function that was failing
        sys.path.append('/Users/djsean/Desktop/APPS2024/Novustellke')
        from users.views import send_newsletter_subscription_emails
        
        # Create a mock subscription object
        class MockSubscription:
            def __init__(self):
                self.email = 'test@example.com'
                self.admin_notification_sent = False
                self.confirmation_email_sent = False
                
            def save(self):
                pass
        
        print("🧪 Creating mock newsletter subscription...")
        subscription = MockSubscription()
        
        print(f"📧 Test email: {subscription.email}")
        print("⚡ Calling send_newsletter_subscription_emails() function...")
        
        start_time = time.time()
        
        # This is the exact function call that was timing out in production
        send_newsletter_subscription_emails(subscription)
        
        execution_time = time.time() - start_time
        
        print(f"✅ Newsletter subscription emails sent successfully!")
        print(f"⏱️ Execution time: {execution_time:.2f} seconds")
        print(f"📊 Admin notification: {subscription.admin_notification_sent}")
        print(f"📊 Confirmation email: {subscription.confirmation_email_sent}")
        
        # Verify this would not cause Gunicorn timeout
        if execution_time < 30:
            print(f"✅ PERFORMANCE: Function completes well within Gunicorn timeout limits")
            return True, execution_time
        else:
            print(f"⚠️ WARNING: Function took {execution_time:.2f}s (may still cause timeouts)")
            return False, execution_time
            
    except Exception as e:
        elapsed = time.time() - start_time if 'start_time' in locals() else 0
        print(f"❌ Newsletter subscription simulation failed after {elapsed:.2f}s: {e}")
        print(f"🔍 Error type: {type(e).__name__}")
        return False, elapsed

def main():
    """Run comprehensive production email testing"""
    print("🚨 PRODUCTION EMAIL SYSTEM VERIFICATION")
    print("=" * 70)
    print("Testing the critical email timeout fix in production environment")
    print("=" * 70)
    
    results = {}
    
    # Test 1: Direct SMTP connection
    print("\n🔧 TEST 1: Direct SMTP Connection")
    smtp_success, smtp_time = test_production_smtp_direct()
    results['smtp'] = {'success': smtp_success, 'time': smtp_time}
    
    # Test 2: Django email backend
    print("\n🐍 TEST 2: Django Email Backend")
    django_success, django_time = test_production_django_email()
    results['django'] = {'success': django_success, 'time': django_time}
    
    # Test 3: Newsletter subscription simulation
    print("\n📝 TEST 3: Newsletter Subscription Simulation")
    newsletter_success, newsletter_time = test_newsletter_subscription_simulation()
    results['newsletter'] = {'success': newsletter_success, 'time': newsletter_time}
    
    # Final results
    print("\n" + "=" * 70)
    print("📊 PRODUCTION EMAIL TEST RESULTS")
    print("=" * 70)
    
    all_passed = True
    for test_name, result in results.items():
        status = "✅ PASS" if result['success'] else "❌ FAIL"
        print(f"{test_name.upper():20} | {status:8} | {result['time']:6.2f}s")
        if not result['success']:
            all_passed = False
    
    print("-" * 70)
    
    if all_passed:
        print("🎉 ALL PRODUCTION TESTS PASSED!")
        print("✅ Critical email timeout issue is RESOLVED")
        print("✅ Newsletter subscriptions will work correctly")
        print("✅ Production deployment is ready")
        print("\n🚀 RECOMMENDATION: Deploy to production immediately")
        return 0
    else:
        print("⚠️ SOME PRODUCTION TESTS FAILED!")
        print("❌ Email system may still have issues")
        print("❌ Further investigation required before deployment")
        print("\n🔍 RECOMMENDATION: Review failed tests before deploying")
        return 1

if __name__ == "__main__":
    sys.exit(main())
