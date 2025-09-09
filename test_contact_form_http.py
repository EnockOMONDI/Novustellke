#!/usr/bin/env python3
"""
HTTP Test for Contact Form
Tests the contact form submission via HTTP request
"""

import requests
import re
from urllib.parse import urljoin

def test_contact_form_submission():
    """Test contact form submission via HTTP"""
    base_url = "http://127.0.0.1:8000"
    contact_url = urljoin(base_url, "/contactus/")
    
    print("🧪 Testing Contact Form via HTTP")
    print("=" * 50)
    print(f"Contact URL: {contact_url}")
    
    try:
        # First, get the contact page to retrieve CSRF token
        print("\n📄 Getting contact page...")
        session = requests.Session()
        response = session.get(contact_url)
        
        if response.status_code == 200:
            print("✅ Contact page loaded successfully")
            
            # Extract CSRF token
            csrf_token = None
            csrf_match = re.search(r'name=["\']csrfmiddlewaretoken["\'] value=["\']([^"\']+)["\']', response.text)
            if csrf_match:
                csrf_token = csrf_match.group(1)
                print(f"✅ CSRF token extracted: {csrf_token[:20]}...")
            else:
                print("❌ CSRF token not found")
                return False
            
            # Prepare form data
            form_data = {
                'csrfmiddlewaretoken': csrf_token,
                'full_name': 'Test User',
                'email': 'test@example.com',
                'phone': '+254712345678',
                'company': 'Test Company',
                'subject': 'Corporate Travel',
                'message': 'This is a test message to verify the enhanced email templates are working correctly.',
                'privacy_consent': 'on'
            }
            
            print("\n📤 Submitting contact form...")
            
            # Submit the form
            submit_response = session.post(contact_url, data=form_data)
            
            if submit_response.status_code == 200:
                print("✅ Form submitted successfully")
                
                # Check for success message in response
                if "Thank you for your inquiry" in submit_response.text:
                    print("✅ Success message found in response")
                    
                    # Extract reference ID if present
                    ref_match = re.search(r'NVT-(\d{5})', submit_response.text)
                    if ref_match:
                        ref_id = ref_match.group(0)
                        print(f"✅ Reference ID found: {ref_id}")
                    
                    return True
                else:
                    print("❌ Success message not found in response")
                    print("Response content preview:")
                    print(submit_response.text[:500] + "...")
                    return False
            else:
                print(f"❌ Form submission failed with status: {submit_response.status_code}")
                return False
                
        else:
            print(f"❌ Failed to load contact page: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed - make sure Django server is running on port 8000")
        return False
    except Exception as e:
        print(f"❌ Error during HTTP test: {e}")
        return False

def test_contact_page_accessibility():
    """Test if contact page is accessible"""
    base_url = "http://127.0.0.1:8000"
    contact_url = urljoin(base_url, "/contactus/")
    
    print("\n🔍 Testing Contact Page Accessibility...")
    
    try:
        response = requests.get(contact_url, timeout=10)
        
        if response.status_code == 200:
            print("✅ Contact page is accessible")
            
            # Check for form elements
            form_checks = [
                ('Contact form', '<form' in response.text and 'contact-form' in response.text),
                ('Name field', 'name="full_name"' in response.text),
                ('Email field', 'name="email"' in response.text),
                ('Subject field', 'name="subject"' in response.text),
                ('Message field', 'name="message"' in response.text),
                ('Privacy consent', 'name="privacy_consent"' in response.text),
                ('CSRF token', 'csrfmiddlewaretoken' in response.text)
            ]
            
            print("\n🔍 Form Element Verification:")
            for check_name, check_result in form_checks:
                status = "✅" if check_result else "❌"
                print(f"  {status} {check_name}")
            
            return all(check[1] for check in form_checks)
        else:
            print(f"❌ Contact page not accessible: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error accessing contact page: {e}")
        return False

if __name__ == "__main__":
    print("🧪 CONTACT FORM HTTP TEST")
    print("=" * 60)
    
    # Test page accessibility first
    accessibility_test = test_contact_page_accessibility()
    
    # Test form submission
    submission_test = test_contact_form_submission()
    
    print("\n" + "=" * 60)
    print("📊 HTTP TEST SUMMARY")
    print("=" * 60)
    print(f"Page Accessibility: {'✅ PASS' if accessibility_test else '❌ FAIL'}")
    print(f"Form Submission: {'✅ PASS' if submission_test else '❌ FAIL'}")
    
    if accessibility_test and submission_test:
        print("\n🎉 ALL HTTP TESTS PASSED!")
        print("✅ Contact form is working correctly")
        print("✅ Enhanced email templates should be sending")
        print("📧 Check email inbox for test messages")
    else:
        print("\n⚠️ SOME HTTP TESTS FAILED")
        print("❌ Please review the error messages above")
    
    print("=" * 60)
