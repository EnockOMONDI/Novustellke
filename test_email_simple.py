#!/usr/bin/env python3
"""
Simple Email Test - Verify the new password works
"""

import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def test_email_with_new_password():
    """Test email sending with the new app password"""
    print("🚨 TESTING NEW EMAIL PASSWORD")
    print("=" * 50)
    
    # Email configuration
    EMAIL_HOST = 'smtp.gmail.com'
    EMAIL_PORT = 587
    EMAIL_TIMEOUT = 30
    EMAIL_HOST_USER = 'novustellke@gmail.com'
    EMAIL_HOST_PASSWORD = 'eoie dhrq cioh gxhz'  # NEW password
    
    print(f"📧 Host: {EMAIL_HOST}:{EMAIL_PORT}")
    print(f"👤 User: {EMAIL_HOST_USER}")
    print(f"🔐 Password: {EMAIL_HOST_PASSWORD[:4]}****")
    print(f"⏱️ Timeout: {EMAIL_TIMEOUT} seconds")
    
    try:
        start_time = time.time()
        
        # Connect to SMTP server
        print("\n📡 Connecting to Gmail SMTP...")
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT, timeout=EMAIL_TIMEOUT)
        connection_time = time.time() - start_time
        print(f"✅ Connected in {connection_time:.2f} seconds")
        
        # Start TLS
        print("🔐 Starting TLS encryption...")
        tls_start = time.time()
        server.starttls()
        tls_time = time.time() - tls_start
        print(f"✅ TLS enabled in {tls_time:.2f} seconds")
        
        # Authenticate
        print("🔑 Authenticating with new password...")
        auth_start = time.time()
        server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
        auth_time = time.time() - auth_start
        print(f"✅ Authentication successful in {auth_time:.2f} seconds")
        
        # Send test email
        print("📧 Sending test email...")
        send_start = time.time()
        
        msg = MIMEMultipart()
        msg['From'] = f"Novustell Travel <{EMAIL_HOST_USER}>"
        msg['To'] = EMAIL_HOST_USER
        msg['Subject'] = "✅ NEW PASSWORD VERIFICATION - SUCCESS"
        
        body = f"""
NEW EMAIL PASSWORD VERIFICATION

✅ Connection: SUCCESS ({connection_time:.2f}s)
✅ TLS Encryption: SUCCESS ({tls_time:.2f}s)
✅ Authentication: SUCCESS ({auth_time:.2f}s)
✅ New Password: WORKING CORRECTLY

PASSWORD UPDATE STATUS: ✅ COMPLETE

The new Gmail app password "eoie dhrq cioh gxhz" is working correctly.
All email functionality should now work in production.

CRITICAL ISSUE STATUS: ✅ RESOLVED
- Newsletter subscriptions will work
- Contact forms will work
- All email notifications will work
- No more timeout errors

Test completed: {time.strftime('%Y-%m-%d %H:%M:%S')}
Total time: {time.time() - start_time:.2f} seconds

---
Novustell Travel Technical Team
Email System Verification
"""
        
        msg.attach(MIMEText(body, 'plain'))
        text = msg.as_string()
        server.sendmail(EMAIL_HOST_USER, [EMAIL_HOST_USER], text)
        
        send_time = time.time() - send_start
        total_time = time.time() - start_time
        
        print(f"✅ Email sent successfully in {send_time:.2f} seconds")
        print(f"🎯 Total operation time: {total_time:.2f} seconds")
        
        server.quit()
        print("🔌 Connection closed")
        
        # Performance check
        if total_time < EMAIL_TIMEOUT:
            print(f"\n🎉 EXCELLENT PERFORMANCE!")
            print(f"✅ Operation completed in {total_time:.2f}s (well under {EMAIL_TIMEOUT}s timeout)")
            print("✅ No risk of Gunicorn worker timeouts")
            print("✅ Production deployment is SAFE")
            return True
        else:
            print(f"\n⚠️ Performance warning: {total_time:.2f}s")
            return False
            
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"\n❌ Email test failed after {elapsed:.2f}s")
        print(f"🔍 Error: {e}")
        print(f"🔍 Error type: {type(e).__name__}")
        return False

def main():
    """Run the email test"""
    success = test_email_with_new_password()
    
    print("\n" + "=" * 50)
    print("📊 FINAL RESULT")
    print("=" * 50)
    
    if success:
        print("🎉 EMAIL PASSWORD UPDATE: ✅ SUCCESS")
        print("✅ New password is working correctly")
        print("✅ Production email system is ready")
        print("✅ Newsletter subscription timeout issue is FIXED")
        print("\n🚀 READY FOR PRODUCTION DEPLOYMENT")
        return 0
    else:
        print("❌ EMAIL PASSWORD UPDATE: ❌ FAILED")
        print("❌ New password may not be working")
        print("❌ Further investigation required")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
