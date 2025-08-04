#!/usr/bin/env python3
"""
Email Functionality Test Script for Novustell Travel
Tests all email features including SMTP authentication, newsletter, and job applications
"""

import os
import sys
import django
from datetime import datetime

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tours_travels.settings')
django.setup()

from django.core.mail import send_mail, get_connection
from django.conf import settings
from django.template.loader import render_to_string
from users.models import NewsletterSubscription, JobApplication
from users.forms import NewsletterSubscriptionSimpleForm, JobApplicationForm


class EmailTester:
    def __init__(self):
        self.test_results = []
        self.success_count = 0
        self.failure_count = 0
    
    def print_header(self, title):
        print(f"\n{'='*60}")
        print(f"🧪 {title}")
        print(f"{'='*60}")
    
    def print_test(self, test_name, status, details=""):
        status_icon = "✅" if status == "PASS" else "❌"
        print(f"{status_icon} {test_name}: {status}")
        if details:
            print(f"   📝 {details}")
        
        if status == "PASS":
            self.success_count += 1
        else:
            self.failure_count += 1
        
        self.test_results.append({
            'test': test_name,
            'status': status,
            'details': details
        })
    
    def test_email_configuration(self):
        """Test email configuration settings"""
        self.print_header("Email Configuration Test")
        
        # Check email settings
        try:
            email_host = getattr(settings, 'EMAIL_HOST', None)
            email_port = getattr(settings, 'EMAIL_PORT', None)
            email_user = getattr(settings, 'EMAIL_HOST_USER', None)
            email_password = getattr(settings, 'EMAIL_HOST_PASSWORD', None)
            
            self.print_test("EMAIL_HOST", "PASS" if email_host else "FAIL", f"Host: {email_host}")
            self.print_test("EMAIL_PORT", "PASS" if email_port else "FAIL", f"Port: {email_port}")
            self.print_test("EMAIL_HOST_USER", "PASS" if email_user else "FAIL", f"User: {email_user}")
            self.print_test("EMAIL_HOST_PASSWORD", "PASS" if email_password else "FAIL", 
                          f"Password: {'*' * len(email_password) if email_password else 'Not set'}")
            
            # Check custom email addresses
            admin_email = getattr(settings, 'ADMIN_EMAIL', None)
            jobs_email = getattr(settings, 'JOBS_EMAIL', None)
            newsletter_email = getattr(settings, 'NEWSLETTER_EMAIL', None)
            
            self.print_test("ADMIN_EMAIL", "PASS" if admin_email else "FAIL", f"Admin: {admin_email}")
            self.print_test("JOBS_EMAIL", "PASS" if jobs_email else "FAIL", f"Jobs: {jobs_email}")
            self.print_test("NEWSLETTER_EMAIL", "PASS" if newsletter_email else "FAIL", f"Newsletter: {newsletter_email}")
            
        except Exception as e:
            self.print_test("Email Configuration", "FAIL", f"Error: {str(e)}")
    
    def test_smtp_connection(self):
        """Test SMTP connection and authentication"""
        self.print_header("SMTP Connection Test")
        
        try:
            # Test connection
            connection = get_connection()
            connection.open()
            self.print_test("SMTP Connection", "PASS", "Successfully connected to Gmail SMTP")
            connection.close()
            
        except Exception as e:
            self.print_test("SMTP Connection", "FAIL", f"Connection error: {str(e)}")
    
    def test_basic_email_sending(self):
        """Test basic email sending functionality"""
        self.print_header("Basic Email Sending Test")
        
        try:
            # Send a simple test email
            subject = f"Novustell Travel Email Test - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            message = """
            This is a test email from the Novustell Travel application.
            
            Email functionality test results:
            - SMTP connection: Working
            - Email authentication: Successful
            - Email sending: Functional
            
            This email was sent automatically by the email testing script.
            """
            
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [settings.ADMIN_EMAIL]
            
            send_mail(
                subject=subject,
                message=message,
                from_email=from_email,
                recipient_list=recipient_list,
                fail_silently=False,
            )
            
            self.print_test("Basic Email Sending", "PASS", 
                          f"Test email sent to {settings.ADMIN_EMAIL}")
            
        except Exception as e:
            self.print_test("Basic Email Sending", "FAIL", f"Error: {str(e)}")
    
    def test_newsletter_subscription_email(self):
        """Test newsletter subscription email functionality"""
        self.print_header("Newsletter Subscription Email Test")
        
        try:
            # Create a test newsletter subscription
            test_email = "test.newsletter@example.com"
            
            # Clean up any existing test subscription
            NewsletterSubscription.objects.filter(email=test_email).delete()
            
            # Create new subscription
            subscription = NewsletterSubscription.objects.create(
                email=test_email,
                travel_tips=True,
                special_offers=True,
                destination_updates=True
            )
            
            # Test admin notification email
            admin_subject = f'New Newsletter Subscription - {subscription.email}'
            admin_message = render_to_string('users/emails/newsletter_admin.html', {
                'subscription': subscription
            })
            
            newsletter_email = getattr(settings, 'NEWSLETTER_EMAIL', 'news@novustelltravel.com')
            
            send_mail(
                subject=admin_subject,
                message='',
                html_message=admin_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[newsletter_email],
                fail_silently=False,
            )
            
            self.print_test("Newsletter Admin Email", "PASS", 
                          f"Admin notification sent to {newsletter_email}")
            
            # Test subscriber confirmation email
            subscriber_subject = 'Welcome to Novustell Travel Newsletter!'
            subscriber_message = render_to_string('users/emails/newsletter_confirmation.html', {
                'subscription': subscription
            })
            
            send_mail(
                subject=subscriber_subject,
                message='',
                html_message=subscriber_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[subscription.email],
                fail_silently=False,
            )
            
            self.print_test("Newsletter Confirmation Email", "PASS", 
                          f"Confirmation email sent to {subscription.email}")
            
            # Clean up test data
            subscription.delete()
            
        except Exception as e:
            self.print_test("Newsletter Email Test", "FAIL", f"Error: {str(e)}")
    
    def test_job_application_email(self):
        """Test job application email functionality"""
        self.print_header("Job Application Email Test")
        
        try:
            # Create a test job application
            test_application = JobApplication(
                full_name="Test Applicant",
                email="test.applicant@example.com",
                phone_number="+254700000000",
                position_applied_for="travel_consultant",
                years_of_experience=3,
                availability_date="2025-09-01",
                cover_letter="This is a test cover letter for email functionality testing."
            )
            
            # Test admin notification email
            admin_subject = f'New Job Application - {test_application.get_position_applied_for_display()}'
            admin_message = render_to_string('users/emails/job_application_admin.html', {
                'application': test_application
            })
            
            jobs_email = getattr(settings, 'JOBS_EMAIL', 'careers@novustelltravel.com')
            
            send_mail(
                subject=admin_subject,
                message='',
                html_message=admin_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[jobs_email],
                fail_silently=False,
            )
            
            self.print_test("Job Application Admin Email", "PASS", 
                          f"Admin notification sent to {jobs_email}")
            
            # Test applicant confirmation email
            applicant_subject = f'Application Received - {test_application.get_position_applied_for_display()}'
            applicant_message = render_to_string('users/emails/job_application_confirmation.html', {
                'application': test_application
            })
            
            send_mail(
                subject=applicant_subject,
                message='',
                html_message=applicant_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[test_application.email],
                fail_silently=False,
            )
            
            self.print_test("Job Application Confirmation Email", "PASS", 
                          f"Confirmation email sent to {test_application.email}")
            
        except Exception as e:
            self.print_test("Job Application Email Test", "FAIL", f"Error: {str(e)}")
    
    def test_user_registration_email(self):
        """Test user registration email functionality"""
        self.print_header("User Registration Email Test")
        
        try:
            from tours_travels.mail import verification_mail
            from django.contrib.auth.models import User
            
            # Create a test user (don't save to database)
            test_user = User(
                username="testuser",
                email="test.user@example.com",
                first_name="Test",
                last_name="User"
            )
            
            # Test verification email
            test_link = "http://localhost:8000/activate/test-uid/test-token"
            
            result = verification_mail(test_link, test_user)
            
            if result:
                self.print_test("User Registration Email", "PASS", 
                              f"Verification email sent to {test_user.email}")
            else:
                self.print_test("User Registration Email", "FAIL", 
                              "Failed to send verification email")
            
        except Exception as e:
            self.print_test("User Registration Email Test", "FAIL", f"Error: {str(e)}")
    
    def print_summary(self):
        """Print test summary"""
        self.print_header("Test Summary")
        
        total_tests = self.success_count + self.failure_count
        success_rate = (self.success_count / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📊 Total Tests: {total_tests}")
        print(f"✅ Passed: {self.success_count}")
        print(f"❌ Failed: {self.failure_count}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        if self.failure_count == 0:
            print(f"\n🎉 All email functionality tests passed!")
            print(f"📧 Email system is working correctly with Gmail SMTP")
            print(f"🔐 Authentication successful with app password")
        else:
            print(f"\n⚠️  Some tests failed. Please check the configuration.")
            print(f"📧 Email routing:")
            print(f"   • Admin notifications: {getattr(settings, 'ADMIN_EMAIL', 'Not set')}")
            print(f"   • Job applications: {getattr(settings, 'JOBS_EMAIL', 'Not set')}")
            print(f"   • Newsletter: {getattr(settings, 'NEWSLETTER_EMAIL', 'Not set')}")
    
    def run_all_tests(self):
        """Run all email functionality tests"""
        print("🚀 Starting Novustell Travel Email Functionality Tests")
        print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        self.test_email_configuration()
        self.test_smtp_connection()
        self.test_basic_email_sending()
        self.test_newsletter_subscription_email()
        self.test_job_application_email()
        self.test_user_registration_email()
        
        self.print_summary()


if __name__ == "__main__":
    tester = EmailTester()
    tester.run_all_tests()
