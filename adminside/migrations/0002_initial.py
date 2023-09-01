# Generated by Django 3.2.20 on 2023-07-30 06:14

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0001_initial'),
        ('adminside', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='package',
            name='bookings',
            field=models.ManyToManyField(through='users.UserBookings', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='package',
            name='destination',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='adminside.destination'),
        ),
        migrations.AddField(
            model_name='package',
            name='travel',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='adminside.travel'),
        ),
        migrations.AddField(
            model_name='itinerarydescription',
            name='itinerary',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='adminside.itinerary'),
        ),
        migrations.AddField(
            model_name='itinerary',
            name='package',
            field=models.OneToOneField(default=1, on_delete=django.db.models.deletion.CASCADE, to='adminside.package'),
        ),
    ]
