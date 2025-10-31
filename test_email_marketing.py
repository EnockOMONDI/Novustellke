#!/usr/bin/env python
"""
Test script for email marketing functionality
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

from email_marketing.models import EmailTemplate, RecipientList, Recipient, EmailCampaign
from email_marketing.services import EmailMarketingService
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_email_marketing_models():
    """Test email marketing models"""
    print("🔍 Testing Email Marketing Models...")
    
    print(f"📧 Email Templates: {EmailTemplate.objects.count()}")
    print(f"📋 Recipient Lists: {RecipientList.objects.count()}")
    print(f"👥 Recipients: {Recipient.objects.count()}")
    print(f"🚀 Email Campaigns: {EmailCampaign.objects.count()}")
    
    # List existing templates
    for template in EmailTemplate.objects.all():
        print(f"   Template: {template.name} ({template.template_type})")
    
    # List existing campaigns
    for campaign in EmailCampaign.objects.all():
        print(f"   Campaign: {campaign.name} (Status: {campaign.status})")
    
    return True

def test_email_service():
    """Test email marketing service"""
    print("\n📧 Testing Email Marketing Service...")
    
    try:
        service = EmailMarketingService()
        print(f"✅ Email service initialized with from_email: {service.from_email}")
        return True
    except Exception as e:
        print(f"❌ Email service initialization failed: {e}")
        return False

def test_template_rendering():
    """Test email template rendering"""
    print("\n🎨 Testing Template Rendering...")
    
    try:
        # Get first template
        template = EmailTemplate.objects.first()
        if not template:
            print("❌ No email templates found")
            return False
        
        print(f"Testing template: {template.name}")
        
        # Test recipient
        recipient = Recipient.objects.filter(email='djseanizellkenya@gmail.com').first()
        if not recipient:
            print("❌ Test recipient not found")
            return False
        
        service = EmailMarketingService()
        context_data = service._prepare_template_context(recipient, 'test-token')
        
        print(f"✅ Template context prepared with {len(context_data)} variables")
        print(f"   Recipient name: {context_data.get('recipient_name')}")
        print(f"   Organization: {context_data.get('organization')}")
        
        # Test rendering
        rendered_html = service._render_email_template(template.html_content, context_data)
        rendered_subject = service._render_email_template(template.subject, context_data)
        
        print(f"✅ Template rendered successfully")
        print(f"   Subject: {rendered_subject}")
        print(f"   HTML length: {len(rendered_html)} characters")
        
        return True
        
    except Exception as e:
        print(f"❌ Template rendering failed: {e}")
        return False

def test_send_test_email():
    """Test sending a test email"""
    print("\n📤 Testing Email Sending...")
    
    try:
        # Get test campaign
        campaign = EmailCampaign.objects.first()
        if not campaign:
            print("❌ No email campaigns found")
            return False
        
        # Get test recipient
        recipient = Recipient.objects.filter(email='djseanizellkenya@gmail.com').first()
        if not recipient:
            print("❌ Test recipient not found")
            return False
        
        print(f"Testing campaign: {campaign.name}")
        print(f"Sending to: {recipient.email}")
        
        service = EmailMarketingService()
        
        # Test sending to single recipient
        success = service._send_email_to_recipient(campaign, recipient)
        
        if success:
            print("✅ Test email sent successfully")
            return True
        else:
            print("❌ Test email sending failed")
            return False
            
    except Exception as e:
        print(f"❌ Email sending error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 EMAIL MARKETING FUNCTIONALITY TESTING")
    print("=" * 50)
    
    tests = [
        ("Models", test_email_marketing_models),
        ("Service", test_email_service),
        ("Template Rendering", test_template_rendering),
        ("Email Sending", test_send_test_email),
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
        print("🎉 ALL TESTS PASSED!")
        return True
    else:
        print("⚠️  Some tests failed. Check the logs above for details.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
