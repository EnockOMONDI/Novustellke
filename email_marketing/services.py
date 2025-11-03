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

    def send_campaign(self, campaign_id, batch_size=50):
        """
        Send an email campaign using memory-efficient batch processing

        Args:
            campaign_id: ID of the campaign to send
            batch_size: Number of recipients to process in each batch (default: 50)
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

            # Get total recipient count without loading all into memory
            total_recipients = self._get_campaign_recipient_count(campaign)

            if total_recipients == 0:
                logger.warning(f"No recipients found for campaign {campaign.name}")
                campaign.status = 'cancelled'
                campaign.save()
                return False

            logger.info(f"Starting campaign {campaign.name} for {total_recipients} recipients using batch size {batch_size}")

            # Process recipients in batches to avoid memory issues
            total_sent = 0
            total_failed = 0
            batch_number = 1

            # Use iterator to process recipients in batches without loading all into memory
            for recipient_batch in self._get_campaign_recipients_batched(campaign, batch_size):
                try:
                    logger.info(f"Processing batch {batch_number} with {len(recipient_batch)} recipients")

                    # Send batch of emails
                    batch_sent, batch_failed = self._send_recipient_batch(campaign, recipient_batch, batch_number)

                    total_sent += batch_sent
                    total_failed += batch_failed

                    logger.info(f"Batch {batch_number} completed: {batch_sent} sent, {batch_failed} failed")

                    # Update campaign progress
                    campaign.emails_sent_count = total_sent
                    campaign.save()

                    batch_number += 1

                except Exception as e:
                    logger.error(f"Error processing batch {batch_number}: {e}")
                    total_failed += len(recipient_batch)
                    batch_number += 1
                    continue

            # Final campaign status update
            if total_sent > 0:
                campaign.status = 'sent'
                campaign.completed_at = timezone.now()
                campaign.emails_sent_count = total_sent
                campaign.save()

                logger.info(f"Campaign {campaign.name} completed: {total_sent} sent, {total_failed} failed out of {total_recipients} total")
                return True
            else:
                campaign.status = 'failed'
                campaign.completed_at = timezone.now()
                campaign.save()
                logger.error(f"Campaign {campaign.name} failed: No emails were sent successfully")
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

    def _get_campaign_recipient_count(self, campaign):
        """Get total count of unique recipients without loading them into memory"""
        recipient_emails = set()

        for recipient_list in campaign.recipient_lists.all():
            for recipient in recipient_list.recipients.filter(is_active=True, subscribed=True).iterator():
                recipient_emails.add(recipient.email)

        return len(recipient_emails)

    def _get_campaign_recipients_batched(self, campaign, batch_size):
        """
        Generator that yields batches of recipients to avoid memory issues

        Args:
            campaign: EmailCampaign instance
            batch_size: Number of recipients per batch

        Yields:
            List of recipients (batch)
        """
        recipient_emails = set()
        current_batch = []

        for recipient_list in campaign.recipient_lists.all():
            # Use iterator() to avoid caching all recipients in memory
            for recipient in recipient_list.recipients.filter(is_active=True, subscribed=True).iterator():
                if recipient.email not in recipient_emails:
                    recipient_emails.add(recipient.email)
                    current_batch.append(recipient)

                    # Yield batch when it reaches the desired size
                    if len(current_batch) >= batch_size:
                        yield current_batch
                        current_batch = []  # Clear batch to free memory

        # Yield remaining recipients if any
        if current_batch:
            yield current_batch

    def _send_recipient_batch(self, campaign, recipients, batch_number):
        """
        Send emails to a batch of recipients

        Args:
            campaign: EmailCampaign instance
            recipients: List of recipients in this batch
            batch_number: Current batch number for logging

        Returns:
            Tuple of (sent_count, failed_count)
        """
        try:
            # Prepare email data for this batch only
            emails_data = self._prepare_bulk_email_data(campaign, recipients)

            # Send emails for this batch
            sent_count = 0
            failed_count = 0

            for i, email_data in enumerate(emails_data, 1):
                try:
                    response = requests.post(
                        f"{self.base_url}/api/send",
                        headers=self.headers,
                        json=email_data,
                        timeout=30
                    )

                    if response.status_code == 200:
                        sent_count += 1
                        recipient_email = email_data['to'][0]['email']
                        recipient_name = email_data['to'][0]['name']
                        logger.info(f"Batch {batch_number}, Email {i}: Sent to {recipient_name} ({recipient_email})")
                    else:
                        failed_count += 1
                        recipient_email = email_data['to'][0]['email']
                        logger.error(f"Batch {batch_number}, Email {i}: Failed to send to {recipient_email}: {response.status_code}")

                except Exception as e:
                    failed_count += 1
                    recipient_email = email_data['to'][0]['email'] if email_data.get('to') else 'unknown'
                    logger.error(f"Batch {batch_number}, Email {i}: Error sending to {recipient_email}: {e}")

            # Create email logs for this batch
            self._create_email_logs_batch(campaign, recipients, sent_count > 0)

            # Clear email data from memory
            del emails_data

            return sent_count, failed_count

        except Exception as e:
            logger.error(f"Error processing batch {batch_number}: {e}")
            return 0, len(recipients)

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

    def _create_email_logs_batch(self, campaign, recipients, success_status=True):
        """Create email logs for a batch of recipients"""
        status = 'sent' if success_status else 'failed'

        for recipient in recipients:
            tracking_token = str(uuid.uuid4())

            EmailLog.objects.get_or_create(
                campaign=campaign,
                recipient=recipient,
                defaults={
                    'subject': campaign.email_template.subject,
                    'sent_to': recipient.email,
                    'tracking_token': tracking_token,
                    'status': status,
                    'sent_at': timezone.now() if success_status else None
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
