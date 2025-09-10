#!/usr/bin/env python3
"""
Logo URL Update Verification Script for Novustell Travel
Tests all email templates to verify correct absolute logo URLs are being used
"""

import os
import sys
import django
from django.template.loader import render_to_string
from django.template import Context, Template
from datetime import datetime

# Setup Django environment
sys.path.append('/Users/djsean/Desktop/APPS2024/Novustellke')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tours_travels.settings')
django.setup()

def test_logo_url_updates():
    """Test all email templates for correct absolute logo URLs"""
    
    print("🔍 LOGO URL UPDATE VERIFICATION TEST")
    print("=" * 70)
    print("Verifying all email templates use correct absolute logo URLs")
    print()
    
    # Expected logo URLs
    WHITE_LOGO_URL = "https://www.novustelltravel.com/static/assets/images/logo/logo-white.png"
    BLUE_LOGO_URL = "https://www.novustelltravel.com/static/assets/images/logo/websitelogo.png"
    
    # Mock data for testing
    mock_data = {
        'contact': {
            'name': 'John Doe',
            'email': 'john@example.com',
            'phone': '+254701234567',
            'subject': 'General Inquiry',
            'message': 'Test message',
            'created_at': datetime.now(),
            'reference_id': 'CNT-12345'
        },
        'ngo': {
            'organization_name': 'Hope Foundation',
            'contact_person': 'Jane Smith',
            'email': 'jane@hopefoundation.org',
            'phone_number': '+254701234567',
            'destination': 'Kenya',
            'travel_dates': '2024-03-15 to 2024-03-20',
            'group_size': '25',
            'budget_range': '$10,000 - $15,000',
            'special_requirements': 'Wheelchair accessible accommodation',
            'created_at': datetime.now(),
            'reference_id': 'NGO-12345'
        },
        'mice': {
            'company_name': 'Tech Corp Ltd',
            'contact_person': 'Mike Johnson',
            'email': 'mike@techcorp.com',
            'phone_number': '+254701234567',
            'event_type': 'Corporate Retreat',
            'destination': 'Mombasa',
            'event_dates': '2024-04-10 to 2024-04-12',
            'attendees': '50',
            'budget_range': '$25,000 - $30,000',
            'special_requirements': 'Conference facilities',
            'created_at': datetime.now(),
            'reference_id': 'MICE-12345'
        },
        'student': {
            'institution_name': 'University of Nairobi',
            'contact_person': 'Dr. Sarah Wilson',
            'email': 'sarah@uon.ac.ke',
            'phone_number': '+254701234567',
            'destination': 'Tanzania',
            'travel_dates': '2024-05-20 to 2024-05-25',
            'student_count': '30',
            'budget_range': '$15,000 - $20,000',
            'educational_focus': 'Wildlife Conservation Studies',
            'special_requirements': 'Educational permits',
            'created_at': datetime.now(),
            'reference_id': 'STU-12345'
        },
        'job_application': {
            'full_name': 'Alice Johnson',
            'email': 'alice@example.com',
            'phone': '+254701234567',
            'position': 'travel_consultant',
            'created_at': datetime.now(),
            'get_position_display': lambda: 'Travel Consultant',
            'resume': 'resume.pdf'
        },
        'newsletter': {
            'email': 'subscriber@example.com',
            'created_at': datetime.now()
        }
    }
    
    # All templates to test with expected logo context
    templates_to_test = [
        # Contact System
        ('Contact Inquiry Admin', 'users/emails/contact_inquiry_admin.html', mock_data['contact'], 'dark'),
        ('Contact Inquiry Confirmation', 'users/emails/contact_inquiry_confirmation.html', mock_data['contact'], 'dark'),
        
        # NGO Travel System
        ('NGO Travel Admin', 'users/emails/ngo_travel_admin.html', mock_data['ngo'], 'dark'),
        ('NGO Travel Confirmation', 'users/emails/ngo_travel_confirmation.html', mock_data['ngo'], 'dark'),
        
        # MICE System
        ('MICE Inquiry Admin', 'users/emails/mice_inquiry_admin.html', mock_data['mice'], 'dark'),
        ('MICE Inquiry Confirmation', 'users/emails/mice_inquiry_confirmation.html', mock_data['mice'], 'dark'),
        
        # Student Travel System
        ('Student Travel Admin', 'users/emails/student_travel_admin.html', mock_data['student'], 'dark'),
        ('Student Travel Confirmation', 'users/emails/student_travel_confirmation.html', mock_data['student'], 'dark'),
        
        # Job Application System
        ('Job Application Admin', 'users/emails/job_application_admin.html', mock_data['job_application'], 'dark'),
        ('Job Application Confirmation', 'users/emails/job_application_confirmation.html', mock_data['job_application'], 'dark'),
        
        # Newsletter System
        ('Newsletter Admin', 'users/emails/newsletter_admin.html', mock_data['newsletter'], 'dark'),
        ('Newsletter Confirmation', 'users/emails/newsletter_confirmation.html', mock_data['newsletter'], 'dark'),
    ]
    
    # Test results tracking
    total_templates = len(templates_to_test)
    successful_updates = 0
    failed_updates = 0
    
    # Test each template
    for template_name, template_path, context_data, background_context in templates_to_test:
        try:
            print(f"🔍 Testing: {template_name}")
            
            # Attempt to render the template
            rendered_content = render_to_string(template_path, context_data)
            
            # Determine expected logo URL based on background context
            expected_logo_url = WHITE_LOGO_URL if background_context == 'dark' else BLUE_LOGO_URL
            
            # Check for correct logo URL usage
            logo_checks = {
                'Correct Logo URL': expected_logo_url in rendered_content,
                'No Django Static Tags': '{% static' not in rendered_content,
                'Absolute URL Format': 'https://www.novustelltravel.com' in rendered_content,
                'Logo Alt Text': 'alt="Novustell Travel"' in rendered_content
            }
            
            # Count successful logo checks
            passed_checks = sum(logo_checks.values())
            total_checks = len(logo_checks)
            
            if passed_checks == total_checks:
                print(f"   ✅ SUCCESS: {passed_checks}/{total_checks} logo URL checks passed")
                successful_updates += 1
            else:
                print(f"   ⚠️  ISSUES: {passed_checks}/{total_checks} logo URL checks passed")
                for check_name, passed in logo_checks.items():
                    if not passed:
                        print(f"      ❌ Failed: {check_name}")
                failed_updates += 1
                
        except Exception as e:
            print(f"   ❌ RENDER FAILED: {str(e)}")
            failed_updates += 1
        
        print()
    
    # Final results
    print("=" * 70)
    print("🎯 LOGO URL UPDATE VERIFICATION RESULTS")
    print("=" * 70)
    print(f"📊 Total Templates Tested: {total_templates}")
    print(f"✅ Successfully Updated: {successful_updates}")
    print(f"❌ Failed Updates: {failed_updates}")
    print(f"📈 Success Rate: {(successful_updates/total_templates)*100:.1f}%")
    print()
    
    if successful_updates == total_templates:
        print("🎉 ALL LOGO URLs SUCCESSFULLY UPDATED!")
        print("✅ All templates now use absolute logo URLs")
        print("✅ No Django static template tags remaining in logo references")
        print("✅ Correct white logo used for dark backgrounds")
        print("✅ All logo alt text properly maintained")
        print("✅ Ready for email delivery across all clients!")
    else:
        print("⚠️  Some templates need attention")
        print(f"   {failed_updates} templates have logo URL issues")
    
    print()
    print("🔗 LOGO URL STANDARDS:")
    print(f"   • Dark Backgrounds: {WHITE_LOGO_URL}")
    print(f"   • Light Backgrounds: {BLUE_LOGO_URL}")
    print("   • All current templates use dark backgrounds (blue #0f238d headers)")
    print("   • All logos maintain responsive sizing (max-width: 150-180px)")

if __name__ == "__main__":
    test_logo_url_updates()
