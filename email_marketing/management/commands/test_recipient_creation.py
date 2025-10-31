"""
Django management command to test recipient creation and demonstrate custom_data usage
"""

from django.core.management.base import BaseCommand
from email_marketing.models import Recipient, RecipientList
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Test recipient creation and demonstrate custom_data field usage'

    def add_arguments(self, parser):
        parser.add_argument(
            '--create-examples',
            action='store_true',
            help='Create example recipients with different custom_data configurations',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🧪 TESTING RECIPIENT CREATION'))
        self.stdout.write('=' * 60)
        
        if options['create_examples']:
            self.create_example_recipients()
        
        self.demonstrate_custom_data_usage()
        
        self.stdout.write(self.style.SUCCESS('\n✅ Recipient creation test completed!'))

    def create_example_recipients(self):
        """Create example recipients with various custom_data configurations"""
        self.stdout.write('\n📝 Creating example recipients...')
        
        # Example 1: Basic recipient with no custom data
        recipient1, created = Recipient.objects.get_or_create(
            email='basic.user@example.com',
            defaults={
                'first_name': 'John',
                'last_name': 'Doe',
                'organization': 'Example High School',
                'position': 'Principal',
                'custom_data': {}  # Empty dict - this should work fine
            }
        )
        
        if created:
            self.stdout.write('   ✅ Created basic recipient (no custom data)')
        else:
            self.stdout.write('   ⚠️  Basic recipient already exists')
        
        # Example 2: Educational institution with detailed data
        recipient2, created = Recipient.objects.get_or_create(
            email='coordinator@modelun.school.edu',
            defaults={
                'first_name': 'Sarah',
                'last_name': 'Johnson',
                'organization': 'International Academy',
                'position': 'Model UN Coordinator',
                'custom_data': {
                    'school_type': 'private',
                    'student_count': 800,
                    'grade_levels': ['9', '10', '11', '12'],
                    'model_un_experience': 'advanced',
                    'previous_participant': True,
                    'budget_range': 'high',
                    'interests': ['model_un', 'debate', 'international_relations'],
                    'contact_preference': 'email',
                    'best_contact_time': 'morning'
                }
            }
        )
        
        if created:
            self.stdout.write('   ✅ Created educational recipient (detailed custom data)')
        else:
            self.stdout.write('   ⚠️  Educational recipient already exists')
        
        # Example 3: Corporate client
        recipient3, created = Recipient.objects.get_or_create(
            email='travel.manager@corporation.com',
            defaults={
                'first_name': 'Michael',
                'last_name': 'Chen',
                'organization': 'Global Corp Inc.',
                'position': 'Travel Manager',
                'custom_data': {
                    'company_size': 'large',
                    'travel_frequency': 'monthly',
                    'preferred_destinations': ['Europe', 'Asia', 'North America'],
                    'budget_category': 'corporate',
                    'group_size_preference': '10-20',
                    'accommodation_level': 'luxury',
                    'special_requirements': ['dietary_restrictions', 'accessibility'],
                    'booking_lead_time': '2-3 months'
                }
            }
        )
        
        if created:
            self.stdout.write('   ✅ Created corporate recipient (business custom data)')
        else:
            self.stdout.write('   ⚠️  Corporate recipient already exists')
        
        # Example 4: NGO organization
        recipient4, created = Recipient.objects.get_or_create(
            email='programs@ngo.org',
            defaults={
                'first_name': 'Maria',
                'last_name': 'Rodriguez',
                'organization': 'Global Education NGO',
                'position': 'Program Director',
                'custom_data': {
                    'organization_type': 'ngo',
                    'focus_areas': ['education', 'youth_development', 'cultural_exchange'],
                    'target_age_group': '15-18',
                    'program_duration': 'annual',
                    'funding_source': 'grants',
                    'participant_count': 50,
                    'geographic_focus': ['Africa', 'Latin America'],
                    'partnership_interest': True
                }
            }
        )
        
        if created:
            self.stdout.write('   ✅ Created NGO recipient (program-specific custom data)')
        else:
            self.stdout.write('   ⚠️  NGO recipient already exists')

    def demonstrate_custom_data_usage(self):
        """Demonstrate how custom_data can be used in email personalization"""
        self.stdout.write('\n📊 CUSTOM_DATA FIELD USAGE EXAMPLES')
        self.stdout.write('-' * 60)
        
        self.stdout.write('\n🎯 Purpose of custom_data field:')
        self.stdout.write('   • Store additional recipient information for email personalization')
        self.stdout.write('   • Enable targeted email campaigns based on specific criteria')
        self.stdout.write('   • Provide context for email template variables')
        self.stdout.write('   • Support advanced segmentation and filtering')
        
        self.stdout.write('\n📝 Example JSON structures:')
        
        self.stdout.write('\n1️⃣  Educational Institution:')
        self.stdout.write('   {')
        self.stdout.write('     "school_type": "public",')
        self.stdout.write('     "student_count": 1200,')
        self.stdout.write('     "grade_levels": ["9", "10", "11", "12"],')
        self.stdout.write('     "model_un_experience": "beginner",')
        self.stdout.write('     "budget_range": "medium",')
        self.stdout.write('     "interests": ["model_un", "debate"]')
        self.stdout.write('   }')
        
        self.stdout.write('\n2️⃣  Corporate Client:')
        self.stdout.write('   {')
        self.stdout.write('     "company_size": "medium",')
        self.stdout.write('     "travel_frequency": "quarterly",')
        self.stdout.write('     "preferred_destinations": ["Europe", "Asia"],')
        self.stdout.write('     "group_size": "5-10",')
        self.stdout.write('     "accommodation_level": "business"')
        self.stdout.write('   }')
        
        self.stdout.write('\n3️⃣  NGO Organization:')
        self.stdout.write('   {')
        self.stdout.write('     "organization_type": "ngo",')
        self.stdout.write('     "focus_areas": ["education", "youth_development"],')
        self.stdout.write('     "target_age_group": "16-18",')
        self.stdout.write('     "funding_source": "donations",')
        self.stdout.write('     "geographic_focus": ["Africa"]')
        self.stdout.write('   }')
        
        self.stdout.write('\n4️⃣  Basic Recipient (empty is fine):')
        self.stdout.write('   {}')
        
        self.stdout.write('\n🔧 How to use in email templates:')
        self.stdout.write('   • Access via: {{ recipient.custom_data.key_name }}')
        self.stdout.write('   • Example: {{ recipient.custom_data.school_type|default:"school" }}')
        self.stdout.write('   • Conditional: {% if recipient.custom_data.budget_range == "high" %}...{% endif %}')
        
        self.stdout.write('\n⚠️  Important notes:')
        self.stdout.write('   • The custom_data field is OPTIONAL - you can leave it empty')
        self.stdout.write('   • Use valid JSON format when adding data')
        self.stdout.write('   • Field is collapsed by default in admin interface')
        self.stdout.write('   • Empty {} is perfectly valid and recommended for basic recipients')
        
        # Show current recipients count
        total_recipients = Recipient.objects.count()
        recipients_with_data = Recipient.objects.exclude(custom_data={}).count()
        recipients_without_data = total_recipients - recipients_with_data
        
        self.stdout.write(f'\n📈 Current database statistics:')
        self.stdout.write(f'   • Total recipients: {total_recipients}')
        self.stdout.write(f'   • With custom data: {recipients_with_data}')
        self.stdout.write(f'   • Without custom data: {recipients_without_data}')
        
        self.stdout.write('\n🎯 Next steps:')
        self.stdout.write('   1. Try adding a recipient through Django admin')
        self.stdout.write('   2. Leave custom_data empty for basic recipients')
        self.stdout.write('   3. Add JSON data only when you need advanced personalization')
        self.stdout.write('   4. Test email templates with different recipient data')
