"""
Management command to set up the Model UN 2025-2026 email marketing campaign
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from email_marketing.models import EmailTemplate, RecipientList, Recipient, EmailCampaign


class Command(BaseCommand):
    help = 'Set up the Model UN 2025-2026 email marketing campaign with template and sample data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--create-samples',
            action='store_true',
            help='Create sample recipients for testing',
        )
        parser.add_argument(
            '--admin-user',
            type=str,
            default='admin',
            help='Username of admin user to assign as campaign creator',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Setting up Model UN 2025-2026 Email Marketing Campaign...'))
        
        # Get or create admin user
        try:
            admin_user = User.objects.get(username=options['admin_user'])
        except User.DoesNotExist:
            admin_user = User.objects.filter(is_superuser=True).first()
            if not admin_user:
                self.stdout.write(
                    self.style.ERROR(f'No admin user found. Please create a superuser first.')
                )
                return
        
        # Create email template
        template_content = self.get_model_un_template_content()
        
        email_template, created = EmailTemplate.objects.get_or_create(
            name="Model UN 2025-2026 Campaign",
            defaults={
                'subject': "Is Your School Ready for the Next Model UN Season?",
                'template_type': 'educational',
                'html_content': template_content,
                'text_content': self.get_text_version(),
                'created_by': admin_user,
                'available_variables': {
                    'recipient_name': 'Name of the recipient',
                    'organization': 'School or organization name',
                    'first_name': 'First name of recipient',
                    'last_name': 'Last name of recipient',
                    'email': 'Email address',
                    'tracking_pixel_url': 'URL for email open tracking',
                    'unsubscribe_url': 'URL for unsubscribing'
                }
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'✅ Created email template: {email_template.name}')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'⚠️  Email template already exists: {email_template.name}')
            )
        
        # Create recipient list for educational institutions
        recipient_list, created = RecipientList.objects.get_or_create(
            name="Educational Institutions - Model UN",
            defaults={
                'description': 'Schools and educational institutions interested in Model UN programs',
                'list_type': 'schools',
                'created_by': admin_user
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'✅ Created recipient list: {recipient_list.name}')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'⚠️  Recipient list already exists: {recipient_list.name}')
            )
        
        # Create sample recipients if requested
        if options['create_samples']:
            self.create_sample_recipients(recipient_list)
        
        # Create email campaign
        campaign, created = EmailCampaign.objects.get_or_create(
            name="Model UN 2025-2026 Outreach Campaign",
            defaults={
                'description': 'Email marketing campaign to promote Model UN travel opportunities to educational institutions',
                'email_template': email_template,
                'status': 'draft',
                'created_by': admin_user,
                'track_opens': True,
                'track_clicks': True
            }
        )
        
        if created:
            campaign.recipient_lists.add(recipient_list)
            self.stdout.write(
                self.style.SUCCESS(f'✅ Created email campaign: {campaign.name}')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'⚠️  Email campaign already exists: {campaign.name}')
            )
        
        # Summary
        self.stdout.write(self.style.SUCCESS('\n🎉 Model UN Campaign Setup Complete!'))
        self.stdout.write(f'📧 Email Template: {email_template.name}')
        self.stdout.write(f'📋 Recipient List: {recipient_list.name} ({recipient_list.recipient_count} recipients)')
        self.stdout.write(f'🚀 Campaign: {campaign.name} (Status: {campaign.get_status_display()})')
        self.stdout.write(f'\n📊 Campaign Statistics:')
        self.stdout.write(f'   Total Recipients: {campaign.total_recipients}')
        self.stdout.write(f'   Emails Sent: {campaign.emails_sent}')
        self.stdout.write(f'\n🔗 Next Steps:')
        self.stdout.write(f'   1. Review the campaign in Django Admin')
        self.stdout.write(f'   2. Add more recipients to the list')
        self.stdout.write(f'   3. Test the email template preview')
        self.stdout.write(f'   4. Schedule or send the campaign')

    def create_sample_recipients(self, recipient_list):
        """Create sample recipients for testing"""
        sample_recipients = [
            {
                'email': 'principal@kenyahighschool.edu',
                'first_name': 'James',
                'last_name': 'Mwangi',
                'organization': 'Kenya High School',
                'position': 'Principal',
                'location': 'Nairobi, Kenya',
                'phone': '+254 700 123 456'
            },
            {
                'email': 'coordinator@alliancehigh.edu',
                'first_name': 'Sarah',
                'last_name': 'Wanjiku',
                'organization': 'Alliance High School',
                'position': 'MUN Coordinator',
                'location': 'Kikuyu, Kenya',
                'phone': '+254 700 234 567'
            },
            {
                'email': 'admin@brookhouseschool.edu',
                'first_name': 'Michael',
                'last_name': 'Thompson',
                'organization': 'Brookhouse School',
                'position': 'Academic Director',
                'location': 'Karen, Nairobi',
                'phone': '+254 700 345 678'
            },
            {
                'email': 'director@iskenya.edu',
                'first_name': 'Patricia',
                'last_name': 'Ochieng',
                'organization': 'International School of Kenya',
                'position': 'Director of Studies',
                'location': 'Nairobi, Kenya',
                'phone': '+254 700 456 789'
            },
            {
                'email': 'principal@stmarysschool.edu',
                'first_name': 'David',
                'last_name': 'Kimani',
                'organization': 'St. Mary\'s School',
                'position': 'Principal',
                'location': 'Nairobi, Kenya',
                'phone': '+254 700 567 890'
            }
        ]
        
        created_count = 0
        for recipient_data in sample_recipients:
            recipient, created = Recipient.objects.get_or_create(
                email=recipient_data['email'],
                defaults=recipient_data
            )
            if created:
                created_count += 1
            recipient.recipient_lists.add(recipient_list)
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ Created {created_count} sample recipients')
        )

    def get_model_un_template_content(self):
        """Get the HTML content for the Model UN email template"""
        # Read the template file content
        import os
        from django.conf import settings
        
        template_path = os.path.join(
            settings.BASE_DIR, 
            'email_marketing', 
            'templates', 
            'email_marketing', 
            'model_un_2025_campaign.html'
        )
        
        try:
            with open(template_path, 'r', encoding='utf-8') as file:
                return file.read()
        except FileNotFoundError:
            # Fallback to basic template if file not found
            return """
            <h1>Model United Nations 2025–2026</h1>
            <p>Dear {{ recipient_name }},</p>
            <p>Your school's participation in Model UN conferences awaits...</p>
            <p>Contact us at info@novustelltravel.com</p>
            """

    def get_text_version(self):
        """Get plain text version of the email"""
        return """
Model United Nations 2025–2026 – Preparing Tomorrow's Global Leaders

Dear {{ recipient_name }},

Model United Nations (MUN) continues to be one of the most transformative platforms for students; nurturing diplomacy, debate, and global awareness while preparing them to thrive as tomorrow's change makers.

For Kenyan students, participation in upcoming prestigious conferences such as Harvard MUN & Yale MUN provides:
- A chance to debate pressing global issues alongside peers from 50+ countries
- Opportunities to build public speaking, negotiation, and leadership skills
- Exposure to leading universities and cultures that broaden academic and career horizons

Upcoming global MUN highlights:
- Yale MUN – January 2026, New Haven
- Harvard MUN – January/February 2026, Boston
- HNMUN – February 2026, Boston

How Novustell Travel Can Partner with You:
At Novustell, we understand that organizing successful international school trips requires more than just flights and accommodation. Through our school partnerships, we:
- Provide end-to-end travel logistics (visas, flights, accommodation, transfers)
- Design custom itineraries that combine MUN participation with cultural, academic, or university exposure visits
- Offer student-focused travel support ensuring safety, structure, and memorable experiences
- Work hand-in-hand with school MUN clubs and coordinators to simplify planning and execution

Why This Matters for Your Students:
By participating in these global MUNs, your students not only sharpen academic skills but also grow into:
- Confident public speakers and negotiators
- Globally aware citizens with strong cultural empathy
- University-ready candidates with distinctive leadership experiences

Contact us:
Email: info@novustelltravel.com
Educational Programs: asiga@novustelltravel.com
Phone: +254 721 115 572 | +254 701 363 551
WhatsApp: +254 701 363 551

Novustell Travel - Think Convenience, Think Novustell

To unsubscribe: {{ unsubscribe_url }}
        """
