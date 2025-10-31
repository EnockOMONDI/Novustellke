"""
Django management command to add the Novustell Holiday Newsletter template to the database
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.template.loader import get_template
from django.template import TemplateDoesNotExist
from email_marketing.models import EmailTemplate
import os


class Command(BaseCommand):
    help = 'Add the Novustell Holiday Newsletter template to the email marketing system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--update',
            action='store_true',
            help='Update the template if it already exists',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 Adding Novustell Holiday Newsletter Template...'))
        
        # Get or create admin user
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            self.stdout.write(self.style.ERROR('❌ No admin user found. Please create a superuser first.'))
            return
        
        # Read the template file content
        template_path = 'email_marketing/templates/email_marketing/novustell_holiday_newsletter_base64_optimized_images.html'
        
        try:
            # Try to read the template file directly
            with open(template_path, 'r', encoding='utf-8') as file:
                html_content = file.read()
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'❌ Template file not found: {template_path}'))
            return
        
        # Template details
        template_name = "Novustell Holiday Newsletter - Base64 Optimized"
        template_subject = "Pick a vibe, we customise the rest: Egypt • South Africa • Mombasa • Mauritius"
        template_description = "Holiday highlights newsletter featuring 4 customizable travel packages with WhatsApp integration and Novustell branding"
        
        # Available template variables
        available_variables = {
            'recipient_name': 'Name of the recipient (fallback: "there")',
            'recipient.first_name': 'First name of recipient',
            'recipient.last_name': 'Last name of recipient', 
            'recipient.email': 'Email address of recipient',
            'recipient.organization': 'Organization/school name',
            'tracking_pixel_url': 'URL for email open tracking',
            'unsubscribe_url': 'URL for unsubscribing from newsletter',
            'campaign.name': 'Name of the email campaign',
            'campaign.id': 'Campaign ID for tracking'
        }
        
        # Create or update the template
        template, created = EmailTemplate.objects.get_or_create(
            name=template_name,
            defaults={
                'subject': template_subject,
                'template_type': 'general',  # Using 'general' as it's for holiday promotions
                'html_content': html_content,
                'text_content': self.get_text_version(),
                'created_by': admin_user,
                'is_active': True,
                'available_variables': available_variables
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'✅ Successfully created email template: {template_name}')
            )
        else:
            if options['update']:
                # Update existing template
                template.subject = template_subject
                template.html_content = html_content
                template.text_content = self.get_text_version()
                template.available_variables = available_variables
                template.is_active = True
                template.save()
                
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Successfully updated email template: {template_name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'⚠️  Template already exists: {template_name}')
                )
                self.stdout.write(
                    self.style.WARNING('Use --update flag to update the existing template')
                )
                return
        
        # Display template information
        self.stdout.write('\n📧 Template Details:')
        self.stdout.write(f'   Name: {template.name}')
        self.stdout.write(f'   Subject: {template.subject}')
        self.stdout.write(f'   Type: {template.get_template_type_display()}')
        self.stdout.write(f'   Status: {"Active" if template.is_active else "Inactive"}')
        self.stdout.write(f'   Created by: {template.created_by.username}')
        self.stdout.write(f'   Created at: {template.created_at}')
        self.stdout.write(f'   Template ID: {template.id}')
        
        self.stdout.write('\n🔧 Available Variables:')
        for var, desc in template.available_variables.items():
            self.stdout.write(f'   {{ {var} }} - {desc}')
        
        self.stdout.write('\n🎯 Next Steps:')
        self.stdout.write('   1. Create recipient lists in Django admin')
        self.stdout.write('   2. Create email campaigns using this template')
        self.stdout.write('   3. Test the template with a small recipient list')
        self.stdout.write('   4. Monitor campaign performance in admin dashboard')
        
        self.stdout.write(self.style.SUCCESS('\n🎉 Template setup completed successfully!'))

    def get_text_version(self):
        """Generate a plain text version of the email"""
        return """
NOVUSTELL TRAVEL - HOLIDAY HIGHLIGHTS

Hi {{ recipient_name|default:"there" }},

November - December Holiday Highlights
From pyramids and wine routes to beach escapes — choose your vibe and we'll tailor it.

🇪🇬 EGYPT: PYRAMIDS & NILE CRUISE
- 8 days from Cairo to Aswan
- Pyramids, Sphinx, Valley of Kings
- 5-star Nile cruise with all meals
- Expert Egyptologist guides
From USD 1,890 – 2,150 per person

🇿🇦 SOUTH AFRICA: CAPE TOWN & WINE ROUTE
- 7 days Cape Town & Stellenbosch
- Table Mountain, wine tastings
- Luxury safari day trip option
- 4-star city & vineyard hotels
From USD 1,670 – 1,920 per person

🇰🇪 MOMBASA: BEACH & CULTURE
- 6 days coast & cultural sites
- Beach resort with water sports
- Gede Ruins, Fort Jesus tours
- All-inclusive beach packages
From USD 890 – 1,240 per person

🇲🇺 MAURITIUS: TROPICAL PARADISE
- 7 days luxury beach resort
- Snorkeling, spa treatments
- Island tours, botanical gardens
- Premium beachfront hotels
From USD 1,970 – 2,179 per person

PREFER SOMETHING DIFFERENT?
Tell us your dates, budget and vibe. We'll tailor flights, stays, and experiences around you.

Contact us:
WhatsApp: +254 701 363 551
Email: info@novustelltravel.com

Novustell Travel
New People Media Center, Kilimani Rd, Nairobi, Kenya

Prices are per person sharing and subject to availability.
"""
