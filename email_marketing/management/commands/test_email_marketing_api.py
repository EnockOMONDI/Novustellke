"""
Django management command to test the Resend email marketing integration.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from email_marketing.models import EmailTemplate, RecipientList, Recipient, EmailCampaign
from email_marketing.services import EmailMarketingService
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Test the Resend email marketing integration'

    def add_arguments(self, parser):
        parser.add_argument(
            '--create-test-data',
            action='store_true',
            help='Create test data (template, recipients, campaign)',
        )
        parser.add_argument(
            '--send-test-campaign',
            type=int,
            help='Send test campaign by ID',
        )
        parser.add_argument(
            '--test-email',
            type=str,
            default='djseanizellkenya@gmail.com',
            help='Test email address for campaign',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🚀 Testing Resend Email Marketing Integration')
        )

        if options['create_test_data']:
            self.create_test_data(options['test_email'])

        if options['send_test_campaign']:
            self.send_test_campaign(options['send_test_campaign'])

        if not options['create_test_data'] and not options['send_test_campaign']:
            self.show_usage()

    def create_test_data(self, test_email):
        """Create test data for email marketing API testing"""
        self.stdout.write('📝 Creating test data...')

        # Get or create admin user
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@novustelltravel.com',
                'is_staff': True,
                'is_superuser': True
            }
        )

        # Create test email template
        template, created = EmailTemplate.objects.get_or_create(
            name='Email Marketing API Test Template',
            defaults={
                'subject': 'Test Email from Novustell Travel - {{recipient_name}}',
                'template_type': 'general',
                'html_content': '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{{subject}}</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <h1 style="color: #0f238d;">Hello {{recipient_name}}!</h1>
        
        <p>This is a test email from the <strong>Resend batch email</strong> integration.</p>
        
        <div style="background: #f8f3fc; padding: 15px; border-radius: 5px; margin: 20px 0;">
            <h3 style="color: #ff9d00; margin-top: 0;">Email Marketing API Features:</h3>
            <ul>
                <li>✅ Bulk email sending</li>
                <li>✅ Personalization with recipient data</li>
                <li>✅ Professional email templates</li>
                <li>✅ Better deliverability</li>
                <li>✅ No Celery infrastructure needed</li>
            </ul>
        </div>
        
        <p><strong>Recipient Details:</strong></p>
        <ul>
            <li>Name: {{first_name}} {{last_name}}</li>
            <li>Email: {{email}}</li>
            <li>Organization: {{organization}}</li>
        </ul>
        
        <div style="background: #0f238d; color: white; padding: 20px; border-radius: 5px; text-align: center; margin: 30px 0;">
            <h2 style="margin: 0; color: white;">{{company_name}}</h2>
            <p style="margin: 5px 0; color: #ff9d00;">{{company_tagline}}</p>
            <p style="margin: 0;">📞 {{company_phone}} | 📱 {{company_whatsapp}}</p>
        </div>
        
        <p style="font-size: 12px; color: #666;">
            If you no longer wish to receive these emails, you can 
            <a href="{{unsubscribe_url}}" style="color: #0f238d;">unsubscribe here</a>.
        </p>
    </div>
</body>
</html>
                ''',
                'text_content': '''
Hello {{recipient_name}}!

This is a test email from the Resend batch email integration.

Email Marketing API Features:
- Bulk email sending
- Personalization with recipient data  
- Professional email templates
- Better deliverability
- No Celery infrastructure needed

Recipient Details:
- Name: {{first_name}} {{last_name}}
- Email: {{email}}
- Organization: {{organization}}

{{company_name}}
{{company_tagline}}
Phone: {{company_phone}} | WhatsApp: {{company_whatsapp}}

Unsubscribe: {{unsubscribe_url}}
                ''',
                'created_by': admin_user,
                'available_variables': {
                    'recipient_name': 'Full name of recipient',
                    'first_name': 'First name',
                    'last_name': 'Last name',
                    'email': 'Email address',
                    'organization': 'Organization name',
                    'company_name': 'Novustell Travel',
                    'company_tagline': 'Think Convenience, Think Novustell',
                    'company_phone': 'Company phone number',
                    'company_whatsapp': 'Company WhatsApp number',
                    'unsubscribe_url': 'Unsubscribe link'
                }
            }
        )

        # Create test recipient list
        recipient_list, created = RecipientList.objects.get_or_create(
            name='Email Marketing API Test List',
            defaults={
                'description': 'Test recipient list for Email Marketing API',
                'list_type': 'custom',
                'created_by': admin_user
            }
        )

        # Create test recipient
        recipient, created = Recipient.objects.get_or_create(
            email=test_email,
            defaults={
                'first_name': 'Test',
                'last_name': 'User',
                'organization': 'Novustell Travel Testing',
                'position': 'Email Marketing Tester',
                'location': 'Nairobi, Kenya',
                'custom_data': {
                    'test_mode': True,
                    'api_version': 'Email Marketing API'
                }
            }
        )
        recipient.recipient_lists.add(recipient_list)

        # Create test campaign
        campaign, created = EmailCampaign.objects.get_or_create(
            name='Email Marketing API Test Campaign',
            defaults={
                'description': 'Test campaign for the Resend batch email integration',
                'email_template': template,
                'status': 'draft',
                'created_by': admin_user,
                'track_opens': True,
                'track_clicks': True
            }
        )
        campaign.recipient_lists.add(recipient_list)

        self.stdout.write(
            self.style.SUCCESS(f'✅ Test data created successfully!')
        )
        self.stdout.write(f'   📧 Template: {template.name} (ID: {template.id})')
        self.stdout.write(f'   📋 Recipient List: {recipient_list.name} (ID: {recipient_list.id})')
        self.stdout.write(f'   👤 Recipient: {recipient.email}')
        self.stdout.write(f'   🚀 Campaign: {campaign.name} (ID: {campaign.id})')
        self.stdout.write('')
        self.stdout.write(f'To send the test campaign, run:')
        self.stdout.write(f'python manage.py test_email_marketing_api --send-test-campaign {campaign.id}')

    def send_test_campaign(self, campaign_id):
        """Send a test campaign using the Email Marketing API"""
        self.stdout.write(f'📤 Sending test campaign ID: {campaign_id}')

        try:
            campaign = EmailCampaign.objects.get(id=campaign_id)
            self.stdout.write(f'   Campaign: {campaign.name}')
            self.stdout.write(f'   Recipients: {campaign.total_recipients}')
            self.stdout.write(f'   Status: {campaign.get_status_display()}')

            if campaign.status != 'draft':
                self.stdout.write(
                    self.style.WARNING(f'⚠️  Campaign is not in draft status: {campaign.get_status_display()}')
                )
                return

            # Send via Email Marketing API
            service = EmailMarketingService()
            success = service.send_campaign(campaign_id)

            if success:
                self.stdout.write(
                    self.style.SUCCESS('✅ Campaign sent successfully via Email Marketing API!')
                )
                
                # Refresh campaign from database
                campaign.refresh_from_db()
                self.stdout.write(f'   Status: {campaign.get_status_display()}')
                self.stdout.write(f'   Emails sent: {campaign.emails_sent_count}')
                self.stdout.write(f'   Started at: {campaign.started_at}')
                self.stdout.write(f'   Completed at: {campaign.completed_at}')
            else:
                self.stdout.write(
                    self.style.ERROR('❌ Failed to send campaign - check logs for details')
                )

        except EmailCampaign.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'❌ Campaign with ID {campaign_id} not found')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error sending campaign: {e}')
            )

    def show_usage(self):
        """Show usage instructions"""
        self.stdout.write('')
        self.stdout.write(self.style.WARNING('Usage Examples:'))
        self.stdout.write('')
        self.stdout.write('1. Create test data:')
        self.stdout.write('   python manage.py test_email_marketing_api --create-test-data')
        self.stdout.write('')
        self.stdout.write('2. Create test data with custom email:')
        self.stdout.write('   python manage.py test_email_marketing_api --create-test-data --test-email your@email.com')
        self.stdout.write('')
        self.stdout.write('3. Send test campaign:')
        self.stdout.write('   python manage.py test_email_marketing_api --send-test-campaign 1')
        self.stdout.write('')
