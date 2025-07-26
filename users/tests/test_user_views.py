"""
Tests for user profile views and authentication
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
from decimal import Decimal
from datetime import date

from users.models import UserProfile, BucketList, Booking
from adminside.models import Package, Destination, Accommodation


class UserProfileViewsTest(TestCase):
    """Test user profile related views"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        # Create test destination and package for bookings
        self.destination = Destination.objects.create(
            name='Test Destination',
            description='Test description'
        )
        
        self.package = Package.objects.create(
            name='Test Package',
            description='Test package description',
            adult_price=1000,
            child_price=700,  # 30% discount for children
            duration_days=3,
            duration_nights=2,
            main_destination=self.destination,
            status=Package.PUBLISHED
        )
        
        # Create test accommodation
        self.accommodation = Accommodation.objects.create(
            name='Test Hotel',
            description='Test hotel description',
            destination=self.destination,
            price_per_room_per_night=100
        )
    
    def test_user_profile_view_requires_login(self):
        """Test that user profile view requires authentication"""
        response = self.client.get(reverse('users:user_profile'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_user_profile_view_authenticated(self):
        """Test user profile view for authenticated user"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(reverse('users:user_profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test User')
        self.assertContains(response, 'test@example.com')
        self.assertContains(response, 'Total Bookings')
        self.assertContains(response, 'Total Spent')
        self.assertContains(response, 'Upcoming Trips')
    
    def test_user_profile_with_bookings(self):
        """Test user profile view with existing bookings"""
        # Create test bookings
        booking1 = Booking.objects.create(
            package=self.package,
            user=self.user,
            full_name='Test User',
            email='test@example.com',
            phone_number='+254701363551',
            number_of_adults=2,
            number_of_children=0,
            number_of_rooms=1,
            package_price=Decimal('2000.00'),
            accommodation_price=Decimal('0.00'),
            travel_price=Decimal('0.00'),
            total_amount=Decimal('2000.00'),
            status='confirmed'
        )

        booking2 = Booking.objects.create(
            package=self.package,
            user=self.user,
            full_name='Test User',
            email='test@example.com',
            phone_number='+254701363551',
            number_of_adults=1,
            number_of_children=1,
            number_of_rooms=1,
            package_price=Decimal('1500.00'),
            accommodation_price=Decimal('0.00'),
            travel_price=Decimal('0.00'),
            total_amount=Decimal('1500.00'),
            status='pending'
        )
        
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(reverse('users:user_profile'))
        self.assertEqual(response.status_code, 200)
        
        # Check statistics
        self.assertContains(response, '2')  # Total bookings
        self.assertContains(response, '$3500')  # Total spent
        self.assertContains(response, '2')  # Upcoming trips (pending + confirmed)
        
        # Check booking display
        self.assertContains(response, booking1.booking_reference)
        self.assertContains(response, booking2.booking_reference)
    
    def test_edit_profile_view_get(self):
        """Test edit profile view GET request"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(reverse('users:edit_profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Edit Your Profile')
        self.assertContains(response, 'Test')  # First name
        self.assertContains(response, 'User')  # Last name
        self.assertContains(response, 'test@example.com')  # Email
    
    def test_edit_profile_view_post(self):
        """Test edit profile view POST request"""
        self.client.login(username='testuser', password='testpass123')
        
        profile_data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'email': 'updated@example.com',
            'phone_number': '+254701363551',
            'date_of_birth': '1990-01-01',
            'nationality': 'Kenyan',
            'passport_number': 'A1234567',
            'emergency_contact_name': 'Emergency Contact',
            'emergency_contact_phone': '+254700000000',
            'preferred_travel_style': 'adventure',
            'dietary_requirements': 'Vegetarian',
            'special_needs': 'None',
            'email_notifications': 'on',
            'marketing_emails': 'on'
        }
        
        response = self.client.post(reverse('users:edit_profile'), profile_data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful update
        
        # Verify user data was updated
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Updated')
        self.assertEqual(self.user.last_name, 'Name')
        self.assertEqual(self.user.email, 'updated@example.com')
        
        # Verify profile data was updated
        profile = self.user.profile
        profile.refresh_from_db()
        self.assertEqual(profile.phone_number, '+254701363551')
        self.assertEqual(profile.date_of_birth, date(1990, 1, 1))
        self.assertEqual(profile.nationality, 'Kenyan')
        self.assertEqual(profile.passport_number, 'A1234567')
        self.assertEqual(profile.emergency_contact_name, 'Emergency Contact')
        self.assertEqual(profile.emergency_contact_phone, '+254700000000')
        self.assertEqual(profile.preferred_travel_style, 'adventure')
        self.assertEqual(profile.dietary_requirements, 'Vegetarian')
        self.assertEqual(profile.special_needs, 'None')
        self.assertTrue(profile.email_notifications)
        self.assertTrue(profile.marketing_emails)
    
    def test_change_password_view_get(self):
        """Test change password view GET request"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(reverse('users:change_password'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Change Password')
        self.assertContains(response, 'Current Password')
        self.assertContains(response, 'New Password')
    
    def test_change_password_view_post_valid(self):
        """Test change password view with valid data"""
        self.client.login(username='testuser', password='testpass123')
        
        password_data = {
            'old_password': 'testpass123',
            'new_password1': 'newpassword456',
            'new_password2': 'newpassword456'
        }
        
        response = self.client.post(reverse('users:change_password'), password_data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful change
        
        # Verify password was changed
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpassword456'))
        self.assertFalse(self.user.check_password('testpass123'))
    
    def test_change_password_view_post_invalid(self):
        """Test change password view with invalid data"""
        self.client.login(username='testuser', password='testpass123')
        
        # Test with wrong old password
        password_data = {
            'old_password': 'wrongpassword',
            'new_password1': 'newpassword456',
            'new_password2': 'newpassword456'
        }
        
        response = self.client.post(reverse('users:change_password'), password_data)
        self.assertEqual(response.status_code, 200)  # Stay on page with errors
        
        # Test with mismatched new passwords
        password_data = {
            'old_password': 'testpass123',
            'new_password1': 'newpassword456',
            'new_password2': 'differentpassword'
        }
        
        response = self.client.post(reverse('users:change_password'), password_data)
        self.assertEqual(response.status_code, 200)  # Stay on page with errors
    
    def test_booking_history_view(self):
        """Test booking history view"""
        # Create test bookings
        booking1 = Booking.objects.create(
            package=self.package,
            user=self.user,
            full_name='Test User',
            email='test@example.com',
            phone_number='+254701363551',
            number_of_adults=2,
            number_of_children=0,
            number_of_rooms=1,
            package_price=Decimal('2000.00'),
            accommodation_price=Decimal('0.00'),
            travel_price=Decimal('0.00'),
            total_amount=Decimal('2000.00'),
            status='confirmed'
        )

        booking2 = Booking.objects.create(
            package=self.package,
            user=self.user,
            full_name='Test User',
            email='test@example.com',
            phone_number='+254701363551',
            number_of_adults=1,
            number_of_children=1,
            number_of_rooms=1,
            package_price=Decimal('1500.00'),
            accommodation_price=Decimal('0.00'),
            travel_price=Decimal('0.00'),
            total_amount=Decimal('1500.00'),
            status='pending'
        )
        
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(reverse('users:booking_history'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Booking History')
        self.assertContains(response, booking1.booking_reference)
        self.assertContains(response, booking2.booking_reference)
    
    def test_booking_history_with_filters(self):
        """Test booking history view with status filter"""
        # Create bookings with different statuses
        confirmed_booking = Booking.objects.create(
            package=self.package,
            user=self.user,
            full_name='Test User',
            email='test@example.com',
            phone_number='+254701363551',
            number_of_adults=1,
            number_of_children=0,
            number_of_rooms=1,
            package_price=Decimal('1000.00'),
            accommodation_price=Decimal('0.00'),
            travel_price=Decimal('0.00'),
            total_amount=Decimal('1000.00'),
            status='confirmed'
        )

        pending_booking = Booking.objects.create(
            package=self.package,
            user=self.user,
            full_name='Test User',
            email='test@example.com',
            phone_number='+254701363551',
            number_of_adults=1,
            number_of_children=0,
            number_of_rooms=1,
            package_price=Decimal('1000.00'),
            accommodation_price=Decimal('0.00'),
            travel_price=Decimal('0.00'),
            total_amount=Decimal('1000.00'),
            status='pending'
        )
        
        self.client.login(username='testuser', password='testpass123')
        
        # Test filter by confirmed status
        response = self.client.get(reverse('users:booking_history') + '?status=confirmed')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, confirmed_booking.booking_reference)
        self.assertNotContains(response, pending_booking.booking_reference)
        
        # Test filter by pending status
        response = self.client.get(reverse('users:booking_history') + '?status=pending')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, pending_booking.booking_reference)
        self.assertNotContains(response, confirmed_booking.booking_reference)
    
    def test_booking_detail_view(self):
        """Test booking detail view"""
        booking = Booking.objects.create(
            package=self.package,
            user=self.user,
            full_name='Test User',
            email='test@example.com',
            phone_number='+254701363551',
            number_of_adults=2,
            number_of_children=0,
            number_of_rooms=1,
            package_price=Decimal('2000.00'),
            accommodation_price=Decimal('0.00'),
            travel_price=Decimal('0.00'),
            total_amount=Decimal('2000.00'),
            status='confirmed'
        )
        
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(reverse('users:booking_detail', args=[booking.booking_reference]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, booking.booking_reference)
        self.assertContains(response, self.package.name)
        self.assertContains(response, '$2000')
    
    def test_bucket_list_view(self):
        """Test bucket list view"""
        # Create bucket list items
        package_item = BucketList.objects.create(
            user=self.user,
            item_type='package',
            package=self.package,
            notes='Want to visit this place',
            priority='high'
        )
        
        accommodation_item = BucketList.objects.create(
            user=self.user,
            item_type='accommodation',
            accommodation=self.accommodation,
            priority='medium'
        )
        
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(reverse('users:bucket_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'My Travel Bucket List')
        self.assertContains(response, self.package.name)
        self.assertContains(response, self.accommodation.name)
        self.assertContains(response, 'Want to visit this place')
    
    def test_bucket_list_with_type_filter(self):
        """Test bucket list view with type filter"""
        # Create different types of bucket list items
        package_item = BucketList.objects.create(
            user=self.user,
            item_type='package',
            package=self.package
        )
        
        accommodation_item = BucketList.objects.create(
            user=self.user,
            item_type='accommodation',
            accommodation=self.accommodation
        )
        
        self.client.login(username='testuser', password='testpass123')
        
        # Test filter by package type
        response = self.client.get(reverse('users:bucket_list') + '?type=package')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.package.name)
        self.assertNotContains(response, self.accommodation.name)
        
        # Test filter by accommodation type
        response = self.client.get(reverse('users:bucket_list') + '?type=accommodation')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.accommodation.name)
        self.assertNotContains(response, self.package.name)
    
    def test_remove_from_bucket_list(self):
        """Test removing item from bucket list"""
        bucket_item = BucketList.objects.create(
            user=self.user,
            item_type='package',
            package=self.package
        )
        
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(reverse('users:remove_from_bucket_list', args=[bucket_item.id]))
        self.assertEqual(response.status_code, 302)  # Redirect after removal
        
        # Verify item was removed
        self.assertFalse(BucketList.objects.filter(id=bucket_item.id).exists())
    
    def test_user_can_only_access_own_data(self):
        """Test that users can only access their own data"""
        # Create another user
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123'
        )
        
        # Create booking for other user
        other_booking = Booking.objects.create(
            package=self.package,
            user=other_user,
            full_name='Other User',
            email='other@example.com',
            phone_number='+254701363552',
            number_of_adults=1,
            number_of_children=0,
            number_of_rooms=1,
            package_price=Decimal('1000.00'),
            accommodation_price=Decimal('0.00'),
            travel_price=Decimal('0.00'),
            total_amount=Decimal('1000.00')
        )
        
        # Create bucket list item for other user
        other_bucket_item = BucketList.objects.create(
            user=other_user,
            item_type='package',
            package=self.package
        )
        
        # Login as first user
        self.client.login(username='testuser', password='testpass123')
        
        # Try to access other user's booking detail
        response = self.client.get(reverse('users:booking_detail', args=[other_booking.booking_reference]))
        self.assertEqual(response.status_code, 404)  # Should not be found
        
        # Try to remove other user's bucket list item
        response = self.client.get(reverse('users:remove_from_bucket_list', args=[other_bucket_item.id]))
        self.assertEqual(response.status_code, 404)  # Should not be found
        
        # Verify bucket list only shows own items
        response = self.client.get(reverse('users:bucket_list'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Other User')  # Should not see other user's items


class BucketListAjaxTest(TestCase):
    """Test AJAX functionality for bucket list"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        self.destination = Destination.objects.create(
            name='Test Destination',
            description='Test description'
        )

        self.package = Package.objects.create(
            name='Test Package',
            description='Test package description',
            adult_price=1000,
            child_price=700,  # 30% discount for children
            duration_days=3,
            duration_nights=2,
            main_destination=self.destination,
            status=Package.PUBLISHED
        )

    def test_add_to_bucket_list_ajax(self):
        """Test adding item to bucket list via AJAX"""
        self.client.login(username='testuser', password='testpass123')

        response = self.client.post(reverse('users:add_to_bucket_list'), {
            'item_type': 'package',
            'item_id': self.package.id,
            'notes': 'Want to visit this place',
            'priority': 'high'
        })

        self.assertEqual(response.status_code, 200)

        # Check if item was added
        bucket_item = BucketList.objects.filter(user=self.user, package=self.package).first()
        self.assertIsNotNone(bucket_item)
        self.assertEqual(bucket_item.notes, 'Want to visit this place')
        self.assertEqual(bucket_item.priority, 'high')

    def test_add_duplicate_to_bucket_list(self):
        """Test adding duplicate item to bucket list"""
        self.client.login(username='testuser', password='testpass123')

        # Add item first time
        BucketList.objects.create(
            user=self.user,
            item_type='package',
            package=self.package
        )

        # Try to add same item again
        response = self.client.post(reverse('users:add_to_bucket_list'), {
            'item_type': 'package',
            'item_id': self.package.id
        })

        self.assertEqual(response.status_code, 200)

        # Should only have one item
        bucket_count = BucketList.objects.filter(user=self.user, package=self.package).count()
        self.assertEqual(bucket_count, 1)
