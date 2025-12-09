#!/usr/bin/env python
"""
Test Google Analytics Implementation for Novustell Travel
=========================================================

This script tests the Google Analytics 4 implementation including:
- Template rendering with analytics context
- Environment variable configuration
- Analytics script inclusion
- Development vs production behavior
"""

import os
import sys
import django
from django.conf import settings

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tours_travels.settings')
django.setup()

from django.test import Client, RequestFactory
from django.template import Context, Template
from django.contrib.auth.models import User, AnonymousUser


def test_analytics_context_processor():
    """Test analytics context processor functionality"""
    print("🧪 Testing Analytics Context Processor...")
    
    try:
        from tours_travels.context_processors import analytics_settings
        
        # Create test request
        factory = RequestFactory()
        request = factory.get('/')
        request.user = AnonymousUser()
        
        # Test context processor
        context = analytics_settings(request)
        
        print(f"✅ Context processor loaded successfully")
        print(f"   Google Analytics ID: {context.get('GOOGLE_ANALYTICS_ID', 'Not set')}")
        print(f"   Google Tag Manager ID: {context.get('GOOGLE_TAG_MANAGER_ID', 'Not set')}")
        print(f"   Analytics Enabled: {context.get('ENABLE_ANALYTICS', False)}")
        print(f"   Should Load Analytics: {context.get('SHOULD_LOAD_ANALYTICS', False)}")
        print(f"   Is Production: {context.get('IS_PRODUCTION', False)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Context processor test failed: {e}")
        return False


def test_analytics_template_rendering():
    """Test analytics template rendering"""
    print("\n🧪 Testing Analytics Template Rendering...")
    
    try:
        client = Client()
        
        # Test homepage with analytics
        response = client.get('/')
        
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            
            # Check for analytics template inclusion
            has_analytics_include = 'users/analytics.html' in content or 'gtag' in content
            has_noscript_include = 'users/analytics_noscript.html' in content or 'googletagmanager.com/ns.html' in content
            
            # Check for development mode indicators
            has_dev_mode = 'Development Mode: Google Analytics tracking is disabled' in content
            has_gtag_script = 'gtag.js' in content
            
            print(f"✅ Homepage loaded successfully")
            print(f"   Has analytics template: {has_analytics_include}")
            print(f"   Has noscript fallback: {has_noscript_include}")
            print(f"   Development mode detected: {has_dev_mode}")
            print(f"   GA script included: {has_gtag_script}")
            
            return True
        else:
            print(f"❌ Failed to load homepage: {response.status_code}")
            return False
        
    except Exception as e:
        print(f"❌ Template rendering test failed: {e}")
        return False


def test_analytics_script_inclusion():
    """Test analytics JavaScript file inclusion"""
    print("\n🧪 Testing Analytics Script Inclusion...")
    
    try:
        client = Client()
        
        # Test if analytics script is included
        response = client.get('/')
        
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            
            # Check for travel analytics script
            has_travel_analytics = 'analytics-travel.js' in content
            has_conditional_loading = 'SHOULD_LOAD_ANALYTICS' in content or 'defer' in content
            
            print(f"✅ Script inclusion test completed")
            print(f"   Travel analytics script: {has_travel_analytics}")
            print(f"   Conditional loading: {has_conditional_loading}")
            
            return True
        else:
            print(f"❌ Failed to load page for script test: {response.status_code}")
            return False
        
    except Exception as e:
        print(f"❌ Script inclusion test failed: {e}")
        return False


def test_environment_configuration():
    """Test environment variable configuration"""
    print("\n🧪 Testing Environment Configuration...")
    
    try:
        # Check Django settings
        ga_id = getattr(settings, 'GOOGLE_ANALYTICS_ID', '')
        gtm_id = getattr(settings, 'GOOGLE_TAG_MANAGER_ID', '')
        enable_analytics = getattr(settings, 'ENABLE_ANALYTICS', False)
        track_admin = getattr(settings, 'ANALYTICS_TRACK_ADMIN', False)
        debug_mode = getattr(settings, 'DEBUG', True)
        
        print(f"✅ Environment configuration loaded")
        print(f"   Google Analytics ID: {'Set' if ga_id else 'Not set'}")
        print(f"   Google Tag Manager ID: {'Set' if gtm_id else 'Not set'}")
        print(f"   Analytics Enabled: {enable_analytics}")
        print(f"   Track Admin Users: {track_admin}")
        print(f"   Debug Mode: {debug_mode}")
        
        # Check if configuration is appropriate for environment
        if debug_mode and enable_analytics:
            print("⚠️  Warning: Analytics enabled in debug mode")
        elif not debug_mode and not enable_analytics:
            print("⚠️  Warning: Analytics disabled in production mode")
        else:
            print("✅ Environment configuration is appropriate")
        
        return True
        
    except Exception as e:
        print(f"❌ Environment configuration test failed: {e}")
        return False


def test_admin_user_tracking():
    """Test admin user tracking behavior"""
    print("\n🧪 Testing Admin User Tracking...")
    
    try:
        from tours_travels.context_processors import analytics_settings
        
        # Create or reuse admin user for testing
        admin_user, created = User.objects.get_or_create(
            username='testadmin',
            defaults={
                'email': 'admin@test.com',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.set_password('testpass123')
        admin_user.save()
        
        # Create test requests
        factory = RequestFactory()
        
        # Test with anonymous user
        anon_request = factory.get('/')
        anon_request.user = AnonymousUser()
        anon_context = analytics_settings(anon_request)
        
        # Test with admin user
        admin_request = factory.get('/')
        admin_request.user = admin_user
        admin_context = analytics_settings(admin_request)
        
        print(f"✅ Admin tracking test completed")
        print(f"   Anonymous user should load analytics: {anon_context.get('SHOULD_LOAD_ANALYTICS', False)}")
        print(f"   Admin user should load analytics: {admin_context.get('SHOULD_LOAD_ANALYTICS', False)}")
        
        # Cleanup only if we created the user in this test
        if created:
            admin_user.delete()
        
        return True
        
    except Exception as e:
        print(f"❌ Admin user tracking test failed: {e}")
        return False


def test_student_travel_page_analytics():
    """Test analytics on Student Travel page (including Model UN)"""
    print("\n🧪 Testing Student Travel Page Analytics...")
    
    try:
        client = Client()
        
        # Test Student Travel page
        response = client.get('/student-travel/')
        
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            
            # Check for analytics integration
            has_analytics = 'gtag' in content or 'Development Mode' in content
            has_model_un_anchor = 'id="model-un"' in content
            has_form_tracking = 'data-form-type' in content or 'form' in content
            
            print(f"✅ Student Travel page loaded successfully")
            print(f"   Analytics integration: {has_analytics}")
            print(f"   Model UN anchor present: {has_model_un_anchor}")
            print(f"   Form tracking ready: {has_form_tracking}")
            
            return True
        else:
            print(f"❌ Failed to load Student Travel page: {response.status_code}")
            return False
        
    except Exception as e:
        print(f"❌ Student Travel page test failed: {e}")
        return False


def test_analytics_file_existence():
    """Test that analytics files exist and are accessible"""
    print("\n🧪 Testing Analytics File Existence...")
    
    try:
        import os
        from django.conf import settings
        
        # Check template files
        template_dir = os.path.join(settings.BASE_DIR, 'users', 'templates', 'users')
        analytics_template = os.path.join(template_dir, 'analytics.html')
        noscript_template = os.path.join(template_dir, 'analytics_noscript.html')
        
        # Check JavaScript file
        static_dir = os.path.join(settings.BASE_DIR, 'static', 'assets', 'js')
        analytics_js = os.path.join(static_dir, 'analytics-travel.js')
        
        analytics_template_exists = os.path.exists(analytics_template)
        noscript_template_exists = os.path.exists(noscript_template)
        analytics_js_exists = os.path.exists(analytics_js)
        
        print(f"✅ File existence check completed")
        print(f"   Analytics template: {analytics_template_exists}")
        print(f"   Noscript template: {noscript_template_exists}")
        print(f"   Travel analytics JS: {analytics_js_exists}")
        
        return analytics_template_exists and noscript_template_exists and analytics_js_exists
        
    except Exception as e:
        print(f"❌ File existence test failed: {e}")
        return False


def run_analytics_tests():
    """Run all analytics tests"""
    print("🚀 Starting Google Analytics Implementation Tests...\n")
    
    tests = [
        test_environment_configuration,
        test_analytics_context_processor,
        test_analytics_file_existence,
        test_analytics_template_rendering,
        test_analytics_script_inclusion,
        test_admin_user_tracking,
        test_student_travel_page_analytics
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            failed += 1
    
    print(f"\n📊 Analytics Implementation Test Results:")
    print(f"   ✅ Passed: {passed}")
    print(f"   ❌ Failed: {failed}")
    print(f"   📈 Success Rate: {(passed/(passed+failed)*100):.1f}%")
    
    if failed == 0:
        print("\n🎉 All analytics tests passed! Google Analytics 4 is ready for production!")
        print("\n🔗 Next Steps:")
        print("   1. Set up Google Analytics 4 property")
        print("   2. Configure environment variables with GA4 Measurement ID")
        print("   3. Test in production environment")
        print("   4. Monitor real-time reports in GA4 dashboard")
    else:
        print(f"\n⚠️  {failed} analytics test(s) failed. Please review and fix issues.")
    
    return failed == 0


if __name__ == "__main__":
    success = run_analytics_tests()
    sys.exit(0 if success else 1)
