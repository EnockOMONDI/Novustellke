from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from django import forms
from django.contrib import messages
from .models import EmailTemplate, RecipientList, Recipient, EmailCampaign, EmailLog


class RecipientAdminForm(forms.ModelForm):
    """Custom form for Recipient admin with improved JSON field handling"""

    custom_data = forms.JSONField(
        required=False,
        initial=dict,
        help_text="""
        Optional JSON data for email personalization. Examples:<br>
        <code>{"school_type": "public", "student_count": 500}</code><br>
        <code>{"interests": ["model_un", "debate"], "budget_range": "medium"}</code><br>
        Leave empty if not needed.
        """,
        widget=forms.Textarea(attrs={
            'rows': 4,
            'cols': 60,
            'placeholder': '{\n  "key": "value",\n  "interests": ["item1", "item2"]\n}'
        })
    )

    class Meta:
        model = Recipient
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make custom_data field truly optional
        if 'custom_data' in self.fields:
            self.fields['custom_data'].required = False


@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'template_type', 'subject', 'created_by', 'created_at', 'is_active']
    list_filter = ['template_type', 'is_active', 'created_at']
    search_fields = ['name', 'subject', 'html_content']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'subject', 'template_type', 'is_active')
        }),
        ('Content', {
            'fields': ('html_content', 'text_content')
        }),
        ('Template Variables', {
            'fields': ('available_variables',),
            'description': 'JSON format: {"variable_name": "description"}'
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change:  # If creating new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


class RecipientInline(admin.TabularInline):
    model = Recipient.recipient_lists.through
    extra = 0
    verbose_name = "Recipient"
    verbose_name_plural = "Recipients"


@admin.register(RecipientList)
class RecipientListAdmin(admin.ModelAdmin):
    list_display = ['name', 'list_type', 'recipient_count', 'created_by', 'created_at', 'is_active']
    list_filter = ['list_type', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at', 'recipient_count']
    inlines = [RecipientInline]

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'list_type', 'is_active')
        }),
        ('Statistics', {
            'fields': ('recipient_count',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change:  # If creating new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Recipient)
class RecipientAdmin(admin.ModelAdmin):
    form = RecipientAdminForm
    list_display = ['email', 'full_name', 'organization', 'position', 'subscribed', 'is_active', 'created_at']
    list_filter = ['subscribed', 'is_active', 'created_at', 'recipient_lists']
    search_fields = ['email', 'first_name', 'last_name', 'organization', 'position']
    readonly_fields = ['created_at', 'updated_at']
    filter_horizontal = ['recipient_lists']

    fieldsets = (
        ('Contact Information', {
            'fields': ('email', 'first_name', 'last_name', 'organization', 'position')
        }),
        ('Additional Details', {
            'fields': ('phone', 'location')
        }),
        ('Personalization Data (Optional)', {
            'fields': ('custom_data',),
            'classes': ('collapse',),
            'description': 'Optional JSON data for email personalization. Can be left empty for basic recipients.'
        }),
        ('List Membership', {
            'fields': ('recipient_lists',)
        }),
        ('Subscription Status', {
            'fields': ('subscribed', 'unsubscribed_at', 'is_active')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['mark_subscribed', 'mark_unsubscribed', 'activate_recipients', 'deactivate_recipients']

    def mark_subscribed(self, request, queryset):
        queryset.update(subscribed=True, unsubscribed_at=None)
        self.message_user(request, f"{queryset.count()} recipients marked as subscribed.")
    mark_subscribed.short_description = "Mark selected recipients as subscribed"

    def mark_unsubscribed(self, request, queryset):
        queryset.update(subscribed=False, unsubscribed_at=timezone.now())
        self.message_user(request, f"{queryset.count()} recipients marked as unsubscribed.")
    mark_unsubscribed.short_description = "Mark selected recipients as unsubscribed"

    def activate_recipients(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f"{queryset.count()} recipients activated.")
    activate_recipients.short_description = "Activate selected recipients"

    def deactivate_recipients(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f"{queryset.count()} recipients deactivated.")
    deactivate_recipients.short_description = "Deactivate selected recipients"


class EmailLogInline(admin.TabularInline):
    model = EmailLog
    extra = 0
    readonly_fields = ['sent_to', 'status', 'sent_at', 'opened_at', 'clicked_at', 'error_message']
    fields = ['recipient', 'sent_to', 'status', 'sent_at', 'opened_at', 'clicked_at']
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(EmailCampaign)
class EmailCampaignAdmin(admin.ModelAdmin):
    list_display = ['name', 'status', 'email_template', 'total_recipients', 'emails_sent', 'emails_opened', 'scheduled_at', 'created_by']
    list_filter = ['status', 'created_at', 'scheduled_at', 'email_template__template_type']
    search_fields = ['name', 'description', 'email_template__name']
    readonly_fields = ['created_at', 'updated_at', 'sent_at', 'total_recipients', 'emails_sent', 'emails_opened', 'emails_clicked', 'celery_task_id', 'task_status', 'emails_sent_count', 'emails_failed_count', 'started_at', 'completed_at']
    filter_horizontal = ['recipient_lists']
    inlines = [EmailLogInline]

    fieldsets = (
        ('Campaign Information', {
            'fields': ('name', 'description', 'status')
        }),
        ('Email Configuration', {
            'fields': ('email_template', 'recipient_lists')
        }),
        ('Scheduling', {
            'fields': ('send_immediately', 'scheduled_at', 'sent_at')
        }),
        ('Tracking Settings', {
            'fields': ('track_opens', 'track_clicks')
        }),
        ('Statistics', {
            'fields': ('total_recipients', 'emails_sent', 'emails_opened', 'emails_clicked'),
            'classes': ('collapse',)
        }),
        ('Task Management', {
            'fields': ('celery_task_id', 'task_status', 'emails_sent_count', 'emails_failed_count', 'started_at', 'completed_at'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change:  # If creating new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    actions = ['send_campaign', 'pause_campaign', 'cancel_campaign']

    def send_campaign(self, request, queryset):
        """Send selected campaigns using Celery background tasks"""
        from .tasks import send_campaign_emails_task

        sent_count = 0

        for campaign in queryset:
            if campaign.status == 'draft':
                try:
                    # Start background task
                    task = send_campaign_emails_task.delay(campaign.id)

                    # Update campaign with task info
                    campaign.status = 'scheduled'
                    campaign.celery_task_id = task.id
                    campaign.task_status = 'queued'
                    campaign.scheduled_at = timezone.now()
                    campaign.save()

                    sent_count += 1

                    self.message_user(
                        request,
                        f"Campaign '{campaign.name}' queued for sending. Task ID: {task.id}",
                        level=messages.SUCCESS
                    )

                except Exception as e:
                    self.message_user(
                        request,
                        f"Failed to queue campaign '{campaign.name}': {e}",
                        level=messages.ERROR
                    )
            else:
                self.message_user(
                    request,
                    f"Campaign '{campaign.name}' is not in draft status (current: {campaign.get_status_display()})",
                    level=messages.WARNING
                )

        if sent_count > 0:
            self.message_user(
                request,
                f"Successfully queued {sent_count} campaign(s) for background sending",
                level=messages.SUCCESS
            )
    send_campaign.short_description = "Send selected campaigns (background processing)"

    def pause_campaign(self, request, queryset):
        queryset.update(status='paused')
        self.message_user(request, f"{queryset.count()} campaigns paused.")
    pause_campaign.short_description = "Pause selected campaigns"

    def cancel_campaign(self, request, queryset):
        queryset.update(status='cancelled')
        self.message_user(request, f"{queryset.count()} campaigns cancelled.")
    cancel_campaign.short_description = "Cancel selected campaigns"


@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = ['campaign', 'sent_to', 'status', 'sent_at', 'opened_at', 'clicked_at']
    list_filter = ['status', 'sent_at', 'opened_at', 'clicked_at', 'campaign']
    search_fields = ['sent_to', 'subject', 'campaign__name', 'recipient__organization']
    readonly_fields = ['created_at', 'updated_at', 'tracking_token']

    fieldsets = (
        ('Email Information', {
            'fields': ('campaign', 'recipient', 'subject', 'sent_to')
        }),
        ('Status', {
            'fields': ('status', 'sent_at', 'error_message')
        }),
        ('Tracking', {
            'fields': ('tracking_token', 'opened_at', 'clicked_at')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def has_add_permission(self, request):
        return False  # Email logs are created automatically

    def has_delete_permission(self, request, obj=None):
        return False  # Preserve email logs for analytics
