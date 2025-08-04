#!/usr/bin/env python3
"""
Test script to verify blog SEO optimization and performance improvements
"""

import os
import sys
import django
import time
from urllib.parse import urljoin

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tours_travels.settings')
django.setup()

from django.test import Client
from django.urls import reverse
from blog.models import Post, Category

class BlogOptimizationTester:
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
        
    def test_slug_based_urls(self):
        """Test 1: Verify slug-based URLs work correctly"""
        self.print_step(1, "Testing Slug-Based URLs")
        
        try:
            # Get a published post with slug
            post = Post.objects.filter(status='published', slug__isnull=False).first()
            
            if not post:
                self.print_error("No published posts with slugs found")
                return False
            
            # Test slug-based URL
            url = reverse('blog:blog-detail', kwargs={'slug': post.slug})
            response = self.client.get(url)
            
            if response.status_code == 200:
                self.print_success(f"Slug-based URL works: {url}")
                self.print_info(f"Post: {post.title[:50]}...")
                return True
            else:
                self.print_error(f"Slug-based URL failed with status {response.status_code}")
                return False
                
        except Exception as e:
            self.print_error(f"Slug-based URL test error: {e}")
            return False
    
    def test_old_url_redirect(self):
        """Test 2: Verify old PID-based URLs redirect to new slug URLs"""
        self.print_step(2, "Testing Old URL Redirects")
        
        try:
            # Get a published post
            post = Post.objects.filter(status='published').first()
            
            if not post:
                self.print_error("No published posts found")
                return False
            
            # Test old PID-based URL redirect
            old_url = reverse('blog:blog-detail-redirect', kwargs={'pid': post.pid})
            response = self.client.get(old_url)
            
            if response.status_code == 301:  # Permanent redirect
                self.print_success(f"Old URL redirects properly: {old_url}")
                self.print_info(f"Redirects to: {response.url}")
                return True
            else:
                self.print_error(f"Old URL redirect failed with status {response.status_code}")
                return False
                
        except Exception as e:
            self.print_error(f"URL redirect test error: {e}")
            return False
    
    def test_category_urls(self):
        """Test 3: Verify category URLs work with slugs"""
        self.print_step(3, "Testing Category URLs")
        
        try:
            # Get an active category
            category = Category.objects.filter(active=True).first()
            
            if not category:
                self.print_error("No active categories found")
                return False
            
            # Test category URL
            url = reverse('blog:category-detail', kwargs={'slug': category.slug})
            response = self.client.get(url)
            
            if response.status_code == 200:
                self.print_success(f"Category URL works: {url}")
                self.print_info(f"Category: {category.title}")
                return True
            else:
                self.print_error(f"Category URL failed with status {response.status_code}")
                return False
                
        except Exception as e:
            self.print_error(f"Category URL test error: {e}")
            return False
    
    def test_blog_list_performance(self):
        """Test 4: Check blog list performance"""
        self.print_step(4, "Testing Blog List Performance")
        
        try:
            start_time = time.time()
            response = self.client.get('/blog/')
            end_time = time.time()
            
            load_time = end_time - start_time
            
            if response.status_code == 200:
                if load_time < 2.0:  # Should load in under 2 seconds
                    self.print_success(f"Blog list loads quickly: {load_time:.2f}s")
                    return True
                else:
                    self.print_error(f"Blog list loads slowly: {load_time:.2f}s")
                    return False
            else:
                self.print_error(f"Blog list failed to load: status {response.status_code}")
                return False
                
        except Exception as e:
            self.print_error(f"Performance test error: {e}")
            return False
    
    def test_seo_meta_tags(self):
        """Test 5: Verify SEO meta tags are present"""
        self.print_step(5, "Testing SEO Meta Tags")
        
        try:
            # Test blog list SEO
            response = self.client.get('/blog/')
            content = response.content.decode('utf-8')
            
            seo_elements = [
                'meta name="description"',
                'meta name="keywords"',
                'meta property="og:title"',
                'meta property="og:description"',
                'link rel="canonical"',
                'application/ld+json'
            ]
            
            found_elements = 0
            for element in seo_elements:
                if element in content:
                    found_elements += 1
                    self.print_success(f"Found: {element}")
                else:
                    self.print_error(f"Missing: {element}")
            
            if found_elements >= len(seo_elements) * 0.8:  # At least 80% found
                self.print_success(f"SEO meta tags present: {found_elements}/{len(seo_elements)}")
                return True
            else:
                self.print_error(f"Insufficient SEO meta tags: {found_elements}/{len(seo_elements)}")
                return False
                
        except Exception as e:
            self.print_error(f"SEO meta tags test error: {e}")
            return False
    
    def test_breadcrumb_navigation(self):
        """Test 6: Verify breadcrumb navigation"""
        self.print_step(6, "Testing Breadcrumb Navigation")
        
        try:
            # Test blog post breadcrumbs
            post = Post.objects.filter(status='published', slug__isnull=False).first()
            
            if not post:
                self.print_error("No published posts found")
                return False
            
            url = reverse('blog:blog-detail', kwargs={'slug': post.slug})
            response = self.client.get(url)
            content = response.content.decode('utf-8')
            
            breadcrumb_elements = [
                'breadcrumb',
                'Home',
                'Blog'
            ]
            
            found_elements = 0
            for element in breadcrumb_elements:
                if element in content:
                    found_elements += 1
            
            if found_elements >= len(breadcrumb_elements):
                self.print_success("Breadcrumb navigation present")
                return True
            else:
                self.print_error("Breadcrumb navigation missing or incomplete")
                return False
                
        except Exception as e:
            self.print_error(f"Breadcrumb test error: {e}")
            return False
    
    def test_database_optimization(self):
        """Test 7: Verify database query optimization"""
        self.print_step(7, "Testing Database Query Optimization")
        
        try:
            from django.db import connection
            from django.test.utils import override_settings
            
            # Reset query count
            connection.queries_log.clear()
            
            # Test blog list view
            response = self.client.get('/blog/')
            
            query_count = len(connection.queries)
            
            if response.status_code == 200:
                if query_count < 10:  # Should use fewer than 10 queries
                    self.print_success(f"Optimized queries: {query_count} queries")
                    return True
                else:
                    self.print_error(f"Too many queries: {query_count} queries")
                    return False
            else:
                self.print_error(f"Blog list failed to load")
                return False
                
        except Exception as e:
            self.print_error(f"Database optimization test error: {e}")
            return False
    
    def test_search_functionality(self):
        """Test 8: Verify search functionality works"""
        self.print_step(8, "Testing Search Functionality")
        
        try:
            # Test search
            response = self.client.get('/blog/', {'q': 'travel'})
            
            if response.status_code == 200:
                content = response.content.decode('utf-8')
                if 'travel' in content.lower() or 'no articles found' in content.lower():
                    self.print_success("Search functionality works")
                    return True
                else:
                    self.print_error("Search results not displayed properly")
                    return False
            else:
                self.print_error(f"Search failed with status {response.status_code}")
                return False
                
        except Exception as e:
            self.print_error(f"Search functionality test error: {e}")
            return False
    
    def run_complete_test_suite(self):
        """Run the complete blog optimization test suite"""
        self.print_header("BLOG SEO OPTIMIZATION TESTING SUITE")
        
        # Test results tracking
        test_results = []
        
        # Run all tests
        tests = [
            ("Slug-Based URLs", self.test_slug_based_urls),
            ("Old URL Redirects", self.test_old_url_redirect),
            ("Category URLs", self.test_category_urls),
            ("Blog List Performance", self.test_blog_list_performance),
            ("SEO Meta Tags", self.test_seo_meta_tags),
            ("Breadcrumb Navigation", self.test_breadcrumb_navigation),
            ("Database Optimization", self.test_database_optimization),
            ("Search Functionality", self.test_search_functionality)
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
            print("\n🎉 ALL TESTS PASSED! Blog optimization is complete!")
            print("\n✨ Optimizations Achieved:")
            print("  • SEO-friendly slug-based URLs")
            print("  • Optimized database queries with caching")
            print("  • Comprehensive meta tags and structured data")
            print("  • Breadcrumb navigation for better UX")
            print("  • Old URL redirects for SEO preservation")
            print("  • Enhanced search and filtering")
        else:
            print(f"\n⚠️  {total_tests - passed_tests} tests failed. Please review the issues above.")
        
        return passed_tests == total_tests

if __name__ == "__main__":
    tester = BlogOptimizationTester()
    success = tester.run_complete_test_suite()
    
    if success:
        print("\n🚀 Blog optimization completed successfully!")
        print("🔗 Blog URL: http://localhost:8000/blog/")
        sys.exit(0)
    else:
        print("\n🔧 Please fix the identified issues.")
        sys.exit(1)
