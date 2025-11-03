from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import EmailValidator


class EmailTemplate(models.Model):
    """Model for storing email marketing templates"""

    TEMPLATE_TYPES = [
        ('educational', 'Educational Institutions'),
        ('corporate', 'Corporate Clients'),
        ('ngo', 'NGO Organizations'),
        ('general', 'General Marketing'),
    ]

    name = models.CharField(max_length=200, help_text="Template name for internal reference")
    subject = models.CharField(max_length=300, help_text="Email subject line")
    template_type = models.CharField(max_length=20, choices=TEMPLATE_TYPES, default='general')
    html_content = models.TextField(help_text="HTML email content")
    text_content = models.TextField(blank=True, help_text="Plain text version (optional)")

    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='email_templates')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    # Template variables for personalization
    available_variables = models.JSONField(
        default=dict,
        help_text="Available template variables for personalization (JSON format)"
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Email Template"
        verbose_name_plural = "Email Templates"

    def __str__(self):
        return f"{self.name} ({self.get_template_type_display()})"


class RecipientList(models.Model):
    """Model for managing email recipient lists"""

    LIST_TYPES = [
        ('schools', 'Educational Institutions'),
        ('universities', 'Universities'),
        ('corporate', 'Corporate Clients'),
        ('ngo', 'NGO Organizations'),
        ('custom', 'Custom List'),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    list_type = models.CharField(max_length=20, choices=LIST_TYPES, default='custom')

    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipient_lists')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Recipient List"
        verbose_name_plural = "Recipient Lists"

    def __str__(self):
        return f"{self.name} ({self.recipients.count()} recipients)"

    @property
    def recipient_count(self):
        return self.recipients.filter(is_active=True).count()


class Recipient(models.Model):
    """Model for individual email recipients"""

    email = models.EmailField(validators=[EmailValidator()])
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    organization = models.CharField(max_length=200, blank=True)
    position = models.CharField(max_length=100, blank=True)

    # Contact details
    phone = models.CharField(max_length=20, blank=True)
    location = models.CharField(max_length=100, blank=True)

    # Relationship to lists
    recipient_lists = models.ManyToManyField(RecipientList, related_name='recipients')

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    # Email preferences
    subscribed = models.BooleanField(default=True)
    unsubscribed_at = models.DateTimeField(null=True, blank=True)

    # Additional data for personalization
    custom_data = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional data for email personalization (JSON format). Leave empty if not needed."
    )

    class Meta:
        ordering = ['organization', 'last_name', 'first_name']
        unique_together = ['email']
        verbose_name = "Recipient"
        verbose_name_plural = "Recipients"

    def __str__(self):
        if self.first_name and self.last_name:
            name = f"{self.first_name} {self.last_name}"
            if self.organization:
                return f"{name} ({self.organization})"
            return name
        elif self.organization:
            return f"{self.email} ({self.organization})"
        return self.email

    @property
    def full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        return ""


class EmailCampaign(models.Model):
    """Model for managing email marketing campaigns"""

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('sending', 'Sending'),
        ('sent', 'Sent'),
        ('paused', 'Paused'),
        ('cancelled', 'Cancelled'),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    # Campaign configuration
    email_template = models.ForeignKey(EmailTemplate, on_delete=models.CASCADE, related_name='campaigns')
    recipient_lists = models.ManyToManyField(RecipientList, related_name='campaigns')

    # Scheduling
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    scheduled_at = models.DateTimeField(null=True, blank=True, help_text="When to send the campaign")
    sent_at = models.DateTimeField(null=True, blank=True)

    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='email_campaigns')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Campaign settings
    send_immediately = models.BooleanField(default=False)
    track_opens = models.BooleanField(default=True)
    track_clicks = models.BooleanField(default=True)

    # Task management fields for Celery background processing
    celery_task_id = models.CharField(max_length=255, blank=True, null=True, help_text="Celery task ID for background processing")
    task_status = models.CharField(max_length=20, default='pending', help_text="Status of the background task")
    emails_sent_count = models.IntegerField(default=0, help_text="Number of emails successfully sent")
    emails_failed_count = models.IntegerField(default=0, help_text="Number of emails that failed to send")
    started_at = models.DateTimeField(null=True, blank=True, help_text="When the campaign started sending")
    completed_at = models.DateTimeField(null=True, blank=True, help_text="When the campaign finished sending")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Email Campaign"
        verbose_name_plural = "Email Campaigns"

    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"

    @property
    def total_recipients(self):
        """Calculate total unique recipients across all lists"""
        recipient_emails = set()
        for recipient_list in self.recipient_lists.all():
            for recipient in recipient_list.recipients.filter(is_active=True, subscribed=True):
                recipient_emails.add(recipient.email)
        return len(recipient_emails)

    @property
    def emails_sent(self):
        return self.email_logs.filter(status='sent').count()

    @property
    def emails_opened(self):
        return self.email_logs.filter(opened_at__isnull=False).count()

    @property
    def emails_clicked(self):
        return self.email_logs.filter(clicked_at__isnull=False).count()

    def save(self, *args, **kwargs):
        """Custom save method"""
        # Just save normally - send_immediately logic is handled in admin
        super().save(*args, **kwargs)


class EmailLog(models.Model):
    """Model for tracking individual email sends and interactions"""

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('bounced', 'Bounced'),
    ]

    campaign = models.ForeignKey(EmailCampaign, on_delete=models.CASCADE, related_name='email_logs')
    recipient = models.ForeignKey(Recipient, on_delete=models.CASCADE, related_name='email_logs')

    # Email details
    subject = models.CharField(max_length=300)
    sent_to = models.EmailField()

    # Status tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    sent_at = models.DateTimeField(null=True, blank=True)
    opened_at = models.DateTimeField(null=True, blank=True)
    clicked_at = models.DateTimeField(null=True, blank=True)

    # Error tracking
    error_message = models.TextField(blank=True)

    # Tracking tokens
    tracking_token = models.CharField(max_length=100, unique=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Email Log"
        verbose_name_plural = "Email Logs"
        unique_together = ['campaign', 'recipient']

    def __str__(self):
        return f"{self.campaign.name} -> {self.sent_to} ({self.get_status_display()})"
