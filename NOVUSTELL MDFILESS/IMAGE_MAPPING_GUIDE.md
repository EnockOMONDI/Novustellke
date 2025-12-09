# Image Mapping Guide for Partial Update

## Package Images Mapping (17 images)

### Your Collected Image → Database Record Name (Excel Sheet: "Packages")

1. **Maasai-Mara-Safari-Adventure-Package-real.jpg**
   - Maps to: "Maasai Mara Safari Adventure"
   - Look for: Record with name containing "Maasai Mara" and "Safari"

2. **Kenya-Highlights-Explorer-Package-real.jpg**
   - Maps to: "Kenya Highlights Explorer"
   - Look for: Record with name containing "Kenya" and "Highlights"

3. **Luxury-Kenya-Safari-Beach-Package-real.jpg**
   - Maps to: "Luxury Kenya Safari & Beach"
   - Look for: Record with name containing "Luxury Kenya Safari Beach"

4. **Serengeti-Migration-Safari-Package-real.jpg**
   - Maps to: "Serengeti Migration Safari"
   - Look for: Record with name containing "Serengeti" and "Migration"

5. **Tanzania-Grand-Circuit-Package-real.jpg**
   - Maps to: "Tanzania Grand Circuit"
   - Look for: Record with name containing "Tanzania" and "Grand Circuit"

6. **Kilimanjaro-Safari-Combo-Package-real.jpg**
   - Maps to: "Kilimanjaro Safari Combo"
   - Look for: Record with name containing "Kilimanjaro" and "Safari"

7. **Kruger-Safari-Budget-Package-real.jpg**
   - Maps to: "Kruger Safari Budget"
   - Look for: Record with name containing "Kruger" and "Budget"

8. **Luxury-South-Africa-Explorer-Package-real.jpg**
   - Maps to: "Luxury South Africa Explorer"
   - Look for: Record with name containing "Luxury South Africa"

9. **Garden-Route-Adventure-Package-real.jpg**
   - Maps to: "Garden Route Adventure"
   - Look for: Record with name containing "Garden Route"

10. **Cape-Town-Wine-Country-Package-real.jpg**
    - Maps to: "Cape Town Wine Country"
    - Look for: Record with name containing "Cape Town" and "Wine"

11. **Gorilla-Trekking-Experience-Package-real.jpg**
    - Maps to: "Gorilla Trekking Experience"
    - Look for: Record with name containing "Gorilla Trekking"

12. **Complete-Rwanda-Adventure-Package-real.jpg**
    - Maps to: "Complete Rwanda Adventure"
    - Look for: Record with name containing "Complete Rwanda"

13. **Rwanda-Cultural-Discovery-Package-real.jpg**
    - Maps to: "Rwanda Cultural Discovery"
    - Look for: Record with name containing "Rwanda Cultural"

14. **Lake-Kivu-Relaxation-Package-real.jpg**
    - Maps to: "Lake Kivu Relaxation"
    - Look for: Record with name containing "Lake Kivu"

15. **Dubai-City-Explorer-Package-real.jpg**
    - Maps to: "Dubai City Explorer"
    - Look for: Record with name containing "Dubai City"

16. **Dubai-Budget-Adventure-Package-real.jpg**
    - Maps to: "Dubai Budget Adventure"
    - Look for: Record with name containing "Dubai Budget"

17. **Luxury-Dubai-Experience-Package-real.jpg**
    - Maps to: "Luxury Dubai Experience"
    - Look for: Record with name containing "Luxury Dubai"

## Destination Images Mapping (12 images)

### Your Collected Image → Database Record Name (Excel Sheet: "Destinations")

1. **Kenya-Destination-real.jpg**
   - Maps to: "Kenya"
   - Look for: Record with name exactly "Kenya"

2. **Tanzania-Destination-real.jpg**
   - Maps to: "Tanzania"
   - Look for: Record with name exactly "Tanzania"

3. **Rwanda-Destination-real.jpg**
   - Maps to: "Rwanda"
   - Look for: Record with name exactly "Rwanda"

4. **South-Africa-Destination-real.jpg**
   - Maps to: "South Africa"
   - Look for: Record with name exactly "South Africa"

5. **Nairobi-Destination-real.jpg**
   - Maps to: "Nairobi"
   - Look for: Record with name exactly "Nairobi"

6. **Mombasa-Destination-real.jpg**
   - Maps to: "Mombasa"
   - Look for: Record with name exactly "Mombasa"

7. **Johannesburg-Destination-real.jpg**
   - Maps to: "Johannesburg"
   - Look for: Record with name exactly "Johannesburg"

8. **Kigali-Destination-real.jpg**
   - Maps to: "Kigali"
   - Look for: Record with name exactly "Kigali"

9. **Maasai-Mara-Destination-real.jpg**
   - Maps to: "Maasai Mara" or "Masai Mara"
   - Look for: Record with name containing "Maasai Mara" or "Masai Mara"

10. **Serengeti-Destination-real.jpg**
    - Maps to: "Serengeti"
    - Look for: Record with name exactly "Serengeti"

11. **Kruger-National-Park-Destination-real.jpg**
    - Maps to: "Kruger National Park"
    - Look for: Record with name containing "Kruger National Park"

12. **Nairobi-National-Park-Destination-real.jpg**
    - Maps to: "Nairobi National Park"
    - Look for: Record with name containing "Nairobi National Park"

## Excel Update Instructions

### Step-by-Step Process:

1. **Open Excel File**: `partial_image_update_20250902.xlsx`

2. **Go to Packages Sheet**:
   - Find the "Featured Image URL" column
   - For each of your 17 package images, find the matching record
   - Paste the UploadCare CDN URL in the "Featured Image URL" cell

3. **Go to Destinations Sheet**:
   - Find the "Current Image URL" column
   - For each of your 12 destination images, find the matching record
   - Paste the UploadCare CDN URL in the "Current Image URL" cell

4. **Save the Excel File**:
   - Save as: `partial_image_update_20250902_UPDATED.xlsx`

### Example URL Format:
```
https://ucarecdn.com/12345678-1234-1234-1234-123456789abc/
```

### Important Notes:
- Only update records that have corresponding collected images
- Leave other records unchanged
- Double-check the record names match your image filenames
- Ensure URLs are complete UploadCare CDN URLs

## Verification Checklist

Before running the bulk update:

- [ ] All 25 images uploaded to UploadCare successfully
- [ ] All 25 UploadCare URLs copied and ready
- [ ] Excel file opened and correct sheets identified
- [ ] 17 package records found and URLs updated
- [ ] 12 destination records found and URLs updated
- [ ] Excel file saved with new name
- [ ] Ready to run bulk_update_images command

## Next Steps After Mapping

1. **Preview Changes**:
   ```bash
   python manage.py bulk_update_images partial_image_update_20250902_UPDATED.xlsx --dry-run
   ```

2. **Apply Changes**:
   ```bash
   python manage.py bulk_update_images partial_image_update_20250902_UPDATED.xlsx --backup
   ```

3. **Verify Results**:
   - Check Django admin for updated image fields
   - Visit website to see new images displayed
   - Confirm 25 records now have new images
