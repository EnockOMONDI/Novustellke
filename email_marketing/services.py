"""
Email Marketing Services
Handles email sending, template rendering, and campaign management
"""

import uuid
import logging
import requests
from django.template import Template, Context
from django.utils import timezone
from django.conf import settings
# from django_ratelimit.decorators import ratelimit  # DEPRECATED - no longer needed with Email Marketing API
from django.core.cache import cache
from .models import EmailCampaign, EmailLog, Recipient

from users.tasks import send_email_via_mailtrap

logger = logging.getLogger(__name__)


class ResendEmailMarketingService:
    """Service class for small manual campaign sends via Resend batch API."""

    def __init__(self):
        self.api_token = getattr(settings, 'RESEND_API_KEY', '')
        self.base_url = 'https://api.resend.com'
        self.headers = {
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json',
        }
        self.from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'Novustell Travel <info@novustelltravel.com>')
        self.batch_limit = getattr(settings, 'EMAIL_MARKETING_BATCH_LIMIT', 99)

    def send_campaign(self, campaign_id):
        """
        Send an email campaign via Resend's batch API.

        Args:
            campaign_id: ID of the campaign to send
        """
        try:
            campaign = EmailCampaign.objects.get(id=campaign_id)

            if campaign.status not in ['draft', 'scheduled']:
                logger.warning(f"Campaign {campaign.name} is not in sendable status: {campaign.status}")
                return False

            # Update campaign status
            campaign.status = 'sending'
            campaign.started_at = timezone.now()
            campaign.save()

            # Get recipients using memory-efficient approach (only email and first_name)
            recipients_data = self._get_campaign_recipients_minimal(campaign)

            if not recipients_data:
                logger.warning(f"No recipients found for campaign {campaign.name}")
                campaign.status = 'cancelled'
                campaign.save()
                return False

            if len(recipients_data) > self.batch_limit:
                raise ValueError(
                    f"Campaign '{campaign.name}' has {len(recipients_data)} recipients. "
                    f"This deployment only supports manual sends up to {self.batch_limit} recipients."
                )

            logger.info(
                "Starting campaign %s for %s recipients using Resend batch API",
                campaign.name,
                len(recipients_data),
            )

            batch_payload = self._prepare_newsletter_data(campaign, recipients_data)

            success = self._send_newsletter(batch_payload)

            if success:
                # Update campaign status
                campaign.status = 'sent'
                campaign.sent_at = timezone.now()
                campaign.completed_at = timezone.now()
                campaign.emails_sent_count = len(recipients_data)
                campaign.save()

                # Create email logs for tracking
                self._create_email_logs_minimal(campaign, recipients_data)

                logger.info(
                    "Campaign %s sent successfully to %s recipients via Resend batch API",
                    campaign.name,
                    len(recipients_data),
                )
                return True
            else:
                campaign.status = 'failed'
                campaign.completed_at = timezone.now()
                campaign.save()
                return False

        except EmailCampaign.DoesNotExist:
            logger.error(f"Campaign with ID {campaign_id} not found")
            return False
        except Exception as e:
            logger.error(f"Error sending campaign {campaign_id}: {e}")
            try:
                campaign = EmailCampaign.objects.get(id=campaign_id)
                campaign.status = 'failed'
                campaign.completed_at = timezone.now()
                campaign.save()
            except:
                pass
            return False

    def _get_campaign_recipients(self, campaign):
        """Get all unique recipients for a campaign"""
        recipient_emails = set()
        recipients = []

        for recipient_list in campaign.recipient_lists.all():
            for recipient in recipient_list.recipients.filter(is_active=True, subscribed=True):
                if recipient.email not in recipient_emails:
                    recipient_emails.add(recipient.email)
                    recipients.append(recipient)

        return recipients

    def _get_campaign_recipients_minimal(self, campaign):
        """
        Get unique recipients with minimal memory usage (only email and first_name)

        Returns:
            List of tuples: [(email, first_name), ...]
        """
        recipient_emails = set()
        recipients_data = []

        for recipient_list in campaign.recipient_lists.all():
            # Use values_list to get only email and first_name, minimizing memory usage
            for email, first_name in recipient_list.recipients.filter(
                is_active=True,
                subscribed=True
            ).values_list('email', 'first_name'):
                if email not in recipient_emails:
                    recipient_emails.add(email)
                    recipients_data.append((email, first_name or email.split('@')[0]))

        return recipients_data

    def _prepare_newsletter_data(self, campaign, recipients_data):
        """
        Prepare Resend batch email payload.

        Args:
            campaign: EmailCampaign instance
            recipients_data: List of tuples [(email, first_name), ...]

        Returns:
            list[dict]: Batch payload for Resend's /emails/batch endpoint
        """
        base_url = getattr(settings, 'BASE_URL', 'https://www.novustelltravel.com')
        subject_template = Template(campaign.email_template.subject)
        html_template = Template(campaign.email_template.html_content)
        payload = []

        for email, first_name in recipients_data:
            context = Context({
                'recipient_name': first_name,
                'organization': '',
                'tracking_pixel_url': '',
                'unsubscribe_url': f'{base_url}/email-marketing/unsubscribe/?email={email}',
                'base_url': base_url,
            })

            personalized_subject = subject_template.render(context)
            personalized_html = html_template.render(context)
            payload.append({
                "from": self.from_email,
                "to": [email],
                "subject": personalized_subject,
                "html": personalized_html,
                "tags": [
                    {"name": "campaign_id", "value": str(campaign.id)},
                    {"name": "campaign_name", "value": campaign.name[:256]},
                ],
            })

        return payload

    def _send_newsletter(self, batch_payload):
        """
        Send a small manual campaign batch via Resend.

        Args:
            batch_payload: Personalized payload for each recipient

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            logger.info(
                "Sending manual campaign batch via Resend: %s recipients",
                len(batch_payload),
            )

            response = requests.post(
                f"{self.base_url}/emails/batch",
                headers=self.headers,
                json=batch_payload,
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()
            logger.info("Resend batch API accepted %s emails", len(data.get("data", [])))
            return True

        except Exception as e:
            logger.error("Unexpected error in Resend batch send: %s", e)
            return False

    def _create_email_logs(self, campaign, recipients):
        """Create email logs for tracking purposes"""
        for recipient in recipients:
            tracking_token = str(uuid.uuid4())

            EmailLog.objects.get_or_create(
                campaign=campaign,
                recipient=recipient,
                defaults={
                    'subject': campaign.email_template.subject,
                    'sent_to': recipient.email,
                    'tracking_token': tracking_token,
                    'status': 'sent',
                    'sent_at': timezone.now()
                }
            )

    def _create_email_logs_minimal(self, campaign, recipients_data):
        """Create email logs for newsletter recipients using minimal data"""
        from .models import EmailLog, Recipient
        import uuid

        for email, first_name in recipients_data:
            tracking_token = str(uuid.uuid4())

            # Get recipient object efficiently
            try:
                recipient = Recipient.objects.get(email=email)

                EmailLog.objects.get_or_create(
                    campaign=campaign,
                    recipient=recipient,
                    defaults={
                        'subject': campaign.email_template.subject,
                        'sent_to': email,
                        'tracking_token': tracking_token,
                        'status': 'sent',
                        'sent_at': timezone.now()
                    }
                )
            except Recipient.DoesNotExist:
                logger.warning(f"Recipient {email} not found for email log creation")
                continue

    def _prepare_template_context(self, recipient):
        """Prepare context data for template rendering"""
        base_url = getattr(settings, 'BASE_URL', 'https://www.novustelltravel.com')

        context_data = {
            # Recipient information - using first name only for personalization
            'recipient_name': recipient.first_name or recipient.email.split('@')[0],
            'first_name': recipient.first_name,
            'last_name': recipient.last_name,
            'email': recipient.email,
            'organization': recipient.organization,
            'position': recipient.position,
            'phone': recipient.phone,
            'location': recipient.location,

            # Company information
            'company_name': 'Novustell Travel',
            'company_tagline': 'Think Convenience, Think Novustell',
            'company_website': 'https://www.novustelltravel.com',
            'company_email': 'Info@novustelltravel.com',
            'company_phone': '+254 721 115 572',
            'company_whatsapp': '+254 701 363 551',

            # Unsubscribe URL
            'unsubscribe_url': f"{base_url}/email-marketing/unsubscribe/{recipient.id}/",

            # Custom data from recipient
            **recipient.custom_data
        }

        return context_data

    def _render_email_template(self, template_content, context_data):
        """Render email template with context data"""
        if not template_content:
            return ""

        try:
            template = Template(template_content)
            context = Context(context_data)
            return template.render(context)
        except Exception as e:
            logger.error(f"Error rendering email template: {e}")
            return template_content  # Return original content if rendering fails


class EmailMarketingService:
    """Service class for handling email marketing operations."""

    def __init__(self):
        self.from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'info@novustelltravel.com')
        self.resend_marketing_service = ResendEmailMarketingService()

    def send_campaign(self, campaign_id):
        """
        Send an email marketing campaign using Resend's batch API.

        Args:
            campaign_id: ID of the campaign to send
        """
        logger.info("Sending campaign %s via Resend batch API", campaign_id)
        return self.resend_marketing_service.send_campaign(campaign_id)

    def send_transactional_email(self, subject, html_message, from_email, recipient_list):
        """
        Send transactional emails using the configured Django backend.
        """
        return send_email_via_mailtrap(
            subject=subject,
            html_message=html_message,
            from_email=from_email,
            recipient_list=recipient_list
        )

    def _check_rate_limit(self, user_id):
        """
        Check if user has exceeded rate limits

        Args:
            user_id (int): ID of the user sending emails

        Raises:
            Exception: If rate limit is exceeded
        """
        minute_key = f"email_rate_minute_{user_id}"
        hour_key = f"email_rate_hour_{user_id}"

        minute_count = cache.get(minute_key, 0)
        hour_count = cache.get(hour_key, 0)

        if minute_count >= settings.EMAIL_RATE_LIMIT_PER_MINUTE:
            raise Exception(f"Rate limit exceeded: {minute_count} emails sent in the last minute (limit: {settings.EMAIL_RATE_LIMIT_PER_MINUTE})")

        if hour_count >= settings.EMAIL_RATE_LIMIT_PER_HOUR:
            raise Exception(f"Rate limit exceeded: {hour_count} emails sent in the last hour (limit: {settings.EMAIL_RATE_LIMIT_PER_HOUR})")

    def _update_rate_limit_counters(self, user_id):
        """
        Update rate limiting counters after successful email send

        Args:
            user_id (int): ID of the user who sent the email
        """
        minute_key = f"email_rate_minute_{user_id}"
        hour_key = f"email_rate_hour_{user_id}"

        # Increment minute counter (expires after 60 seconds)
        try:
            cache.add(minute_key, 0, 60)
            cache.incr(minute_key)
        except ValueError:
            cache.set(minute_key, 1, 60)

        # Increment hour counter (expires after 3600 seconds)
        try:
            cache.add(hour_key, 0, 3600)
            cache.incr(hour_key)
        except ValueError:
            cache.set(hour_key, 1, 3600)
    
    def create_sample_recipients(self):
        """
        Create sample recipients for testing (development only)
        """
        if not settings.DEBUG:
            logger.warning("Sample recipients can only be created in DEBUG mode")
            return
        
        from .models import RecipientList
        
        # Create sample recipient list
        sample_list, created = RecipientList.objects.get_or_create(
            name="Sample Educational Institutions",
            defaults={
                'description': "Sample list for testing email marketing",
                'list_type': 'schools',
                'created_by_id': 1  # Assuming admin user exists
            }
        )
        
        # Sample recipients data
        sample_recipients = [
            {
                'email': 'principal@sampleschool.edu',
                'first_name': 'John',
                'last_name': 'Smith',
                'organization': 'Sample High School',
                'position': 'Principal',
                'location': 'Nairobi, Kenya'
            },
            {
                'email': 'coordinator@testacademy.edu',
                'first_name': 'Mary',
                'last_name': 'Johnson',
                'organization': 'Test Academy',
                'position': 'MUN Coordinator',
                'location': 'Mombasa, Kenya'
            },
            {
                'email': 'admin@demoschool.edu',
                'first_name': 'David',
                'last_name': 'Wilson',
                'organization': 'Demo International School',
                'position': 'Academic Director',
                'location': 'Kisumu, Kenya'
            }
        ]
        
        for recipient_data in sample_recipients:
            recipient, created = Recipient.objects.get_or_create(
                email=recipient_data['email'],
                defaults=recipient_data
            )
            recipient.recipient_lists.add(sample_list)
        
        logger.info(f"Created sample recipient list with {len(sample_recipients)} recipients")
        return sample_list


# Global service instance
email_marketing_service = EmailMarketingService()
