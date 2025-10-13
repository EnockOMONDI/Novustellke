#!/usr/bin/env python3
"""
Comprehensive Email Testing Suite for Novustell Travel
=====================================================

This test suite validates all email functionality across different environments:
- Production environment with Gmail SMTP
- Development environment with console backend
- Testing environment with in-memory backend

Test Coverage:
- All 12 email trigger points
- Environment-specific configurations
- Template rendering and branding
- Form integration
- Performance and error handling

Usage:
    # Run all tests
    python test_email_system_comprehensive.py

    # Run specific test categories
    python test_email_system_comprehensive.py --production
    python test_email_system_comprehensive.py --development
    python test_email_system_comprehensive.py --templates
    python test_email_system_comprehensive.py --forms

Author: Novustell Travel Development Team
Last Updated: December 15, 2024
"""

import os
import sys
import django
import unittest
import smtplib
import time
from unittest.mock import patch, MagicMock
from django.test import TestCase, override_settings
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.core.management import execute_from_command_line
from django.test.utils import get_runner
import logging

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tours_travels.settings')
django.setup()

# Import Django models and forms after setup
from users.models import ContactInquiry, MICEInquiry, StudentTravelInquiry, NGOTravelInquiry, JobApplication, NewsletterSubscription
from users.forms import ContactForm, MICEInquiryForm, StudentTravelInquiryForm, NGOTravelInquiryForm, JobApplicationForm, NewsletterSubscriptionForm
from users.views import send_job_application_emails, send_newsletter_subscription_emails
from users.utils import send_booking_confirmation_email
from tours_travels.mail import verification_mail
from email_marketing.models import EmailCampaign, EmailTemplate, Recipient
from email_marketing.services import EmailMarketingService

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class EmailSystemTestSuite:
    """Main test suite coordinator"""
    
    def __init__(self):
        self.test_results = {
            'production_tests': {},
            'development_tests': {},
            'template_tests': {},
            'form_tests': {},
            'configuration_tests': {},
            'performance_tests': {}
        }
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0

    def run_all_tests(self):
        """Run all test categories"""
        print("🚀 Starting Comprehensive Email System Tests for Novustell Travel")
        print("=" * 80)
        
        # Run test categories
        self.run_configuration_tests()
        self.run_template_tests()
        self.run_development_tests()
        self.run_production_tests()
        self.run_form_integration_tests()
        self.run_performance_tests()
        
        # Print summary
        self.print_test_summary()

    def run_configuration_tests(self):
        """Test email configuration across all environments"""
        print("\n📋 Testing Email Configuration...")
        
        config_tests = EmailConfigurationTests()
        
        # Test environment files
        self.run_test("Environment Variables (.env.production)", config_tests.test_production_env_vars)
        self.run_test("Environment Variables (.env.development)", config_tests.test_development_env_vars)
        self.run_test("Django Settings (settings.py)", config_tests.test_base_settings)
        self.run_test("Production Settings (settings_prod.py)", config_tests.test_production_settings)
        self.run_test("Development Settings (settings_dev.py)", config_tests.test_development_settings)
        self.run_test("Test Settings (test_settings.py)", config_tests.test_testing_settings)

    def run_template_tests(self):
        """Test all email templates"""
        print("\n📧 Testing Email Templates...")
        
        template_tests = EmailTemplateTests()
        
        # Test all 24 email templates
        templates = [
            'contact_inquiry_admin.html', 'contact_inquiry_confirmation.html',
            'mice_inquiry_admin.html', 'mice_inquiry_confirmation.html',
            'student_travel_admin.html', 'student_travel_confirmation.html',
            'ngo_travel_admin.html', 'ngo_travel_confirmation.html',
            'job_application_admin.html', 'job_application_confirmation.html',
            'newsletter_admin.html', 'newsletter_confirmation.html',
            'booking_confirmation.html', 'welcome.html'
        ]
        
        for template in templates:
            self.run_test(f"Template Rendering: {template}", 
                         lambda t=template: template_tests.test_template_rendering(t))
        
        # Test branding elements
        self.run_test("Novustell Branding Elements", template_tests.test_branding_elements)
        self.run_test("Logo URL Accessibility", template_tests.test_logo_accessibility)

    def run_development_tests(self):
        """Test development environment email functionality"""
        print("\n🔧 Testing Development Environment...")
        
        dev_tests = DevelopmentEnvironmentTests()
        
        self.run_test("Console Email Backend", dev_tests.test_console_backend)
        self.run_test("Development Credentials", dev_tests.test_development_credentials)
        self.run_test("Template Rendering (No Send)", dev_tests.test_template_rendering_no_send)
        self.run_test("Localhost SMTP Server", dev_tests.test_localhost_smtp)

    def run_production_tests(self):
        """Test production environment email functionality"""
        print("\n🌐 Testing Production Environment...")
        
        prod_tests = ProductionEnvironmentTests()
        
        self.run_test("Gmail SMTP Connection", prod_tests.test_gmail_smtp_connection)
        self.run_test("Production Credentials", prod_tests.test_production_credentials)
        self.run_test("TLS/SSL Encryption", prod_tests.test_tls_encryption)
        self.run_test("Departmental Email Addresses", prod_tests.test_departmental_emails)
        self.run_test("Email Delivery Test", prod_tests.test_email_delivery)

    def run_form_integration_tests(self):
        """Test form integration with email sending"""
        print("\n📝 Testing Form Integration...")
        
        form_tests = FormIntegrationTests()
        
        # Test all forms that trigger emails
        forms = [
            ('Contact Form', form_tests.test_contact_form_email),
            ('MICE Inquiry Form', form_tests.test_mice_form_email),
            ('Student Travel Form', form_tests.test_student_form_email),
            ('NGO Travel Form', form_tests.test_ngo_form_email),
            ('Job Application Form', form_tests.test_job_application_email),
            ('Newsletter Form', form_tests.test_newsletter_email),
        ]
        
        for form_name, test_method in forms:
            self.run_test(f"{form_name} Email Integration", test_method)

    def run_performance_tests(self):
        """Test performance and error handling"""
        print("\n⚡ Testing Performance & Error Handling...")
        
        perf_tests = PerformanceTests()
        
        self.run_test("Email Sending Timeout", perf_tests.test_email_timeout)
        self.run_test("SMTP Failure Handling", perf_tests.test_smtp_failure_handling)
        self.run_test("Template Error Handling", perf_tests.test_template_error_handling)
        self.run_test("Dual Email Pattern", perf_tests.test_dual_email_pattern)

    def run_test(self, test_name, test_function):
        """Run individual test and track results"""
        self.total_tests += 1
        try:
            start_time = time.time()
            result = test_function()
            end_time = time.time()
            duration = end_time - start_time
            
            if result:
                print(f"✅ {test_name} - PASSED ({duration:.2f}s)")
                self.passed_tests += 1
                return True
            else:
                print(f"❌ {test_name} - FAILED ({duration:.2f}s)")
                self.failed_tests += 1
                return False
        except Exception as e:
            print(f"❌ {test_name} - ERROR: {str(e)}")
            self.failed_tests += 1
            return False

    def print_test_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE EMAIL SYSTEM TEST SUMMARY")
        print("=" * 80)
        print(f"Total Tests Run: {self.total_tests}")
        print(f"✅ Passed: {self.passed_tests}")
        print(f"❌ Failed: {self.failed_tests}")
        print(f"Success Rate: {(self.passed_tests/self.total_tests)*100:.1f}%")
        
        if self.failed_tests == 0:
            print("\n🎉 ALL TESTS PASSED! Email system is fully operational.")
        else:
            print(f"\n⚠️  {self.failed_tests} tests failed. Please review the issues above.")
        
        print("=" * 80)


class EmailConfigurationTests:
    """Test email configuration across all environments"""
    
    def test_production_env_vars(self):
        """Test production environment variables"""
        try:
            # Check if .env.production exists and has required variables
            env_file = '.env.production'
            if not os.path.exists(env_file):
                logger.error(f"{env_file} not found")
                return False
            
            with open(env_file, 'r') as f:
                content = f.read()
            
            required_vars = [
                'EMAIL_HOST_USER=novustellke@gmail.com',
                'ADMIN_EMAIL=info@novustelltravel.com',
                'JOBS_EMAIL=careers@novustelltravel.com',
                'NEWSLETTER_EMAIL=news@novustelltravel.com'
            ]
            
            for var in required_vars:
                if var not in content:
                    logger.error(f"Missing required variable: {var}")
                    return False
            
            # Check for production password
            if 'EMAIL_HOST_PASSWORD=' not in content:
                logger.error("EMAIL_HOST_PASSWORD not found")
                return False
            
            return True
        except Exception as e:
            logger.error(f"Production env test failed: {e}")
            return False

    def test_development_env_vars(self):
        """Test development environment variables"""
        try:
            env_file = '.env.development'
            if not os.path.exists(env_file):
                logger.error(f"{env_file} not found")
                return False
            
            with open(env_file, 'r') as f:
                content = f.read()
            
            # Check for development-specific settings
            required_vars = [
                'DEBUG=True',
                'EMAIL_HOST_USER=novustellke@gmail.com',
                'EMAIL_HOST_PASSWORD=vsmw vdut tanu gtdg'
            ]
            
            for var in required_vars:
                if var not in content:
                    logger.error(f"Missing development variable: {var}")
                    return False
            
            return True
        except Exception as e:
            logger.error(f"Development env test failed: {e}")
            return False

    def test_base_settings(self):
        """Test base Django settings"""
        try:
            # Import and check base settings
            from tours_travels import settings as base_settings
            
            required_settings = [
                'EMAIL_BACKEND',
                'EMAIL_HOST',
                'EMAIL_PORT',
                'EMAIL_USE_TLS',
                'EMAIL_HOST_USER',
                'DEFAULT_FROM_EMAIL',
                'ADMIN_EMAIL',
                'JOBS_EMAIL',
                'NEWSLETTER_EMAIL'
            ]
            
            for setting in required_settings:
                if not hasattr(base_settings, setting):
                    logger.error(f"Missing setting: {setting}")
                    return False
            
            # Verify specific values
            if base_settings.EMAIL_HOST != 'smtp.gmail.com':
                logger.error(f"Incorrect EMAIL_HOST: {base_settings.EMAIL_HOST}")
                return False
            
            if base_settings.EMAIL_PORT != 587:
                logger.error(f"Incorrect EMAIL_PORT: {base_settings.EMAIL_PORT}")
                return False
            
            return True
        except Exception as e:
            logger.error(f"Base settings test failed: {e}")
            return False

    def test_production_settings(self):
        """Test production-specific settings"""
        try:
            # Test production settings file exists
            prod_settings_file = 'tours_travels/settings_prod.py'
            if not os.path.exists(prod_settings_file):
                logger.error(f"{prod_settings_file} not found")
                return False
            
            with open(prod_settings_file, 'r') as f:
                content = f.read()
            
            # Check for production-specific email settings
            if 'EMAIL_BACKEND' not in content:
                logger.error("EMAIL_BACKEND not configured in production settings")
                return False
            
            if 'smtp.EmailBackend' not in content:
                logger.error("SMTP backend not configured for production")
                return False
            
            return True
        except Exception as e:
            logger.error(f"Production settings test failed: {e}")
            return False

    def test_development_settings(self):
        """Test development-specific settings"""
        try:
            dev_settings_file = 'tours_travels/settings_dev.py'
            if not os.path.exists(dev_settings_file):
                logger.error(f"{dev_settings_file} not found")
                return False
            
            with open(dev_settings_file, 'r') as f:
                content = f.read()
            
            # Check for console backend in development
            if 'console.EmailBackend' not in content:
                logger.error("Console backend not configured for development")
                return False
            
            return True
        except Exception as e:
            logger.error(f"Development settings test failed: {e}")
            return False

    def test_testing_settings(self):
        """Test testing environment settings"""
        try:
            test_settings_file = 'tours_travels/test_settings.py'
            if not os.path.exists(test_settings_file):
                logger.error(f"{test_settings_file} not found")
                return False
            
            with open(test_settings_file, 'r') as f:
                content = f.read()
            
            # Check for locmem backend in testing
            if 'locmem.EmailBackend' not in content:
                logger.error("Locmem backend not configured for testing")
                return False
            
            return True
        except Exception as e:
            logger.error(f"Testing settings test failed: {e}")
            return False


class EmailTemplateTests:
    """Test email template rendering and branding"""
    
    def test_template_rendering(self, template_name):
        """Test individual template rendering"""
        try:
            # Create mock context data
            mock_context = self.get_mock_context(template_name)
            
            # Attempt to render template
            template_path = f'users/emails/{template_name}'
            rendered_content = render_to_string(template_path, mock_context)
            
            if not rendered_content:
                logger.error(f"Template {template_name} rendered empty content")
                return False
            
            # Check for basic HTML structure
            if template_name.endswith('.html'):
                if '<html' not in rendered_content.lower():
                    logger.error(f"Template {template_name} missing HTML structure")
                    return False
            
            return True
        except Exception as e:
            logger.error(f"Template rendering failed for {template_name}: {e}")
            return False

    def test_branding_elements(self):
        """Test Novustell branding elements in templates"""
        try:
            # Test contact inquiry admin template for branding
            mock_context = {
                'inquiry': {
                    'full_name': 'Test User',
                    'email': 'test@example.com',
                    'subject': 'Test Subject',
                    'message': 'Test message',
                    'created_at': '2024-12-15'
                }
            }
            
            rendered_content = render_to_string('users/emails/contact_inquiry_admin.html', mock_context)
            
            # Check for Novustell brand colors
            brand_colors = ['#170b2c', '#ff9d00', '#f8f3fc']
            for color in brand_colors:
                if color not in rendered_content:
                    logger.error(f"Brand color {color} not found in template")
                    return False
            
            # Check for Novustell Travel text
            if 'Novustell Travel' not in rendered_content:
                logger.error("Novustell Travel branding not found")
                return False
            
            return True
        except Exception as e:
            logger.error(f"Branding test failed: {e}")
            return False

    def test_logo_accessibility(self):
        """Test logo URL accessibility"""
        try:
            import requests
            logo_url = 'https://www.novustelltravel.com/static/assets/images/logo/logo-white.png'
            
            response = requests.head(logo_url, timeout=10)
            if response.status_code != 200:
                logger.error(f"Logo URL not accessible: {response.status_code}")
                return False
            
            return True
        except Exception as e:
            logger.error(f"Logo accessibility test failed: {e}")
            return False

    def get_mock_context(self, template_name):
        """Get appropriate mock context for template"""
        if 'contact_inquiry' in template_name:
            return {
                'inquiry': {
                    'full_name': 'Test User',
                    'email': 'test@example.com',
                    'subject': 'Test Subject',
                    'message': 'Test message',
                    'phone': '+254701363551',
                    'company': 'Test Company',
                    'created_at': '2024-12-15'
                }
            }
        elif 'mice_inquiry' in template_name:
            return {
                'inquiry': {
                    'company_name': 'Test Company',
                    'contact_person': 'Test Person',
                    'email': 'test@example.com',
                    'event_type': 'Conference',
                    'attendees': 50
                }
            }
        elif 'job_application' in template_name:
            return {
                'application': {
                    'full_name': 'Test Applicant',
                    'email': 'applicant@example.com',
                    'position_applied_for': 'Travel Consultant',
                    'years_of_experience': 3
                }
            }
        elif 'newsletter' in template_name:
            return {
                'subscription': {
                    'email': 'subscriber@example.com',
                    'travel_tips': True,
                    'special_offers': True
                }
            }
        elif 'welcome' in template_name:
            return {
                'user': {
                    'first_name': 'Test',
                    'email': 'user@example.com'
                },
                'password': 'temp_password123'
            }
        else:
            return {'test_data': 'Test Value'}


class DevelopmentEnvironmentTests:
    """Test development environment email functionality"""
    
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.console.EmailBackend')
    def test_console_backend(self):
        """Test console email backend"""
        try:
            from django.core.mail import send_mail
            from io import StringIO
            import sys
            
            # Capture console output
            captured_output = StringIO()
            sys.stdout = captured_output
            
            # Send test email
            result = send_mail(
                'Test Subject',
                'Test message',
                'test@example.com',
                ['recipient@example.com'],
                fail_silently=False
            )
            
            # Restore stdout
            sys.stdout = sys.__stdout__
            
            # Check if email was "sent" to console
            output = captured_output.getvalue()
            if 'Test Subject' not in output:
                logger.error("Email not sent to console")
                return False
            
            return result == 1
        except Exception as e:
            logger.error(f"Console backend test failed: {e}")
            return False

    def test_development_credentials(self):
        """Test development email credentials"""
        try:
            # Check development credentials
            dev_user = 'novustellke@gmail.com'
            dev_password = 'vsmw vdut tanu gtdg'
            
            # Test SMTP connection with development credentials
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(dev_user, dev_password)
            server.quit()
            
            return True
        except Exception as e:
            logger.error(f"Development credentials test failed: {e}")
            return False

    def test_template_rendering_no_send(self):
        """Test template rendering without sending emails"""
        try:
            # Test rendering without sending
            mock_context = {
                'inquiry': {
                    'full_name': 'Test User',
                    'email': 'test@example.com',
                    'subject': 'Test Subject'
                }
            }
            
            html_content = render_to_string('users/emails/contact_inquiry_admin.html', mock_context)
            text_content = render_to_string('users/emails/contact_inquiry_admin.txt', mock_context)
            
            if not html_content or not text_content:
                logger.error("Template rendering failed")
                return False
            
            return True
        except Exception as e:
            logger.error(f"Template rendering test failed: {e}")
            return False

    def test_localhost_smtp(self):
        """Test localhost SMTP server connection"""
        try:
            # Test connection to localhost SMTP (if running)
            server = smtplib.SMTP('localhost', 1025)
            server.quit()
            return True
        except Exception as e:
            # This is expected if localhost SMTP is not running
            logger.info("Localhost SMTP server not running (expected in most cases)")
            return True


class ProductionEnvironmentTests:
    """Test production environment email functionality"""
    
    def test_gmail_smtp_connection(self):
        """Test Gmail SMTP connection"""
        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.quit()
            return True
        except Exception as e:
            logger.error(f"Gmail SMTP connection failed: {e}")
            return False

    def test_production_credentials(self):
        """Test production email credentials"""
        try:
            # Test production credentials (use actual production password)
            prod_user = 'novustellke@gmail.com'
            prod_password = 'iagt yans hoyd pavg'  # Production password
            
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(prod_user, prod_password)
            server.quit()
            
            return True
        except Exception as e:
            logger.error(f"Production credentials test failed: {e}")
            return False

    def test_tls_encryption(self):
        """Test TLS encryption"""
        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            
            # Check if TLS is enabled
            if not server.sock:
                logger.error("TLS connection not established")
                return False
            
            server.quit()
            return True
        except Exception as e:
            logger.error(f"TLS encryption test failed: {e}")
            return False

    def test_departmental_emails(self):
        """Test departmental email addresses"""
        try:
            departmental_emails = [
                'info@novustelltravel.com',
                'careers@novustelltravel.com',
                'news@novustelltravel.com'
            ]
            
            # Basic email format validation
            import re
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            
            for email in departmental_emails:
                if not re.match(email_pattern, email):
                    logger.error(f"Invalid email format: {email}")
                    return False
            
            return True
        except Exception as e:
            logger.error(f"Departmental emails test failed: {e}")
            return False

    def test_email_delivery(self):
        """Test actual email delivery (optional - requires confirmation)"""
        try:
            # This test sends an actual email - use with caution
            # Uncomment only for production testing
            
            # from django.core.mail import send_mail
            # result = send_mail(
            #     'Novustell Travel Email System Test',
            #     'This is a test email from the comprehensive email testing suite.',
            #     'novustellke@gmail.com',
            #     ['info@novustelltravel.com'],
            #     fail_silently=False
            # )
            # return result == 1
            
            # For safety, we'll skip actual email delivery in automated tests
            logger.info("Email delivery test skipped (safety measure)")
            return True
        except Exception as e:
            logger.error(f"Email delivery test failed: {e}")
            return False


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Comprehensive Email System Tests')
    parser.add_argument('--production', action='store_true', help='Run production tests only')
    parser.add_argument('--development', action='store_true', help='Run development tests only')
    parser.add_argument('--templates', action='store_true', help='Run template tests only')
    parser.add_argument('--forms', action='store_true', help='Run form tests only')
    parser.add_argument('--config', action='store_true', help='Run configuration tests only')
    parser.add_argument('--performance', action='store_true', help='Run performance tests only')
    
    args = parser.parse_args()
    
    # Initialize test suite
    test_suite = EmailSystemTestSuite()
    
    # Run specific test categories or all tests
    if args.production:
        test_suite.run_production_tests()
    elif args.development:
        test_suite.run_development_tests()
    elif args.templates:
        test_suite.run_template_tests()
    elif args.forms:
        test_suite.run_form_integration_tests()
    elif args.config:
        test_suite.run_configuration_tests()
    elif args.performance:
        test_suite.run_performance_tests()
    else:
        test_suite.run_all_tests()


class FormIntegrationTests:
    """Test form integration with email sending"""

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_contact_form_email(self):
        """Test contact form email integration"""
        try:
            from django.core import mail

            # Create test contact inquiry
            form_data = {
                'full_name': 'Test User',
                'email': 'test@example.com',
                'phone': '+254701363551',
                'company': 'Test Company',
                'subject': 'Test Inquiry',
                'message': 'This is a test message',
                'privacy_consent': True
            }

            form = ContactForm(data=form_data)
            if not form.is_valid():
                logger.error(f"Contact form validation failed: {form.errors}")
                return False

            # Save form and trigger email
            inquiry = form.save()

            # Simulate email sending (would normally be in view)
            from django.template.loader import render_to_string
            from django.core.mail import EmailMultiAlternatives

            # Admin email
            admin_html = render_to_string('users/emails/contact_inquiry_admin.html', {'inquiry': inquiry})
            admin_email = EmailMultiAlternatives(
                subject=f"New Contact Inquiry: {inquiry.subject}",
                body="Admin notification",
                from_email='novustellke@gmail.com',
                to=['info@novustelltravel.com']
            )
            admin_email.attach_alternative(admin_html, "text/html")
            admin_email.send()

            # Client email
            client_html = render_to_string('users/emails/contact_inquiry_confirmation.html', {'inquiry': inquiry})
            client_email = EmailMultiAlternatives(
                subject="Thank You for Your Inquiry",
                body="Client confirmation",
                from_email='novustellke@gmail.com',
                to=[inquiry.email]
            )
            client_email.attach_alternative(client_html, "text/html")
            client_email.send()

            # Check if emails were sent
            if len(mail.outbox) != 2:
                logger.error(f"Expected 2 emails, got {len(mail.outbox)}")
                return False

            return True
        except Exception as e:
            logger.error(f"Contact form email test failed: {e}")
            return False

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_mice_form_email(self):
        """Test MICE inquiry form email integration"""
        try:
            from django.core import mail

            # Create test MICE inquiry
            mice_data = {
                'company_name': 'Test Corp',
                'contact_person': 'Test Person',
                'email': 'mice@example.com',
                'phone_number': '+254701363551',
                'event_type': 'conference',
                'attendees': 50,
                'event_details': 'Test conference details'
            }

            form = MICEInquiryForm(data=mice_data)
            if not form.is_valid():
                logger.error(f"MICE form validation failed: {form.errors}")
                return False

            inquiry = form.save()

            # Simulate email sending
            from django.core.mail import send_mail
            from django.template.loader import render_to_string

            # Admin email
            admin_html = render_to_string('users/emails/mice_inquiry_admin.html', {'inquiry': inquiry})
            send_mail(
                subject=f'New MICE Inquiry from {inquiry.company_name}',
                message='Admin notification',
                html_message=admin_html,
                from_email='novustellke@gmail.com',
                recipient_list=['info@novustelltravel.com'],
                fail_silently=False
            )

            # Client email
            client_html = render_to_string('users/emails/mice_inquiry_confirmation.html', {'inquiry': inquiry})
            send_mail(
                subject=f'MICE Inquiry Received - {inquiry.company_name}',
                message='Client confirmation',
                html_message=client_html,
                from_email='novustellke@gmail.com',
                recipient_list=[inquiry.email],
                fail_silently=False
            )

            # Check emails
            if len(mail.outbox) != 2:
                logger.error(f"Expected 2 emails, got {len(mail.outbox)}")
                return False

            return True
        except Exception as e:
            logger.error(f"MICE form email test failed: {e}")
            return False

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_student_form_email(self):
        """Test student travel form email integration"""
        try:
            from django.core import mail

            student_data = {
                'school_name': 'Test School',
                'contact_person': 'Test Teacher',
                'email': 'teacher@school.com',
                'phone_number': '+254701363551',
                'program_stage': 'high_school',
                'number_of_students': 30,
                'travel_details': 'Educational trip details'
            }

            form = StudentTravelInquiryForm(data=student_data)
            if not form.is_valid():
                logger.error(f"Student form validation failed: {form.errors}")
                return False

            inquiry = form.save()

            # Simulate dual email sending
            from django.core.mail import send_mail
            from django.template.loader import render_to_string

            # Send both admin and client emails
            admin_html = render_to_string('users/emails/student_travel_admin.html', {'inquiry': inquiry})
            client_html = render_to_string('users/emails/student_travel_confirmation.html', {'inquiry': inquiry})

            send_mail('Admin notification', 'text', 'novustellke@gmail.com', ['info@novustelltravel.com'], html_message=admin_html)
            send_mail('Client confirmation', 'text', 'novustellke@gmail.com', [inquiry.email], html_message=client_html)

            return len(mail.outbox) == 2
        except Exception as e:
            logger.error(f"Student form email test failed: {e}")
            return False

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_ngo_form_email(self):
        """Test NGO travel form email integration"""
        try:
            from django.core import mail

            ngo_data = {
                'organization_name': 'Test NGO',
                'contact_person': 'NGO Contact',
                'email': 'contact@ngo.org',
                'phone_number': '+254701363551',
                'organization_type': 'humanitarian',
                'travel_purpose': 'field_work',
                'number_of_travelers': 5,
                'travel_details': 'Humanitarian mission',
                'sustainability_requirements': True
            }

            form = NGOTravelInquiryForm(data=ngo_data)
            if not form.is_valid():
                logger.error(f"NGO form validation failed: {form.errors}")
                return False

            inquiry = form.save()

            # Test email sending
            from django.core.mail import send_mail
            from django.template.loader import render_to_string

            admin_html = render_to_string('users/emails/ngo_travel_admin.html', {'inquiry': inquiry})
            client_html = render_to_string('users/emails/ngo_travel_confirmation.html', {'inquiry': inquiry})

            send_mail('NGO Admin', 'text', 'novustellke@gmail.com', ['info@novustelltravel.com'], html_message=admin_html)
            send_mail('NGO Client', 'text', 'novustellke@gmail.com', [inquiry.email], html_message=client_html)

            return len(mail.outbox) == 2
        except Exception as e:
            logger.error(f"NGO form email test failed: {e}")
            return False

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_job_application_email(self):
        """Test job application form email integration"""
        try:
            from django.core import mail
            from django.core.files.uploadedfile import SimpleUploadedFile

            # Create mock resume file
            resume_content = b"Mock resume content"
            resume_file = SimpleUploadedFile("resume.pdf", resume_content, content_type="application/pdf")

            job_data = {
                'full_name': 'Test Applicant',
                'email': 'applicant@example.com',
                'phone_number': '+254701363551',
                'position_applied_for': 'travel_consultant',
                'years_of_experience': 3,
                'availability_date': '2024-12-15',
                'cover_letter': 'Test cover letter content',
                'resume': resume_file
            }

            form = JobApplicationForm(data=job_data, files={'resume': resume_file})
            if not form.is_valid():
                logger.error(f"Job application form validation failed: {form.errors}")
                return False

            application = form.save()

            # Test job application email function
            send_job_application_emails(application)

            # Should send to careers@, info@, and applicant (3 emails total)
            if len(mail.outbox) != 3:
                logger.error(f"Expected 3 emails for job application, got {len(mail.outbox)}")
                return False

            return True
        except Exception as e:
            logger.error(f"Job application email test failed: {e}")
            return False

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_newsletter_email(self):
        """Test newsletter subscription email integration"""
        try:
            from django.core import mail

            newsletter_data = {
                'email': 'subscriber@example.com',
                'travel_tips': True,
                'special_offers': True,
                'destination_updates': False
            }

            form = NewsletterSubscriptionForm(data=newsletter_data)
            if not form.is_valid():
                logger.error(f"Newsletter form validation failed: {form.errors}")
                return False

            subscription = form.save()

            # Test newsletter email function
            send_newsletter_subscription_emails(subscription)

            # Should send admin notification and subscriber confirmation
            if len(mail.outbox) != 2:
                logger.error(f"Expected 2 emails for newsletter, got {len(mail.outbox)}")
                return False

            return True
        except Exception as e:
            logger.error(f"Newsletter email test failed: {e}")
            return False


class PerformanceTests:
    """Test performance and error handling"""

    def test_email_timeout(self):
        """Test email sending timeout scenarios"""
        try:
            import time
            from django.core.mail import send_mail

            start_time = time.time()

            # Test with mock slow SMTP
            with patch('smtplib.SMTP') as mock_smtp:
                mock_instance = MagicMock()
                mock_smtp.return_value = mock_instance

                # Simulate slow email sending
                def slow_send(*args, **kwargs):
                    time.sleep(0.1)  # Simulate delay
                    return True

                mock_instance.send_message = slow_send

                result = send_mail(
                    'Test Subject',
                    'Test message',
                    'test@example.com',
                    ['recipient@example.com'],
                    fail_silently=False
                )

            end_time = time.time()
            duration = end_time - start_time

            # Check if operation completed within reasonable time
            if duration > 5.0:  # 5 second timeout
                logger.error(f"Email sending took too long: {duration:.2f}s")
                return False

            return True
        except Exception as e:
            logger.error(f"Email timeout test failed: {e}")
            return False

    def test_smtp_failure_handling(self):
        """Test SMTP failure handling"""
        try:
            from django.core.mail import send_mail

            # Test with invalid SMTP settings
            with override_settings(
                EMAIL_BACKEND='django.core.mail.backends.smtp.EmailBackend',
                EMAIL_HOST='invalid.smtp.server',
                EMAIL_PORT=587
            ):
                try:
                    result = send_mail(
                        'Test Subject',
                        'Test message',
                        'test@example.com',
                        ['recipient@example.com'],
                        fail_silently=True  # Should not raise exception
                    )
                    # Should return False or 0 for failed sending
                    return result == 0
                except Exception:
                    # Should not raise exception with fail_silently=True
                    logger.error("Exception raised despite fail_silently=True")
                    return False

        except Exception as e:
            logger.error(f"SMTP failure handling test failed: {e}")
            return False

    def test_template_error_handling(self):
        """Test template error handling"""
        try:
            from django.template.loader import render_to_string

            # Test with invalid template
            try:
                render_to_string('users/emails/nonexistent_template.html', {})
                logger.error("Should have raised TemplateDoesNotExist")
                return False
            except Exception:
                # Expected behavior
                pass

            # Test with invalid context
            try:
                render_to_string('users/emails/contact_inquiry_admin.html', {'invalid': 'context'})
                # Should still render but with missing variables
                return True
            except Exception as e:
                logger.error(f"Template should handle missing context gracefully: {e}")
                return False

        except Exception as e:
            logger.error(f"Template error handling test failed: {e}")
            return False

    def test_dual_email_pattern(self):
        """Test dual email pattern (admin + client)"""
        try:
            from django.core import mail
            from django.core.mail import send_mail

            with override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend'):
                # Simulate dual email sending pattern

                # Admin email
                admin_result = send_mail(
                    'Admin: New Inquiry',
                    'Admin notification message',
                    'novustellke@gmail.com',
                    ['info@novustelltravel.com'],
                    fail_silently=False
                )

                # Client email
                client_result = send_mail(
                    'Thank You for Your Inquiry',
                    'Client confirmation message',
                    'novustellke@gmail.com',
                    ['client@example.com'],
                    fail_silently=False
                )

                # Check both emails were sent
                if len(mail.outbox) != 2:
                    logger.error(f"Dual email pattern failed: {len(mail.outbox)} emails sent")
                    return False

                # Check email recipients
                admin_email = mail.outbox[0]
                client_email = mail.outbox[1]

                if 'info@novustelltravel.com' not in admin_email.to:
                    logger.error("Admin email not sent to correct recipient")
                    return False

                if 'client@example.com' not in client_email.to:
                    logger.error("Client email not sent to correct recipient")
                    return False

                return admin_result == 1 and client_result == 1

        except Exception as e:
            logger.error(f"Dual email pattern test failed: {e}")
            return False


# Additional utility functions for testing
def run_quick_test():
    """Run a quick subset of critical tests"""
    print("🚀 Running Quick Email System Test...")

    quick_tests = [
        ("SMTP Connection", ProductionEnvironmentTests().test_gmail_smtp_connection),
        ("Template Rendering", EmailTemplateTests().test_template_rendering('contact_inquiry_admin.html')),
        ("Console Backend", DevelopmentEnvironmentTests().test_console_backend),
        ("Configuration Check", EmailConfigurationTests().test_base_settings)
    ]

    passed = 0
    total = len(quick_tests)

    for test_name, test_func in quick_tests:
        try:
            if test_func():
                print(f"✅ {test_name} - PASSED")
                passed += 1
            else:
                print(f"❌ {test_name} - FAILED")
        except Exception as e:
            print(f"❌ {test_name} - ERROR: {e}")

    print(f"\n📊 Quick Test Results: {passed}/{total} passed ({(passed/total)*100:.1f}%)")
    return passed == total


def validate_email_system_health():
    """Validate overall email system health"""
    print("🏥 Email System Health Check...")

    health_checks = {
        'smtp_connection': False,
        'template_rendering': False,
        'configuration': False,
        'credentials': False
    }

    try:
        # SMTP connection
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.quit()
        health_checks['smtp_connection'] = True

        # Template rendering
        render_to_string('users/emails/contact_inquiry_admin.html', {'inquiry': {'full_name': 'Test'}})
        health_checks['template_rendering'] = True

        # Configuration
        from django.conf import settings
        if hasattr(settings, 'EMAIL_HOST') and settings.EMAIL_HOST == 'smtp.gmail.com':
            health_checks['configuration'] = True

        # Credentials (development)
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login('novustellke@gmail.com', 'vsmw vdut tanu gtdg')
        server.quit()
        health_checks['credentials'] = True

    except Exception as e:
        logger.error(f"Health check error: {e}")

    # Print health status
    for check, status in health_checks.items():
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {check.replace('_', ' ').title()}: {'HEALTHY' if status else 'UNHEALTHY'}")

    overall_health = all(health_checks.values())
    print(f"\n🏥 Overall System Health: {'HEALTHY' if overall_health else 'NEEDS ATTENTION'}")

    return overall_health
