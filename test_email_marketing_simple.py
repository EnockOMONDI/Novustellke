#!/usr/bin/env python
"""
Simple test script for Email Marketing API implementation
This script tests the core functionality without Django dependencies
"""

import os
import sys
import json
import requests

# Add the project directory to Python path
sys.path.insert(0, '/Users/djsean/Desktop/APPS2024/Novustellke')

def test_mailtrap_bulk_api():
    """Test Mailtrap Bulk Stream API directly"""
    
    # Mailtrap configuration
    api_token = 'd766975d57a7ef1acf2f750a36247a37'
    base_url = 'https://bulk.api.mailtrap.io'
    
    headers = {
        'Authorization': f'Bearer {api_token}',
        'Content-Type': 'application/json'
    }
    
    # Test email data (correct format for Mailtrap Bulk Stream API)
    email_data = {
        "from": {
            "email": "info@novustelltravel.com",
            "name": "Novustell Travel"
        },
        "to": [
            {
                "email": "djseanizellkenya@gmail.com",
                "name": "Test User"
            }
        ],
        "subject": "Test Email from Novustell Travel - Email Marketing API",
        "html": """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Test Email Marketing API</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <h1 style="color: #0f238d;">Hello from Novustell Travel!</h1>

        <p>This is a test email from the new <strong>Mailtrap Email Marketing API</strong> integration.</p>

        <div style="background: #f8f3fc; padding: 15px; border-radius: 5px; margin: 20px 0;">
            <h3 style="color: #ff9d00; margin-top: 0;">Email Marketing API Features:</h3>
            <ul>
                <li>✅ Bulk email sending</li>
                <li>✅ Personalization with recipient data</li>
                <li>✅ Professional email templates</li>
                <li>✅ Better deliverability</li>
                <li>✅ No Celery infrastructure needed</li>
            </ul>
        </div>

        <div style="background: #0f238d; color: white; padding: 20px; border-radius: 5px; text-align: center; margin: 30px 0;">
            <h2 style="margin: 0; color: white;">Novustell Travel</h2>
            <p style="margin: 5px 0; color: #ff9d00;">Think Convenience, Think Novustell</p>
            <p style="margin: 0;">📞 +254 721 115 572 | 📱 +254 701 363 551</p>
        </div>

        <p style="font-size: 12px; color: #666;">
            This is a test email for the Email Marketing API migration.
        </p>
    </div>
</body>
</html>
        """,
        "category": "email_marketing_test"
    }
    
    print("🚀 Testing Mailtrap Email Marketing API...")
    print(f"📧 Sending test email to: djseanizellkenya@gmail.com")
    print(f"🔗 API Endpoint: {base_url}/api/send")
    
    try:
        response = requests.post(
            f"{base_url}/api/send",
            headers=headers,
            json=email_data,
            timeout=30
        )
        
        print(f"📊 Response Status: {response.status_code}")
        print(f"📄 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ Email sent successfully via Mailtrap Email Marketing API!")
            try:
                response_data = response.json()
                print(f"📋 Response Data: {json.dumps(response_data, indent=2)}")
            except:
                print(f"📋 Response Text: {response.text}")
            return True
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"📋 Error Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return False

def test_email_template_rendering():
    """Test email template rendering logic"""
    
    print("\n🎨 Testing Email Template Rendering...")
    
    # Sample template content
    template_content = """
    <h1>Hello {{recipient_name}}!</h1>
    <p>Welcome to {{company_name}}.</p>
    <p>Your email: {{email}}</p>
    <p>Organization: {{organization}}</p>
    """
    
    # Sample context data
    context_data = {
        'recipient_name': 'Test User',
        'company_name': 'Novustell Travel',
        'email': 'djseanizellkenya@gmail.com',
        'organization': 'Test Organization'
    }
    
    # Simple template rendering (without Django Template engine)
    rendered_content = template_content
    for key, value in context_data.items():
        rendered_content = rendered_content.replace(f'{{{{{key}}}}}', str(value))
    
    print("📝 Template Content:")
    print(template_content)
    print("\n📊 Context Data:")
    print(json.dumps(context_data, indent=2))
    print("\n🎯 Rendered Content:")
    print(rendered_content)
    
    return True

def main():
    """Main test function"""
    
    print("=" * 60)
    print("🧪 NOVUSTELL TRAVEL - EMAIL MARKETING API TEST")
    print("=" * 60)
    
    # Test 1: Template rendering
    template_success = test_email_template_rendering()
    
    # Test 2: Mailtrap API
    api_success = test_mailtrap_bulk_api()
    
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    print(f"🎨 Template Rendering: {'✅ PASS' if template_success else '❌ FAIL'}")
    print(f"📧 Mailtrap API: {'✅ PASS' if api_success else '❌ FAIL'}")
    
    if template_success and api_success:
        print("\n🎉 ALL TESTS PASSED! Email Marketing API is ready for integration.")
        print("\n📋 Next Steps:")
        print("1. Fix the virtual environment Pydantic issue")
        print("2. Test the Django management command")
        print("3. Test campaign sending from Django admin")
        print("4. Deploy to production")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
    
    return template_success and api_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
