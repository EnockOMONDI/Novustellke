#!/usr/bin/env python
"""
Import script for General client list.xlsx
Creates a new recipient list "general clients list" with 999 Excel recipients + 2 manual recipients
"""

import os
import sys
import django
import pandas as pd
from django.db import transaction

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tours_travels.settings')
django.setup()

from email_marketing.models import Recipient, RecipientList
from django.contrib.auth.models import User

def import_general_clients():
    """Import recipients from General client list.xlsx and add manual recipients"""
    
    print("🚀 Starting import of General client list...")
    print("=" * 60)
    
    # Read Excel file
    try:
        df = pd.read_excel('General client list.xlsx')
        print(f"✅ Successfully read Excel file: {len(df)} records found")
    except Exception as e:
        print(f"❌ Error reading Excel file: {e}")
        return False
    
    # Get admin user for created_by field
    try:
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            admin_user = User.objects.filter(is_staff=True).first()
        if not admin_user:
            print("❌ No admin or staff user found. Creating default admin user...")
            admin_user = User.objects.create_user(
                username='import_admin',
                email='admin@novustelltravel.com',
                is_staff=True,
                is_superuser=True
            )
            print(f"✅ Created admin user: {admin_user.username}")
        else:
            print(f"✅ Using admin user: {admin_user.username}")
    except Exception as e:
        print(f"❌ Error getting admin user: {e}")
        return False

    # Create or get recipient list
    try:
        recipient_list, created = RecipientList.objects.get_or_create(
            name="general clients list",
            defaults={
                'description': 'Imported from General client list.xlsx - contains 999 Excel recipients plus 2 manual additions',
                'created_by': admin_user
            }
        )
        if created:
            print(f"✅ Created new recipient list: '{recipient_list.name}'")
        else:
            print(f"⚠️  Using existing recipient list: '{recipient_list.name}'")
            # Clear existing recipients to avoid duplicates
            recipient_list.recipients.clear()
            print("   Cleared existing recipients to avoid duplicates")
    except Exception as e:
        print(f"❌ Error creating recipient list: {e}")
        return False
    
    # Import Excel recipients
    excel_imported = 0
    excel_skipped = 0
    
    print(f"\n📊 Importing {len(df)} recipients from Excel...")
    
    with transaction.atomic():
        for index, row in df.iterrows():
            try:
                # Extract data from Excel row
                email = str(row['E-mail']).strip()
                first_name = str(row['First Name']).strip() if pd.notna(row['First Name']) else ""

                # Skip if email is invalid
                if not email or email == 'nan':
                    excel_skipped += 1
                    continue

                # Create or update recipient (no full_name field in model)
                recipient, created = Recipient.objects.get_or_create(
                    email=email,
                    defaults={
                        'first_name': first_name,
                        'last_name': "",  # As requested: leave blank
                        'organization': "",  # As requested: leave blank
                        'position': "",  # As requested: leave blank
                        'phone': "",  # As requested: leave blank
                        'location': "",  # As requested: leave blank
                        'is_active': True,
                        'subscribed': True,
                        'custom_data': {}
                    }
                )
                
                # Add to recipient list
                recipient_list.recipients.add(recipient)
                excel_imported += 1
                
                # Progress indicator
                if (index + 1) % 100 == 0:
                    print(f"   Processed {index + 1}/{len(df)} records...")
                    
            except Exception as e:
                print(f"   ⚠️  Error importing row {index + 1}: {e}")
                excel_skipped += 1
                continue
    
    print(f"✅ Excel import completed:")
    print(f"   - Successfully imported: {excel_imported} recipients")
    print(f"   - Skipped (errors): {excel_skipped} recipients")
    
    # Add manual recipients
    print(f"\n👤 Adding 2 manual recipients...")
    
    manual_recipients = [
        {
            'email': 'davina578@gmail.com',
            'first_name': 'Davina',
            'last_name': ''
        },
        {
            'email': 'quinta.omondi@gmail.com',
            'first_name': 'Quinta',
            'last_name': ''
        }
    ]
    
    manual_imported = 0
    manual_skipped = 0
    
    with transaction.atomic():
        for recipient_data in manual_recipients:
            try:
                recipient, created = Recipient.objects.get_or_create(
                    email=recipient_data['email'],
                    defaults={
                        'first_name': recipient_data['first_name'],
                        'last_name': recipient_data['last_name'],
                        'organization': "",  # As requested: leave blank
                        'position': "",  # As requested: leave blank
                        'phone': "",  # As requested: leave blank
                        'location': "",  # As requested: leave blank
                        'is_active': True,
                        'subscribed': True,
                        'custom_data': {}
                    }
                )

                # Add to recipient list
                recipient_list.recipients.add(recipient)
                manual_imported += 1

                print(f"   ✅ Added: {recipient_data['email']} ({recipient_data['first_name']})")
                
            except Exception as e:
                print(f"   ❌ Error adding {recipient_data['email']}: {e}")
                manual_skipped += 1
                continue
    
    # Final summary
    total_recipients = recipient_list.recipients.count()
    
    print(f"\n🎉 IMPORT COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print(f"📊 FINAL SUMMARY:")
    print(f"   • Excel recipients imported: {excel_imported}")
    print(f"   • Manual recipients added: {manual_imported}")
    print(f"   • Total recipients in list: {total_recipients}")
    print(f"   • Recipient list name: '{recipient_list.name}'")
    print(f"   • List description: {recipient_list.description}")
    
    # Verification
    expected_total = 999 + 2  # 999 from Excel + 2 manual
    if total_recipients == expected_total:
        print(f"✅ SUCCESS: Expected {expected_total} recipients, got {total_recipients}")
    else:
        print(f"⚠️  WARNING: Expected {expected_total} recipients, got {total_recipients}")
    
    return True

if __name__ == "__main__":
    success = import_general_clients()
    if success:
        print(f"\n🚀 Import completed successfully!")
        sys.exit(0)
    else:
        print(f"\n❌ Import failed!")
        sys.exit(1)
