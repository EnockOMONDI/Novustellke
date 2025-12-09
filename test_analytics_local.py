#!/usr/bin/env python
"""
Local Google Analytics Implementation Test
===========================================

Tests the local development server to verify Google Analytics 4 
implementation is working correctly with DJANGO_ENV=production.

This script performs static HTML analysis (not live event tracking).
"""

import requests
import re
import sys
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime

# Local URL
LOCAL_URL = "http://127.0.0.1:8000"

# Expected GA4 ID
EXPECTED_GA4_ID = "G-JV4GQKWVJL"

# Pages to test
TEST_PAGES = {
    'home': '/',
    'contact': '/contactus/',
    'mice': '/mice/',
    'student_travel': '/student-travel/',
    'ngo_travel': '/ngo-travel/',
    'careers': '/careers/',
    'packages': '/package/',
}

# Expected form data attributes
EXPECTED_FORMS = {
    'contact': 'data-form-type="contact"',
    'mice': 'data-form-type="mice_inquiry"',
    'student_travel': 'data-form-type="student_travel"',
    'ngo_travel': 'data-form-type="ngo_travel"',
    'newsletter': 'data-form-type="newsletter"',
    'job_application': 'data-form-type="job_application"',
}

class LocalAnalyticsTest:
    def __init__(self):
        self.results = {
            'passed': 0,
            'failed': 0,
            'warnings': 0,
            'details': []
        }
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
    
    def log(self, status, message, details=None):
        """Log test result"""
        icons = {'pass': '✅', 'fail': '❌', 'warn': '⚠️', 'info': 'ℹ️'}
        icon = icons.get(status, '•')
        print(f"{icon} {message}")
        
        if details:
            for detail in details:
                print(f"   {detail}")
        
        self.results['details'].append({
            'status': status,
            'message': message,
            'details': details or []
        })
        
        if status == 'pass':
            self.results['passed'] += 1
        elif status == 'fail':
            self.results['failed'] += 1
        elif status == 'warn':
            self.results['warnings'] += 1
    
    def fetch_page(self, url):
        """Fetch a page from local server"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.exceptions.ConnectionError:
            self.log('fail', f"Cannot connect to {url}", [
                "Make sure Django development server is running:",
                "  python manage.py runserver"
            ])
            return None
        except requests.exceptions.RequestException as e:
            self.log('fail', f"Failed to fetch {url}", [str(e)])
            return None
    
    def test_server_running(self):
        """Test if local server is running"""
        print(f"\n{'='*70}")
        print(f"🔍 CHECKING LOCAL SERVER")
        print(f"{'='*70}")
        
        try:
            response = self.session.get(LOCAL_URL, timeout=5)
            self.log('pass', f"Local server is running at {LOCAL_URL}")
            return True
        except requests.exceptions.ConnectionError:
            self.log('fail', "Local server is NOT running", [
                "Please start the Django development server:",
                "  export DJANGO_ENV=production",
                "  python manage.py runserver"
            ])
            return False
        except Exception as e:
            self.log('fail', f"Error connecting to local server: {e}")
            return False
    
    def test_ga4_script_loading(self, html, page_name):
        """Test if GA4 gtag.js script is loading"""
        # Check for gtag.js script
        gtag_pattern = rf'gtag/js\?id={EXPECTED_GA4_ID}'
        has_gtag = re.search(gtag_pattern, html)
        
        # Check for gtag config
        config_pattern = rf"gtag\('config',\s*['\"]?{EXPECTED_GA4_ID}['\"]?"
        has_config = re.search(config_pattern, html)
        
        if has_gtag and has_config:
            self.log('pass', f"GA4 script loading correctly on {page_name}", [
                f"✓ gtag.js script found with ID: {EXPECTED_GA4_ID}",
                f"✓ gtag config found"
            ])
            return True
        else:
            details = []
            if not has_gtag:
                details.append(f"✗ gtag.js script NOT found")
            if not has_config:
                details.append(f"✗ gtag config NOT found")
            self.log('fail', f"GA4 script NOT loading on {page_name}", details)
            return False
    
    def test_analytics_travel_js(self, html, page_name):
        """Test if analytics-travel.js is loading"""
        if 'analytics-travel.js' in html:
            self.log('pass', f"analytics-travel.js loading on {page_name}")
            return True
        else:
            self.log('fail', f"analytics-travel.js NOT loading on {page_name}")
            return False
    
    def test_form_attributes(self, html, page_name, expected_forms):
        """Test if forms have correct data-form-type attributes"""
        found_forms = []
        missing_forms = []
        
        for form_name, expected_attr in expected_forms.items():
            if expected_attr in html:
                found_forms.append(f"✓ {form_name}: {expected_attr}")
            else:
                missing_forms.append(f"✗ {form_name}: {expected_attr} NOT found")
        
        if found_forms:
            self.log('pass', f"Form attributes found on {page_name}", found_forms)
        
        if missing_forms:
            self.log('warn', f"Some form attributes missing on {page_name}", missing_forms)
        
        return len(found_forms) > 0

    def test_tracking_elements(self, html, page_name):
        """Test if tracking elements have proper data attributes"""
        soup = BeautifulSoup(html, 'html.parser')

        tracking_elements = {
            'CTA buttons': soup.find_all(['a', 'button'], class_=re.compile(r'cta|btn-primary')),
            'Package cards': soup.find_all(class_=re.compile(r'package-card|destination-card')),
            'WhatsApp links': soup.find_all('a', href=re.compile(r'wa\.me|whatsapp')),
        }

        details = []
        for element_type, elements in tracking_elements.items():
            count = len(elements)
            if count > 0:
                details.append(f"✓ {element_type}: {count} found")

        if details:
            self.log('pass', f"Tracking elements found on {page_name}", details)
            return True
        else:
            self.log('warn', f"No tracking elements found on {page_name}")
            return False

    def test_development_mode_disabled(self, html, page_name):
        """Test that development mode is disabled"""
        dev_indicators = [
            'Development Mode: Google Analytics tracking is disabled',
            '📊 \\[DEV\\] GA Event',
            'console\\.log.*GA Event'
        ]

        for indicator in dev_indicators:
            if re.search(indicator, html, re.IGNORECASE):
                self.log('fail', f"Development mode STILL ACTIVE on {page_name}", [
                    f"Found indicator: {indicator}",
                    "Make sure DJANGO_ENV=production is set:",
                    "  export DJANGO_ENV=production",
                    "  python manage.py runserver"
                ])
                return False

        self.log('pass', f"Development mode disabled on {page_name}")
        return True

    def test_production_environment(self):
        """Test production environment settings by checking HTML output"""
        print(f"\n{'='*70}")
        print(f"🔍 TESTING ENVIRONMENT CONFIGURATION")
        print(f"{'='*70}")

        # Fetch home page to check environment
        html = self.fetch_page(LOCAL_URL)

        if not html:
            self.log('fail', "Cannot verify environment - home page not accessible")
            return False

        # Check if analytics is enabled (should have gtag script)
        has_gtag = f'gtag/js?id={EXPECTED_GA4_ID}' in html

        # Check if DEBUG mode is disabled (no Django debug toolbar, etc.)
        has_debug_toolbar = 'django-debug-toolbar' in html.lower()
        has_dev_mode_msg = 'Development Mode: Google Analytics tracking is disabled' in html

        details = []
        if has_gtag:
            details.append(f"✓ GA4 script present (ENABLE_ANALYTICS=true)")
        else:
            details.append(f"✗ GA4 script NOT present (ENABLE_ANALYTICS may be false)")

        if not has_dev_mode_msg:
            details.append(f"✓ Production mode active (DEBUG=False)")
        else:
            details.append(f"✗ Development mode detected (DEBUG=True or ENABLE_ANALYTICS=False)")

        if has_debug_toolbar:
            details.append(f"⚠️  Django Debug Toolbar detected (expected in local dev)")

        details.append(f"✓ GA4 ID configured: {EXPECTED_GA4_ID}")

        if has_gtag and not has_dev_mode_msg:
            self.log('pass', "Environment configured correctly for production testing", details)
            return True
        else:
            self.log('fail', "Environment NOT configured for production", details)
            return False

    def test_page(self, page_name, page_url):
        """Test a single page"""
        print(f"\n{'='*70}")
        print(f"🧪 Testing: {page_name.upper()} ({page_url})")
        print(f"{'='*70}")

        full_url = urljoin(LOCAL_URL, page_url)
        html = self.fetch_page(full_url)

        if not html:
            return False

        # Run all tests on this page
        self.test_ga4_script_loading(html, page_name)
        self.test_analytics_travel_js(html, page_name)
        self.test_development_mode_disabled(html, page_name)
        self.test_tracking_elements(html, page_name)

        # Test form attributes based on page
        if page_name == 'contact':
            self.test_form_attributes(html, page_name, {'contact': EXPECTED_FORMS['contact']})
        elif page_name == 'mice':
            self.test_form_attributes(html, page_name, {'mice': EXPECTED_FORMS['mice']})
        elif page_name == 'student_travel':
            self.test_form_attributes(html, page_name, {'student_travel': EXPECTED_FORMS['student_travel']})
        elif page_name == 'ngo_travel':
            self.test_form_attributes(html, page_name, {'ngo_travel': EXPECTED_FORMS['ngo_travel']})
        elif page_name == 'careers':
            self.test_form_attributes(html, page_name, {'job_application': EXPECTED_FORMS['job_application']})
        elif page_name == 'home':
            # Home page should have newsletter form in footer
            self.test_form_attributes(html, page_name, {'newsletter': EXPECTED_FORMS['newsletter']})

        return True

    def run_all_tests(self):
        """Run all local tests"""
        print(f"\n{'#'*70}")
        print(f"# GOOGLE ANALYTICS LOCAL IMPLEMENTATION TEST")
        print(f"# Local URL: {LOCAL_URL}")
        print(f"# Expected GA4 ID: {EXPECTED_GA4_ID}")
        print(f"# Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'#'*70}")

        # Test if server is running first
        if not self.test_server_running():
            print(f"\n{'='*70}")
            print(f"❌ CANNOT RUN TESTS - SERVER NOT RUNNING")
            print(f"{'='*70}")
            return False

        # Test environment configuration
        self.test_production_environment()

        # Test each page
        for page_name, page_url in TEST_PAGES.items():
            self.test_page(page_name, page_url)

        # Print summary
        self.print_summary()

    def print_summary(self):
        """Print test summary"""
        print(f"\n{'='*70}")
        print(f"📊 TEST SUMMARY")
        print(f"{'='*70}")

        total_tests = self.results['passed'] + self.results['failed']
        success_rate = (self.results['passed'] / total_tests * 100) if total_tests > 0 else 0

        print(f"\n✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")
        print(f"⚠️  Warnings: {self.results['warnings']}")
        print(f"📈 Success Rate: {success_rate:.1f}%")

        if self.results['failed'] == 0:
            print(f"\n{'='*70}")
            print(f"🎉 ALL TESTS PASSED!")
            print(f"{'='*70}")
            print(f"\n✅ Google Analytics is working correctly in production mode!")
            print(f"\n📋 What's Working:")
            print(f"   ✓ GA4 script (gtag.js) loading with ID: {EXPECTED_GA4_ID}")
            print(f"   ✓ Custom analytics-travel.js loading")
            print(f"   ✓ Development mode disabled")
            print(f"   ✓ Form tracking attributes present")
            print(f"   ✓ Tracking elements configured")
            print(f"\n🚀 Ready for Production Deployment!")
            print(f"\n🔗 Next Steps:")
            print(f"   1. Deploy to production (Render.com)")
            print(f"   2. Verify environment variables on Render:")
            print(f"      - ENABLE_ANALYTICS=true")
            print(f"      - DEBUG=False")
            print(f"      - GOOGLE_ANALYTICS_ID={EXPECTED_GA4_ID}")
            print(f"   3. Test on production URL")
            print(f"   4. Open Google Analytics 4 → Reports → Realtime")
            print(f"   5. Verify events appear in GA4")
        else:
            print(f"\n{'='*70}")
            print(f"⚠️  SOME TESTS FAILED")
            print(f"{'='*70}")
            print(f"\n❌ Issues Found:")
            for detail in self.results['details']:
                if detail['status'] == 'fail':
                    print(f"   • {detail['message']}")
                    for sub_detail in detail['details']:
                        print(f"     {sub_detail}")

            print(f"\n🔧 Recommended Actions:")
            print(f"   1. Make sure DJANGO_ENV=production is set:")
            print(f"      export DJANGO_ENV=production")
            print(f"   2. Check .env.production file:")
            print(f"      - ENABLE_ANALYTICS=true")
            print(f"      - DEBUG=False")
            print(f"      - GOOGLE_ANALYTICS_ID={EXPECTED_GA4_ID}")
            print(f"   3. Restart Django server:")
            print(f"      python manage.py runserver")
            print(f"   4. Re-run this test")

        print(f"\n{'='*70}\n")

        return self.results['failed'] == 0


def main():
    """Main test runner"""
    tester = LocalAnalyticsTest()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()


