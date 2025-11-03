#!/usr/bin/env python
"""
Simple email test script for Novustell Travel
Tests the Mailtrap HTTP API integration
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append('/Users/djsean/Desktop/APPS2024/Novustellke')

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tours_travels.settings')
django.setup()

from users.tasks import send_email_via_mailtrap
from django.conf import settings

def test_simple_email():
    """Test basic email functionality"""
    print("🧪 Testing Mailtrap HTTP API...")
    print(f"Mailtrap API Token: {settings.MAILTRAP_API_TOKEN[:8]}...")
    print(f"From Email: {settings.DEFAULT_FROM_EMAIL}")
    
    # Send simple test email
    result = send_email_via_mailtrap(
        subject="🧪 Simple Email Test - Novustell Travel",
        html_message="""
        <h2>🧪 Email System Test</h2>
        <p>This is a simple test email to verify the Mailtrap HTTP API is working correctly.</p>
        <p><strong>Test Details:</strong></p>
        <ul>
            <li>Sent via: Mailtrap HTTP API</li>
            <li>From: Novustell Travel</li>
            <li>Time: Just now</li>
            <li>Purpose: Basic functionality verification</li>
        </ul>
        <p>If you receive this email, the basic email system is working! ✅</p>
        <hr>
        <p><em>Novustell Travel - Think Convenience, Think Novustell</em></p>
        """,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=['djseanizellkenya@gmail.com']
    )
    
    print(f"📧 Email sending result: {result}")
    if result:
        print("✅ SUCCESS: Email sent successfully via Mailtrap HTTP API!")
        print("📬 Please check your inbox at djseanizellkenya@gmail.com")
        return True
    else:
        print("❌ FAILED: Email could not be sent")
        return False

if __name__ == "__main__":
    test_simple_email()
