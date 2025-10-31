"""
Email Marketing Services
Handles email sending, template rendering, and campaign management
"""

import uuid
import logging
from django.template import Template, Context
from django.utils import timezone
from django.conf import settings
from django.urls import reverse
from django_ratelimit.decorators import ratelimit
from django.core.cache import cache
from .models import EmailCampaign, EmailLog, Recipient

# Import Mailtrap HTTP API functions
from users.tasks import send_email_via_mailtrap

logger = logging.getLogger(__name__)


class EmailMarketingService:
    """Service class for handling email marketing operations"""
    
    def __init__(self):
        self.from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'info@novustelltravel.com')
    
    def send_campaign(self, campaign_id):
        """
        Send an email marketing campaign
        """
        try:
            campaign = EmailCampaign.objects.get(id=campaign_id)
            
            if campaign.status not in ['draft', 'scheduled']:
                logger.warning(f"Campaign {campaign.name} is not in sendable status: {campaign.status}")
                return False
            
            # Update campaign status
            campaign.status = 'sending'
            campaign.save()
            
            # Get all unique recipients
            recipients = self._get_campaign_recipients(campaign)
            
            sent_count = 0
            failed_count = 0
            
            for recipient in recipients:
                try:
                    success = self._send_email_to_recipient(campaign, recipient)
                    if success:
                        sent_count += 1
                    else:
                        failed_count += 1
                except Exception as e:
                    logger.error(f"Error sending email to {recipient.email}: {e}")
                    failed_count += 1
            
            # Update campaign status
            campaign.status = 'sent'
            campaign.sent_at = timezone.now()
            campaign.save()
            
            logger.info(f"Campaign {campaign.name} completed: {sent_count} sent, {failed_count} failed")
            return True
            
        except EmailCampaign.DoesNotExist:
            logger.error(f"Campaign with ID {campaign_id} not found")
            return False
        except Exception as e:
            logger.error(f"Error sending campaign {campaign_id}: {e}")
            return False
    
    def _get_campaign_recipients(self, campaign):
        """
        Get all unique recipients for a campaign
        """
        recipient_emails = set()
        recipients = []
        
        for recipient_list in campaign.recipient_lists.all():
            for recipient in recipient_list.recipients.filter(is_active=True, subscribed=True):
                if recipient.email not in recipient_emails:
                    recipient_emails.add(recipient.email)
                    recipients.append(recipient)
        
        return recipients
    
    def _send_email_to_recipient(self, campaign, recipient):
        """
        Send email to a single recipient
        """
        try:
            # Generate tracking token
            tracking_token = str(uuid.uuid4())
            
            # Create or get email log
            email_log, created = EmailLog.objects.get_or_create(
                campaign=campaign,
                recipient=recipient,
                defaults={
                    'subject': campaign.email_template.subject,
                    'sent_to': recipient.email,
                    'tracking_token': tracking_token,
                    'status': 'pending'
                }
            )
            
            if not created and email_log.status == 'sent':
                logger.info(f"Email already sent to {recipient.email} for campaign {campaign.name}")
                return True
            
            # Prepare template context
            context_data = self._prepare_template_context(recipient, tracking_token)
            
            # Render email content
            html_content = self._render_email_template(campaign.email_template.html_content, context_data)
            text_content = self._render_email_template(campaign.email_template.text_content, context_data) if campaign.email_template.text_content else None
            
            # Create email message
            subject = self._render_email_template(campaign.email_template.subject, context_data)

            # Check rate limiting before sending (skip for testing)
            # self._check_rate_limit(campaign.created_by.id if campaign.created_by else 1)

            # Send email via Mailtrap HTTP API
            success = send_email_via_mailtrap(
                subject=subject,
                html_message=html_content,
                from_email=self.from_email,
                recipient_list=[recipient.email]
            )

            if not success:
                raise Exception("Mailtrap HTTP API returned failure")
            
            # Update email log
            email_log.status = 'sent'
            email_log.sent_at = timezone.now()
            email_log.save()

            # Update rate limiting counters (skip for testing)
            # self._update_rate_limit_counters(campaign.created_by.id if campaign.created_by else 1)

            logger.info(f"Email sent successfully to {recipient.email} for campaign {campaign.name} via Mailtrap HTTP API")
            return True
            
        except Exception as e:
            # Update email log with error
            if 'email_log' in locals():
                email_log.status = 'failed'
                email_log.error_message = str(e)
                email_log.save()
            
            logger.error(f"Failed to send email to {recipient.email}: {e}")
            return False
    
    def _prepare_template_context(self, recipient, tracking_token):
        """
        Prepare context data for template rendering
        """
        # Base URL for tracking
        base_url = getattr(settings, 'BASE_URL', 'https://www.novustelltravel.com')
        
        context_data = {
            # Recipient information
            'recipient_name': recipient.full_name or recipient.email,
            'first_name': recipient.first_name,
            'last_name': recipient.last_name,
            'email': recipient.email,
            'organization': recipient.organization,
            'position': recipient.position,
            'phone': recipient.phone,
            'location': recipient.location,
            
            # Tracking URLs
            'tracking_token': tracking_token,
            'tracking_pixel_url': f"{base_url}/email-marketing/track/open/{tracking_token}/",
            'click_tracking_url': f"{base_url}/email-marketing/track/click/{tracking_token}/",
            'unsubscribe_url': f"{base_url}/email-marketing/unsubscribe/{recipient.id}/",
            
            # Company information
            'company_name': 'Novustell Travel',
            'company_tagline': 'Think Convenience, Think Novustell',
            'company_website': 'https://www.novustelltravel.com',
            'company_email': 'Info@novustelltravel.com',
            'company_phone': '+254 721 115 572',
            'company_whatsapp': '+254 701 363 551',
            
            # Custom data from recipient
            **recipient.custom_data
        }
        
        return context_data
    
    def _render_email_template(self, template_content, context_data):
        """
        Render email template with context data
        """
        if not template_content:
            return ""

        try:
            template = Template(template_content)
            context = Context(context_data)
            return template.render(context)
        except Exception as e:
            logger.error(f"Error rendering email template: {e}")
            return template_content  # Return original content if rendering fails

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
