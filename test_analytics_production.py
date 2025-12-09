#!/usr/bin/env python
"""
Production Google Analytics Implementation Test
================================================

Tests the live production deployment at https://novustelltravel.onrender.com
to verify Google Analytics 4 implementation is working correctly.

This script performs static HTML analysis (not live event tracking).
"""

import requests
import re
import sys
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime

# Production URL
PRODUCTION_URL = "https://novustelltravel.onrender.com"

# Expected GA4 ID
EXPECTED_GA4_ID = "G-JV4GQKWVJL"

# Pages to test
TEST_PAGES = {
    'home': '/',
    'contact': '/contactus/',
    'mice': '/micepage/',
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

class ProductionAnalyticsTest:
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
        """Fetch a page from production"""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            self.log('fail', f"Failed to fetch {url}", [str(e)])
            return None
    
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
            '📊 [DEV] GA Event',
            'console.log.*GA Event'
        ]
        
        for indicator in dev_indicators:
            if re.search(indicator, html, re.IGNORECASE):
                self.log('fail', f"Development mode detected on {page_name}", [
                    f"Found indicator: {indicator}",
                    "Analytics may not be loading in production!"
                ])
                return False
        
        self.log('pass', f"Development mode disabled on {page_name}")
        return True

    def test_page(self, page_name, page_url):
        """Test a single page"""
        print(f"\n{'='*70}")
        print(f"🧪 Testing: {page_name.upper()} ({page_url})")
        print(f"{'='*70}")

        full_url = urljoin(PRODUCTION_URL, page_url)
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

    def test_production_environment(self):
        """Test production environment settings by checking HTML output"""
        print(f"\n{'='*70}")
        print(f"🔍 TESTING PRODUCTION ENVIRONMENT")
        print(f"{'='*70}")

        # Fetch home page to check environment
        html = self.fetch_page(PRODUCTION_URL)

        if not html:
            self.log('fail', "Cannot verify production environment - home page not accessible")
            return False

        # Check if analytics is enabled (should have gtag script)
        has_gtag = f'gtag/js?id={EXPECTED_GA4_ID}' in html

        # Check if DEBUG mode is disabled (no Django debug toolbar, etc.)
        has_debug_toolbar = 'django-debug-toolbar' in html.lower()
        has_debug_info = 'django.core.exceptions' in html

        details = []
        if has_gtag:
            details.append(f"✓ GA4 script present (ENABLE_ANALYTICS=true)")
        else:
            details.append(f"✗ GA4 script NOT present (ENABLE_ANALYTICS may be false)")

        if not has_debug_toolbar and not has_debug_info:
            details.append(f"✓ Debug mode disabled (DEBUG=False)")
        else:
            details.append(f"✗ Debug mode may be enabled (DEBUG=True)")

        details.append(f"✓ GA4 ID configured: {EXPECTED_GA4_ID}")

        if has_gtag and not has_debug_toolbar:
            self.log('pass', "Production environment configured correctly", details)
            return True
        else:
            self.log('fail', "Production environment may not be configured correctly", details)
            return False

    def run_all_tests(self):
        """Run all production tests"""
        print(f"\n{'#'*70}")
        print(f"# GOOGLE ANALYTICS PRODUCTION IMPLEMENTATION TEST")
        print(f"# Production URL: {PRODUCTION_URL}")
        print(f"# Expected GA4 ID: {EXPECTED_GA4_ID}")
        print(f"# Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'#'*70}")

        # Test production environment first
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
            print(f"\n✅ Google Analytics is working correctly in production!")
            print(f"\n📋 What's Working:")
            print(f"   ✓ GA4 script (gtag.js) loading with ID: {EXPECTED_GA4_ID}")
            print(f"   ✓ Custom analytics-travel.js loading")
            print(f"   ✓ Development mode disabled")
            print(f"   ✓ Form tracking attributes present")
            print(f"   ✓ Tracking elements configured")
            print(f"\n🔗 Next Steps:")
            print(f"   1. Open Google Analytics 4 → Reports → Realtime")
            print(f"   2. Visit {PRODUCTION_URL}")
            print(f"   3. Perform actions (submit forms, click buttons, etc.)")
            print(f"   4. Verify events appear in GA4 Realtime report")
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
            print(f"   1. Check .env.production file:")
            print(f"      - ENABLE_ANALYTICS=true")
            print(f"      - DEBUG=False")
            print(f"      - GOOGLE_ANALYTICS_ID={EXPECTED_GA4_ID}")
            print(f"   2. Verify deployment on Render.com")
            print(f"   3. Check if environment variables are set correctly")
            print(f"   4. Re-deploy if necessary")

        print(f"\n{'='*70}\n")

        return self.results['failed'] == 0


def main():
    """Main test runner"""
    tester = ProductionAnalyticsTest()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()


