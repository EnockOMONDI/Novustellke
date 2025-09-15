#!/usr/bin/env python
"""
Test script for the Email Marketing System
Tests all components of the email marketing app
"""

import os
import sys
import django
from django.conf import settings

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tours_travels.settings')
django.setup()

from django.test import TestCase
from django.contrib.auth.models import User
from email_marketing.models import EmailTemplate, RecipientList, Recipient, EmailCampaign, EmailLog
from email_marketing.services import EmailMarketingService
from django.template import Template, Context


def test_models():
    """Test all email marketing models"""
    print("🧪 Testing Email Marketing Models...")
    
    # Test EmailTemplate model
    try:
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            print("❌ No admin user found. Creating test user...")
            admin_user = User.objects.create_user(
                username='testadmin',
                email='test@example.com',
                password='testpass123',
                is_superuser=True,
                is_staff=True
            )
        
        # Test EmailTemplate
        template = EmailTemplate.objects.create(
            name="Test Template",
            subject="Test Subject",
            template_type="educational",
            html_content="<h1>Hello {{ recipient_name }}</h1>",
            text_content="Hello {{ recipient_name }}",
            created_by=admin_user
        )
        print(f"✅ EmailTemplate created: {template}")
        
        # Test RecipientList
        recipient_list = RecipientList.objects.create(
            name="Test List",
            description="Test recipient list",
            list_type="schools",
            created_by=admin_user
        )
        print(f"✅ RecipientList created: {recipient_list}")
        
        # Test Recipient
        recipient = Recipient.objects.create(
            email="test@school.edu",
            first_name="John",
            last_name="Doe",
            organization="Test School",
            position="Principal"
        )
        recipient.recipient_lists.add(recipient_list)
        print(f"✅ Recipient created: {recipient}")
        
        # Test EmailCampaign
        campaign = EmailCampaign.objects.create(
            name="Test Campaign",
            description="Test email campaign",
            email_template=template,
            created_by=admin_user
        )
        campaign.recipient_lists.add(recipient_list)
        print(f"✅ EmailCampaign created: {campaign}")
        print(f"   Total recipients: {campaign.total_recipients}")
        
        print("✅ All models tested successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Model test failed: {e}")
        return False


def test_template_rendering():
    """Test email template rendering"""
    print("\n🧪 Testing Template Rendering...")
    
    try:
        # Test template rendering
        template_content = """
        <h1>Hello {{ recipient_name }}!</h1>
        <p>Welcome to {{ organization }}.</p>
        <p>Contact us at {{ company_email }}</p>
        """
        
        context_data = {
            'recipient_name': 'John Doe',
            'organization': 'Test School',
            'company_email': 'info@novustelltravel.com'
        }
        
        template = Template(template_content)
        context = Context(context_data)
        rendered = template.render(context)
        
        # Check if variables were replaced
        assert 'John Doe' in rendered
        assert 'Test School' in rendered
        assert 'info@novustelltravel.com' in rendered
        assert '{{' not in rendered  # No unrendered variables
        
        print("✅ Template rendering successful!")
        print(f"   Rendered content preview: {rendered[:100]}...")
        return True
        
    except Exception as e:
        print(f"❌ Template rendering test failed: {e}")
        return False


def test_model_un_template():
    """Test the Model UN template specifically"""
    print("\n🧪 Testing Model UN Template...")
    
    try:
        # Get the Model UN template
        template = EmailTemplate.objects.filter(name="Model UN 2025-2026 Campaign").first()
        
        if not template:
            print("❌ Model UN template not found. Run setup command first.")
            return False
        
        print(f"✅ Found Model UN template: {template.name}")
        print(f"   Subject: {template.subject}")
        print(f"   Type: {template.get_template_type_display()}")
        print(f"   HTML content length: {len(template.html_content)} characters")
        print(f"   Text content length: {len(template.text_content)} characters")
        
        # Test template rendering with sample data
        context_data = {
            'recipient_name': 'Dr. Sarah Johnson',
            'organization': 'Brookhouse School',
            'first_name': 'Sarah',
            'last_name': 'Johnson',
            'email': 'sarah.johnson@brookhouse.edu',
            'tracking_pixel_url': 'https://example.com/track/pixel/123',
            'unsubscribe_url': 'https://example.com/unsubscribe/456',
            'company_name': 'Novustell Travel',
            'company_email': 'info@novustelltravel.com'
        }
        
        django_template = Template(template.html_content)
        context = Context(context_data)
        rendered_html = django_template.render(context)
        
        # Check for key content
        assert 'Model United Nations' in rendered_html
        assert 'Dr. Sarah Johnson' in rendered_html
        assert 'Brookhouse School' in rendered_html
        assert 'Yale MUN' in rendered_html
        assert 'Harvard MUN' in rendered_html
        assert 'Novustell Travel' in rendered_html
        
        print("✅ Model UN template rendering successful!")
        print(f"   Rendered HTML length: {len(rendered_html)} characters")
        
        return True
        
    except Exception as e:
        print(f"❌ Model UN template test failed: {e}")
        return False


def test_email_service():
    """Test the email marketing service"""
    print("\n🧪 Testing Email Marketing Service...")
    
    try:
        service = EmailMarketingService()
        print(f"✅ EmailMarketingService initialized")
        print(f"   From email: {service.from_email}")
        
        # Test context preparation
        recipient = Recipient.objects.filter(email__icontains='test').first()
        if not recipient:
            print("❌ No test recipient found")
            return False
        
        context_data = service._prepare_template_context(recipient, 'test-token-123')
        
        # Check required context variables
        required_vars = [
            'recipient_name', 'email', 'organization', 'tracking_token',
            'tracking_pixel_url', 'unsubscribe_url', 'company_name'
        ]
        
        for var in required_vars:
            assert var in context_data, f"Missing context variable: {var}"
        
        print("✅ Email service context preparation successful!")
        print(f"   Context variables: {list(context_data.keys())}")
        
        return True
        
    except Exception as e:
        print(f"❌ Email service test failed: {e}")
        return False


def test_campaign_statistics():
    """Test campaign statistics and analytics"""
    print("\n🧪 Testing Campaign Statistics...")
    
    try:
        # Get the Model UN campaign
        campaign = EmailCampaign.objects.filter(name__icontains="Model UN").first()
        
        if not campaign:
            print("❌ Model UN campaign not found")
            return False
        
        print(f"✅ Found campaign: {campaign.name}")
        print(f"   Status: {campaign.get_status_display()}")
        print(f"   Total recipients: {campaign.total_recipients}")
        print(f"   Emails sent: {campaign.emails_sent}")
        print(f"   Emails opened: {campaign.emails_opened}")
        print(f"   Emails clicked: {campaign.emails_clicked}")
        
        # Test recipient lists
        print(f"   Recipient lists: {campaign.recipient_lists.count()}")
        for recipient_list in campaign.recipient_lists.all():
            print(f"     - {recipient_list.name}: {recipient_list.recipient_count} recipients")
        
        return True
        
    except Exception as e:
        print(f"❌ Campaign statistics test failed: {e}")
        return False


def test_admin_integration():
    """Test Django admin integration"""
    print("\n🧪 Testing Django Admin Integration...")
    
    try:
        from django.contrib import admin
        from email_marketing.admin import (
            EmailTemplateAdmin, RecipientListAdmin, 
            RecipientAdmin, EmailCampaignAdmin, EmailLogAdmin
        )
        
        # Check if models are registered
        registered_models = admin.site._registry
        
        models_to_check = [
            EmailTemplate, RecipientList, Recipient, EmailCampaign, EmailLog
        ]
        
        for model in models_to_check:
            if model in registered_models:
                print(f"✅ {model.__name__} registered in admin")
            else:
                print(f"❌ {model.__name__} NOT registered in admin")
                return False
        
        print("✅ All models properly registered in Django admin!")
        return True
        
    except Exception as e:
        print(f"❌ Admin integration test failed: {e}")
        return False


def run_all_tests():
    """Run all tests"""
    print("🚀 Starting Email Marketing System Tests...\n")
    
    tests = [
        test_models,
        test_template_rendering,
        test_model_un_template,
        test_email_service,
        test_campaign_statistics,
        test_admin_integration
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            failed += 1
    
    print(f"\n📊 Test Results:")
    print(f"   ✅ Passed: {passed}")
    print(f"   ❌ Failed: {failed}")
    print(f"   📈 Success Rate: {(passed/(passed+failed)*100):.1f}%")
    
    if failed == 0:
        print("\n🎉 All tests passed! Email Marketing System is ready for production!")
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please review and fix issues.")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
