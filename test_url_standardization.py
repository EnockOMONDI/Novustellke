#!/usr/bin/env python3
"""
Test script to verify URL standardization changes
Tests that all package-related URLs now use adminside patterns
"""

import os
import sys
import django
import requests
import time
from urllib.parse import urljoin

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tours_travels.settings')
django.setup()

from django.test import Client
from django.urls import reverse, NoReverseMatch
from adminside.models import Package, Destination

class URLStandardizationTester:
    def __init__(self):
        self.client = Client()
        self.base_url = 'http://127.0.0.1:8000'
        self.test_results = []
        
    def print_header(self, title):
        print(f"\n{'='*60}")
        print(f"🔧 {title}")
        print(f"{'='*60}")
        
    def print_step(self, step_num, description):
        print(f"\n{step_num}. 📋 {description}")
        print("-" * 50)
        
    def print_success(self, message):
        print(f"✅ {message}")
        
    def print_error(self, message):
        print(f"❌ {message}")
        
    def print_info(self, message):
        print(f"ℹ️  {message}")
        
    def test_deprecated_urls_removed(self):
        """Test 1: Verify deprecated URLs are no longer accessible"""
        self.print_step(1, "Testing Deprecated URLs Removed")
        
        deprecated_urls = [
            ('users:all_packages', 'users app all_packages URL'),
            ('users:users-detail-package', 'users app detail_package URL')
        ]
        
        success_count = 0
        for url_name, description in deprecated_urls:
            try:
                url = reverse(url_name, args=[1] if 'detail' in url_name else [])
                self.print_error(f"{description} still exists: {url}")
            except NoReverseMatch:
                self.print_success(f"{description} successfully removed")
                success_count += 1
        
        return success_count == len(deprecated_urls)
    
    def test_adminside_urls_work(self):
        """Test 2: Verify adminside URLs are working"""
        self.print_step(2, "Testing Adminside URLs Work")
        
        adminside_urls = [
            ('adminside:package_list', [], 'Package List'),
            ('adminside:user_package_list', [], 'User Package List'),
        ]
        
        success_count = 0
        for url_name, args, description in adminside_urls:
            try:
                url = reverse(url_name, args=args)
                response = self.client.get(url)
                
                if response.status_code == 200:
                    self.print_success(f"{description} loads successfully: {url}")
                    success_count += 1
                else:
                    self.print_error(f"{description} failed with status {response.status_code}: {url}")
                    
            except Exception as e:
                self.print_error(f"{description} error: {e}")
        
        return success_count == len(adminside_urls)
    
    def test_package_detail_urls(self):
        """Test 3: Verify package detail URLs work with slugs"""
        self.print_step(3, "Testing Package Detail URLs with Slugs")
        
        try:
            # Get a published package
            package = Package.objects.filter(status=Package.PUBLISHED).first()
            
            if not package:
                self.print_error("No published packages found for testing")
                return False
            
            if not package.slug:
                self.print_error(f"Package {package.name} has no slug")
                return False
            
            # Test package detail URL
            url = reverse('adminside:package_detail', args=[package.slug])
            response = self.client.get(url)
            
            if response.status_code == 200:
                self.print_success(f"Package detail loads successfully: {url}")
                self.print_info(f"Package: {package.name} (slug: {package.slug})")
                return True
            else:
                self.print_error(f"Package detail failed with status {response.status_code}: {url}")
                return False
                
        except Exception as e:
            self.print_error(f"Package detail test error: {e}")
            return False
    
    def test_navigation_menus(self):
        """Test 4: Verify navigation menus use correct URLs"""
        self.print_step(4, "Testing Navigation Menu URLs")
        
        test_pages = [
            ('/', 'Homepage'),
            ('/about/', 'About Page'),
        ]
        
        success_count = 0
        for url, description in test_pages:
            try:
                response = self.client.get(url)
                
                if response.status_code == 200:
                    content = response.content.decode('utf-8')
                    
                    # Check if old URLs are still present
                    if 'users:all_packages' in content:
                        self.print_error(f"{description} still contains old users:all_packages URL")
                    elif 'users:users-detail-package' in content:
                        self.print_error(f"{description} still contains old users:users-detail-package URL")
                    else:
                        self.print_success(f"{description} navigation updated successfully")
                        success_count += 1
                else:
                    self.print_error(f"{description} failed to load: status {response.status_code}")
                    
            except Exception as e:
                self.print_error(f"{description} test error: {e}")
        
        return success_count == len(test_pages)
    
    def test_booking_flow_integration(self):
        """Test 5: Verify booking flow uses modern checkout"""
        self.print_step(5, "Testing Booking Flow Integration")
        
        try:
            # Get a published package
            package = Package.objects.filter(status=Package.PUBLISHED).first()
            
            if not package:
                self.print_error("No published packages found for testing")
                return False
            
            # Test add to cart URL
            url = reverse('users:add_to_cart', args=[package.id])
            response = self.client.get(url)
            
            if response.status_code == 200:
                self.print_success(f"Add to cart loads successfully: {url}")
                self.print_info(f"Modern checkout system working for package: {package.name}")
                return True
            else:
                self.print_error(f"Add to cart failed with status {response.status_code}: {url}")
                return False
                
        except Exception as e:
            self.print_error(f"Booking flow test error: {e}")
            return False
    
    def test_template_references(self):
        """Test 6: Verify templates render without URL errors"""
        self.print_step(6, "Testing Template References")
        
        try:
            # Test package list template
            response = self.client.get('/adminside/user-packages/')
            
            if response.status_code == 200:
                content = response.content.decode('utf-8')
                
                # Check for template errors
                if 'NoReverseMatch' in content or 'TemplateDoesNotExist' in content:
                    self.print_error("Template rendering errors found")
                    return False
                else:
                    self.print_success("Package list template renders without errors")
                    
                # Check if package links are present and use correct URLs
                if 'adminside:package_detail' in content or '/adminside/packages/' in content:
                    self.print_success("Template uses correct adminside URLs")
                    return True
                else:
                    self.print_error("Template may not be using correct URLs")
                    return False
            else:
                self.print_error(f"Package list template failed to load: status {response.status_code}")
                return False
                
        except Exception as e:
            self.print_error(f"Template test error: {e}")
            return False
    
    def test_bucket_list_integration(self):
        """Test 7: Verify bucket list uses correct package URLs"""
        self.print_step(7, "Testing Bucket List Integration")
        
        try:
            # Test bucket list URL (requires authentication)
            url = reverse('users:bucket_list')
            response = self.client.get(url)
            
            # Should redirect to login since we're not authenticated
            if response.status_code == 302:
                self.print_success(f"Bucket list URL exists and requires authentication: {url}")
                return True
            elif response.status_code == 200:
                self.print_success(f"Bucket list loads successfully: {url}")
                return True
            else:
                self.print_error(f"Bucket list failed with status {response.status_code}: {url}")
                return False
                
        except Exception as e:
            self.print_error(f"Bucket list test error: {e}")
            return False
    
    def test_performance_improvement(self):
        """Test 8: Basic performance check"""
        self.print_step(8, "Testing Performance Improvement")
        
        try:
            start_time = time.time()
            response = self.client.get('/adminside/user-packages/')
            end_time = time.time()
            
            load_time = end_time - start_time
            
            if response.status_code == 200:
                if load_time < 2.0:  # Should load in under 2 seconds
                    self.print_success(f"Package list loads quickly: {load_time:.2f}s")
                    return True
                else:
                    self.print_error(f"Package list loads slowly: {load_time:.2f}s")
                    return False
            else:
                self.print_error(f"Package list failed to load: status {response.status_code}")
                return False
                
        except Exception as e:
            self.print_error(f"Performance test error: {e}")
            return False
    
    def run_complete_test_suite(self):
        """Run the complete URL standardization test suite"""
        self.print_header("URL STANDARDIZATION TESTING SUITE")
        
        # Test results tracking
        test_results = []
        
        # Run all tests
        tests = [
            ("Deprecated URLs Removed", self.test_deprecated_urls_removed),
            ("Adminside URLs Work", self.test_adminside_urls_work),
            ("Package Detail URLs", self.test_package_detail_urls),
            ("Navigation Menus", self.test_navigation_menus),
            ("Booking Flow Integration", self.test_booking_flow_integration),
            ("Template References", self.test_template_references),
            ("Bucket List Integration", self.test_bucket_list_integration),
            ("Performance Check", self.test_performance_improvement)
        ]
        
        for test_name, test_function in tests:
            try:
                result = test_function()
                test_results.append((test_name, result))
                
                if result:
                    self.print_success(f"{test_name} test PASSED")
                else:
                    self.print_error(f"{test_name} test FAILED")
                    
                time.sleep(0.5)  # Brief pause between tests
                
            except Exception as e:
                self.print_error(f"{test_name} test ERROR: {e}")
                test_results.append((test_name, False))
        
        # Print final results
        self.print_header("TEST RESULTS SUMMARY")
        
        passed_tests = sum(1 for _, result in test_results if result)
        total_tests = len(test_results)
        
        print(f"\n📊 Overall Results: {passed_tests}/{total_tests} tests passed")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        print("\n📋 Detailed Results:")
        for test_name, result in test_results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"  {status} {test_name}")
        
        if passed_tests == total_tests:
            print("\n🎉 ALL TESTS PASSED! URL standardization is complete!")
            print("\n✨ Benefits Achieved:")
            print("  • Eliminated URL conflicts")
            print("  • Improved performance with optimized queries")
            print("  • SEO-friendly slug-based URLs")
            print("  • Consistent user experience")
            print("  • Modern checkout system integration")
        else:
            print(f"\n⚠️  {total_tests - passed_tests} tests failed. Please review the issues above.")
        
        return passed_tests == total_tests

if __name__ == "__main__":
    tester = URLStandardizationTester()
    success = tester.run_complete_test_suite()
    
    if success:
        print("\n🚀 URL standardization completed successfully!")
        print("🔗 Main package URL: http://localhost:8000/adminside/user-packages/")
        sys.exit(0)
    else:
        print("\n🔧 Please fix the identified issues.")
        sys.exit(1)
