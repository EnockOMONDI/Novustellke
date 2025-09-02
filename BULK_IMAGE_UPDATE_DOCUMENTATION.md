# Novustell Travel - Bulk Image Update System Documentation

## Overview

The Bulk Image Update System provides comprehensive tools for exporting travel data to Excel format and performing bulk image updates across the Novustell Travel database. This system supports destinations, packages, accommodations, and deals.

## Features

### ✅ Excel Export Functionality
- **Complete Database Export**: All travel-related data with image URLs
- **Structured Sheets**: Separate sheets for each data type
- **Image URL Extraction**: Current UploadCare URLs included
- **Metadata Included**: All relevant fields for each record type

### ✅ Bulk Image Update System
- **Multiple Update Methods**: Management commands, Django admin integration
- **Dry Run Mode**: Preview changes before applying
- **Error Handling**: Comprehensive validation and error reporting
- **Backup Creation**: Automatic backup before bulk operations
- **Progress Tracking**: Real-time progress indicators

## Installation & Setup

### 1. Install Required Packages
```bash
pip install openpyxl pandas
```

### 2. Verify Management Commands
```bash
python manage.py help export_to_excel
python manage.py help bulk_update_images
```

## Usage Methods

### Method 1: Django Management Commands

#### Export Data to Excel
```bash
# Basic export
python manage.py export_to_excel

# Custom output file and path
python manage.py export_to_excel --output my_export.xlsx --path /path/to/directory

# Example output
python manage.py export_to_excel --output novustell_export_2024.xlsx --path ./exports/
```

#### Bulk Update Images
```bash
# Dry run (preview only)
python manage.py bulk_update_images path/to/updated_file.xlsx --dry-run

# Update specific sheet only
python manage.py bulk_update_images path/to/updated_file.xlsx --sheet Packages --dry-run

# Apply changes with backup
python manage.py bulk_update_images path/to/updated_file.xlsx --backup

# Update all sheets
python manage.py bulk_update_images path/to/updated_file.xlsx
```

### Method 2: Django Admin Interface

#### Access Bulk Operations
1. Login to Django Admin: `/admin/`
2. Navigate to "Bulk Export" or "Bulk Import" (available in admin menu)

#### Export Process
1. Go to `/admin/bulk-export/`
2. Click "Export to Excel"
3. Download the generated Excel file

#### Import Process
1. Go to `/admin/bulk-import/`
2. Upload your updated Excel file
3. Check "Dry Run" for preview
4. Click "Process Excel File"
5. Review results and apply if satisfied

## Excel File Structure

### Sheet: "Destinations"
| Column | Description |
|--------|-------------|
| ID | Destination ID (required for updates) |
| Name | Destination name |
| Slug | URL slug |
| Destination Type | Country/City/Place |
| Description | Full description (HTML stripped) |
| Current Image URL | UploadCare CDN URL |
| Parent Destination | Parent destination name |
| Meta Title | SEO title |
| Meta Description | SEO description |
| Starting Price | Base price |
| Is Active | Active status |
| Created At | Creation timestamp |
| Updated At | Last update timestamp |

### Sheet: "Packages"
| Column | Description |
|--------|-------------|
| ID | Package ID (required for updates) |
| Name | Package name |
| Slug | URL slug |
| Description | Package description |
| Main Destination | Primary destination |
| Adult Price | Adult pricing |
| Child Price | Child pricing |
| Duration Days | Trip duration |
| Status | Publication status |
| Featured Image URL | UploadCare CDN URL |
| Is Featured | Featured status |
| Created At | Creation timestamp |
| Updated At | Last update timestamp |

### Sheet: "Accommodations"
| Column | Description |
|--------|-------------|
| ID | Accommodation ID (required for updates) |
| Name | Accommodation name |
| Slug | URL slug |
| Description | Accommodation description |
| Destination | Location destination |
| Accommodation Type | Hotel/Lodge/Camp type |
| Price Per Night | Nightly rate |
| Featured Image URL | UploadCare CDN URL |
| Is Active | Active status |
| Created At | Creation timestamp |
| Updated At | Last update timestamp |

### Sheet: "Deals"
| Column | Description |
|--------|-------------|
| ID | Deal ID (required for updates) |
| Title | Deal title |
| Slug | URL slug |
| Description | Deal description |
| Discount Percentage | Discount amount |
| Original Price | Pre-discount price |
| Discounted Price | Final price |
| Valid From | Start date |
| Valid Until | End date |
| Featured Image URL | UploadCare CDN URL |
| Is Active | Active status |
| Is Featured | Featured status |
| Created At | Creation timestamp |
| Updated At | Last update timestamp |

## Image URL Requirements

### Supported Formats
- **Direct URLs**: `https://example.com/image.jpg`
- **UploadCare URLs**: `https://ucarecdn.com/uuid/`
- **File Extensions**: .jpg, .jpeg, .png, .gif, .webp

### URL Validation
- URLs must be accessible and return valid image content
- UploadCare URLs are preferred for consistency
- Invalid URLs will be skipped with error messages

## Best Practices

### 1. Always Use Dry Run First
```bash
python manage.py bulk_update_images file.xlsx --dry-run
```

### 2. Create Backups
```bash
python manage.py bulk_update_images file.xlsx --backup
```

### 3. Process in Batches
- For large datasets, consider processing one sheet at a time
- Use `--sheet` parameter to target specific data types

### 4. Validate Excel File
- Ensure ID column is first column
- Verify "Image URL" column exists
- Check for empty rows or invalid data

### 5. Monitor Progress
- Watch console output for progress indicators
- Review error messages for failed updates
- Verify changes in Django admin after completion

## Error Handling

### Common Errors and Solutions

#### "Excel file not found"
- **Cause**: Incorrect file path
- **Solution**: Verify file path and permissions

#### "No image URL column found"
- **Cause**: Missing or incorrectly named image URL column
- **Solution**: Ensure column is named "Image URL" (case insensitive)

#### "Record with ID X not found"
- **Cause**: Invalid or deleted record ID
- **Solution**: Verify IDs exist in database, remove invalid rows

#### "Failed to upload image"
- **Cause**: Invalid URL or network issues
- **Solution**: Check URL accessibility, verify image format

### Error Logs
- All errors are logged with detailed messages
- Use dry-run mode to identify issues before applying changes
- Check Django logs for detailed error information

## Performance Considerations

### Large Datasets
- **Batch Processing**: Process sheets individually for large datasets
- **Memory Usage**: Monitor memory usage during bulk operations
- **Network Timeouts**: Allow extra time for image downloads/uploads

### Optimization Tips
- Use UploadCare URLs when possible (faster processing)
- Remove unnecessary rows from Excel file
- Process during low-traffic periods

## Security Considerations

### Access Control
- Bulk operations require Django admin access
- Implement proper user permissions
- Monitor bulk operation logs

### Data Validation
- All URLs are validated before processing
- Invalid data is skipped with error messages
- Backup creation prevents data loss

## Troubleshooting

### Command Not Found
```bash
# Verify Django app is installed
python manage.py check

# List available commands
python manage.py help
```

### Import Errors
```bash
# Check required packages
pip list | grep openpyxl
pip list | grep pandas

# Install if missing
pip install openpyxl pandas
```

### Permission Errors
```bash
# Check file permissions
ls -la path/to/excel/file.xlsx

# Verify Django has write access to output directory
```

## Support

For technical support or questions about the bulk image update system:

1. **Check Logs**: Review Django logs for detailed error messages
2. **Dry Run**: Always test with dry-run mode first
3. **Documentation**: Refer to this documentation for common issues
4. **Backup**: Ensure backups are created before bulk operations

## Version History

- **v1.0**: Initial implementation with management commands
- **v1.1**: Added Django admin integration
- **v1.2**: Enhanced error handling and validation
- **v1.3**: Added backup functionality and progress tracking

---

**Last Updated**: December 2024  
**Compatibility**: Django 4.2+, Python 3.8+  
**Dependencies**: openpyxl, pandas, pyuploadcare
