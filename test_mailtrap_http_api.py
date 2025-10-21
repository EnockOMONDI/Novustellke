#!/usr/bin/env python
"""
Test script for Mailtrap HTTP API integration
Tests all email functionality after migration from SMTP to HTTP API
"""

import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tours_travels.settings_prod')
django.setup()

# Now import Django modules
from django.conf import settings
from users.tasks import (
    send_email_via_mailtrap,
    send_contact_inquiry_emails,
    send_mice_inquiry_emails,
    send_student_travel_emails,
    send_ngo_travel_emails,
    send_job_application_emails,
    send_newsletter_subscription_emails
)
from users.models import (
    ContactInquiry,
    MICEInquiry,
    StudentTravelInquiry,
    NGOTravelInquiry,
    JobApplication,
    NewsletterSubscription
)
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_mailtrap_configuration():
    """Test Mailtrap configuration"""
    print("🔧 Testing Mailtrap Configuration...")
    
    # Check if API token is configured
    api_token = getattr(settings, 'MAILTRAP_API_TOKEN', None)
    if not api_token:
        print("❌ MAILTRAP_API_TOKEN not configured")
        return False
    
    if api_token == 'your-token-here':
        print("❌ MAILTRAP_API_TOKEN is still set to default value")
        return False
    
    print(f"✅ MAILTRAP_API_TOKEN configured: {api_token[:8]}...")
    
    # Check email addresses
    print(f"✅ DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
    print(f"✅ ADMIN_EMAIL: {settings.ADMIN_EMAIL}")
    print(f"✅ JOBS_EMAIL: {settings.JOBS_EMAIL}")
    print(f"✅ NEWSLETTER_EMAIL: {settings.NEWSLETTER_EMAIL}")
    
    return True

def test_basic_email_sending():
    """Test basic email sending via Mailtrap HTTP API"""
    print("\n📧 Testing Basic Email Sending...")
    
    try:
        result = send_email_via_mailtrap(
            subject="Test Email - Mailtrap HTTP API",
            html_message="<h1>Test Email</h1><p>This is a test email sent via Mailtrap HTTP API.</p>",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.ADMIN_EMAIL]
        )
        
        if result:
            print("✅ Basic email sending successful")
            return True
        else:
            print("❌ Basic email sending failed")
            return False
            
    except Exception as e:
        print(f"❌ Basic email sending error: {e}")
        return False

def test_contact_inquiry_emails():
    """Test contact inquiry email functionality"""
    print("\n📞 Testing Contact Inquiry Emails...")
    
    try:
        # Create a test contact inquiry
        inquiry = ContactInquiry.objects.create(
            full_name="Test User",
            email="test@example.com",
            phone="+254701363551",
            subject="Test Contact Inquiry",
            message="This is a test contact inquiry message."
        )
        
        # Send emails
        result = send_contact_inquiry_emails(inquiry)
        
        if result.get('success'):
            print("✅ Contact inquiry emails sent successfully")
            print(f"   Admin email: {'✅' if result.get('admin_email_sent') else '❌'}")
            print(f"   User email: {'✅' if result.get('user_email_sent') else '❌'}")
            return True
        else:
            print(f"❌ Contact inquiry emails failed: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Contact inquiry email error: {e}")
        return False

def test_mice_inquiry_emails():
    """Test MICE inquiry email functionality"""
    print("\n🏢 Testing MICE Inquiry Emails...")
    
    try:
        # Create a test MICE inquiry
        inquiry = MICEInquiry.objects.create(
            company_name="Test Company",
            contact_person="Test Contact",
            email="test@example.com",
            phone_number="+254701363551",
            event_type="Conference",
            attendees=50,
            event_details="Test requirements for the conference"
        )
        
        # Send emails
        result = send_mice_inquiry_emails(inquiry)
        
        if result.get('success'):
            print("✅ MICE inquiry emails sent successfully")
            print(f"   Admin email: {'✅' if result.get('admin_email_sent') else '❌'}")
            print(f"   User email: {'✅' if result.get('user_email_sent') else '❌'}")
            return True
        else:
            print(f"❌ MICE inquiry emails failed: {result}")
            return False
            
    except Exception as e:
        print(f"❌ MICE inquiry email error: {e}")
        return False

def test_newsletter_subscription_emails():
    """Test newsletter subscription email functionality"""
    print("\n📰 Testing Newsletter Subscription Emails...")
    
    try:
        # Delete existing subscription if it exists to avoid duplicate key error
        NewsletterSubscription.objects.filter(email="test@example.com").delete()
        
        # Create a test newsletter subscription
        subscription = NewsletterSubscription.objects.create(
            email="test@example.com",
            travel_tips=True,
            special_offers=True,
            destination_updates=True
        )
        
        # Send emails
        result = send_newsletter_subscription_emails(subscription)
        
        if result.get('success'):
            print("✅ Newsletter subscription emails sent successfully")
            print(f"   Admin email: {'✅' if result.get('admin_email_sent') else '❌'}")
            print(f"   User email: {'✅' if result.get('user_email_sent') else '❌'}")
            return True
        else:
            print(f"❌ Newsletter subscription emails failed: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Newsletter subscription email error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 MAILTRAP HTTP API EMAIL TESTING")
    print("=" * 50)
    
    tests = [
        ("Configuration", test_mailtrap_configuration),
        ("Basic Email", test_basic_email_sending),
        ("Contact Inquiry", test_contact_inquiry_emails),
        ("MICE Inquiry", test_mice_inquiry_emails),
        ("Newsletter Subscription", test_newsletter_subscription_emails),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:20} | {status}")
        if result:
            passed += 1
    
    print("-" * 50)
    print(f"Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Mailtrap HTTP API is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Check the logs above for details.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
