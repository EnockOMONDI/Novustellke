from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import BigAutoField

# Create your models here.
class UserBookings(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    package = models.ForeignKey("adminside.Package", on_delete=models.CASCADE)
    
    # Attributes
    number_of_adults = models.PositiveIntegerField(default=1)
    number_of_children = models.PositiveIntegerField(default=0)
    number_of_rooms = models.PositiveIntegerField(default=1)
    booking_date = models.DateField(auto_now_add=True)
    include_travelling = models.BooleanField(default=False)
    paid=models.BooleanField(default=False)
    total_amount=models.PositiveIntegerField(default=0)


    def __str__(self):
        return f'{self.user.first_name} | {self.package.package_name} | {self.booking_date}'

class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    date_posted = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title