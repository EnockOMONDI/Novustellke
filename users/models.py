from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import BigAutoField
from django_ckeditor_5.fields import CKEditor5Field
import uuid
from decimal import Decimal
from django.db.models.signals import post_save
from django.dispatch import receiver



class UserBookings(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    package = models.ForeignKey("adminside.Package", on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    number_of_adults = models.PositiveIntegerField()
    number_of_children = models.PositiveIntegerField(blank=True, null=True)
    number_of_rooms = models.PositiveIntegerField(default=1)
    booking_date = models.DateField(auto_now_add=True)
    include_travelling = models.BooleanField(default=False)
    special_requests = CKEditor5Field(config_name='default', blank=True, null=True, help_text="Any special requests or requirements")
    paid=models.BooleanField(default=False)
    total_amount = models.PositiveIntegerField(default=0, blank=True, null=True)


    class Meta:
        ordering = ('-booking_date', )

    def __str__(self):
        return f"Booking for {self.full_name}  {self.package.name} on {self.booking_date}"


class Booking(models.Model):
    """
    Modern booking model for guest and registered users
    """
    PENDING = 'pending'
    CONFIRMED = 'confirmed'
    CANCELLED = 'cancelled'
    COMPLETED = 'completed'

    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (CONFIRMED, 'Confirmed'),
        (CANCELLED, 'Cancelled'),
        (COMPLETED, 'Completed'),
    ]

    # Booking identification
    booking_reference = models.CharField(max_length=20, unique=True, editable=False)

    # Package and user information
    package = models.ForeignKey("adminside.Package", on_delete=models.CASCADE, related_name='modern_bookings')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='modern_bookings')

    # Guest information (required for all bookings)
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)

    # Traveler details
    number_of_adults = models.PositiveIntegerField(default=1)
    number_of_children = models.PositiveIntegerField(default=0)
    number_of_rooms = models.PositiveIntegerField(default=1)

    # Selected add-ons
    selected_accommodations = models.ManyToManyField(
        "adminside.Accommodation",
        blank=True,
        related_name='modern_bookings'
    )
    selected_travel_modes = models.ManyToManyField(
        "adminside.TravelMode",
        blank=True,
        related_name='modern_bookings'
    )

    # Pricing
    package_price = models.DecimalField(max_digits=10, decimal_places=2)
    accommodation_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    travel_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    # Additional information
    special_requests = CKEditor5Field(config_name='default', blank=True, null=True)
    travel_date = models.DateField(null=True, blank=True)

    # Status and timestamps
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Email tracking
    confirmation_email_sent = models.BooleanField(default=False)
    admin_notification_sent = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.booking_reference:
            self.booking_reference = self.generate_booking_reference()
        super().save(*args, **kwargs)

    def generate_booking_reference(self):
        """Generate unique booking reference"""
        import random
        import string
        while True:
            reference = 'NVT' + ''.join(random.choices(string.digits, k=7))
            if not Booking.objects.filter(booking_reference=reference).exists():
                return reference

    def calculate_total(self):
        """Calculate total booking amount"""
        total = self.package_price
        total += self.accommodation_price
        total += self.travel_price
        return total

    def __str__(self):
        return f"Booking {self.booking_reference} - {self.full_name}"


class GuestBooking(models.Model):
    """
    Temporary booking model for session-based cart system
    """
    session_key = models.CharField(max_length=40)
    package = models.ForeignKey("adminside.Package", on_delete=models.CASCADE)

    # Selected add-ons (stored as JSON or comma-separated IDs)
    selected_accommodation_ids = models.TextField(blank=True, default='')
    selected_travel_mode_ids = models.TextField(blank=True, default='')

    # Traveler details
    number_of_adults = models.PositiveIntegerField(default=1)
    number_of_children = models.PositiveIntegerField(default=0)
    number_of_rooms = models.PositiveIntegerField(default=1)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['session_key', 'package']

    def get_selected_accommodations(self):
        """Get selected accommodation objects"""
        if not self.selected_accommodation_ids:
            return []
        from adminside.models import Accommodation
        ids = [int(id.strip()) for id in self.selected_accommodation_ids.split(',') if id.strip()]
        return Accommodation.objects.filter(id__in=ids)

    def get_selected_travel_modes(self):
        """Get selected travel mode objects"""
        if not self.selected_travel_mode_ids:
            return []
        from adminside.models import TravelMode
        ids = [int(id.strip()) for id in self.selected_travel_mode_ids.split(',') if id.strip()]
        return TravelMode.objects.filter(id__in=ids)

    def calculate_total_price(self):
        """Calculate total price for this booking"""
        total = Decimal(str(self.package.adult_price)) * self.number_of_adults

        # Add children pricing (usually discounted)
        if self.number_of_children > 0:
            child_price = Decimal(str(self.package.child_price)) if hasattr(self.package, 'child_price') else Decimal(str(self.package.adult_price)) * Decimal('0.7')
            total += child_price * self.number_of_children

        # Add accommodation costs
        for accommodation in self.get_selected_accommodations():
            total += Decimal(str(accommodation.price_per_room_per_night)) * self.number_of_rooms * self.package.duration_days

        # Add travel costs
        for travel_mode in self.get_selected_travel_modes():
            total += Decimal(str(travel_mode.price_per_person)) * (self.number_of_adults + self.number_of_children)

        return total

    def __str__(self):
        return f"Guest Booking - {self.package.name} ({self.session_key[:8]}...)"


# users/models.py
class MICEInquiry(models.Model):
    company_name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=15)
    event_type = models.CharField(max_length=50, choices=[
        ('Meeting', 'Meeting'),
        ('Incentive', 'Incentive'),
        ('Conference', 'Conference'),
        ('Exhibition', 'Exhibition')
    ])
    attendees = models.PositiveIntegerField()
    event_details = CKEditor5Field(config_name='default', help_text="Detailed event information and requirements")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.company_name} - {self.event_type}"


class StudentTravelInquiry(models.Model):
    school_name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=15)
    program_stage = models.CharField(max_length=50, choices=[
        ('Registration & Training', 'Registration & Training'),
        ('Regional Round', 'Regional Round'),
        ('Global Round', 'Global Round'),
        ('Tournament of Champions', 'Tournament of Champions')
    ])
    number_of_students = models.PositiveIntegerField()
    travel_details = CKEditor5Field(config_name='default', help_text="Detailed travel requirements and information")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.school_name} - {self.program_stage}"


class NGOTravelInquiry(models.Model):
    organization_name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=15)
    organization_type = models.CharField(max_length=50, choices=[
        ('NGO', 'Non-Governmental Organization'),
        ('Humanitarian', 'Humanitarian Organization'),
        ('Charity', 'Charity Organization'),
        ('Development', 'Development Agency'),
        ('Relief', 'Relief Organization'),
        ('Other', 'Other')
    ])
    travel_purpose = models.CharField(max_length=100, choices=[
        ('Emergency Response', 'Emergency Response'),
        ('Field Operations', 'Field Operations'),
        ('Volunteer Coordination', 'Volunteer Coordination'),
        ('Project Implementation', 'Project Implementation'),
        ('Capacity Building', 'Capacity Building'),
        ('Monitoring & Evaluation', 'Monitoring & Evaluation'),
        ('Other', 'Other')
    ])
    number_of_travelers = models.PositiveIntegerField()
    travel_details = CKEditor5Field(config_name='default', help_text="Detailed travel requirements and information")
    sustainability_requirements = models.BooleanField(default=False, help_text="Do you require sustainable travel options?")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.organization_name} - {self.travel_purpose}"


class UserProfile(models.Model):
    """
    Extended user profile for additional information and preferences
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    nationality = models.CharField(max_length=100, blank=True, null=True)
    passport_number = models.CharField(max_length=50, blank=True, null=True)
    emergency_contact_name = models.CharField(max_length=100, blank=True, null=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True, null=True)

    # Travel preferences
    preferred_travel_style = models.CharField(
        max_length=50,
        choices=[
            ('budget', 'Budget Travel'),
            ('mid_range', 'Mid-Range'),
            ('luxury', 'Luxury'),
            ('adventure', 'Adventure'),
            ('cultural', 'Cultural'),
            ('wildlife', 'Wildlife Safari'),
            ('beach', 'Beach & Relaxation'),
        ],
        blank=True,
        null=True
    )

    dietary_requirements = models.TextField(blank=True, null=True, help_text="Any dietary restrictions or preferences")
    special_needs = models.TextField(blank=True, null=True, help_text="Any special assistance requirements")

    # Account settings
    email_notifications = models.BooleanField(default=True, help_text="Receive email notifications about bookings and offers")
    marketing_emails = models.BooleanField(default=False, help_text="Receive marketing emails and travel deals")

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - Profile"

    @property
    def total_bookings(self):
        """Get total number of bookings for this user"""
        return Booking.objects.filter(user=self.user).count()

    @property
    def total_spent(self):
        """Get total amount spent by this user"""
        bookings = Booking.objects.filter(user=self.user)
        return sum(booking.total_amount for booking in bookings)


class BucketList(models.Model):
    """
    User's travel bucket list for packages and accommodations
    """
    ITEM_TYPES = [
        ('package', 'Travel Package'),
        ('accommodation', 'Accommodation'),
        ('destination', 'Destination'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bucket_list')
    item_type = models.CharField(max_length=20, choices=ITEM_TYPES)

    # Foreign keys to different models (only one will be used per item)
    package = models.ForeignKey('adminside.Package', on_delete=models.CASCADE, blank=True, null=True)
    accommodation = models.ForeignKey('adminside.Accommodation', on_delete=models.CASCADE, blank=True, null=True)
    destination = models.ForeignKey('adminside.Destination', on_delete=models.CASCADE, blank=True, null=True)

    # Additional notes
    notes = models.TextField(blank=True, null=True, help_text="Personal notes about this bucket list item")
    priority = models.CharField(
        max_length=10,
        choices=[
            ('high', 'High Priority'),
            ('medium', 'Medium Priority'),
            ('low', 'Low Priority'),
        ],
        default='medium'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [
            ['user', 'package'],
            ['user', 'accommodation'],
            ['user', 'destination'],
        ]
        ordering = ['-created_at']

    def __str__(self):
        if self.package:
            return f"{self.user.username} - {self.package.name}"
        elif self.accommodation:
            return f"{self.user.username} - {self.accommodation.name}"
        elif self.destination:
            return f"{self.user.username} - {self.destination.name}"
        return f"{self.user.username} - Bucket List Item"

    @property
    def item_name(self):
        """Get the name of the bucket list item"""
        if self.package:
            return self.package.name
        elif self.accommodation:
            return self.accommodation.name
        elif self.destination:
            return self.destination.name
        return "Unknown Item"

    @property
    def item_image(self):
        """Get the image of the bucket list item"""
        if self.package:
            return self.package.featured_image
        elif self.accommodation:
            return getattr(self.accommodation, 'image', None)
        elif self.destination:
            return getattr(self.destination, 'image', None)
        return None


# Signal to create UserProfile when User is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()
    else:
        UserProfile.objects.create(user=instance)