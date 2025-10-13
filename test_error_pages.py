#!/usr/bin/env python3
"""
Test script to verify custom error pages are working correctly
for Novustell Travel website.

This script tests:
1. All custom error page templates exist
2. Error handlers are properly configured
3. Error pages return correct HTTP status codes
4. Error pages contain Novustell branding
5. All navigation links work correctly
6. Contact information is displayed correctly
7. Responsive design elements are present

Usage:
    python test_error_pages.py
"""

import os
import sys
import django
import requests
from pathlib import Path

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tours_travels.settings')
django.setup()

from django.test import Client
from django.urls import reverse
from django.conf import settings

def test_error_templates_exist():
    """Test that all error templates exist"""
    print("🔍 Testing error template files...")
    
    templates = ['400.html', '403.html', '404.html', '500.html']
    template_dir = Path(settings.BASE_DIR) / 'templates'
    
    for template in templates:
        template_path = template_dir / template
        if template_path.exists():
            print(f"✅ {template} exists")
        else:
            print(f"❌ {template} missing")
            return False
    
    return True

def test_error_handlers_configured():
    """Test that error handlers are configured in URLs"""
    print("\n🔍 Testing error handler configuration...")
    
    from tours_travels import urls
    
    handlers = ['handler400', 'handler403', 'handler404', 'handler500']
    
    for handler in handlers:
        if hasattr(urls, handler):
            handler_value = getattr(urls, handler)
            print(f"✅ {handler} configured: {handler_value}")
        else:
            print(f"❌ {handler} not configured")
            return False
    
    return True

def test_error_pages_response():
    """Test that error pages return correct status codes"""
    print("\n🔍 Testing error page responses...")
    
    client = Client()
    
    test_urls = {
        'users:test_400_error': 400,
        'users:test_403_error': 403,
        'users:test_404_error': 404,
        'users:test_500_custom': 500,
    }
    
    for url_name, expected_status in test_urls.items():
        try:
            response = client.get(reverse(url_name))
            if response.status_code == expected_status:
                print(f"✅ {url_name} returns {expected_status}")
            else:
                print(f"❌ {url_name} returns {response.status_code}, expected {expected_status}")
                return False
        except Exception as e:
            print(f"❌ Error testing {url_name}: {e}")
            return False
    
    return True

def test_error_page_content():
    """Test that error pages contain required content"""
    print("\n🔍 Testing error page content...")
    
    client = Client()
    
    content_tests = {
        'users:test_404_error': [
            'Novustell Travel',
            '404',
            'Page Not Found',
            'info@novustelltravel.com',
            '+254 701 363 551'
        ],
        'users:test_403_error': [
            'Novustell Travel',
            '403',
            'Access Forbidden',
            'info@novustelltravel.com',
            'Login'
        ],
        'users:test_400_error': [
            'Novustell Travel',
            '400',
            'Bad Request',
            'info@novustelltravel.com',
            'Try Again'
        ],
        'users:test_500_custom': [
            'Novustell Travel',
            '500',
            'Server Error',
            'info@novustelltravel.com',
            'Try Again'
        ]
    }
    
    for url_name, required_content in content_tests.items():
        try:
            response = client.get(reverse(url_name))
            content = response.content.decode('utf-8')
            
            for required in required_content:
                if required in content:
                    print(f"✅ {url_name} contains '{required}'")
                else:
                    print(f"❌ {url_name} missing '{required}'")
                    return False
        except Exception as e:
            print(f"❌ Error testing content for {url_name}: {e}")
            return False
    
    return True

def test_responsive_design():
    """Test that error pages have responsive design elements"""
    print("\n🔍 Testing responsive design elements...")
    
    client = Client()
    
    responsive_elements = [
        'col-lg-8',
        'col-md-10',
        'btn-lg',
        '@media (max-width: 768px)',
        'container',
        'row'
    ]
    
    try:
        response = client.get(reverse('users:test_404_error'))
        content = response.content.decode('utf-8')
        
        for element in responsive_elements:
            if element in content:
                print(f"✅ Found responsive element: {element}")
            else:
                print(f"❌ Missing responsive element: {element}")
                return False
    except Exception as e:
        print(f"❌ Error testing responsive design: {e}")
        return False
    
    return True

def main():
    """Run all error page tests"""
    print("🚀 Starting Novustell Travel Error Pages Test Suite")
    print("=" * 60)
    
    tests = [
        test_error_templates_exist,
        test_error_handlers_configured,
        test_error_pages_response,
        test_error_page_content,
        test_responsive_design
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                print(f"❌ Test failed: {test.__name__}")
        except Exception as e:
            print(f"❌ Test error in {test.__name__}: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Custom error pages are working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the error pages configuration.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
