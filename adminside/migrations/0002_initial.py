# Generated by Django 5.0.3 on 2024-03-26 23:34

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('adminside', '0001_initial'),
        ('users', '0001_initial'),
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
            model_name='itinerary',
            name='package',
            field=models.OneToOneField(default=1, on_delete=django.db.models.deletion.CASCADE, to='adminside.package'),
        ),
        migrations.AddField(
            model_name='package',
            name='travel',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='adminside.travel'),
        ),
    ]
