from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import BigAutoField
from ckeditor.fields import RichTextField



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
    special_requests = RichTextField(config_name='minimal', blank=True, null=True, help_text="Any special requests or requirements")
    paid=models.BooleanField(default=False)
    total_amount = models.PositiveIntegerField(default=0, blank=True, null=True)


    class Meta:
        ordering = ('-booking_date', )

    def __str__(self):
        return f"Booking for {self.full_name}  {self.package.name} on {self.booking_date}"


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
    event_details = RichTextField(config_name='default', help_text="Detailed event information and requirements")
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
    travel_details = RichTextField(config_name='default', help_text="Detailed travel requirements and information")
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
    travel_details = RichTextField(config_name='default', help_text="Detailed travel requirements and information")
    sustainability_requirements = models.BooleanField(default=False, help_text="Do you require sustainable travel options?")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.organization_name} - {self.travel_purpose}"