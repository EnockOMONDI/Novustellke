#!/usr/bin/env python3
"""
Script to organize collected real images into proper folder structure for UploadCare upload
"""

import os
import shutil
from pathlib import Path

def organize_collected_images():
    """
    Organize collected real images into a separate folder structure for UploadCare upload
    """
    
    # Define the collected images
    collected_images = {
        'packages': [
            'Maasai-Mara-Safari-Adventure-Package-real.jpg',
            'Kenya-Highlights-Explorer-Package-real.jpg',
            'Luxury-Kenya-Safari-Beach-Package-real.jpg',
            'Serengeti-Migration-Safari-Package-real.jpg',
            'Tanzania-Grand-Circuit-Package-real.jpg',
            'Kilimanjaro-Safari-Combo-Package-real.jpg',
            'Kruger-Safari-Budget-Package-real.jpg',
            'Luxury-South-Africa-Explorer-Package-real.jpg',
            'Garden-Route-Adventure-Package-real.jpg',
            'Cape-Town-Wine-Country-Package-real.jpg',
            'Gorilla-Trekking-Experience-Package-real.jpg',
            'Complete-Rwanda-Adventure-Package-real.jpg',
            'Rwanda-Cultural-Discovery-Package-real.jpg',
            'Lake-Kivu-Relaxation-Package-real.jpg',
            'Dubai-City-Explorer-Package-real.jpg',
            'Dubai-Budget-Adventure-Package-real.jpg',
            'Luxury-Dubai-Experience-Package-real.jpg'
        ],
        'destinations': [
            'Kenya-Destination-real.jpg',
            'Tanzania-Destination-real.jpg',
            'Rwanda-Destination-real.jpg',
            'South-Africa-Destination-real.jpg',
            'Nairobi-Destination-real.jpg',
            'Mombasa-Destination-real.jpg',
            'Johannesburg-Destination-real.jpg',
            'Kigali-Destination-real.jpg',
            'Maasai-Mara-Destination-real.jpg',
            'Serengeti-Destination-real.jpg',
            'Kruger-National-Park-Destination-real.jpg',
            'Nairobi-National-Park-Destination-real.jpg'  # Converted from PNG
        ]
    }
    
    # Create output directory structure
    output_base = Path('collected-images-for-uploadcare')
    output_base.mkdir(exist_ok=True)
    
    # Create category folders
    for category in ['packages', 'destinations', 'accommodations']:
        (output_base / category).mkdir(exist_ok=True)
    
    # Source directory (where your downloaded images are)
    source_dir = Path('.')  # Adjust this path to where your images are located
    
    # Copy collected images to organized structure
    copied_count = 0
    missing_count = 0
    
    print("🗂️  Organizing collected images for UploadCare upload...")
    print("=" * 60)
    
    for category, filenames in collected_images.items():
        print(f"\n📁 Processing {category}:")
        
        for filename in filenames:
            source_file = source_dir / filename
            dest_file = output_base / category / filename
            
            if source_file.exists():
                shutil.copy2(source_file, dest_file)
                print(f"   ✅ Copied: {filename}")
                copied_count += 1
            else:
                print(f"   ❌ Missing: {filename}")
                missing_count += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Summary:")
    print(f"   ✅ Images copied: {copied_count}")
    print(f"   ❌ Images missing: {missing_count}")
    print(f"   📁 Output folder: {output_base.absolute()}")
    
    if missing_count > 0:
        print(f"\n⚠️  {missing_count} images were not found in the current directory.")
        print("   Please ensure all collected images are in the same folder as this script.")
    
    print(f"\n🚀 Next steps:")
    print(f"   1. Upload all images from '{output_base}' to UploadCare")
    print(f"   2. Export database to Excel")
    print(f"   3. Map UploadCare URLs to corresponding records")
    print(f"   4. Use bulk_update_images command to update database")

if __name__ == "__main__":
    organize_collected_images()
