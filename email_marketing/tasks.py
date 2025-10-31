"""
Celery tasks for email marketing campaigns
"""

import logging
import uuid
from celery import shared_task
from django.utils import timezone
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

# Set up logging
logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def send_campaign_emails_task(self, campaign_id):
    """
    Send all emails for a campaign asynchronously
    
    Args:
        campaign_id (int): ID of the EmailCampaign to send
        
    Returns:
        dict: Results summary with counts and status
    """
    try:
        from email_marketing.models import EmailCampaign, EmailLog
        from email_marketing.services import EmailMarketingService
        
        # Get the campaign
        try:
            campaign = EmailCampaign.objects.get(id=campaign_id)
        except ObjectDoesNotExist:
            logger.error(f"Campaign {campaign_id} not found")
            return {'error': f'Campaign {campaign_id} not found'}
        
        # Update campaign status
        campaign.status = 'sending'
        campaign.celery_task_id = self.request.id
        campaign.started_at = timezone.now()
        campaign.save()
        
        logger.info(f"Starting campaign {campaign.name} (ID: {campaign_id})")
        
        # Initialize service
        service = EmailMarketingService()
        
        # Get all recipients for this campaign
        recipients = []
        for recipient_list in campaign.recipient_lists.all():
            recipients.extend(recipient_list.recipients.filter(subscribed=True, is_active=True))
        
        # Remove duplicates
        unique_recipients = list(set(recipients))
        total_recipients = len(unique_recipients)
        
        logger.info(f"Sending to {total_recipients} unique recipients")
        
        # Track results
        sent_count = 0
        failed_count = 0
        
        # Send emails to each recipient
        for recipient in unique_recipients:
            try:
                # Create individual task for each email
                result = send_single_email_task.delay(campaign_id, recipient.id)
                sent_count += 1
                
                # Update progress
                campaign.emails_sent_count = sent_count
                campaign.save()
                
            except Exception as e:
                logger.error(f"Failed to queue email for {recipient.email}: {e}")
                failed_count += 1
                campaign.emails_failed_count = failed_count
                campaign.save()
        
        # Update campaign status
        campaign.status = 'sent'
        campaign.completed_at = timezone.now()
        campaign.save()
        
        result = {
            'campaign_id': campaign_id,
            'campaign_name': campaign.name,
            'total_recipients': total_recipients,
            'emails_queued': sent_count,
            'emails_failed': failed_count,
            'status': 'completed'
        }
        
        logger.info(f"Campaign {campaign.name} completed: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Campaign {campaign_id} failed: {e}")
        
        # Update campaign status on failure
        try:
            campaign = EmailCampaign.objects.get(id=campaign_id)
            campaign.status = 'failed'
            campaign.completed_at = timezone.now()
            campaign.save()
        except:
            pass
        
        # Retry the task
        if self.request.retries < self.max_retries:
            logger.info(f"Retrying campaign {campaign_id} (attempt {self.request.retries + 1})")
            raise self.retry(countdown=60 * (self.request.retries + 1))
        
        return {'error': str(e), 'campaign_id': campaign_id}

@shared_task(bind=True, max_retries=3)
def send_single_email_task(self, campaign_id, recipient_id):
    """
    Send a single email with retry logic
    
    Args:
        campaign_id (int): ID of the EmailCampaign
        recipient_id (int): ID of the Recipient
        
    Returns:
        dict: Result of the email sending
    """
    try:
        from email_marketing.models import EmailCampaign, Recipient, EmailLog
        from email_marketing.services import EmailMarketingService
        
        # Get campaign and recipient
        campaign = EmailCampaign.objects.get(id=campaign_id)
        recipient = Recipient.objects.get(id=recipient_id)
        
        # Check if email already sent
        existing_log = EmailLog.objects.filter(
            campaign=campaign,
            recipient=recipient,
            status='sent'
        ).first()
        
        if existing_log:
            logger.info(f"Email already sent to {recipient.email} for campaign {campaign.name}")
            return {'status': 'already_sent', 'recipient': recipient.email}
        
        # Initialize service
        service = EmailMarketingService()
        
        # Send the email
        success = service._send_email_to_recipient(campaign, recipient)
        
        if success:
            logger.info(f"Email sent successfully to {recipient.email}")
            return {
                'status': 'sent',
                'recipient': recipient.email,
                'campaign': campaign.name
            }
        else:
            logger.error(f"Failed to send email to {recipient.email}")
            return {
                'status': 'failed',
                'recipient': recipient.email,
                'campaign': campaign.name
            }
            
    except Exception as e:
        logger.error(f"Error sending email to recipient {recipient_id}: {e}")
        
        # Retry the task
        if self.request.retries < self.max_retries:
            logger.info(f"Retrying email to recipient {recipient_id} (attempt {self.request.retries + 1})")
            raise self.retry(countdown=30 * (self.request.retries + 1))
        
        return {
            'status': 'failed',
            'error': str(e),
            'recipient_id': recipient_id,
            'campaign_id': campaign_id
        }

@shared_task
def process_scheduled_campaigns_task():
    """
    Check for scheduled campaigns and execute them
    
    Returns:
        dict: Summary of processed campaigns
    """
    try:
        from email_marketing.models import EmailCampaign
        
        # Get campaigns scheduled for now or earlier
        now = timezone.now()
        scheduled_campaigns = EmailCampaign.objects.filter(
            status='scheduled',
            scheduled_at__lte=now
        )
        
        processed_count = 0
        results = []
        
        for campaign in scheduled_campaigns:
            logger.info(f"Processing scheduled campaign: {campaign.name}")
            
            # Start the campaign
            result = send_campaign_emails_task.delay(campaign.id)
            
            results.append({
                'campaign_id': campaign.id,
                'campaign_name': campaign.name,
                'task_id': result.id
            })
            
            processed_count += 1
        
        logger.info(f"Processed {processed_count} scheduled campaigns")
        
        return {
            'processed_count': processed_count,
            'campaigns': results
        }
        
    except Exception as e:
        logger.error(f"Error processing scheduled campaigns: {e}")
        return {'error': str(e)}

@shared_task
def cleanup_old_email_logs_task(days_old=30):
    """
    Clean up old email logs to save database space
    
    Args:
        days_old (int): Number of days old logs to keep
        
    Returns:
        dict: Summary of cleanup operation
    """
    try:
        from email_marketing.models import EmailLog
        from datetime import timedelta
        
        cutoff_date = timezone.now() - timedelta(days=days_old)
        
        # Delete old logs
        deleted_count, _ = EmailLog.objects.filter(
            sent_at__lt=cutoff_date
        ).delete()
        
        logger.info(f"Cleaned up {deleted_count} old email logs")
        
        return {
            'deleted_count': deleted_count,
            'cutoff_date': cutoff_date.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error cleaning up email logs: {e}")
        return {'error': str(e)}

@shared_task
def update_email_tracking_task(tracking_token, event_type):
    """
    Update email tracking information
    
    Args:
        tracking_token (str): Unique tracking token
        event_type (str): Type of event ('open', 'click')
        
    Returns:
        dict: Result of tracking update
    """
    try:
        from email_marketing.models import EmailLog
        
        # Find the email log
        email_log = EmailLog.objects.filter(tracking_token=tracking_token).first()
        
        if not email_log:
            logger.warning(f"Email log not found for tracking token: {tracking_token}")
            return {'error': 'Email log not found'}
        
        # Update tracking information
        now = timezone.now()
        
        if event_type == 'open' and not email_log.opened_at:
            email_log.opened_at = now
            email_log.save()
            logger.info(f"Email opened: {email_log.recipient.email}")
            
        elif event_type == 'click' and not email_log.clicked_at:
            email_log.clicked_at = now
            email_log.save()
            logger.info(f"Email clicked: {email_log.recipient.email}")
        
        return {
            'status': 'updated',
            'event_type': event_type,
            'recipient': email_log.recipient.email
        }
        
    except Exception as e:
        logger.error(f"Error updating email tracking: {e}")
        return {'error': str(e)}
