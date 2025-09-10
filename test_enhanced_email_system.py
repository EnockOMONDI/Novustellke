#!/usr/bin/env python3
"""
Enhanced Email System Test
Tests all email templates and form submission workflows
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

def test_email_template_rendering():
    """Test all email templates for proper rendering"""
    print("🧪 ENHANCED EMAIL SYSTEM TEST")
    print("=" * 60)
    
    # Mock inquiry data for testing
    mock_inquiries = {
        'contact': {
            'full_name': 'John Doe',
            'email': 'john@example.com',
            'phone': '+254712345678',
            'company': 'Test Company',
            'subject': 'General Inquiry',
            'message': 'This is a test message for contact inquiry.',
            'created_at': datetime.now(),
            'id': 12345
        },
        'ngo': {
            'organization_name': 'Test NGO Organization',
            'contact_person': 'Jane Smith',
            'email': 'jane@testngo.org',
            'phone_number': '+254712345678',
            'organization_type': 'Non-Profit',
            'number_of_travelers': 15,
            'budget_range': '$10,000 - $15,000',
            'sustainability_requirements': True,
            'travel_details': 'Educational mission to rural areas for community development.',
            'created_at': datetime.now(),
            'id': 67890
        },
        'mice': {
            'company_name': 'Corporate Solutions Ltd',
            'contact_person': 'Michael Johnson',
            'email': 'michael@corpsolutions.com',
            'phone_number': '+254712345678',
            'event_type': 'Conference',
            'attendees': 150,
            'event_details': 'Annual corporate conference with international speakers.',
            'created_at': datetime.now(),
            'id': 11111
        },
        'student': {
            'school_name': 'International Academy',
            'contact_person': 'Sarah Wilson',
            'email': 'sarah@intlacademy.edu',
            'phone_number': '+254712345678',
            'travel_type': 'Educational Tour',
            'number_of_students': 45,
            'number_of_supervisors': 5,
            'student_age_group': '16-18 years',
            'budget_range': '$20,000 - $25,000',
            'travel_details': 'Educational tour to historical sites and cultural centers.',
            'created_at': datetime.now(),
            'id': 22222
        }
    }
    
    # Email templates to test
    email_templates = [
        # Contact Inquiry (Already Enhanced)
        ('Contact Inquiry Admin', 'users/emails/contact_inquiry_admin.html', mock_inquiries['contact']),
        ('Contact Inquiry Confirmation', 'users/emails/contact_inquiry_confirmation.html', mock_inquiries['contact']),
        
        # NGO Travel (Newly Created)
        ('NGO Travel Admin', 'users/emails/ngo_travel_admin.html', mock_inquiries['ngo']),
        ('NGO Travel Confirmation', 'users/emails/ngo_travel_confirmation.html', mock_inquiries['ngo']),
        
        # MICE Inquiry (Newly Created)
        ('MICE Inquiry Admin', 'users/emails/mice_inquiry_admin.html', mock_inquiries['mice']),
        ('MICE Inquiry Confirmation', 'users/emails/mice_inquiry_confirmation.html', mock_inquiries['mice']),
        
        # Student Travel (Newly Created)
        ('Student Travel Admin', 'users/emails/student_travel_admin.html', mock_inquiries['student']),
        ('Student Travel Confirmation', 'users/emails/student_travel_confirmation.html', mock_inquiries['student']),
    ]
    
    results = []
    
    for template_name, template_path, mock_data in email_templates:
        print(f"\n📧 Testing: {template_name}")
        print("-" * 40)
        
        try:
            # Create mock inquiry object
            class MockInquiry:
                def __init__(self, data):
                    for key, value in data.items():
                        setattr(self, key, value)
            
            inquiry = MockInquiry(mock_data)
            
            # Test template rendering
            rendered_content = render_to_string(template_path, {'inquiry': inquiry})
            
            # Check for key elements
            checks = [
                ('Template renders', len(rendered_content) > 0),
                ('Contains Novustell branding', 'Novustell Travel' in rendered_content),
                ('Contains logo reference', 'logo' in rendered_content.lower()),
                ('Contains contact information', 'Info@novustelltravel.com' in rendered_content),
                ('Contains phone numbers', '+254 721 115 572' in rendered_content),
                ('Contains WhatsApp', '+254 701 363 551' in rendered_content),
                ('Contains office address', 'New Peoples Media Center' in rendered_content),
                ('Contains tagline', 'Think Convenience, Think Novustell' in rendered_content),
                ('Contains business hours', 'Business Hours' in rendered_content),
                ('Contains proper styling', 'background-color' in rendered_content),
            ]
            
            # Additional specific checks based on template type
            if 'admin' in template_path:
                checks.extend([
                    ('Contains priority notice', 'Priority' in rendered_content or 'priority' in rendered_content),
                    ('Contains department assignment', 'Department' in rendered_content or 'Team' in rendered_content),
                    ('Contains response protocol', 'Response' in rendered_content or 'Protocol' in rendered_content),
                ])
            
            if 'confirmation' in template_path:
                checks.extend([
                    ('Contains thank you message', 'Thank you' in rendered_content or 'thank you' in rendered_content),
                    ('Contains next steps', 'What Happens Next' in rendered_content or 'Next Steps' in rendered_content),
                    ('Contains reference ID', f'{inquiry.id:05d}' in rendered_content),
                ])
            
            # Specific template checks
            if 'ngo' in template_path:
                checks.extend([
                    ('Contains NGO-specific content', 'NGO' in rendered_content or 'humanitarian' in rendered_content),
                    ('Contains organization name', inquiry.organization_name in rendered_content),
                ])
            
            if 'mice' in template_path:
                checks.extend([
                    ('Contains MICE-specific content', 'MICE' in rendered_content or 'Corporate' in rendered_content),
                    ('Contains company name', inquiry.company_name in rendered_content),
                    ('Contains event type', inquiry.event_type in rendered_content),
                ])
            
            if 'student' in template_path:
                checks.extend([
                    ('Contains student-specific content', 'Student' in rendered_content or 'Educational' in rendered_content),
                    ('Contains school name', inquiry.school_name in rendered_content),
                ])
            
            # Report results
            passed_checks = 0
            total_checks = len(checks)
            
            for check_name, check_result in checks:
                status = "✅" if check_result else "❌"
                print(f"  {status} {check_name}")
                if check_result:
                    passed_checks += 1
            
            success_rate = (passed_checks / total_checks) * 100
            print(f"\n📊 Success Rate: {passed_checks}/{total_checks} ({success_rate:.1f}%)")
            
            results.append({
                'template': template_name,
                'success_rate': success_rate,
                'passed': passed_checks,
                'total': total_checks,
                'status': 'PASS' if success_rate >= 80 else 'FAIL'
            })
            
        except Exception as e:
            print(f"❌ Template rendering failed: {e}")
            results.append({
                'template': template_name,
                'success_rate': 0,
                'passed': 0,
                'total': 0,
                'status': 'ERROR',
                'error': str(e)
            })
    
    # Summary Report
    print("\n" + "=" * 60)
    print("📊 ENHANCED EMAIL SYSTEM TEST SUMMARY")
    print("=" * 60)
    
    total_templates = len(results)
    passed_templates = sum(1 for r in results if r['status'] == 'PASS')
    failed_templates = sum(1 for r in results if r['status'] == 'FAIL')
    error_templates = sum(1 for r in results if r['status'] == 'ERROR')
    
    print(f"Total Templates Tested: {total_templates}")
    print(f"✅ Passed: {passed_templates}")
    print(f"❌ Failed: {failed_templates}")
    print(f"🚨 Errors: {error_templates}")
    
    print("\n📋 Detailed Results:")
    for result in results:
        status_icon = "✅" if result['status'] == 'PASS' else "❌" if result['status'] == 'FAIL' else "🚨"
        print(f"  {status_icon} {result['template']}: {result['success_rate']:.1f}% ({result['passed']}/{result['total']})")
        if 'error' in result:
            print(f"      Error: {result['error']}")
    
    # Overall Assessment
    overall_success = (passed_templates / total_templates) * 100
    print(f"\n🎯 Overall Success Rate: {overall_success:.1f}%")
    
    if overall_success >= 90:
        print("🎉 EXCELLENT! Email system is fully enhanced and ready for production.")
    elif overall_success >= 80:
        print("✅ GOOD! Email system is mostly ready with minor issues to address.")
    elif overall_success >= 60:
        print("⚠️ NEEDS IMPROVEMENT! Several templates require attention.")
    else:
        print("❌ CRITICAL ISSUES! Email system needs significant work.")
    
    # Recommendations
    print("\n📝 RECOMMENDATIONS:")
    if error_templates > 0:
        print("  🚨 Fix template rendering errors immediately")
    if failed_templates > 0:
        print("  ⚠️ Review failed templates for missing branding elements")
    if passed_templates == total_templates:
        print("  🎉 All templates passed! Ready for production deployment")
        print("  📧 Test actual email sending with SMTP configuration")
        print("  🔍 Verify email delivery across different email clients")
    
    print("=" * 60)
    
    return results

if __name__ == "__main__":
    test_email_template_rendering()
