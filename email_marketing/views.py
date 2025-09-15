from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
import uuid
import logging

from .models import EmailCampaign, EmailLog, Recipient

logger = logging.getLogger(__name__)


@require_GET
def email_tracking_pixel(request, tracking_token):
    """
    Tracking pixel for email opens
    """
    try:
        email_log = get_object_or_404(EmailLog, tracking_token=tracking_token)
        if not email_log.opened_at:
            email_log.opened_at = timezone.now()
            email_log.save()
            logger.info(f"Email opened: {email_log.campaign.name} -> {email_log.sent_to}")
    except Exception as e:
        logger.error(f"Error tracking email open: {e}")

    # Return 1x1 transparent pixel
    pixel_data = b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\x00\x00\x00\x21\xF9\x04\x01\x00\x00\x00\x00\x2C\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x04\x01\x00\x3B'
    return HttpResponse(pixel_data, content_type='image/gif')


@require_GET
def email_click_tracking(request, tracking_token):
    """
    Click tracking for email links
    """
    try:
        email_log = get_object_or_404(EmailLog, tracking_token=tracking_token)
        if not email_log.clicked_at:
            email_log.clicked_at = timezone.now()
            email_log.save()
            logger.info(f"Email clicked: {email_log.campaign.name} -> {email_log.sent_to}")

        # Redirect to the intended URL (you can pass this as a parameter)
        redirect_url = request.GET.get('url', 'https://www.novustelltravel.com')
        return HttpResponse(f'<script>window.location.href="{redirect_url}";</script>')
    except Exception as e:
        logger.error(f"Error tracking email click: {e}")
        return HttpResponse('<script>window.location.href="https://www.novustelltravel.com";</script>')


def unsubscribe_recipient(request, recipient_id):
    """
    Unsubscribe recipient from email marketing
    """
    try:
        recipient = get_object_or_404(Recipient, id=recipient_id)

        if request.method == 'POST':
            recipient.subscribed = False
            recipient.unsubscribed_at = timezone.now()
            recipient.save()

            return render(request, 'email_marketing/unsubscribe_success.html', {
                'recipient': recipient
            })

        return render(request, 'email_marketing/unsubscribe_confirm.html', {
            'recipient': recipient
        })
    except Exception as e:
        logger.error(f"Error unsubscribing recipient: {e}")
        return render(request, 'email_marketing/unsubscribe_error.html')


def email_preview(request, template_id):
    """
    Preview email template with sample data
    """
    from .models import EmailTemplate

    try:
        template = get_object_or_404(EmailTemplate, id=template_id)

        # Sample data for preview
        sample_data = {
            'recipient_name': 'John Doe',
            'organization': 'Sample School',
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@sampleschool.edu',
            'tracking_token': 'sample-tracking-token',
            'unsubscribe_url': '#',
        }

        # Render the template with sample data
        from django.template import Template, Context
        html_template = Template(template.html_content)
        rendered_html = html_template.render(Context(sample_data))

        return HttpResponse(rendered_html)
    except Exception as e:
        logger.error(f"Error previewing email template: {e}")
        return HttpResponse(f"Error previewing template: {e}")


@csrf_exempt
def campaign_analytics(request, campaign_id):
    """
    Get campaign analytics data
    """
    try:
        campaign = get_object_or_404(EmailCampaign, id=campaign_id)

        analytics_data = {
            'campaign_name': campaign.name,
            'status': campaign.status,
            'total_recipients': campaign.total_recipients,
            'emails_sent': campaign.emails_sent,
            'emails_opened': campaign.emails_opened,
            'emails_clicked': campaign.emails_clicked,
            'open_rate': (campaign.emails_opened / campaign.emails_sent * 100) if campaign.emails_sent > 0 else 0,
            'click_rate': (campaign.emails_clicked / campaign.emails_sent * 100) if campaign.emails_sent > 0 else 0,
            'sent_at': campaign.sent_at.isoformat() if campaign.sent_at else None,
            'created_at': campaign.created_at.isoformat(),
        }

        return JsonResponse(analytics_data)
    except Exception as e:
        logger.error(f"Error getting campaign analytics: {e}")
        return JsonResponse({'error': str(e)}, status=500)
