"""
Email sending functions using Django mail.
Production delivery is handled by Resend via the configured Django backend.
"""
import logging
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)


def send_email_via_mailtrap(subject, html_message, from_email, recipient_list):
    """
    Send email using Django's mail layer.

    Args:
        subject (str): Email subject
        html_message (str): HTML message content
        from_email (str): From email (e.g., "App Name <info@domain.com>")
        recipient_list (list): List of recipient email addresses

    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        logger.info("Sending transactional email: subject='%s', recipients=%s", subject, recipient_list)

        plain_message = strip_tags(html_message)
        message = EmailMultiAlternatives(
            subject=subject,
            body=plain_message,
            from_email=from_email,
            to=[email.strip() for email in recipient_list],
        )
        message.attach_alternative(html_message, "text/html")
        message.send(fail_silently=False)

        logger.info("Transactional email sent successfully")
        return True

    except Exception as e:
        logger.error("Failed to send transactional email: %s", e)
        return False


def send_contact_inquiry_emails(inquiry):
    """
    Send email notifications for contact inquiries

    Args:
        inquiry: ContactInquiry object

    Returns:
        dict: Status of email sending with details
    """
    try:
        logger.info(f"Sending emails for contact inquiry {inquiry.id}")

        # Track email sending status
        admin_sent = False
        user_sent = False

        # Send admin notification email
        try:
            admin_subject = f'New Contact Inquiry from {inquiry.full_name}'
            admin_message_html = render_to_string('users/emails/contact_inquiry_admin.html', {
                'inquiry': inquiry
            })

            admin_sent = send_email_via_mailtrap(
                subject=admin_subject,
                html_message=admin_message_html,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.ADMIN_EMAIL],
            )

            if admin_sent:
                logger.info(f"Admin notification sent for contact inquiry {inquiry.id}")
            else:
                logger.error(f"Failed to send admin email for contact inquiry {inquiry.id}")

        except Exception as e:
            logger.error(f"Failed to send admin email for contact inquiry {inquiry.id}: {e}")

        # Send user confirmation email
        try:
            user_subject = 'Contact Inquiry Received - Novustell Travel'
            user_message_html = render_to_string('users/emails/contact_inquiry_confirmation.html', {
                'inquiry': inquiry
            })

            user_sent = send_email_via_mailtrap(
                subject=user_subject,
                html_message=user_message_html,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[inquiry.email],
            )

            if user_sent:
                logger.info(f"User confirmation sent for contact inquiry {inquiry.id}")
            else:
                logger.error(f"Failed to send user email for contact inquiry {inquiry.id}")

        except Exception as e:
            logger.error(f"Failed to send user email for contact inquiry {inquiry.id}: {e}")

        # Return status
        success = admin_sent and user_sent
        if not success:
            logger.warning(f"Some emails failed for contact inquiry {inquiry.id}: admin={admin_sent}, user={user_sent}")

        return {
            'success': success,
            'admin_email_sent': admin_sent,
            'user_email_sent': user_sent,
        }

    except Exception as e:
        error_msg = f"Unexpected error sending emails for contact inquiry {inquiry.id}: {e}"
        logger.error(error_msg)
        return {'success': False, 'error': error_msg}


def send_student_travel_emails(inquiry):
    """
    Send email notifications for student travel inquiries

    Args:
        inquiry: StudentTravelInquiry object

    Returns:
        dict: Status of email sending with details
    """
    try:
        logger.info(f"Sending emails for student travel inquiry {inquiry.id}")

        # Track email sending status
        admin_sent = False
        careers_sent = False
        user_sent = False

        # Send admin notification email
        try:
            admin_subject = f'New Student Travel Inquiry from {inquiry.contact_person}'
            admin_message_html = render_to_string('users/emails/student_travel_admin.html', {
                'inquiry': inquiry
            })

            admin_sent = send_email_via_mailtrap(
                subject=admin_subject,
                html_message=admin_message_html,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.ADMIN_EMAIL],
            )

        except Exception as e:
            logger.error(f"Failed to send admin email for student travel inquiry {inquiry.id}: {e}")

        # Send careers notification email
        try:
            careers_subject = f'New Student Travel Inquiry from {inquiry.contact_person}'
            careers_message_html = render_to_string('users/emails/student_travel_admin.html', {
                'inquiry': inquiry
            })

            careers_sent = send_email_via_mailtrap(
                subject=careers_subject,
                html_message=careers_message_html,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.JOBS_EMAIL],
            )

        except Exception as e:
            logger.error(f"Failed to send careers email for student travel inquiry {inquiry.id}: {e}")

        # Send user confirmation email
        try:
            user_subject = 'Student Travel Inquiry Received - Novustell Travel'
            user_message_html = render_to_string('users/emails/student_travel_confirmation.html', {
                'inquiry': inquiry
            })

            user_sent = send_email_via_mailtrap(
                subject=user_subject,
                html_message=user_message_html,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[inquiry.email],
            )

        except Exception as e:
            logger.error(f"Failed to send user email for student travel inquiry {inquiry.id}: {e}")

        # Return status
        success = admin_sent and careers_sent and user_sent
        return {
            'success': success,
            'admin_email_sent': admin_sent,
            'careers_email_sent': careers_sent,
            'user_email_sent': user_sent,
        }

    except Exception as e:
        error_msg = f"Unexpected error sending emails for student travel inquiry {inquiry.id}: {e}"
        logger.error(error_msg)
        return {'success': False, 'error': error_msg}


def send_mice_inquiry_emails(inquiry):
    """
    Send email notifications for MICE inquiries

    Args:
        inquiry: MICEInquiry object

    Returns:
        dict: Status of email sending with details
    """
    try:
        logger.info(f"Sending emails for MICE inquiry {inquiry.id}")

        # Send admin notification email
        admin_subject = f'New MICE Inquiry from {inquiry.contact_person}'
        admin_message_html = render_to_string('users/emails/mice_inquiry_admin.html', {
            'inquiry': inquiry
        })

        admin_sent = send_email_via_mailtrap(
            subject=admin_subject,
            html_message=admin_message_html,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.ADMIN_EMAIL],
        )

        # Send user confirmation email
        user_subject = 'MICE Inquiry Received - Novustell Travel'
        user_message_html = render_to_string('users/emails/mice_inquiry_confirmation.html', {
            'inquiry': inquiry
        })

        user_sent = send_email_via_mailtrap(
            subject=user_subject,
            html_message=user_message_html,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[inquiry.email],
        )

        return {
            'success': admin_sent and user_sent,
            'admin_email_sent': admin_sent,
            'user_email_sent': user_sent,
        }

    except Exception as e:
        error_msg = f"Unexpected error sending emails for MICE inquiry {inquiry.id}: {e}"
        logger.error(error_msg)
        return {'success': False, 'error': error_msg}


def send_newsletter_subscription_emails(subscription):
    """
    Send email notifications for newsletter subscriptions

    Args:
        subscription: NewsletterSubscription object

    Returns:
        dict: Status of email sending with details
    """
    try:
        logger.info(f"Sending emails for newsletter subscription {subscription.id}")

        # Send admin notification email
        admin_subject = f'New Newsletter Subscription: {subscription.email}'
        admin_message_html = render_to_string('users/emails/newsletter_admin.html', {
            'subscription': subscription
        })

        admin_sent = send_email_via_mailtrap(
            subject=admin_subject,
            html_message=admin_message_html,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.NEWSLETTER_EMAIL],
        )

        # Send user welcome email
        user_subject = 'Welcome to Novustell Travel Newsletter!'
        user_message_html = render_to_string('users/emails/newsletter_confirmation.html', {
            'subscription': subscription
        })

        user_sent = send_email_via_mailtrap(
            subject=user_subject,
            html_message=user_message_html,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[subscription.email],
        )

        return {
            'success': admin_sent and user_sent,
            'admin_email_sent': admin_sent,
            'user_email_sent': user_sent,
        }

    except Exception as e:
        error_msg = f"Unexpected error sending emails for newsletter subscription {subscription.id}: {e}"
        logger.error(error_msg)
        return {'success': False, 'error': error_msg}


def send_ngo_travel_emails(inquiry):
    """
    Send email notifications for NGO travel inquiries

    Args:
        inquiry: NGOTravelInquiry object

    Returns:
        dict: Status of email sending with details
    """
    try:
        logger.info(f"Sending emails for NGO travel inquiry {inquiry.id}")

        # Send admin notification email
        admin_subject = f'New NGO Travel Inquiry from {inquiry.organization_name}'
        admin_message_html = render_to_string('users/emails/ngo_travel_admin.html', {
            'inquiry': inquiry
        })

        admin_sent = send_email_via_mailtrap(
            subject=admin_subject,
            html_message=admin_message_html,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.ADMIN_EMAIL],
        )

        # Send user confirmation email
        user_subject = 'NGO Travel Inquiry Received - Novustell Travel'
        user_message_html = render_to_string('users/emails/ngo_travel_confirmation.html', {
            'inquiry': inquiry
        })

        user_sent = send_email_via_mailtrap(
            subject=user_subject,
            html_message=user_message_html,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[inquiry.email],
        )

        return {
            'success': admin_sent and user_sent,
            'admin_email_sent': admin_sent,
            'user_email_sent': user_sent,
        }

    except Exception as e:
        error_msg = f"Unexpected error sending emails for NGO travel inquiry {inquiry.id}: {e}"
        logger.error(error_msg)
        return {'success': False, 'error': error_msg}


def send_job_application_emails(job_application):
    """
    Send email notifications for job applications

    Args:
        job_application: JobApplication object

    Returns:
        dict: Status of email sending with details
    """
    try:
        logger.info(f"Sending emails for job application {job_application.id}")

        # Send admin notification email to both careers and info email addresses
        admin_subject = f'New Job Application - {job_application.get_position_display()}'
        admin_message_html = render_to_string('users/emails/job_application_admin.html', {
            'application': job_application
        })

        # Send to both careers and info email addresses
        careers_email = getattr(settings, 'JOBS_EMAIL', 'careers@novustelltravel.com')
        info_email = getattr(settings, 'ADMIN_EMAIL', 'info@novustelltravel.com')
        recipient_list = [careers_email, info_email]

        admin_sent = send_email_via_mailtrap(
            subject=admin_subject,
            html_message=admin_message_html,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
        )

        # Send applicant confirmation email
        applicant_subject = f'Application Received - {job_application.get_position_display()}'
        applicant_message_html = render_to_string('users/emails/job_application_confirmation.html', {
            'application': job_application
        })

        applicant_sent = send_email_via_mailtrap(
            subject=applicant_subject,
            html_message=applicant_message_html,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[job_application.email],
        )

        # Update email tracking
        job_application.admin_notification_sent = admin_sent
        job_application.applicant_confirmation_sent = applicant_sent
        job_application.save()

        return {
            'success': admin_sent and applicant_sent,
            'admin_email_sent': admin_sent,
            'applicant_email_sent': applicant_sent,
        }

    except Exception as e:
        error_msg = f"Unexpected error sending emails for job application {job_application.id}: {e}"
        logger.error(error_msg)
        return {'success': False, 'error': error_msg}
