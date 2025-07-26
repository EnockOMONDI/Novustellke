"""
Unit tests for users app models
"""

from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from decimal import Decimal
from datetime import date, datetime, timedelta

from users.models import UserProfile, BucketList, Booking
from adminside.models import Package, Destination, Accommodation, TravelMode


class UserProfileModelTest(TestCase):
    """Test cases for UserProfile model"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
    
    def test_user_profile_creation(self):
        """Test that UserProfile is automatically created when User is created"""
        # Profile should be created automatically via signal
        self.assertTrue(hasattr(self.user, 'profile'))
        self.assertIsInstance(self.user.profile, UserProfile)
    
    def test_user_profile_str_method(self):
        """Test UserProfile string representation"""
        expected = f"{self.user.get_full_name()} - Profile"
        self.assertEqual(str(self.user.profile), expected)
    
    def test_user_profile_fields(self):
        """Test UserProfile field assignments"""
        profile = self.user.profile
        profile.phone_number = '+254701363551'
        profile.date_of_birth = date(1990, 1, 1)
        profile.nationality = 'Kenyan'
        profile.passport_number = 'A1234567'
        profile.emergency_contact_name = 'Emergency Contact'
        profile.emergency_contact_phone = '+254700000000'
        profile.preferred_travel_style = 'adventure'
        profile.dietary_requirements = 'Vegetarian'
        profile.special_needs = 'Wheelchair accessible'
        profile.email_notifications = True
        profile.marketing_emails = False
        profile.save()
        
        # Refresh from database
        profile.refresh_from_db()
        
        self.assertEqual(profile.phone_number, '+254701363551')
        self.assertEqual(profile.date_of_birth, date(1990, 1, 1))
        self.assertEqual(profile.nationality, 'Kenyan')
        self.assertEqual(profile.passport_number, 'A1234567')
        self.assertEqual(profile.emergency_contact_name, 'Emergency Contact')
        self.assertEqual(profile.emergency_contact_phone, '+254700000000')
        self.assertEqual(profile.preferred_travel_style, 'adventure')
        self.assertEqual(profile.dietary_requirements, 'Vegetarian')
        self.assertEqual(profile.special_needs, 'Wheelchair accessible')
        self.assertTrue(profile.email_notifications)
        self.assertFalse(profile.marketing_emails)
    
    def test_total_bookings_property(self):
        """Test total_bookings property"""
        # Create test destination and package
        destination = Destination.objects.create(
            name='Test Destination',
            description='Test description'
        )
        package = Package.objects.create(
            name='Test Package',
            description='Test package description',
            adult_price=1000,
            child_price=700,  # 30% discount for children
            duration_days=3,
            duration_nights=2,
            main_destination=destination,
            status=Package.PUBLISHED
        )
        
        # Create bookings
        Booking.objects.create(
            package=package,
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
            total_amount=Decimal('2000.00')
        )
        
        Booking.objects.create(
            package=package,
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
            total_amount=Decimal('1500.00')
        )
        
        self.assertEqual(self.user.profile.total_bookings, 2)
    
    def test_total_spent_property(self):
        """Test total_spent property"""
        # Create test destination and package
        destination = Destination.objects.create(
            name='Test Destination',
            description='Test description'
        )
        package = Package.objects.create(
            name='Test Package',
            description='Test package description',
            adult_price=1000,
            child_price=700,  # 30% discount for children
            duration_days=3,
            duration_nights=2,
            main_destination=destination,
            status=Package.PUBLISHED
        )
        
        # Create bookings
        Booking.objects.create(
            package=package,
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
            total_amount=Decimal('2000.00')
        )
        
        Booking.objects.create(
            package=package,
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
            total_amount=Decimal('1500.00')
        )
        
        self.assertEqual(self.user.profile.total_spent, Decimal('3500.00'))


class BucketListModelTest(TestCase):
    """Test cases for BucketList model"""
    
    def setUp(self):
        """Set up test data"""
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
        
        self.accommodation = Accommodation.objects.create(
            name='Test Hotel',
            description='Test hotel description',
            destination=self.destination,
            price_per_room_per_night=100
        )
    
    def test_bucket_list_package_creation(self):
        """Test creating bucket list item for package"""
        bucket_item = BucketList.objects.create(
            user=self.user,
            item_type='package',
            package=self.package,
            notes='Want to visit this place',
            priority='high'
        )
        
        self.assertEqual(bucket_item.user, self.user)
        self.assertEqual(bucket_item.item_type, 'package')
        self.assertEqual(bucket_item.package, self.package)
        self.assertEqual(bucket_item.notes, 'Want to visit this place')
        self.assertEqual(bucket_item.priority, 'high')
    
    def test_bucket_list_accommodation_creation(self):
        """Test creating bucket list item for accommodation"""
        bucket_item = BucketList.objects.create(
            user=self.user,
            item_type='accommodation',
            accommodation=self.accommodation,
            priority='medium'
        )
        
        self.assertEqual(bucket_item.item_type, 'accommodation')
        self.assertEqual(bucket_item.accommodation, self.accommodation)
        self.assertEqual(bucket_item.priority, 'medium')
    
    def test_bucket_list_destination_creation(self):
        """Test creating bucket list item for destination"""
        bucket_item = BucketList.objects.create(
            user=self.user,
            item_type='destination',
            destination=self.destination,
            priority='low'
        )
        
        self.assertEqual(bucket_item.item_type, 'destination')
        self.assertEqual(bucket_item.destination, self.destination)
        self.assertEqual(bucket_item.priority, 'low')
    
    def test_bucket_list_str_method(self):
        """Test BucketList string representation"""
        bucket_item = BucketList.objects.create(
            user=self.user,
            item_type='package',
            package=self.package
        )
        
        expected = f"{self.user.username} - {self.package.name}"
        self.assertEqual(str(bucket_item), expected)
    
    def test_bucket_list_item_name_property(self):
        """Test item_name property"""
        # Test package item
        package_item = BucketList.objects.create(
            user=self.user,
            item_type='package',
            package=self.package
        )
        self.assertEqual(package_item.item_name, self.package.name)
        
        # Test accommodation item
        accommodation_item = BucketList.objects.create(
            user=self.user,
            item_type='accommodation',
            accommodation=self.accommodation
        )
        self.assertEqual(accommodation_item.item_name, self.accommodation.name)
        
        # Test destination item
        destination_item = BucketList.objects.create(
            user=self.user,
            item_type='destination',
            destination=self.destination
        )
        self.assertEqual(destination_item.item_name, self.destination.name)
    
    def test_bucket_list_unique_constraints(self):
        """Test unique constraints for bucket list items"""
        # Create first item
        BucketList.objects.create(
            user=self.user,
            item_type='package',
            package=self.package
        )
        
        # Try to create duplicate - should raise IntegrityError
        with self.assertRaises(IntegrityError):
            BucketList.objects.create(
                user=self.user,
                item_type='package',
                package=self.package
            )


class BookingModelTest(TestCase):
    """Test cases for Booking model"""
    
    def setUp(self):
        """Set up test data"""
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
    
    def test_booking_creation(self):
        """Test basic booking creation"""
        booking = Booking.objects.create(
            package=self.package,
            user=self.user,
            full_name='Test User',
            email='test@example.com',
            phone_number='+254701363551',
            number_of_adults=2,
            number_of_children=1,
            number_of_rooms=1,
            package_price=Decimal('2000.00'),
            accommodation_price=Decimal('300.00'),
            travel_price=Decimal('500.00'),
            total_amount=Decimal('2800.00'),
            special_requests='Vegetarian meals'
        )
        
        self.assertEqual(booking.package, self.package)
        self.assertEqual(booking.user, self.user)
        self.assertEqual(booking.full_name, 'Test User')
        self.assertEqual(booking.email, 'test@example.com')
        self.assertEqual(booking.phone_number, '+254701363551')
        self.assertEqual(booking.number_of_adults, 2)
        self.assertEqual(booking.number_of_children, 1)
        self.assertEqual(booking.number_of_rooms, 1)
        self.assertEqual(booking.total_amount, Decimal('2800.00'))
        self.assertEqual(booking.special_requests, 'Vegetarian meals')
        self.assertEqual(booking.status, 'pending')  # Default status
    
    def test_booking_reference_generation(self):
        """Test that booking reference is automatically generated"""
        booking = Booking.objects.create(
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
            total_amount=Decimal('1000.00')
        )
        
        self.assertIsNotNone(booking.booking_reference)
        self.assertTrue(len(booking.booking_reference) > 0)
    
    def test_booking_str_method(self):
        """Test Booking string representation"""
        booking = Booking.objects.create(
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
            total_amount=Decimal('1000.00')
        )
        
        expected = f"Booking {booking.booking_reference} - Test User"
        self.assertEqual(str(booking), expected)
    
    def test_booking_without_user(self):
        """Test creating booking without user (guest booking)"""
        booking = Booking.objects.create(
            package=self.package,
            full_name='Guest User',
            email='guest@example.com',
            phone_number='+254701363551',
            number_of_adults=1,
            number_of_children=0,
            number_of_rooms=1,
            package_price=Decimal('1000.00'),
            accommodation_price=Decimal('0.00'),
            travel_price=Decimal('0.00'),
            total_amount=Decimal('1000.00')
        )
        
        self.assertIsNone(booking.user)
        self.assertEqual(booking.full_name, 'Guest User')
        self.assertEqual(booking.email, 'guest@example.com')
    
    def test_booking_status_choices(self):
        """Test booking status field choices"""
        booking = Booking.objects.create(
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
            total_amount=Decimal('1000.00')
        )
        
        # Test default status
        self.assertEqual(booking.status, 'pending')
        
        # Test status changes
        booking.status = 'confirmed'
        booking.save()
        booking.refresh_from_db()
        self.assertEqual(booking.status, 'confirmed')
        
        booking.status = 'cancelled'
        booking.save()
        booking.refresh_from_db()
        self.assertEqual(booking.status, 'cancelled')
        
        booking.status = 'completed'
        booking.save()
        booking.refresh_from_db()
        self.assertEqual(booking.status, 'completed')
