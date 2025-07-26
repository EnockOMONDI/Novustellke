"""
Tests for email functionality
"""

from django.test import TestCase, override_settings
from django.core import mail
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from decimal import Decimal

from users.models import Booking
from users.checkout_views import send_booking_confirmation_email, send_welcome_email
from adminside.models import Package, Destination


@override_settings(
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    DEFAULT_FROM_EMAIL='test@novustelltravel.com'
)
class EmailFunctionalityTest(TestCase):
    """Test email sending functionality"""
    
    def setUp(self):
        """Set up test data"""
        # Clear mail outbox
        mail.outbox = []
        
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        # Create test destination and package
        self.destination = Destination.objects.create(
            name='Maasai Mara',
            description='Famous wildlife reserve'
        )
        
        self.package = Package.objects.create(
            name='Maasai Mara Safari',
            description='3-day wildlife safari',
            adult_price=1500,
            child_price=1050,  # 30% discount for children
            duration_days=3,
            duration_nights=2,
            main_destination=self.destination,
            status=Package.PUBLISHED
        )
        
        # Create test booking
        self.booking = Booking.objects.create(
            package=self.package,
            user=self.user,
            full_name='Test User',
            email='test@example.com',
            phone_number='+254701363551',
            number_of_adults=2,
            number_of_children=1,
            number_of_rooms=1,
            package_price=Decimal('3000.00'),
            accommodation_price=Decimal('400.00'),
            travel_price=Decimal('300.00'),
            total_amount=Decimal('3700.00'),
            special_requests='Vegetarian meals'
        )
    
    def test_booking_confirmation_email_sending(self):
        """Test sending booking confirmation email"""
        # Send email
        send_booking_confirmation_email(self.booking, is_new_user=False)
        
        # Check that email was sent
        self.assertEqual(len(mail.outbox), 1)
        
        email = mail.outbox[0]
        self.assertEqual(email.to, ['test@example.com'])
        self.assertIn('Booking Confirmation', email.subject)
        self.assertIn(self.booking.booking_reference, email.subject)
        
        # Check email content
        self.assertIn('Test User', email.body)
        self.assertIn(self.package.name, email.body)
        self.assertIn(self.booking.booking_reference, email.body)
        self.assertIn('$3700', email.body)
        
        # Check HTML content
        self.assertIn('Test User', email.alternatives[0][0])
        self.assertIn(self.package.name, email.alternatives[0][0])
        self.assertIn('Vegetarian meals', email.alternatives[0][0])
    
    def test_booking_confirmation_email_new_user(self):
        """Test booking confirmation email for new user"""
        # Send email for new user
        send_booking_confirmation_email(self.booking, is_new_user=True)
        
        # Check that email was sent
        self.assertEqual(len(mail.outbox), 1)
        
        email = mail.outbox[0]
        html_content = email.alternatives[0][0]
        
        # Should contain new user welcome section
        self.assertIn('Your Account is Ready', html_content)
        self.assertIn('Access your dashboard', html_content)
        self.assertIn(self.booking.email, html_content)
    
    def test_booking_confirmation_email_existing_user(self):
        """Test booking confirmation email for existing user"""
        # Send email for existing user
        send_booking_confirmation_email(self.booking, is_new_user=False)
        
        # Check that email was sent
        self.assertEqual(len(mail.outbox), 1)
        
        email = mail.outbox[0]
        html_content = email.alternatives[0][0]
        
        # Should contain existing user dashboard section
        self.assertIn('Manage Your Booking', html_content)
        self.assertIn('Go to Dashboard', html_content)
    
    def test_welcome_email_sending(self):
        """Test sending welcome email to new user"""
        password = 'temppass123'
        
        # Send welcome email
        send_welcome_email(self.user, password)
        
        # Check that email was sent
        self.assertEqual(len(mail.outbox), 1)
        
        email = mail.outbox[0]
        self.assertEqual(email.to, ['test@example.com'])
        self.assertEqual(email.subject, 'Welcome to Novustell Travel')
        
        # Check email content
        self.assertIn('Test', email.body)  # First name
        self.assertIn(password, email.body)
        self.assertIn('test@example.com', email.body)
        
        # Check HTML content
        html_content = email.alternatives[0][0]
        self.assertIn('Welcome to Novustell Travel', html_content)
        self.assertIn('Test', html_content)  # First name
        self.assertIn(password, html_content)
        self.assertIn('test@example.com', html_content)
        self.assertIn('Your Account Login Details', html_content)
        self.assertIn('Security Information', html_content)
    
    def test_email_template_rendering(self):
        """Test email template rendering"""
        # Test booking confirmation template
        context = {
            'booking': self.booking,
            'is_new_user': True,
            'dashboard_url': 'http://localhost:8000/profile/',
            'whatsapp_link': 'https://api.whatsapp.com/send?phone=254701363551'
        }
        
        html_content = render_to_string('users/emails/booking_confirmation.html', context)
        
        # Check that all context variables are rendered
        self.assertIn(self.booking.booking_reference, html_content)
        self.assertIn(self.booking.full_name, html_content)
        self.assertIn(self.package.name, html_content)
        self.assertIn('$3700', html_content)
        self.assertIn('Your Account is Ready', html_content)
        self.assertIn('http://localhost:8000/profile/', html_content)
        
        # Test welcome email template
        welcome_context = {
            'user': self.user,
            'password': 'temppass123'
        }
        
        welcome_html = render_to_string('users/emails/welcome.html', welcome_context)
        
        # Check welcome email content
        self.assertIn('Welcome to Novustell Travel', welcome_html)
        self.assertIn('Test', welcome_html)  # First name
        self.assertIn('temppass123', welcome_html)
        self.assertIn('test@example.com', welcome_html)
    
    def test_email_error_handling(self):
        """Test email error handling"""
        # Test with invalid email settings
        with override_settings(EMAIL_BACKEND='django.core.mail.backends.smtp.EmailBackend',
                             EMAIL_HOST='invalid.host',
                             EMAIL_PORT=587):
            
            # Should not raise exception due to error handling
            try:
                send_booking_confirmation_email(self.booking)
                send_welcome_email(self.user, 'password123')
            except Exception as e:
                self.fail(f"Email functions should handle errors gracefully: {e}")
    
    def test_booking_confirmation_email_updates_booking(self):
        """Test that sending confirmation email updates booking status"""
        # Initially, confirmation_email_sent should be False
        self.assertFalse(self.booking.confirmation_email_sent)
        
        # Send email
        send_booking_confirmation_email(self.booking)
        
        # Refresh booking from database
        self.booking.refresh_from_db()
        
        # Should be marked as sent
        self.assertTrue(self.booking.confirmation_email_sent)
    
    def test_email_content_security(self):
        """Test that email content is properly escaped"""
        # Create booking with potentially dangerous content
        dangerous_booking = Booking.objects.create(
            package=self.package,
            user=self.user,
            full_name='<script>alert("xss")</script>Test User',
            email='test@example.com',
            phone_number='+254701363551',
            number_of_adults=1,
            number_of_children=0,
            number_of_rooms=1,
            total_amount=Decimal('1000.00'),
            special_requests='<script>alert("xss")</script>Special request'
        )
        
        # Send email
        send_booking_confirmation_email(dangerous_booking)
        
        # Check that email was sent
        self.assertEqual(len(mail.outbox), 1)
        
        email = mail.outbox[0]
        html_content = email.alternatives[0][0]
        
        # Script tags should be escaped or removed
        self.assertNotIn('<script>', html_content)
        self.assertNotIn('alert("xss")', html_content)
    
    def test_email_personalization(self):
        """Test email personalization features"""
        # Test with user having different names
        user_with_long_name = User.objects.create_user(
            username='longname',
            email='longname@example.com',
            first_name='Very Long First Name',
            last_name='Very Long Last Name'
        )
        
        # Send welcome email
        send_welcome_email(user_with_long_name, 'password123')
        
        # Check that email was sent
        self.assertEqual(len(mail.outbox), 1)
        
        email = mail.outbox[0]
        html_content = email.alternatives[0][0]
        
        # Should contain the user's first name
        self.assertIn('Very Long First Name', html_content)
        self.assertIn('longname@example.com', html_content)
    
    def test_email_links_and_urls(self):
        """Test that email contains proper links and URLs"""
        # Send booking confirmation email
        send_booking_confirmation_email(self.booking, is_new_user=True)
        
        # Check that email was sent
        self.assertEqual(len(mail.outbox), 1)
        
        email = mail.outbox[0]
        html_content = email.alternatives[0][0]
        
        # Should contain dashboard link
        self.assertIn('/profile/', html_content)
        
        # Should contain WhatsApp link
        self.assertIn('whatsapp.com', html_content)
        self.assertIn('254701363551', html_content)  # Phone number
        
        # Should contain proper mailto links
        self.assertIn('info@novustelltravel.com', html_content)
    
    def test_multiple_email_sending(self):
        """Test sending multiple emails in sequence"""
        # Send welcome email
        send_welcome_email(self.user, 'password123')
        
        # Send booking confirmation
        send_booking_confirmation_email(self.booking)
        
        # Should have sent 2 emails
        self.assertEqual(len(mail.outbox), 2)
        
        # Check email subjects
        subjects = [email.subject for email in mail.outbox]
        self.assertIn('Welcome to Novustell Travel', subjects)
        self.assertIn(f'Booking Confirmation - {self.booking.booking_reference}', subjects)
        
        # Check recipients
        recipients = [email.to[0] for email in mail.outbox]
        self.assertEqual(recipients, ['test@example.com', 'test@example.com'])
    
    def test_email_encoding_and_special_characters(self):
        """Test email handling of special characters and encoding"""
        # Create user with special characters
        special_user = User.objects.create_user(
            username='special',
            email='special@example.com',
            first_name='José',
            last_name='García'
        )
        
        # Create booking with special characters
        special_booking = Booking.objects.create(
            package=self.package,
            user=special_user,
            full_name='José García',
            email='special@example.com',
            phone_number='+254701363551',
            number_of_adults=1,
            number_of_children=0,
            number_of_rooms=1,
            total_amount=Decimal('1000.00'),
            special_requests='Café con leche, habitación con vista al océano'
        )
        
        # Send emails
        send_welcome_email(special_user, 'password123')
        send_booking_confirmation_email(special_booking)
        
        # Should have sent 2 emails without errors
        self.assertEqual(len(mail.outbox), 2)
        
        # Check that special characters are preserved
        welcome_email = mail.outbox[0]
        booking_email = mail.outbox[1]
        
        self.assertIn('José', welcome_email.alternatives[0][0])
        self.assertIn('García', welcome_email.alternatives[0][0])
        self.assertIn('océano', booking_email.alternatives[0][0])
