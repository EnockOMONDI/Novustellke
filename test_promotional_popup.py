#!/usr/bin/env python
"""
Comprehensive test suite for Promotional Popup functionality
Tests models, views, API endpoints, and admin interface
"""

import os
import sys
import django
import json
from datetime import datetime

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tours_travels.settings')
django.setup()

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from users.models import PromotionalPopup


class PromotionalPopupTestSuite:
    """Comprehensive test suite for promotional popup system"""
    
    def __init__(self):
        self.client = Client()
        self.test_results = []
        
    def log_test(self, test_name, status, message=""):
        """Log test results"""
        self.test_results.append({
            'test': test_name,
            'status': status,
            'message': message,
            'timestamp': datetime.now().strftime('%H:%M:%S')
        })
        status_icon = "✅" if status == "PASS" else "❌"
        print(f"{status_icon} {test_name}: {message}")
    
    def test_model_creation(self):
        """Test PromotionalPopup model creation and methods"""
        try:
            # Test model creation
            popup = PromotionalPopup.objects.create(
                title="Test Popup",
                inquiry_button_text="Test Button",
                inquiry_url="/test/",
                is_active=True,
                display_order=1
            )
            
            # Test string representation
            assert str(popup) == "Test Popup (Active)"
            
            # Test methods
            initial_views = popup.view_count
            initial_clicks = popup.click_count
            
            popup.increment_view_count()
            popup.increment_click_count()
            
            popup.refresh_from_db()
            assert popup.view_count == initial_views + 1
            assert popup.click_count == initial_clicks + 1
            
            # Test click-through rate calculation
            ctr = popup.click_through_rate
            assert ctr == 100.0  # 1 click / 1 view * 100
            
            # Test get_inquiry_url method
            assert popup.get_inquiry_url() == "/test/"
            
            popup.inquiry_url = ""
            assert popup.get_inquiry_url() == "/contactus/"
            
            self.log_test("Model Creation & Methods", "PASS", "All model functionality working correctly")
            return True
            
        except Exception as e:
            self.log_test("Model Creation & Methods", "FAIL", str(e))
            return False
    
    def test_api_endpoints(self):
        """Test API endpoints for popup data and tracking"""
        try:
            # Create test popup
            popup = PromotionalPopup.objects.create(
                title="API Test Popup",
                inquiry_button_text="API Test Button",
                inquiry_url="/api-test/",
                is_active=True,
                display_order=1
            )
            
            # Test get active popup endpoint
            response = self.client.get('/api/popup/active/')
            assert response.status_code == 200
            
            data = json.loads(response.content)
            assert data['success'] == True
            assert data['popup']['title'] == "API Test Popup"
            assert data['popup']['inquiry_button_text'] == "API Test Button"
            assert data['popup']['inquiry_url'] == "/api-test/"
            
            # Test click tracking endpoint
            response = self.client.post(
                '/api/popup/track-click/',
                data=json.dumps({'popup_id': popup.id}),
                content_type='application/json'
            )
            assert response.status_code == 200
            
            track_data = json.loads(response.content)
            assert track_data['success'] == True
            
            # Verify click was tracked
            popup.refresh_from_db()
            assert popup.click_count == 1
            
            self.log_test("API Endpoints", "PASS", "All API endpoints working correctly")
            return True
            
        except Exception as e:
            self.log_test("API Endpoints", "FAIL", str(e))
            return False
    
    def test_inactive_popup_handling(self):
        """Test handling of inactive popups"""
        try:
            # Deactivate all popups
            PromotionalPopup.objects.all().update(is_active=False)
            
            # Test API response for no active popups
            response = self.client.get('/api/popup/active/')
            assert response.status_code == 200
            
            data = json.loads(response.content)
            assert data['success'] == False
            assert 'No active popup available' in data['message']
            
            self.log_test("Inactive Popup Handling", "PASS", "Correctly handles no active popups")
            return True
            
        except Exception as e:
            self.log_test("Inactive Popup Handling", "FAIL", str(e))
            return False
    
    def test_popup_ordering(self):
        """Test popup display order functionality"""
        try:
            # Create multiple popups with different orders
            popup1 = PromotionalPopup.objects.create(
                title="Second Popup",
                display_order=2,
                is_active=True
            )
            
            popup2 = PromotionalPopup.objects.create(
                title="First Popup",
                display_order=1,
                is_active=True
            )
            
            popup3 = PromotionalPopup.objects.create(
                title="Third Popup",
                display_order=3,
                is_active=True
            )
            
            # Test that first popup by order is returned
            response = self.client.get('/api/popup/active/')
            data = json.loads(response.content)
            
            assert data['success'] == True
            assert data['popup']['title'] == "First Popup"
            
            self.log_test("Popup Ordering", "PASS", "Display order working correctly")
            return True
            
        except Exception as e:
            self.log_test("Popup Ordering", "FAIL", str(e))
            return False
    
    def test_homepage_integration(self):
        """Test popup integration with homepage"""
        try:
            # Test homepage loads successfully
            response = self.client.get('/')
            assert response.status_code == 200
            
            # Check that popup template is included
            content = response.content.decode('utf-8')
            assert 'promotional-popup-overlay' in content
            assert 'promotionalPopupModal' in content
            
            self.log_test("Homepage Integration", "PASS", "Popup integrated with homepage")
            return True
            
        except Exception as e:
            self.log_test("Homepage Integration", "FAIL", str(e))
            return False
    
    def test_error_handling(self):
        """Test error handling in API endpoints"""
        try:
            # Test tracking click for non-existent popup
            response = self.client.post(
                '/api/popup/track-click/',
                data=json.dumps({'popup_id': 99999}),
                content_type='application/json'
            )
            
            data = json.loads(response.content)
            assert data['success'] == False
            assert 'not found' in data['message'].lower()
            
            # Test tracking click without popup_id
            response = self.client.post(
                '/api/popup/track-click/',
                data=json.dumps({}),
                content_type='application/json'
            )
            
            data = json.loads(response.content)
            assert data['success'] == False
            assert 'required' in data['message'].lower()
            
            self.log_test("Error Handling", "PASS", "API error handling working correctly")
            return True
            
        except Exception as e:
            self.log_test("Error Handling", "FAIL", str(e))
            return False
    
    def run_all_tests(self):
        """Run all tests and display results"""
        print("🚀 Starting Promotional Popup Test Suite")
        print("=" * 60)
        
        # Clean up existing test data
        PromotionalPopup.objects.filter(title__contains="Test").delete()
        PromotionalPopup.objects.filter(title__contains="API").delete()
        
        tests = [
            self.test_model_creation,
            self.test_api_endpoints,
            self.test_inactive_popup_handling,
            self.test_popup_ordering,
            self.test_homepage_integration,
            self.test_error_handling
        ]
        
        passed = 0
        failed = 0
        
        for test in tests:
            if test():
                passed += 1
            else:
                failed += 1
        
        print("\n" + "=" * 60)
        print(f"📊 Test Results Summary:")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"📈 Success Rate: {(passed/(passed+failed)*100):.1f}%")
        
        if failed == 0:
            print("\n🎉 All tests passed! Promotional popup system is working correctly.")
        else:
            print(f"\n⚠️  {failed} test(s) failed. Please review the issues above.")
        
        return failed == 0


if __name__ == "__main__":
    test_suite = PromotionalPopupTestSuite()
    success = test_suite.run_all_tests()
    sys.exit(0 if success else 1)
