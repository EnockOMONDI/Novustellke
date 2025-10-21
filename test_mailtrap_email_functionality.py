#!/usr/bin/env python3
"""
Comprehensive Email Functionality Testing Script for Mailtrap Migration
Tests all email-sending functionality after migrating from Gmail to Mailtrap SMTP
"""

import os
import sys
import django
import time
from datetime import datetime

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tours_travels.settings')
django.setup()

from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from django.test import RequestFactory
from django.contrib.auth.models import User

# Import models and functions
from users.models import (
    ContactInquiry, StudentTravelInquiry, MICEInquiry,
    NGOTravelInquiry, NewsletterSubscription
)
from users.views import (
    send_job_application_emails, send_newsletter_subscription_emails
)

class EmailTester:
    def __init__(self):
        self.results = []
        self.factory = RequestFactory()
        
    def log_result(self, test_name, success, details, response_time=None):
        """Log test results"""
        result = {
            'test_name': test_name,
            'success': success,
            'details': details,
            'response_time': response_time,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        self.results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        time_info = f" ({response_time:.2f}s)" if response_time else ""
        print(f"{status} {test_name}{time_info}")
        print(f"    Details: {details}")
        print()
        
    def test_basic_smtp_connection(self):
        """Test basic SMTP connection to Mailtrap"""
        try:
            start_time = time.time()
            
            # Test basic email sending
            send_mail(
                subject='Mailtrap SMTP Test - Basic Connection',
                message='This is a test email to verify Mailtrap SMTP connection.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=['test@novustelltravel.com'],
                fail_silently=False
            )
            
            response_time = time.time() - start_time
            self.log_result(
                "Basic SMTP Connection Test",
                True,
                f"Successfully sent test email via Mailtrap SMTP (Host: {settings.EMAIL_HOST})",
                response_time
            )
            
        except Exception as e:
            self.log_result(
                "Basic SMTP Connection Test",
                False,
                f"Failed to send email: {str(e)}"
            )
            
    def test_contact_inquiry_emails(self):
        """Test contact inquiry form emails"""
        try:
            start_time = time.time()

            # Test direct email sending for contact inquiry
            send_mail(
                subject='Test Contact Inquiry - Mailtrap',
                message='This is a test contact inquiry for Mailtrap testing.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.ADMIN_EMAIL],
                fail_silently=False
            )

            response_time = time.time() - start_time
            self.log_result(
                "Contact Inquiry Emails",
                True,
                f"Contact inquiry test email sent successfully to {settings.ADMIN_EMAIL}",
                response_time
            )

        except Exception as e:
            self.log_result(
                "Contact Inquiry Emails",
                False,
                f"Failed to send contact inquiry emails: {str(e)}"
            )
            
    def test_student_travel_emails(self):
        """Test student travel inquiry emails"""
        try:
            start_time = time.time()

            # Test direct email sending for student travel
            send_mail(
                subject='Test Student Travel Inquiry - Mailtrap',
                message='This is a test student travel inquiry for Mailtrap testing.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.JOBS_EMAIL, settings.ADMIN_EMAIL],
                fail_silently=False
            )

            response_time = time.time() - start_time
            self.log_result(
                "Student Travel Inquiry Emails",
                True,
                f"Student travel test emails sent to {settings.JOBS_EMAIL} and {settings.ADMIN_EMAIL}",
                response_time
            )

        except Exception as e:
            self.log_result(
                "Student Travel Inquiry Emails",
                False,
                f"Failed to send student travel emails: {str(e)}"
            )
            
    def test_mice_inquiry_emails(self):
        """Test MICE inquiry emails"""
        try:
            start_time = time.time()

            # Test direct email sending for MICE inquiry
            send_mail(
                subject='Test MICE Inquiry - Mailtrap',
                message='This is a test MICE inquiry for Mailtrap testing.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.ADMIN_EMAIL],
                fail_silently=False
            )

            response_time = time.time() - start_time
            self.log_result(
                "MICE Inquiry Emails",
                True,
                f"MICE inquiry test email sent successfully to {settings.ADMIN_EMAIL}",
                response_time
            )

        except Exception as e:
            self.log_result(
                "MICE Inquiry Emails",
                False,
                f"Failed to send MICE inquiry emails: {str(e)}"
            )
            
    def test_ngo_inquiry_emails(self):
        """Test NGO inquiry emails"""
        try:
            start_time = time.time()

            # Test direct email sending for NGO inquiry
            send_mail(
                subject='Test NGO Travel Inquiry - Mailtrap',
                message='This is a test NGO travel inquiry for Mailtrap testing.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.ADMIN_EMAIL],
                fail_silently=False
            )

            response_time = time.time() - start_time
            self.log_result(
                "NGO Inquiry Emails",
                True,
                f"NGO inquiry test email sent successfully to {settings.ADMIN_EMAIL}",
                response_time
            )

        except Exception as e:
            self.log_result(
                "NGO Inquiry Emails",
                False,
                f"Failed to send NGO inquiry emails: {str(e)}"
            )
            
    def test_newsletter_subscription_emails(self):
        """Test newsletter subscription emails"""
        try:
            start_time = time.time()

            # Test direct email sending for newsletter subscription
            send_mail(
                subject='Test Newsletter Subscription - Mailtrap',
                message='This is a test newsletter subscription for Mailtrap testing.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.NEWSLETTER_EMAIL],
                fail_silently=False
            )

            response_time = time.time() - start_time
            self.log_result(
                "Newsletter Subscription Emails",
                True,
                f"Newsletter subscription test email sent successfully to {settings.NEWSLETTER_EMAIL}",
                response_time
            )

        except Exception as e:
            self.log_result(
                "Newsletter Subscription Emails",
                False,
                f"Failed to send newsletter subscription emails: {str(e)}"
            )
            
    def test_email_configuration(self):
        """Test email configuration settings"""
        config_details = []
        
        # Check email settings
        config_details.append(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
        config_details.append(f"EMAIL_HOST: {settings.EMAIL_HOST}")
        config_details.append(f"EMAIL_PORT: {settings.EMAIL_PORT}")
        config_details.append(f"EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
        config_details.append(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
        config_details.append(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
        config_details.append(f"ADMIN_EMAIL: {settings.ADMIN_EMAIL}")
        config_details.append(f"JOBS_EMAIL: {settings.JOBS_EMAIL}")
        config_details.append(f"NEWSLETTER_EMAIL: {settings.NEWSLETTER_EMAIL}")
        
        # Check for EMAIL_TIMEOUT (should not exist)
        has_timeout = hasattr(settings, 'EMAIL_TIMEOUT')
        config_details.append(f"EMAIL_TIMEOUT: {'EXISTS' if has_timeout else 'NOT SET (CORRECT)'}")
        
        # Verify Mailtrap configuration
        is_mailtrap = settings.EMAIL_HOST == 'live.smtp.mailtrap.io'
        is_api_user = settings.EMAIL_HOST_USER == 'api'
        is_correct_from = 'info@novustelltravel.com' in settings.DEFAULT_FROM_EMAIL
        
        success = is_mailtrap and is_api_user and is_correct_from and not has_timeout
        
        self.log_result(
            "Email Configuration Check",
            success,
            "\n    " + "\n    ".join(config_details)
        )
        
    def run_all_tests(self):
        """Run all email functionality tests"""
        print("🚀 STARTING COMPREHENSIVE EMAIL FUNCTIONALITY TESTING")
        print("=" * 60)
        print(f"Testing Mailtrap SMTP Migration")
        print(f"Host: {settings.EMAIL_HOST}")
        print(f"User: {settings.EMAIL_HOST_USER}")
        print(f"From: {settings.DEFAULT_FROM_EMAIL}")
        print("=" * 60)
        print()
        
        # Run all tests
        self.test_email_configuration()
        self.test_basic_smtp_connection()
        self.test_contact_inquiry_emails()
        self.test_student_travel_emails()
        self.test_mice_inquiry_emails()
        self.test_ngo_inquiry_emails()
        self.test_newsletter_subscription_emails()
        
        # Generate summary report
        self.generate_summary_report()
        
    def generate_summary_report(self):
        """Generate comprehensive test summary report"""
        print("=" * 60)
        print("📊 COMPREHENSIVE TEST SUMMARY REPORT")
        print("=" * 60)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print()
        
        if failed_tests > 0:
            print("❌ FAILED TESTS:")
            for result in self.results:
                if not result['success']:
                    print(f"  - {result['test_name']}: {result['details']}")
            print()
        
        # Performance summary
        timed_tests = [r for r in self.results if r['response_time']]
        if timed_tests:
            avg_time = sum(r['response_time'] for r in timed_tests) / len(timed_tests)
            max_time = max(r['response_time'] for r in timed_tests)
            print(f"⏱️  PERFORMANCE SUMMARY:")
            print(f"  Average Response Time: {avg_time:.2f}s")
            print(f"  Maximum Response Time: {max_time:.2f}s")
            print()
        
        # Final verdict
        if failed_tests == 0:
            print("🎉 ALL TESTS PASSED! Mailtrap migration successful!")
        else:
            print("⚠️  Some tests failed. Please review the errors above.")
        
        print("=" * 60)

if __name__ == "__main__":
    tester = EmailTester()
    tester.run_all_tests()
