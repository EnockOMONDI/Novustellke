"""
Django management command to provide complete email template inventory
"""

from django.core.management.base import BaseCommand
from django.db.models import Count
from email_marketing.models import EmailTemplate, EmailCampaign
from django.utils import timezone


class Command(BaseCommand):
    help = 'Provide complete inventory of email templates in the system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--detailed',
            action='store_true',
            help='Show detailed information for each template',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('📊 EMAIL TEMPLATE INVENTORY REPORT'))
        self.stdout.write('=' * 60)
        
        # Get all templates
        templates = EmailTemplate.objects.all().order_by('-created_at')
        
        # Summary statistics
        total_templates = templates.count()
        active_templates = templates.filter(is_active=True).count()
        inactive_templates = templates.filter(is_active=False).count()
        
        # Breakdown by template type
        type_breakdown = templates.values('template_type').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Display summary
        self.stdout.write(f'\n📈 SUMMARY STATISTICS:')
        self.stdout.write(f'   Total Templates: {total_templates}')
        self.stdout.write(f'   Active Templates: {active_templates}')
        self.stdout.write(f'   Inactive Templates: {inactive_templates}')
        
        # Display breakdown by type
        self.stdout.write(f'\n📋 BREAKDOWN BY TYPE:')
        for item in type_breakdown:
            template_type = item['template_type']
            count = item['count']
            # Get display name for template type
            display_name = dict(EmailTemplate.TEMPLATE_TYPES).get(template_type, template_type)
            self.stdout.write(f'   {display_name}: {count} templates')
        
        # Display all templates
        self.stdout.write(f'\n📧 ALL EMAIL TEMPLATES:')
        self.stdout.write('-' * 60)
        
        if not templates.exists():
            self.stdout.write(self.style.WARNING('   No email templates found in the system.'))
            return
        
        for i, template in enumerate(templates, 1):
            status_icon = "✅" if template.is_active else "❌"
            type_display = template.get_template_type_display()
            
            self.stdout.write(f'\n{i}. {status_icon} {template.name}')
            self.stdout.write(f'   ID: {template.id}')
            self.stdout.write(f'   Subject: {template.subject}')
            self.stdout.write(f'   Type: {type_display}')
            self.stdout.write(f'   Status: {"Active" if template.is_active else "Inactive"}')
            self.stdout.write(f'   Created: {template.created_at.strftime("%Y-%m-%d %H:%M")}')
            self.stdout.write(f'   Created by: {template.created_by.username}')
            
            # Get campaign count for this template
            campaign_count = EmailCampaign.objects.filter(email_template=template).count()
            self.stdout.write(f'   Campaigns using this template: {campaign_count}')
            
            if options['detailed']:
                # Show available variables
                if template.available_variables:
                    self.stdout.write(f'   Available Variables:')
                    for var, desc in template.available_variables.items():
                        self.stdout.write(f'     • {{ {var} }} - {desc}')
                
                # Show recent campaigns
                recent_campaigns = EmailCampaign.objects.filter(
                    email_template=template
                ).order_by('-created_at')[:3]
                
                if recent_campaigns.exists():
                    self.stdout.write(f'   Recent Campaigns:')
                    for campaign in recent_campaigns:
                        status_icon = "📤" if campaign.status == 'sent' else "📝"
                        self.stdout.write(f'     {status_icon} {campaign.name} ({campaign.get_status_display()})')
        
        # Display usage statistics
        self.stdout.write(f'\n📊 USAGE STATISTICS:')
        self.stdout.write('-' * 60)
        
        # Templates with campaigns
        templates_with_campaigns = templates.annotate(
            campaign_count=Count('campaigns')
        ).filter(campaign_count__gt=0).order_by('-campaign_count')
        
        if templates_with_campaigns.exists():
            self.stdout.write(f'\n🎯 MOST USED TEMPLATES:')
            for template in templates_with_campaigns[:5]:  # Top 5
                self.stdout.write(f'   • {template.name}: {template.campaign_count} campaigns')
        
        # Templates never used
        unused_templates = templates.annotate(
            campaign_count=Count('campaigns')
        ).filter(campaign_count=0)
        
        if unused_templates.exists():
            self.stdout.write(f'\n⚠️  UNUSED TEMPLATES ({unused_templates.count()}):')
            for template in unused_templates:
                self.stdout.write(f'   • {template.name} (Created: {template.created_at.strftime("%Y-%m-%d")})')
        
        # Recent activity
        recent_templates = templates.filter(
            created_at__gte=timezone.now() - timezone.timedelta(days=30)
        ).order_by('-created_at')
        
        if recent_templates.exists():
            self.stdout.write(f'\n🆕 RECENTLY CREATED (Last 30 days):')
            for template in recent_templates:
                days_ago = (timezone.now() - template.created_at).days
                self.stdout.write(f'   • {template.name} ({days_ago} days ago)')
        
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write(self.style.SUCCESS('📊 Email Template Inventory Report Complete'))
        
        # Recommendations
        self.stdout.write(f'\n💡 RECOMMENDATIONS:')
        if inactive_templates > 0:
            self.stdout.write(f'   • Review {inactive_templates} inactive templates - consider archiving or reactivating')
        if unused_templates.exists():
            self.stdout.write(f'   • Consider testing {unused_templates.count()} unused templates in campaigns')
        if total_templates < 5:
            self.stdout.write(f'   • Consider creating more template variations for different audiences')
        
        self.stdout.write(f'\n🔗 QUICK ACTIONS:')
        self.stdout.write(f'   • View templates in admin: /admin/email_marketing/emailtemplate/')
        self.stdout.write(f'   • Create new campaign: /admin/email_marketing/emailcampaign/add/')
        self.stdout.write(f'   • View campaign reports: /admin/email_marketing/emailcampaign/')
