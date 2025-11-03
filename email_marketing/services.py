"""
Email Marketing Services
Handles email sending, template rendering, and campaign management
"""

import uuid
import logging
import requests
import json
from django.template import Template, Context
from django.utils import timezone
from django.conf import settings
from django.urls import reverse
# from django_ratelimit.decorators import ratelimit  # DEPRECATED - no longer needed with Email Marketing API
from django.core.cache import cache
from .models import EmailCampaign, EmailLog, Recipient

# Import Mailtrap HTTP API functions for transactional emails
from users.tasks import send_email_via_mailtrap

logger = logging.getLogger(__name__)


class MailtrapEmailMarketingService:
    """Service class for Mailtrap Email Marketing API (Bulk Stream)"""

    def __init__(self):
        self.api_token = getattr(settings, 'MAILTRAP_API_TOKEN', 'd766975d57a7ef1acf2f750a36247a37')
        self.base_url = 'https://bulk.api.mailtrap.io'
        self.headers = {
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json'
        }
        self.from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'Novustell Travel <info@novustelltravel.com>')

    def send_campaign(self, campaign_id):
        """
        Send an email marketing campaign using Mailtrap Email Marketing API
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

            # Get all unique recipients
            recipients = self._get_campaign_recipients(campaign)

            if not recipients:
                logger.warning(f"No recipients found for campaign {campaign.name}")
                campaign.status = 'cancelled'
                campaign.save()
                return False

            # Prepare personalized email data for each recipient
            emails_data = self._prepare_bulk_email_data(campaign, recipients)

            # Send personalized emails via Mailtrap Email Marketing API
            success = self._send_bulk_email(emails_data)

            if success:
                # Update campaign status
                campaign.status = 'sent'
                campaign.sent_at = timezone.now()
                campaign.completed_at = timezone.now()
                campaign.emails_sent_count = len(recipients)
                campaign.save()

                # Create email logs for tracking
                self._create_email_logs(campaign, recipients)

                logger.info(f"Campaign {campaign.name} sent successfully to {len(recipients)} recipients")
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

    def _prepare_bulk_email_data(self, campaign, recipients):
        """
        Prepare email data for Mailtrap bulk sending with proper personalization.

        Since Mailtrap Bulk Stream API doesn't support per-recipient template variables,
        we'll send individual personalized emails to each recipient.
        """
        # Parse from email
        if '<' in self.from_email and '>' in self.from_email:
            from_name = self.from_email.split('<')[0].strip()
            from_email_addr = self.from_email.split('<')[1].split('>')[0].strip()
        else:
            from_name = "Novustell Travel"
            from_email_addr = self.from_email.strip()

        # Prepare individual emails for each recipient with personalized content
        emails_data = []

        for recipient in recipients:
            # Prepare personalized context for this recipient
            context_data = self._prepare_template_context(recipient)

            # Render the email template with recipient-specific context
            rendered_html = self._render_email_template(campaign.email_template.html_content, context_data)
            rendered_subject = self._render_email_template(campaign.email_template.subject, context_data)

            # Create individual email data for this recipient
            email_data = {
                "from": {
                    "email": from_email_addr,
                    "name": from_name
                },
                "to": [{
                    "email": recipient.email,
                    "name": recipient.first_name or recipient.email.split('@')[0]
                }],
                "subject": rendered_subject,
                "html": rendered_html,
                "category": f"campaign_{campaign.id}",
                "custom_variables": {
                    "recipient_id": str(recipient.id),
                    "campaign_id": str(campaign.id),
                    "recipient_name": recipient.first_name or recipient.email.split('@')[0]
                }
            }

            emails_data.append(email_data)

        return emails_data

    def _send_bulk_email(self, emails_data):
        """
        Send personalized emails via Mailtrap Email Marketing API.

        Since we need per-recipient personalization, we send individual emails
        rather than using bulk sending with the same content.
        """
        successful_sends = 0
        total_emails = len(emails_data)

        logger.info(f"Sending {total_emails} personalized emails via Mailtrap Email Marketing API")

        for i, email_data in enumerate(emails_data, 1):
            try:
                response = requests.post(
                    f"{self.base_url}/api/send",
                    headers=self.headers,
                    json=email_data,
                    timeout=30
                )

                if response.status_code == 200:
                    successful_sends += 1
                    recipient_email = email_data['to'][0]['email']
                    recipient_name = email_data['to'][0]['name']
                    logger.info(f"Email {i}/{total_emails} sent successfully to {recipient_name} ({recipient_email})")
                else:
                    recipient_email = email_data['to'][0]['email']
                    logger.error(f"Failed to send email {i}/{total_emails} to {recipient_email}: {response.status_code} - {response.text}")

            except requests.exceptions.RequestException as e:
                recipient_email = email_data['to'][0]['email']
                logger.error(f"Request error sending email {i}/{total_emails} to {recipient_email}: {e}")
            except Exception as e:
                recipient_email = email_data['to'][0]['email'] if email_data.get('to') else 'unknown'
                logger.error(f"Unexpected error sending email {i}/{total_emails} to {recipient_email}: {e}")

        logger.info(f"Email sending completed: {successful_sends}/{total_emails} emails sent successfully")

        # Return True if at least one email was sent successfully
        return successful_sends > 0

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
    """Service class for handling email marketing operations (Hybrid approach)"""

    def __init__(self):
        self.from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'info@novustelltravel.com')
        self.mailtrap_marketing_service = MailtrapEmailMarketingService()

    def send_campaign(self, campaign_id):
        """
        Send an email marketing campaign using Mailtrap Email Marketing API
        """
        logger.info(f"Sending campaign {campaign_id} via Mailtrap Email Marketing API")
        return self.mailtrap_marketing_service.send_campaign(campaign_id)

    def send_transactional_email(self, subject, html_message, from_email, recipient_list):
        """
        Send transactional emails using the existing Mailtrap HTTP API
        This method preserves the existing transactional email functionality
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
