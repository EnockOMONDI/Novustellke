"""
Integration tests for the complete booking flow
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core import mail
from django.contrib.sessions.models import Session
from decimal import Decimal
from datetime import date, timedelta

from users.models import Booking, UserProfile
from adminside.models import Package, Destination, Accommodation, TravelMode
from users.cart import Cart
from users.form_persistence import FormDataManager


class BookingFlowIntegrationTest(TestCase):
    """Test the complete booking flow from package selection to confirmation"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Create test destination
        self.destination = Destination.objects.create(
            name='Maasai Mara',
            description='Famous wildlife reserve'
        )
        
        # Create test package
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
        
        # Create test accommodation
        self.accommodation = Accommodation.objects.create(
            name='Safari Lodge',
            description='Luxury safari lodge',
            destination=self.destination,
            price_per_room_per_night=200,
            is_active=True
        )
        self.package.available_accommodations.add(self.accommodation)
        
        # Create test travel mode
        self.travel_mode = TravelMode.objects.create(
            name='4WD Safari Vehicle',
            description='Comfortable safari vehicle',
            price_per_person=100,
            is_active=True
        )
        self.package.available_travel_modes.add(self.travel_mode)
    
    def test_guest_booking_flow_complete(self):
        """Test complete guest booking flow with automatic user creation"""
        # Step 1: Add package to cart
        response = self.client.post(reverse('users:add_to_cart', args=[self.package.id]), {
            'adults': 2,
            'children': 1,
            'rooms': 1
        })
        self.assertEqual(response.status_code, 302)  # Redirect to customization
        
        # Verify package is in cart
        cart = Cart(self.client)
        cart_items = cart.get_cart_items()
        self.assertEqual(len(cart_items), 1)
        self.assertEqual(cart_items[0]['package'], self.package)
        self.assertEqual(cart_items[0]['adults'], 2)
        self.assertEqual(cart_items[0]['children'], 1)
        self.assertEqual(cart_items[0]['rooms'], 1)
        
        # Step 2: Customize booking (add accommodations and travel modes)
        response = self.client.post(reverse('users:checkout_customize', args=[self.package.id]), {
            'accommodations': [self.accommodation.id],
            'travel_modes': [self.travel_mode.id],
            'custom_accommodation': '',
            'self_drive': False
        })
        self.assertEqual(response.status_code, 302)  # Redirect to details
        
        # Verify customizations are saved
        cart_items = cart.get_cart_items()
        self.assertIn(self.accommodation, cart_items[0]['accommodations'])
        self.assertIn(self.travel_mode, cart_items[0]['travel_modes'])
        
        # Step 3: Enter guest details
        guest_data = {
            'full_name': 'John Doe',
            'email': 'john.doe@example.com',
            'phone_number': '+254701363551',
            'travel_date': (date.today() + timedelta(days=30)).isoformat(),
            'special_requests': 'Vegetarian meals please',
            'terms_accepted': True,
            'marketing_consent': False
        }
        
        response = self.client.post(reverse('users:checkout_details'), guest_data)
        self.assertEqual(response.status_code, 302)  # Redirect to summary
        
        # Step 4: Review and confirm booking
        response = self.client.get(reverse('users:checkout_summary'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'John Doe')
        self.assertContains(response, 'john.doe@example.com')
        self.assertContains(response, self.package.name)
        
        # Clear mail outbox before confirmation
        mail.outbox = []
        
        # Confirm booking
        response = self.client.post(reverse('users:checkout_summary'))
        self.assertEqual(response.status_code, 302)  # Redirect to confirmation
        
        # Verify booking was created
        booking = Booking.objects.filter(email='john.doe@example.com').first()
        self.assertIsNotNone(booking)
        self.assertEqual(booking.full_name, 'John Doe')
        self.assertEqual(booking.package, self.package)
        self.assertEqual(booking.number_of_adults, 2)
        self.assertEqual(booking.number_of_children, 1)
        self.assertEqual(booking.number_of_rooms, 1)
        self.assertEqual(booking.special_requests, 'Vegetarian meals please')
        
        # Verify user was created automatically
        user = User.objects.filter(email='john.doe@example.com').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.first_name, 'John')
        self.assertEqual(user.last_name, 'Doe')
        self.assertEqual(booking.user, user)
        
        # Verify user profile was created
        self.assertTrue(hasattr(user, 'profile'))
        self.assertIsInstance(user.profile, UserProfile)
        
        # Verify emails were sent
        self.assertEqual(len(mail.outbox), 2)  # Welcome email + booking confirmation
        
        # Check welcome email
        welcome_email = None
        confirmation_email = None
        for email in mail.outbox:
            if 'Welcome to Novustell Travel' in email.subject:
                welcome_email = email
            elif 'Booking Confirmation' in email.subject:
                confirmation_email = email
        
        self.assertIsNotNone(welcome_email)
        self.assertIsNotNone(confirmation_email)
        self.assertEqual(welcome_email.to, ['john.doe@example.com'])
        self.assertEqual(confirmation_email.to, ['john.doe@example.com'])
        
        # Verify cart is cleared after booking
        cart_items = cart.get_cart_items()
        self.assertEqual(len(cart_items), 0)
    
    def test_existing_user_booking_flow(self):
        """Test booking flow for existing user"""
        # Create existing user
        existing_user = User.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            password='testpass123',
            first_name='Jane',
            last_name='Smith'
        )
        
        # Step 1: Add package to cart
        self.client.post(reverse('users:add_to_cart', args=[self.package.id]), {
            'adults': 1,
            'children': 0,
            'rooms': 1
        })
        
        # Step 2: Skip customization (no add-ons)
        self.client.post(reverse('users:checkout_customize', args=[self.package.id]), {
            'accommodations': [],
            'travel_modes': [],
            'custom_accommodation': '',
            'self_drive': True  # Use self-drive
        })
        
        # Step 3: Enter details with existing email
        guest_data = {
            'full_name': 'Jane Smith',
            'email': 'existing@example.com',  # Existing user email
            'phone_number': '+254701363552',
            'travel_date': (date.today() + timedelta(days=45)).isoformat(),
            'special_requests': 'Window seat preference',
            'terms_accepted': True,
            'marketing_consent': True
        }
        
        self.client.post(reverse('users:checkout_details'), guest_data)
        
        # Clear mail outbox
        mail.outbox = []
        
        # Step 4: Confirm booking
        response = self.client.post(reverse('users:checkout_summary'))
        self.assertEqual(response.status_code, 302)
        
        # Verify booking was created and linked to existing user
        booking = Booking.objects.filter(email='existing@example.com').first()
        self.assertIsNotNone(booking)
        self.assertEqual(booking.user, existing_user)
        self.assertEqual(booking.full_name, 'Jane Smith')
        
        # Verify only booking confirmation email was sent (no welcome email)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Booking Confirmation', mail.outbox[0].subject)
        self.assertEqual(mail.outbox[0].to, ['existing@example.com'])
        
        # Verify no duplicate user was created
        user_count = User.objects.filter(email='existing@example.com').count()
        self.assertEqual(user_count, 1)
    
    def test_booking_flow_with_form_persistence(self):
        """Test that form data persists across navigation"""
        # Step 1: Add package to cart
        self.client.post(reverse('users:add_to_cart', args=[self.package.id]), {
            'adults': 3,
            'children': 2,
            'rooms': 2
        })
        
        # Step 2: Enter partial details
        partial_data = {
            'full_name': 'Test User',
            'email': 'test@example.com',
            'phone_number': '+254701363553'
            # Missing required fields
        }
        
        response = self.client.post(reverse('users:checkout_details'), partial_data)
        # Should stay on details page due to missing fields
        
        # Navigate back to customization
        response = self.client.get(reverse('users:checkout_customize', args=[self.package.id]))
        self.assertEqual(response.status_code, 200)
        
        # Navigate forward to details again
        response = self.client.get(reverse('users:checkout_details'))
        self.assertEqual(response.status_code, 200)
        
        # Check if form data was preserved (this would need to be implemented in the view)
        # For now, we'll test the FormDataManager directly
        
        # Test FormDataManager functionality
        form_manager = FormDataManager(self.client)
        
        # Save some test data
        test_data = {
            'full_name': 'Test User',
            'email': 'test@example.com',
            'phone_number': '+254701363553'
        }
        form_manager.save_form_data('details', test_data)
        
        # Retrieve the data
        retrieved_data = form_manager.get_form_data('details')
        self.assertEqual(retrieved_data['full_name'], 'Test User')
        self.assertEqual(retrieved_data['email'], 'test@example.com')
        self.assertEqual(retrieved_data['phone_number'], '+254701363553')
        
        # Test data clearing
        form_manager.clear_form_data('details')
        cleared_data = form_manager.get_form_data('details')
        self.assertEqual(cleared_data, {})
    
    def test_booking_pricing_calculation(self):
        """Test that booking pricing is calculated correctly"""
        # Add package to cart with specific quantities
        self.client.post(reverse('users:add_to_cart', args=[self.package.id]), {
            'adults': 2,
            'children': 1,
            'rooms': 1
        })
        
        # Add accommodations and travel modes
        self.client.post(reverse('users:checkout_customize', args=[self.package.id]), {
            'accommodations': [self.accommodation.id],
            'travel_modes': [self.travel_mode.id]
        })
        
        # Enter details and confirm
        guest_data = {
            'full_name': 'Pricing Test',
            'email': 'pricing@example.com',
            'phone_number': '+254701363554',
            'travel_date': (date.today() + timedelta(days=30)).isoformat(),
            'terms_accepted': True
        }
        
        self.client.post(reverse('users:checkout_details'), guest_data)
        self.client.post(reverse('users:checkout_summary'))
        
        # Verify pricing calculation
        booking = Booking.objects.filter(email='pricing@example.com').first()
        self.assertIsNotNone(booking)
        
        # Expected calculations:
        # Package: 2 adults * $1500 + 1 child * ($1500 * 0.7) = $3000 + $1050 = $4050
        # Accommodation: 1 room * $200/night * 2 nights = $400
        # Travel: (2 adults + 1 child) * $100 = $300
        # Total: $4050 + $400 + $300 = $4750
        
        expected_package_price = Decimal('4050.00')
        expected_accommodation_price = Decimal('400.00')
        expected_travel_price = Decimal('300.00')
        expected_total = Decimal('4750.00')
        
        self.assertEqual(booking.package_price, expected_package_price)
        self.assertEqual(booking.accommodation_price, expected_accommodation_price)
        self.assertEqual(booking.travel_price, expected_travel_price)
        self.assertEqual(booking.total_amount, expected_total)
    
    def test_booking_flow_validation(self):
        """Test validation in booking flow"""
        # Try to access checkout without items in cart
        response = self.client.get(reverse('users:checkout_details'))
        self.assertEqual(response.status_code, 302)  # Should redirect
        
        # Add package to cart
        self.client.post(reverse('users:add_to_cart', args=[self.package.id]), {
            'adults': 1,
            'children': 0,
            'rooms': 1
        })
        
        # Try to submit details with invalid data
        invalid_data = {
            'full_name': '',  # Empty name
            'email': 'invalid-email',  # Invalid email
            'phone_number': '',  # Empty phone
            'terms_accepted': False  # Terms not accepted
        }
        
        response = self.client.post(reverse('users:checkout_details'), invalid_data)
        # Should stay on details page with errors
        self.assertEqual(response.status_code, 200)
        
        # Submit valid data
        valid_data = {
            'full_name': 'Valid User',
            'email': 'valid@example.com',
            'phone_number': '+254701363555',
            'travel_date': (date.today() + timedelta(days=30)).isoformat(),
            'terms_accepted': True
        }
        
        response = self.client.post(reverse('users:checkout_details'), valid_data)
        self.assertEqual(response.status_code, 302)  # Should redirect to summary
    
    def test_cart_functionality(self):
        """Test cart operations"""
        cart = Cart(self.client)
        
        # Test adding package
        cart.add_package(self.package, adults=2, children=1, rooms=1)
        cart_items = cart.get_cart_items()
        self.assertEqual(len(cart_items), 1)
        
        # Test adding accommodation
        cart.add_accommodation(self.package.id, self.accommodation.id)
        cart_items = cart.get_cart_items()
        self.assertIn(self.accommodation, cart_items[0]['accommodations'])
        
        # Test adding travel mode
        cart.add_travel_mode(self.package.id, self.travel_mode.id)
        cart_items = cart.get_cart_items()
        self.assertIn(self.travel_mode, cart_items[0]['travel_modes'])
        
        # Test removing accommodation
        cart.remove_accommodation(self.package.id, self.accommodation.id)
        cart_items = cart.get_cart_items()
        self.assertNotIn(self.accommodation, cart_items[0]['accommodations'])
        
        # Test clearing cart
        cart.clear()
        cart_items = cart.get_cart_items()
        self.assertEqual(len(cart_items), 0)
