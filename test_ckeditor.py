#!/usr/bin/env python
"""
Test script to verify CKEditor functionality in Django admin
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tours_travels.settings')
django.setup()

from django.contrib.auth.models import User
from adminside.models import Package, Destination, Accommodation
from blog.models import Post, Category
from django.test import Client
from django.urls import reverse

def test_ckeditor_admin_integration():
    """Test CKEditor integration in Django admin"""
    
    print("🧪 Testing CKEditor Admin Integration")
    print("=" * 50)
    
    # Test 1: Check if CKEditor is properly configured
    print("1. Testing CKEditor Configuration...")
    try:
        from ckeditor.fields import RichTextField
        from ckeditor_uploader.fields import RichTextUploadingField
        print("   ✅ CKEditor imports successful")
    except ImportError as e:
        print(f"   ❌ CKEditor import failed: {e}")
        return False
    
    # Test 2: Check model field configurations
    print("\n2. Testing Model Field Configurations...")
    
    # Test Package model
    try:
        package_fields = Package._meta.get_fields()
        rich_text_fields = [f for f in package_fields if isinstance(f, RichTextField)]
        print(f"   ✅ Package model has {len(rich_text_fields)} RichTextField(s)")
        for field in rich_text_fields:
            print(f"      - {field.name}")
    except Exception as e:
        print(f"   ❌ Package model test failed: {e}")
    
    # Test Destination model
    try:
        destination_fields = Destination._meta.get_fields()
        rich_text_fields = [f for f in destination_fields if isinstance(f, RichTextField)]
        print(f"   ✅ Destination model has {len(rich_text_fields)} RichTextField(s)")
        for field in rich_text_fields:
            print(f"      - {field.name}")
    except Exception as e:
        print(f"   ❌ Destination model test failed: {e}")
    
    # Test Accommodation model
    try:
        accommodation_fields = Accommodation._meta.get_fields()
        rich_text_fields = [f for f in accommodation_fields if isinstance(f, RichTextField)]
        print(f"   ✅ Accommodation model has {len(rich_text_fields)} RichTextField(s)")
        for field in rich_text_fields:
            print(f"      - {field.name}")
    except Exception as e:
        print(f"   ❌ Accommodation model test failed: {e}")
    
    # Test Blog Post model
    try:
        post_fields = Post._meta.get_fields()
        rich_text_fields = [f for f in post_fields if isinstance(f, RichTextField)]
        print(f"   ✅ Post model has {len(rich_text_fields)} RichTextField(s)")
        for field in rich_text_fields:
            print(f"      - {field.name}")
    except Exception as e:
        print(f"   ❌ Post model test failed: {e}")
    
    # Test 3: Check CKEditor configurations
    print("\n3. Testing CKEditor Configurations...")
    try:
        from django.conf import settings
        ckeditor_configs = getattr(settings, 'CKEDITOR_CONFIGS', {})
        print(f"   ✅ Found {len(ckeditor_configs)} CKEditor configurations:")
        for config_name in ckeditor_configs.keys():
            print(f"      - {config_name}")
            
        # Check specific configurations
        if 'default' in ckeditor_configs:
            default_config = ckeditor_configs['default']
            toolbar = default_config.get('toolbar_Custom', [])
            print(f"      Default config has {len(toolbar)} toolbar groups")
            
        if 'blog' in ckeditor_configs:
            blog_config = ckeditor_configs['blog']
            styles = blog_config.get('stylesSet', [])
            print(f"      Blog config has {len(styles)} custom styles")
            
        if 'minimal' in ckeditor_configs:
            print("      Minimal config available")
            
    except Exception as e:
        print(f"   ❌ CKEditor configuration test failed: {e}")
    
    # Test 4: Check admin registration
    print("\n4. Testing Admin Registration...")
    try:
        from django.contrib import admin
        
        # Check if models are registered
        registered_models = admin.site._registry.keys()
        models_to_check = [Package, Destination, Accommodation, Post]
        
        for model in models_to_check:
            if model in registered_models:
                print(f"   ✅ {model.__name__} is registered in admin")
            else:
                print(f"   ❌ {model.__name__} is NOT registered in admin")
                
    except Exception as e:
        print(f"   ❌ Admin registration test failed: {e}")
    
    # Test 5: Check static files configuration
    print("\n5. Testing Static Files Configuration...")
    try:
        from django.conf import settings
        
        # Check if CKEditor is in INSTALLED_APPS
        installed_apps = getattr(settings, 'INSTALLED_APPS', [])
        if 'ckeditor' in installed_apps:
            print("   ✅ 'ckeditor' is in INSTALLED_APPS")
        else:
            print("   ❌ 'ckeditor' is NOT in INSTALLED_APPS")
            
        if 'ckeditor_uploader' in installed_apps:
            print("   ✅ 'ckeditor_uploader' is in INSTALLED_APPS")
        else:
            print("   ❌ 'ckeditor_uploader' is NOT in INSTALLED_APPS")
            
        # Check upload path
        upload_path = getattr(settings, 'CKEDITOR_UPLOAD_PATH', None)
        if upload_path:
            print(f"   ✅ CKEditor upload path: {upload_path}")
        else:
            print("   ❌ CKEditor upload path not configured")
            
    except Exception as e:
        print(f"   ❌ Static files configuration test failed: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 CKEditor Integration Test Complete!")
    print("\nNext Steps:")
    print("1. Log into admin interface at http://127.0.0.1:8000/admin/")
    print("2. Navigate to any model with RichTextField")
    print("3. Verify CKEditor toolbar appears and functions correctly")
    print("4. Test image upload functionality")
    print("5. Test custom styles and formatting options")
    
    return True

def create_test_data():
    """Create test data for CKEditor testing"""
    print("\n📝 Creating Test Data...")
    
    try:
        # Create a test destination
        destination, created = Destination.objects.get_or_create(
            name="Test Destination",
            defaults={
                'slug': 'test-destination',
                'destination_type': 'city',
                'description': '<h2>Welcome to Test Destination</h2><p>This is a <span style="background-color: #ff9d00; color: white; padding: 2px 8px; border-radius: 3px;">travel highlight</span> for testing CKEditor functionality.</p>'
            }
        )
        if created:
            print("   ✅ Test destination created")
        else:
            print("   ℹ️  Test destination already exists")
            
        # Create a test category
        category, created = Category.objects.get_or_create(
            title="Test Category",
            defaults={'slug': 'test-category'}
        )
        if created:
            print("   ✅ Test category created")
        else:
            print("   ℹ️  Test category already exists")
            
        # Create a test blog post
        post, created = Post.objects.get_or_create(
            title="Test Blog Post",
            defaults={
                'slug': 'test-blog-post',
                'excerpt': '<p>This is a <strong>test excerpt</strong> with <em>rich text formatting</em>.</p>',
                'content': '''
                <h2 style="color: #0f238d; font-weight: bold; margin-bottom: 15px;">Blog Heading</h2>
                <p>This is a comprehensive test of CKEditor functionality with various formatting options:</p>
                <ul>
                    <li><strong>Bold text</strong></li>
                    <li><em>Italic text</em></li>
                    <li><u>Underlined text</u></li>
                </ul>
                <div style="background-color: #f8f9fa; border-left: 4px solid #0f238d; padding: 15px; margin: 15px 0;">
                    <strong>Travel Tip:</strong> This is a custom styled travel tip box.
                </div>
                <p>Visit <span style="color: #0f238d; font-weight: bold; font-size: 1.1em;">Paris</span> for an amazing experience!</p>
                ''',
                'category': category,
                'status': 'published'
            }
        )
        if created:
            print("   ✅ Test blog post created")
        else:
            print("   ℹ️  Test blog post already exists")
            
    except Exception as e:
        print(f"   ❌ Test data creation failed: {e}")

if __name__ == "__main__":
    test_ckeditor_admin_integration()
    create_test_data()
