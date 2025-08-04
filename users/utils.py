from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string


class TokenGenerator(PasswordResetTokenGenerator):
	pass

generate_token=TokenGenerator()





def send_booking_confirmation_email(booking):
    """
    Send booking confirmation email
    """
    try:
        # Email subject
        subject = f'Web Booking - Booking ID {booking.id}'

        # Prepare email context
        email_context = {
            'booking_id': booking.id,
            'full_name': booking.full_name,
            'package_name': booking.package.package_name,
            'number_of_adults': booking.number_of_adults,
            'number_of_children': booking.number_of_children or 0,
            'number_of_rooms': booking.number_of_rooms,
            'total_amount': booking.total_amount,
            'include_travelling': 'Yes' if booking.include_travelling else 'No',
        }

        # Render email body from a template
        email_body = render_to_string('users/booking_confirmation.html', email_context)

        # Send email using Django's send_mail function
        send_mail(
            subject,
            email_body,
            settings.DEFAULT_FROM_EMAIL,
            ['info@novustelltravel.com'],  # Recipient email
            html_message=email_body,  # Optional: HTML email
            fail_silently=False,
        )
        return True
    except Exception as e:
        # Log the error or handle it as needed
        print(f"Email sending failed: {e}")
        return False