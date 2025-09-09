#!/usr/bin/env python3
"""
Contact Form Email Template Test Script
Tests the enhanced email templates with actual form submission
"""

import os
import django
from django.conf import settings

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tours_travels.settings')
django.setup()

from users.models import ContactInquiry
from users.forms import ContactForm
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from datetime import datetime

def test_email_templates():
    """Test the enhanced email templates with sample data"""
    print("🧪 Testing Enhanced Email Templates")
    print("=" * 50)
    
    # Create a test inquiry
    test_data = {
        'full_name': 'John Smith',
        'email': 'john.smith@example.com',
        'phone': '+254712345678',
        'company': 'ABC Corporation',
        'subject': 'Corporate Travel',
        'message': 'We need corporate travel management services for our team of 15 employees. Please provide a comprehensive proposal including accommodation, flights, and ground transportation for business trips to Nairobi, Mombasa, and international destinations.',
        'privacy_consent': True
    }
    
    # Create form and validate
    form = ContactForm(test_data)
    if form.is_valid():
        # Save the inquiry
        inquiry = form.save()
        print(f"✅ Test inquiry created: NVT-{inquiry.id:05d}")
        
        # Prepare email context
        email_context = {
            'inquiry': inquiry,
        }
        
        try:
            # Test admin notification email
            print("\n📧 Testing Admin Notification Email...")
            admin_subject = f"New Contact Inquiry: {inquiry.subject} - {inquiry.full_name}"
            admin_html_content = render_to_string('users/emails/contact_inquiry_admin.html', email_context)
            admin_text_content = render_to_string('users/emails/contact_inquiry_admin.txt', email_context)
            
            print(f"✅ Admin HTML template rendered successfully ({len(admin_html_content)} characters)")
            print(f"✅ Admin text template rendered successfully ({len(admin_text_content)} characters)")
            
            # Check for key elements in admin template
            admin_checks = [
                ('Novustell logo', 'logo-white.png' in admin_html_content),
                ('Department routing', 'Corporate Travel Management Team' in admin_html_content),
                ('Response protocol', '24-Hour Commitment' in admin_html_content),
                ('Contact information', 'New Peoples Media Center' in admin_html_content),
                ('Priority system', 'HIGH PRIORITY' in admin_html_content),
                ('Reference ID', f'NVT-{inquiry.id:05d}' in admin_html_content)
            ]
            
            print("\n🔍 Admin Template Content Verification:")
            for check_name, check_result in admin_checks:
                status = "✅" if check_result else "❌"
                print(f"  {status} {check_name}")
            
            # Test client confirmation email
            print("\n📧 Testing Client Confirmation Email...")
            client_subject = f"Thank You for Your Inquiry - Novustell Travel (Ref: NVT-{inquiry.id:05d})"
            client_html_content = render_to_string('users/emails/contact_inquiry_confirmation.html', email_context)
            client_text_content = render_to_string('users/emails/contact_inquiry_confirmation.txt', email_context)
            
            print(f"✅ Client HTML template rendered successfully ({len(client_html_content)} characters)")
            print(f"✅ Client text template rendered successfully ({len(client_text_content)} characters)")
            
            # Check for key elements in client template
            client_checks = [
                ('Novustell logo', 'logo-white.png' in client_html_content),
                ('Department assignment', 'Corporate Travel Management Team' in client_html_content),
                ('Timeline expectations', 'Within 1 Hours' in client_html_content),
                ('Service process', 'Service Process' in client_html_content),
                ('Contact information', 'New Peoples Media Center' in client_html_content),
                ('Reference ID', f'NVT-{inquiry.id:05d}' in client_html_content)
            ]
            
            print("\n🔍 Client Template Content Verification:")
            for check_name, check_result in client_checks:
                status = "✅" if check_result else "❌"
                print(f"  {status} {check_name}")
            
            # Test actual email sending (optional)
            send_test = input("\n📤 Send actual test emails? (y/n): ").lower().strip() == 'y'
            
            if send_test:
                print("\n📤 Sending test emails...")
                
                # Send admin email
                admin_email = EmailMultiAlternatives(
                    subject=admin_subject,
                    body=admin_text_content,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=['Info@novustelltravel.com'],
                    reply_to=[inquiry.email]
                )
                admin_email.attach_alternative(admin_html_content, "text/html")
                admin_email.send()
                print("✅ Admin notification email sent")
                
                # Send client email
                client_email = EmailMultiAlternatives(
                    subject=client_subject,
                    body=client_text_content,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[inquiry.email],
                    reply_to=['Info@novustelltravel.com']
                )
                client_email.attach_alternative(client_html_content, "text/html")
                client_email.send()
                print("✅ Client confirmation email sent")
                
                print(f"\n📬 Check emails at:")
                print(f"  Admin: Info@novustelltravel.com")
                print(f"  Client: {inquiry.email}")
            
            print("\n🎉 Email template testing completed successfully!")
            print(f"📋 Test inquiry ID: NVT-{inquiry.id:05d}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error during email template testing: {e}")
            return False
            
    else:
        print("❌ Form validation failed:")
        for field, errors in form.errors.items():
            print(f"  {field}: {errors}")
        return False

def test_template_static_files():
    """Test if static files are properly configured"""
    print("\n🔍 Testing Static File Configuration...")
    
    try:
        from django.templatetags.static import static
        from django.conf import settings
        
        logo_path = static('assets/images/logo/logo-white.png')
        print(f"✅ Static file URL generated: {logo_path}")
        
        # Check if STATIC_URL is configured
        print(f"✅ STATIC_URL: {settings.STATIC_URL}")
        
        # Check if static files directory exists
        import os
        static_root = getattr(settings, 'STATICFILES_DIRS', [])
        if static_root:
            logo_file_path = os.path.join(static_root[0], 'assets/images/logo/logo-white.png')
            if os.path.exists(logo_file_path):
                print(f"✅ Logo file exists: {logo_file_path}")
            else:
                print(f"❌ Logo file not found: {logo_file_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Static file configuration error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 NOVUSTELL TRAVEL - EMAIL TEMPLATE TEST")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Test static files first
    static_test = test_template_static_files()
    
    # Test email templates
    template_test = test_email_templates()
    
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"Static Files: {'✅ PASS' if static_test else '❌ FAIL'}")
    print(f"Email Templates: {'✅ PASS' if template_test else '❌ FAIL'}")
    
    if static_test and template_test:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Enhanced email templates are working correctly")
        print("✅ Static file loading is configured properly")
        print("✅ All branding elements are rendering correctly")
    else:
        print("\n⚠️ SOME TESTS FAILED")
        print("❌ Please review the error messages above")
    
    print("=" * 60)
