#!/usr/bin/env python
"""
Test script for Student Travel Model UN integration
Tests form functionality, email workflows, and template rendering
"""

import os
import sys
import django
from django.conf import settings

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tours_travels.settings')
django.setup()

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.core import mail
from django.template.loader import render_to_string
from users.models import StudentTravelInquiry
from users.forms import StudentTravelInquiryForm


def test_model_un_form_choices():
    """Test that Model UN option is available in form choices"""
    print("🧪 Testing Model UN Form Choices...")
    
    try:
        form = StudentTravelInquiryForm()
        program_stage_choices = form.fields['program_stage'].choices
        
        # Check if Model UN option exists
        model_un_found = False
        for choice_value, choice_label in program_stage_choices:
            if choice_value == 'Model UN 2025-2026':
                model_un_found = True
                print(f"✅ Found Model UN option: {choice_value} - {choice_label}")
                break
        
        if not model_un_found:
            print("❌ Model UN option not found in form choices")
            return False
        
        # Print all available choices
        print("📋 All available program stage choices:")
        for choice_value, choice_label in program_stage_choices:
            print(f"   - {choice_value}: {choice_label}")
        
        return True
        
    except Exception as e:
        print(f"❌ Form choices test failed: {e}")
        return False


def test_model_creation():
    """Test creating StudentTravelInquiry with Model UN option"""
    print("\n🧪 Testing Model UN Inquiry Creation...")
    
    try:
        # Create a Model UN inquiry
        inquiry = StudentTravelInquiry.objects.create(
            school_name="Test International School",
            contact_person="Dr. Sarah Johnson",
            email="sarah.johnson@testschool.edu",
            phone_number="+254700123456",
            program_stage="Model UN 2025-2026",
            number_of_students=15,
            travel_details="We are interested in participating in Yale MUN and Harvard MUN conferences. Our delegation consists of 15 students and 3 supervisors."
        )
        
        print(f"✅ Created Model UN inquiry: {inquiry}")
        print(f"   School: {inquiry.school_name}")
        print(f"   Program Stage: {inquiry.program_stage}")
        print(f"   Students: {inquiry.number_of_students}")
        print(f"   Reference ID: STU-{inquiry.id:05d}")
        
        return inquiry
        
    except Exception as e:
        print(f"❌ Model creation test failed: {e}")
        return None


def test_form_submission():
    """Test form submission with Model UN option"""
    print("\n🧪 Testing Model UN Form Submission...")
    
    try:
        form_data = {
            'school_name': 'Brookhouse International School',
            'contact_person': 'Michael Thompson',
            'email': 'michael.thompson@brookhouse.edu',
            'phone_number': '+254701234567',
            'program_stage': 'Model UN 2025-2026',
            'number_of_students': 20,
            'travel_details': 'Our school is planning to participate in the upcoming Model UN conferences including Yale MUN and Harvard MUN. We need comprehensive travel arrangements for 20 students and 4 supervisors.'
        }
        
        form = StudentTravelInquiryForm(data=form_data)
        
        if form.is_valid():
            inquiry = form.save()
            print(f"✅ Form submission successful: {inquiry}")
            print(f"   Program Stage: {inquiry.program_stage}")
            return inquiry
        else:
            print(f"❌ Form validation failed: {form.errors}")
            return None
        
    except Exception as e:
        print(f"❌ Form submission test failed: {e}")
        return None


def test_email_template_rendering():
    """Test email template rendering with Model UN inquiry"""
    print("\n🧪 Testing Email Template Rendering...")
    
    try:
        # Create a test inquiry
        inquiry = StudentTravelInquiry.objects.create(
            school_name="Alliance High School",
            contact_person="Dr. James Mwangi",
            email="james.mwangi@alliance.edu",
            phone_number="+254702345678",
            program_stage="Model UN 2025-2026",
            number_of_students=12,
            travel_details="We want to participate in Harvard MUN 2026. Please provide a comprehensive travel package."
        )
        
        # Test admin email template
        admin_html = render_to_string('users/emails/student_travel_admin.html', {
            'inquiry': inquiry
        })
        
        # Check for Model UN-specific content in admin email
        model_un_checks = [
            'Model UN 2025-2026' in admin_html,
            'MUN PROGRAM' in admin_html,
            'Model UN Specialist Team' in admin_html,
            'MUN specialist' in admin_html
        ]
        
        print(f"✅ Admin email template rendered ({len(admin_html)} characters)")
        print(f"   Model UN content checks: {sum(model_un_checks)}/4 passed")
        
        # Test user confirmation template
        user_html = render_to_string('users/emails/student_travel_confirmation.html', {
            'inquiry': inquiry
        })
        
        # Check for Model UN-specific content in user email
        user_checks = [
            'Model UN travel inquiry' in user_html,
            'Model UN Travel Team' in user_html,
            'Model UN Specialist Team' in user_html,
            'Yale MUN' in user_html or 'Harvard MUN' in user_html
        ]
        
        print(f"✅ User confirmation template rendered ({len(user_html)} characters)")
        print(f"   Model UN content checks: {sum(user_checks)}/4 passed")
        
        return all(model_un_checks) and all(user_checks)
        
    except Exception as e:
        print(f"❌ Email template rendering test failed: {e}")
        return False


def test_email_workflow():
    """Test complete email workflow for Model UN inquiry"""
    print("\n🧪 Testing Model UN Email Workflow...")
    
    try:
        # Clear any existing emails
        mail.outbox = []
        
        # Create a test inquiry
        inquiry = StudentTravelInquiry.objects.create(
            school_name="Kenya High School",
            contact_person="Dr. Patricia Ochieng",
            email="patricia.ochieng@kenyahigh.edu",
            phone_number="+254703456789",
            program_stage="Model UN 2025-2026",
            number_of_students=18,
            travel_details="We are planning to send our MUN delegation to Yale MUN 2026. Please provide a detailed proposal."
        )
        
        # Simulate the email sending process from views.py
        from django.core.mail import send_mail
        from django.template.loader import render_to_string
        
        # Admin email
        admin_subject = f'New Student Travel Inquiry from {inquiry.school_name}'
        admin_message_html = render_to_string('users/emails/student_travel_admin.html', {
            'inquiry': inquiry
        })
        admin_message_txt = render_to_string('users/emails/student_travel_admin.txt', {
            'inquiry': inquiry
        })
        
        # User email
        user_subject = f'Student Travel Inquiry Received - {inquiry.school_name}'
        user_message_html = render_to_string('users/emails/student_travel_confirmation.html', {
            'inquiry': inquiry
        })
        user_message_txt = render_to_string('users/emails/student_travel_confirmation.txt', {
            'inquiry': inquiry
        })
        
        print(f"✅ Email templates rendered successfully")
        print(f"   Admin subject: {admin_subject}")
        print(f"   User subject: {user_subject}")
        print(f"   Admin HTML length: {len(admin_message_html)} characters")
        print(f"   User HTML length: {len(user_message_html)} characters")
        
        # Check for Model UN-specific content
        admin_has_mun = 'Model UN' in admin_message_html and 'MUN' in admin_message_html
        user_has_mun = 'Model UN' in user_message_html and 'MUN' in user_message_html
        
        print(f"   Admin email has Model UN content: {admin_has_mun}")
        print(f"   User email has Model UN content: {user_has_mun}")
        
        return admin_has_mun and user_has_mun
        
    except Exception as e:
        print(f"❌ Email workflow test failed: {e}")
        return False


def test_web_form_integration():
    """Test web form integration with Model UN option"""
    print("\n🧪 Testing Web Form Integration...")
    
    try:
        client = Client()
        
        # Get the student travel page
        response = client.get('/student-travel/')
        
        if response.status_code == 200:
            print(f"✅ Student travel page loaded successfully")
            
            # Check if Model UN option is in the form
            content = response.content.decode('utf-8')
            has_model_un = 'Model UN 2025-2026' in content
            has_model_un_section = 'id="model-un"' in content
            
            print(f"   Form has Model UN option: {has_model_un}")
            print(f"   Page has Model UN section: {has_model_un_section}")
            
            return has_model_un and has_model_un_section
        else:
            print(f"❌ Failed to load student travel page: {response.status_code}")
            return False
        
    except Exception as e:
        print(f"❌ Web form integration test failed: {e}")
        return False


def run_all_tests():
    """Run all tests"""
    print("🚀 Starting Student Travel Model UN Integration Tests...\n")
    
    tests = [
        test_model_un_form_choices,
        test_model_creation,
        test_form_submission,
        test_email_template_rendering,
        test_email_workflow,
        test_web_form_integration
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
        print("\n🎉 All tests passed! Model UN integration is ready for production!")
        print("\n🔗 Next Steps:")
        print("   1. Test the form submission on the website")
        print("   2. Verify email delivery in production")
        print("   3. Test the anchor link: /student-travel/#model-un")
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please review and fix issues.")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
