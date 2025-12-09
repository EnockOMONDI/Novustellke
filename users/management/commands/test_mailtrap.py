"""
Django management command to test Mailtrap email integration
Usage: python manage.py test_mailtrap
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from users.tasks import send_email_via_mailtrap
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Test Mailtrap email integration by sending a test email'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            default='enock@novustelltravel.com',
            help='Email address to send test email to (default: enock@novustelltravel.com)',
        )

    def handle(self, *args, **options):
        recipient_email = options['email']
        
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS('🧪 MAILTRAP EMAIL INTEGRATION TEST'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write('')

        # Step 1: Validate Configuration
        self.stdout.write(self.style.WARNING('📋 Step 1: Validating Mailtrap Configuration...'))
        self.stdout.write('')
        
        config_valid = self.validate_configuration()
        
        if not config_valid:
            self.stdout.write(self.style.ERROR('❌ Configuration validation failed. Please check your settings.'))
            return

        self.stdout.write('')
        
        # Step 2: Send Test Email
        self.stdout.write(self.style.WARNING('📧 Step 2: Sending Test Email...'))
        self.stdout.write('')
        
        success = self.send_test_email(recipient_email)
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 70))
        
        if success:
            self.stdout.write(self.style.SUCCESS('✅ TEST COMPLETED SUCCESSFULLY!'))
            self.stdout.write(self.style.SUCCESS(f'✅ Test email sent to: {recipient_email}'))
            self.stdout.write(self.style.SUCCESS('✅ Check the recipient inbox for the test email'))
        else:
            self.stdout.write(self.style.ERROR('❌ TEST FAILED!'))
            self.stdout.write(self.style.ERROR('❌ Email was not sent successfully'))
            self.stdout.write(self.style.ERROR('❌ Check the error logs above for details'))
        
        self.stdout.write(self.style.SUCCESS('=' * 70))

    def validate_configuration(self):
        """Validate Mailtrap configuration settings"""
        all_valid = True
        
        # Check MAILTRAP_API_TOKEN
        api_token = getattr(settings, 'MAILTRAP_API_TOKEN', None)
        if not api_token:
            self.stdout.write(self.style.ERROR('   ❌ MAILTRAP_API_TOKEN not configured'))
            all_valid = False
        elif api_token == 'your-token-here':
            self.stdout.write(self.style.ERROR('   ❌ MAILTRAP_API_TOKEN is set to default value'))
            all_valid = False
        else:
            masked_token = f"{api_token[:8]}...{api_token[-4:]}" if len(api_token) > 12 else "***"
            self.stdout.write(self.style.SUCCESS(f'   ✅ MAILTRAP_API_TOKEN: {masked_token}'))
        
        # Check DEFAULT_FROM_EMAIL
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', None)
        if not from_email:
            self.stdout.write(self.style.ERROR('   ❌ DEFAULT_FROM_EMAIL not configured'))
            all_valid = False
        else:
            self.stdout.write(self.style.SUCCESS(f'   ✅ DEFAULT_FROM_EMAIL: {from_email}'))
        
        # Check ADMIN_EMAIL
        admin_email = getattr(settings, 'ADMIN_EMAIL', None)
        if admin_email:
            self.stdout.write(self.style.SUCCESS(f'   ✅ ADMIN_EMAIL: {admin_email}'))
        
        # Check mailtrap package
        try:
            from mailtrap import Mail, Address, MailtrapClient
            self.stdout.write(self.style.SUCCESS('   ✅ Mailtrap package installed'))
        except ImportError:
            self.stdout.write(self.style.ERROR('   ❌ Mailtrap package not installed'))
            all_valid = False
        
        return all_valid

    def send_test_email(self, recipient_email):
        """Send a test email using the Mailtrap integration"""
        
        subject = "🧪 Mailtrap Integration Test - Novustell Travel"
        
        html_message = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #007bff; color: white; padding: 20px; text-align: center; }}
                .content {{ background-color: #f9f9f9; padding: 20px; margin-top: 20px; }}
                .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
                .success {{ color: #28a745; font-weight: bold; }}
                ul {{ background-color: white; padding: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🧪 Email Integration Test</h1>
                </div>
                <div class="content">
                    <h2 class="success">✅ Success!</h2>
                    <p>This is a test email from <strong>Novustell Travel</strong> to verify that the Mailtrap HTTP API integration is working correctly.</p>
                    
                    <h3>📋 Test Details:</h3>
                    <ul>
                        <li><strong>Sent via:</strong> Mailtrap HTTP API</li>
                        <li><strong>From:</strong> {settings.DEFAULT_FROM_EMAIL}</li>
                        <li><strong>To:</strong> {recipient_email}</li>
                        <li><strong>Purpose:</strong> Integration Testing</li>
                        <li><strong>Status:</strong> <span class="success">Delivered Successfully</span></li>
                    </ul>
                    
                    <p>If you're reading this email, it means the Mailtrap integration is working perfectly! 🎉</p>
                </div>
                <div class="footer">
                    <p><em>Novustell Travel - Think Convenience, Think Novustell</em></p>
                    <p>This is an automated test email. No action is required.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        self.stdout.write(f'   📤 Sending to: {recipient_email}')
        self.stdout.write(f'   📝 Subject: {subject}')
        self.stdout.write(f'   📧 From: {settings.DEFAULT_FROM_EMAIL}')
        self.stdout.write('')
        
        try:
            result = send_email_via_mailtrap(
                subject=subject,
                html_message=html_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient_email]
            )
            
            if result:
                self.stdout.write(self.style.SUCCESS('   ✅ Email sent successfully via Mailtrap API'))
                return True
            else:
                self.stdout.write(self.style.ERROR('   ❌ Email sending failed (returned False)'))
                return False
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'   ❌ Exception occurred: {str(e)}'))
            logger.exception("Error sending test email")
            return False

