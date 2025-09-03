"""
Django management command to generate placeholder images for Novustell Travel records
Creates 1080x1350 JPG placeholders for records without images
Creates .txt files with current URLs for records with existing images
"""

import os
import re
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from PIL import Image, ImageDraw, ImageFont
from adminside.models import Destination, Package, Accommodation, Deal


class Command(BaseCommand):
    help = 'Generate placeholder images and URL files for Novustell Travel database records'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output-dir',
            type=str,
            default='novustell-images',
            help='Output directory name (default: novustell-images)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview what would be created without actually creating files'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Overwrite existing files if they exist'
        )

    def handle(self, *args, **options):
        self.dry_run = options['dry_run']
        self.force = options['force']
        self.output_dir = options['output_dir']
        
        # Set up output directory in Django project root
        self.base_path = os.path.join(settings.BASE_DIR, self.output_dir)
        
        self.stdout.write(
            self.style.SUCCESS(f'🎨 Starting placeholder image generation for Novustell Travel')
        )
        
        if self.dry_run:
            self.stdout.write(
                self.style.WARNING('🔍 DRY RUN MODE - No files will be created')
            )

        try:
            # Phase 1: Database Analysis
            self.analyze_database()
            
            # Phase 2: Create folder structure
            self.create_folder_structure()
            
            # Phase 3: Generate placeholder files
            self.generate_placeholder_files()
            
            # Phase 4: Generate summary report
            self.generate_summary_report()
            
        except Exception as e:
            raise CommandError(f'Placeholder generation failed: {str(e)}')

    def analyze_database(self):
        """Phase 1: Analyze database records and their current image status"""
        self.stdout.write('\n📊 Phase 1: Analyzing database records...')
        
        # Query all models
        self.packages = Package.objects.all()
        self.destinations = Destination.objects.all()
        self.accommodations = Accommodation.objects.all()
        self.deals = Deal.objects.all()
        
        # Analyze image status
        self.stats = {
            'packages': {
                'total': self.packages.count(),
                'with_images': 0,
                'without_images': 0,
                'records': []
            },
            'destinations': {
                'total': self.destinations.count(),
                'with_images': 0,
                'without_images': 0,
                'records': []
            },
            'accommodations': {
                'total': self.accommodations.count(),
                'with_images': 0,
                'without_images': 0,
                'records': []
            },
            'deals': {
                'total': self.deals.count(),
                'with_images': 0,
                'without_images': 0,
                'records': []
            }
        }
        
        # Analyze packages
        for package in self.packages:
            has_image = bool(package.featured_image and str(package.featured_image).strip())
            record_info = {
                'id': package.id,
                'name': package.name,
                'slug': package.slug,
                'has_image': has_image,
                'image_url': str(package.featured_image) if has_image else None
            }
            self.stats['packages']['records'].append(record_info)
            if has_image:
                self.stats['packages']['with_images'] += 1
            else:
                self.stats['packages']['without_images'] += 1
        
        # Analyze destinations
        for destination in self.destinations:
            has_image = bool(destination.image and str(destination.image).strip())
            record_info = {
                'id': destination.id,
                'name': destination.name,
                'slug': destination.slug,
                'has_image': has_image,
                'image_url': str(destination.image) if has_image else None
            }
            self.stats['destinations']['records'].append(record_info)
            if has_image:
                self.stats['destinations']['with_images'] += 1
            else:
                self.stats['destinations']['without_images'] += 1
        
        # Analyze accommodations
        for accommodation in self.accommodations:
            has_image = bool(accommodation.image and str(accommodation.image).strip())
            record_info = {
                'id': accommodation.id,
                'name': accommodation.name,
                'slug': accommodation.slug,
                'has_image': has_image,
                'image_url': str(accommodation.image) if has_image else None
            }
            self.stats['accommodations']['records'].append(record_info)
            if has_image:
                self.stats['accommodations']['with_images'] += 1
            else:
                self.stats['accommodations']['without_images'] += 1
        
        # Analyze deals
        for deal in self.deals:
            has_image = bool(deal.featured_image and str(deal.featured_image).strip())
            record_info = {
                'id': deal.id,
                'name': deal.title,  # Deals use 'title' instead of 'name'
                'slug': deal.slug,
                'has_image': has_image,
                'image_url': str(deal.featured_image) if has_image else None
            }
            self.stats['deals']['records'].append(record_info)
            if has_image:
                self.stats['deals']['with_images'] += 1
            else:
                self.stats['deals']['without_images'] += 1
        
        # Print analysis results
        self.print_analysis_results()

    def print_analysis_results(self):
        """Print database analysis results"""
        self.stdout.write('\n📋 Database Analysis Results:')
        self.stdout.write('=' * 60)
        
        total_records = 0
        total_with_images = 0
        total_without_images = 0
        
        for category, data in self.stats.items():
            total_records += data['total']
            total_with_images += data['with_images']
            total_without_images += data['without_images']
            
            self.stdout.write(f'\n📦 {category.upper()}:')
            self.stdout.write(f'   Total: {data["total"]}')
            self.stdout.write(f'   With images: {data["with_images"]} (will create .txt files)')
            self.stdout.write(f'   Without images: {data["without_images"]} (will create .jpg placeholders)')
        
        self.stdout.write('\n📊 SUMMARY:')
        self.stdout.write(f'   Total records: {total_records}')
        self.stdout.write(f'   .txt files to create: {total_with_images}')
        self.stdout.write(f'   .jpg placeholders to create: {total_without_images}')
        self.stdout.write('=' * 60)

    def create_folder_structure(self):
        """Phase 2: Create the folder structure"""
        self.stdout.write('\n📁 Phase 2: Creating folder structure...')
        
        categories = ['packages', 'destinations', 'accommodations', 'deals']
        
        if not self.dry_run:
            # Create base directory
            os.makedirs(self.base_path, exist_ok=True)
            self.stdout.write(f'   ✅ Created base directory: {self.base_path}')
            
            # Create category directories
            for category in categories:
                category_path = os.path.join(self.base_path, category)
                os.makedirs(category_path, exist_ok=True)
                self.stdout.write(f'   ✅ Created directory: {category_path}')
        else:
            self.stdout.write(f'   🔍 Would create base directory: {self.base_path}')
            for category in categories:
                category_path = os.path.join(self.base_path, category)
                self.stdout.write(f'   🔍 Would create directory: {category_path}')

    def sanitize_filename(self, name):
        """Clean record names for filesystem compatibility"""
        if not name:
            return 'unnamed'
        
        # Replace spaces with hyphens
        name = name.replace(' ', '-')
        
        # Remove special characters except hyphens and alphanumeric
        name = re.sub(r'[^a-zA-Z0-9\-]', '', name)
        
        # Remove multiple consecutive hyphens
        name = re.sub(r'-+', '-', name)
        
        # Remove leading/trailing hyphens
        name = name.strip('-')
        
        # Truncate to 50 characters max
        if len(name) > 50:
            name = name[:50].rstrip('-')
        
        # Ensure we have something
        if not name:
            name = 'unnamed'
            
        return name

    def create_placeholder_image(self, record_name, record_type, output_path):
        """Create a 1080x1350 JPG placeholder image with text overlay"""
        try:
            # Create 1080x1350 portrait image with Novustell background color
            img = Image.new('RGB', (1080, 1350), color='#f8f3fc')
            draw = ImageDraw.Draw(img)

            # Try to load a better font, fall back to default if not available
            try:
                # Try to load a larger font
                font_large = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 48)
                font_medium = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 36)
                font_small = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 24)
            except:
                try:
                    # Alternative font paths for different systems
                    font_large = ImageFont.truetype("arial.ttf", 48)
                    font_medium = ImageFont.truetype("arial.ttf", 36)
                    font_small = ImageFont.truetype("arial.ttf", 24)
                except:
                    # Fall back to default font
                    font_large = ImageFont.load_default()
                    font_medium = ImageFont.load_default()
                    font_small = ImageFont.load_default()

            # Novustell brand colors
            primary_blue = '#0f238d'
            accent_orange = '#ff9d00'

            # Add Novustell branding at the top
            brand_text = "NOVUSTELL TRAVEL"
            brand_bbox = draw.textbbox((0, 0), brand_text, font=font_medium)
            brand_width = brand_bbox[2] - brand_bbox[0]
            brand_x = (1080 - brand_width) // 2
            draw.text((brand_x, 100), brand_text, fill=accent_orange, font=font_medium)

            # Add a decorative line
            draw.rectangle([340, 180, 740, 185], fill=primary_blue)

            # Add record type
            type_text = record_type.upper()
            type_bbox = draw.textbbox((0, 0), type_text, font=font_small)
            type_width = type_bbox[2] - type_bbox[0]
            type_x = (1080 - type_width) // 2
            draw.text((type_x, 220), type_text, fill=primary_blue, font=font_small)

            # Add record name (main text)
            # Split long names into multiple lines
            words = record_name.replace('-', ' ').split()
            lines = []
            current_line = []

            for word in words:
                test_line = ' '.join(current_line + [word])
                test_bbox = draw.textbbox((0, 0), test_line, font=font_large)
                test_width = test_bbox[2] - test_bbox[0]

                if test_width <= 900:  # Leave some margin
                    current_line.append(word)
                else:
                    if current_line:
                        lines.append(' '.join(current_line))
                        current_line = [word]
                    else:
                        lines.append(word)

            if current_line:
                lines.append(' '.join(current_line))

            # Limit to 4 lines max
            if len(lines) > 4:
                lines = lines[:3] + ['...']

            # Center the text vertically
            total_text_height = len(lines) * 60  # Approximate line height
            start_y = (1350 - total_text_height) // 2

            for i, line in enumerate(lines):
                line_bbox = draw.textbbox((0, 0), line, font=font_large)
                line_width = line_bbox[2] - line_bbox[0]
                line_x = (1080 - line_width) // 2
                line_y = start_y + (i * 60)
                draw.text((line_x, line_y), line, fill=primary_blue, font=font_large)

            # Add placeholder indicator at bottom
            placeholder_text = "PLACEHOLDER IMAGE"
            placeholder_bbox = draw.textbbox((0, 0), placeholder_text, font=font_small)
            placeholder_width = placeholder_bbox[2] - placeholder_bbox[0]
            placeholder_x = (1080 - placeholder_width) // 2
            draw.text((placeholder_x, 1250), placeholder_text, fill='#666666', font=font_small)

            # Save as JPG with high quality
            img.save(output_path, 'JPEG', quality=90, optimize=True)
            return True

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'   ❌ Failed to create image {output_path}: {str(e)}')
            )
            return False

    def create_url_file(self, record_name, record_type, output_path, image_url):
        """Create a .txt file containing the current image URL"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(image_url)
            return True
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'   ❌ Failed to create URL file {output_path}: {str(e)}')
            )
            return False

    def generate_placeholder_files(self):
        """Phase 3: Generate placeholder files for all records"""
        self.stdout.write('\n🎨 Phase 3: Generating placeholder files...')

        self.files_created = {
            'jpg_files': 0,
            'txt_files': 0,
            'errors': 0,
            'skipped': 0
        }

        # Process each category
        categories = ['packages', 'destinations', 'accommodations', 'deals']

        for category in categories:
            self.stdout.write(f'\n📦 Processing {category}...')
            category_path = os.path.join(self.base_path, category)

            for record in self.stats[category]['records']:
                self.process_record(record, category, category_path)

    def process_record(self, record, category, category_path):
        """Process a single record to create either JPG or TXT file"""
        # Sanitize the record name for filename
        sanitized_name = self.sanitize_filename(record['name'])

        # Create filename based on naming convention
        record_type = category.rstrip('s').title()  # packages -> Package
        if category == 'accommodations':
            record_type = 'Accommodation'

        if record['has_image']:
            # Create .txt file with current URL
            filename = f"{sanitized_name}-{record_type}-placeholder.txt"
            filepath = os.path.join(category_path, filename)

            if not self.dry_run:
                if os.path.exists(filepath) and not self.force:
                    self.stdout.write(f'   ⚠️  Skipped (exists): {filename}')
                    self.files_created['skipped'] += 1
                else:
                    if self.create_url_file(sanitized_name, record_type, filepath, record['image_url']):
                        self.stdout.write(f'   ✅ Created URL file: {filename}')
                        self.files_created['txt_files'] += 1
                    else:
                        self.files_created['errors'] += 1
            else:
                self.stdout.write(f'   🔍 Would create URL file: {filename}')
        else:
            # Create .jpg placeholder
            filename = f"{sanitized_name}-{record_type}-placeholder.jpg"
            filepath = os.path.join(category_path, filename)

            if not self.dry_run:
                if os.path.exists(filepath) and not self.force:
                    self.stdout.write(f'   ⚠️  Skipped (exists): {filename}')
                    self.files_created['skipped'] += 1
                else:
                    if self.create_placeholder_image(sanitized_name, record_type, filepath):
                        self.stdout.write(f'   ✅ Created placeholder: {filename}')
                        self.files_created['jpg_files'] += 1
                    else:
                        self.files_created['errors'] += 1
            else:
                self.stdout.write(f'   🔍 Would create placeholder: {filename}')

    def generate_summary_report(self):
        """Phase 4: Generate final summary report"""
        self.stdout.write('\n' + '='*80)
        self.stdout.write(self.style.SUCCESS('🎉 PLACEHOLDER GENERATION COMPLETE'))
        self.stdout.write('='*80)

        if not self.dry_run:
            self.stdout.write(f'📁 Output Directory: {self.base_path}')
            self.stdout.write(f'📊 Files Created:')
            self.stdout.write(f'   📸 JPG Placeholders: {self.files_created["jpg_files"]}')
            self.stdout.write(f'   📄 URL Text Files: {self.files_created["txt_files"]}')
            self.stdout.write(f'   ⚠️  Skipped (existing): {self.files_created["skipped"]}')
            self.stdout.write(f'   ❌ Errors: {self.files_created["errors"]}')

            total_files = self.files_created["jpg_files"] + self.files_created["txt_files"]
            self.stdout.write(f'   ✅ Total Files Created: {total_files}')
        else:
            self.stdout.write('🔍 DRY RUN COMPLETED - No files were actually created')

        self.stdout.write('\n💡 Next Steps:')
        self.stdout.write('   1. Review the generated placeholder files')
        self.stdout.write('   2. Replace JPG placeholders with actual images')
        self.stdout.write('   3. Upload new images to UploadCare')
        self.stdout.write('   4. Use the bulk_update_images command to update the database')

        self.stdout.write(f'\n📅 Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        self.stdout.write('='*80)
