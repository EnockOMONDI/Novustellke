"""
Django management command for bulk image updates from Excel file
"""

import os
import requests
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.core.files.base import ContentFile
from openpyxl import load_workbook
from pyuploadcare import Uploadcare, File as UploadcareFile

from adminside.models import Destination, Package, Accommodation, Deal


class Command(BaseCommand):
    help = 'Bulk update images from Excel file for Novustell Travel database'

    def add_arguments(self, parser):
        parser.add_argument(
            'excel_file',
            type=str,
            help='Path to Excel file with updated image URLs'
        )
        parser.add_argument(
            '--sheet',
            type=str,
            choices=['Destinations', 'Packages', 'Accommodations', 'Deals', 'all'],
            default='all',
            help='Specific sheet to process (default: all)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview changes without applying them'
        )
        parser.add_argument(
            '--backup',
            action='store_true',
            help='Create backup before applying changes'
        )

    def handle(self, *args, **options):
        excel_file = options['excel_file']
        sheet_name = options['sheet']
        dry_run = options['dry_run']
        create_backup = options['backup']

        # Validate file exists
        if not os.path.exists(excel_file):
            raise CommandError(f'Excel file not found: {excel_file}')

        self.stdout.write(
            self.style.SUCCESS(f'🔄 Starting bulk image update from: {excel_file}')
        )

        if dry_run:
            self.stdout.write(
                self.style.WARNING('🔍 DRY RUN MODE - No changes will be applied')
            )

        try:
            # Load workbook
            wb = load_workbook(excel_file)
            
            # Create backup if requested
            if create_backup and not dry_run:
                self.create_backup()

            # Process sheets
            if sheet_name == 'all':
                sheets_to_process = ['Destinations', 'Packages', 'Accommodations', 'Deals']
            else:
                sheets_to_process = [sheet_name]

            total_updates = 0
            total_errors = 0

            for sheet in sheets_to_process:
                if sheet in wb.sheetnames:
                    updates, errors = self.process_sheet(wb[sheet], sheet, dry_run)
                    total_updates += updates
                    total_errors += errors
                else:
                    self.stdout.write(
                        self.style.WARNING(f'⚠️  Sheet "{sheet}" not found in Excel file')
                    )

            # Summary
            self.print_summary(total_updates, total_errors, dry_run)

        except Exception as e:
            raise CommandError(f'Bulk update failed: {str(e)}')

    def process_sheet(self, worksheet, sheet_name, dry_run):
        """Process a specific worksheet"""
        self.stdout.write(f'\n📋 Processing {sheet_name} sheet...')
        
        # Get headers
        headers = [cell.value for cell in worksheet[1]]
        
        # Find image URL column
        image_col_index = None
        for i, header in enumerate(headers):
            if 'image url' in str(header).lower():
                image_col_index = i
                break
        
        if image_col_index is None:
            self.stdout.write(
                self.style.WARNING(f'⚠️  No image URL column found in {sheet_name}')
            )
            return 0, 0

        updates = 0
        errors = 0

        # Process each row
        for row_num, row in enumerate(worksheet.iter_rows(min_row=2, values_only=True), 2):
            try:
                record_id = row[0]  # First column should be ID
                new_image_url = row[image_col_index]
                
                if not record_id or not new_image_url:
                    continue

                # Update based on sheet type
                if sheet_name == 'Destinations':
                    success = self.update_destination_image(record_id, new_image_url, dry_run)
                elif sheet_name == 'Packages':
                    success = self.update_package_image(record_id, new_image_url, dry_run)
                elif sheet_name == 'Accommodations':
                    success = self.update_accommodation_image(record_id, new_image_url, dry_run)
                elif sheet_name == 'Deals':
                    success = self.update_deal_image(record_id, new_image_url, dry_run)
                else:
                    success = False

                if success:
                    updates += 1
                    if not dry_run:
                        self.stdout.write(f'   ✅ Updated {sheet_name} ID {record_id}')
                    else:
                        self.stdout.write(f'   🔍 Would update {sheet_name} ID {record_id}')
                else:
                    errors += 1

            except Exception as e:
                errors += 1
                self.stdout.write(
                    self.style.ERROR(f'   ❌ Error processing row {row_num}: {str(e)}')
                )

        return updates, errors

    def update_destination_image(self, record_id, image_url, dry_run):
        """Update destination image"""
        try:
            destination = Destination.objects.get(id=record_id)
            
            if dry_run:
                return True
            
            # Update image
            if self.is_uploadcare_url(image_url):
                destination.image = image_url
            else:
                # Download and upload to UploadCare
                uploaded_file = self.upload_to_uploadcare(image_url)
                if uploaded_file:
                    destination.image = uploaded_file
                else:
                    return False
            
            destination.save()
            return True
            
        except Destination.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'   ❌ Destination with ID {record_id} not found')
            )
            return False

    def update_package_image(self, record_id, image_url, dry_run):
        """Update package image"""
        try:
            package = Package.objects.get(id=record_id)
            
            if dry_run:
                return True
            
            # Update image
            if self.is_uploadcare_url(image_url):
                package.featured_image = image_url
            else:
                # Download and upload to UploadCare
                uploaded_file = self.upload_to_uploadcare(image_url)
                if uploaded_file:
                    package.featured_image = uploaded_file
                else:
                    return False
            
            package.save()
            return True
            
        except Package.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'   ❌ Package with ID {record_id} not found')
            )
            return False

    def update_accommodation_image(self, record_id, image_url, dry_run):
        """Update accommodation image"""
        try:
            accommodation = Accommodation.objects.get(id=record_id)
            
            if dry_run:
                return True
            
            # Update image
            if self.is_uploadcare_url(image_url):
                accommodation.image = image_url
            else:
                # Download and upload to UploadCare
                uploaded_file = self.upload_to_uploadcare(image_url)
                if uploaded_file:
                    accommodation.image = uploaded_file
                else:
                    return False
            
            accommodation.save()
            return True
            
        except Accommodation.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'   ❌ Accommodation with ID {record_id} not found')
            )
            return False

    def update_deal_image(self, record_id, image_url, dry_run):
        """Update deal image"""
        try:
            deal = Deal.objects.get(id=record_id)
            
            if dry_run:
                return True
            
            # Update image
            if self.is_uploadcare_url(image_url):
                deal.featured_image = image_url
            else:
                # Download and upload to UploadCare
                uploaded_file = self.upload_to_uploadcare(image_url)
                if uploaded_file:
                    deal.featured_image = uploaded_file
                else:
                    return False
            
            deal.save()
            return True
            
        except Deal.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'   ❌ Deal with ID {record_id} not found')
            )
            return False

    def is_uploadcare_url(self, url):
        """Check if URL is already an UploadCare URL"""
        return 'ucarecdn.com' in str(url) or 'uploadcare.com' in str(url)

    def upload_to_uploadcare(self, image_url):
        """Upload image from URL to UploadCare"""
        try:
            # This is a simplified version - you'll need to implement
            # actual UploadCare integration based on your setup
            self.stdout.write(f'   📤 Uploading {image_url} to UploadCare...')
            
            # For now, return the URL as-is
            # In production, implement actual UploadCare upload
            return image_url
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'   ❌ Failed to upload {image_url}: {str(e)}')
            )
            return None

    def create_backup(self):
        """Create database backup before bulk updates"""
        self.stdout.write('💾 Creating backup...')
        
        backup_file = f'backup_before_bulk_update_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        
        # Use the export command to create backup
        from django.core.management import call_command
        call_command('export_to_excel', output=backup_file)
        
        self.stdout.write(f'   ✅ Backup created: {backup_file}')

    def print_summary(self, total_updates, total_errors, dry_run):
        """Print update summary"""
        self.stdout.write('\n' + '='*60)
        if dry_run:
            self.stdout.write(self.style.SUCCESS('🔍 DRY RUN SUMMARY'))
        else:
            self.stdout.write(self.style.SUCCESS('✅ BULK UPDATE SUMMARY'))
        self.stdout.write('='*60)
        self.stdout.write(f'📊 Total records processed: {total_updates + total_errors}')
        self.stdout.write(f'✅ Successful updates: {total_updates}')
        self.stdout.write(f'❌ Errors: {total_errors}')
        self.stdout.write(f'📅 Completed: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        
        if dry_run:
            self.stdout.write('\n💡 To apply changes, run without --dry-run flag')
        else:
            self.stdout.write('\n🎉 Bulk image update completed!')
        
        self.stdout.write('='*60)
