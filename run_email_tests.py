#!/usr/bin/env python3
"""
Novustell Travel Email Test Runner
=================================

Simple script to run email system tests with different configurations.

Usage:
    python run_email_tests.py                    # Run all tests
    python run_email_tests.py --quick           # Run quick health check
    python run_email_tests.py --production      # Test production environment
    python run_email_tests.py --development     # Test development environment
    python run_email_tests.py --ci              # Run CI-friendly tests (no actual email sending)

Author: Novustell Travel Development Team
Last Updated: December 15, 2024
"""

import os
import sys
import argparse
import subprocess
import time
from datetime import datetime

def print_banner():
    """Print test runner banner"""
    print("=" * 80)
    print("🚀 NOVUSTELL TRAVEL EMAIL SYSTEM TEST RUNNER")
    print("=" * 80)
    print(f"📅 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🐍 Python: {sys.version.split()[0]}")
    print(f"📁 Working Directory: {os.getcwd()}")
    print("=" * 80)

def check_prerequisites():
    """Check if all prerequisites are met"""
    print("🔍 Checking Prerequisites...")
    
    # Check if Django is available
    try:
        import django
        print(f"✅ Django {django.get_version()} - Available")
    except ImportError:
        print("❌ Django - Not installed")
        return False
    
    # Check if test file exists
    if not os.path.exists('test_email_system_comprehensive.py'):
        print("❌ test_email_system_comprehensive.py - Not found")
        return False
    else:
        print("✅ test_email_system_comprehensive.py - Found")
    
    # Check if environment files exist
    env_files = ['.env.production', '.env.development']
    for env_file in env_files:
        if os.path.exists(env_file):
            print(f"✅ {env_file} - Found")
        else:
            print(f"⚠️  {env_file} - Not found (optional)")
    
    # Check if Django settings are configured
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tours_travels.settings')
        django.setup()
        print("✅ Django Settings - Configured")
    except Exception as e:
        print(f"❌ Django Settings - Error: {e}")
        return False
    
    print("✅ All prerequisites met!")
    return True

def run_quick_test():
    """Run quick health check"""
    print("\n🏥 Running Quick Health Check...")
    
    try:
        # Import and run quick test
        exec(open('test_email_system_comprehensive.py').read())
        
        # Run quick test function
        result = run_quick_test()
        
        if result:
            print("🎉 Quick test PASSED - Email system is healthy!")
            return True
        else:
            print("⚠️  Quick test FAILED - Check email system configuration")
            return False
            
    except Exception as e:
        print(f"❌ Quick test ERROR: {e}")
        return False

def run_comprehensive_tests(test_type=None):
    """Run comprehensive test suite"""
    print(f"\n🧪 Running Comprehensive Tests{f' ({test_type})' if test_type else ''}...")
    
    # Build command
    cmd = ['python', 'test_email_system_comprehensive.py']
    if test_type:
        cmd.append(f'--{test_type}')
    
    try:
        # Run tests
        start_time = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)  # 5 minute timeout
        end_time = time.time()
        
        duration = end_time - start_time
        
        # Print results
        print(f"⏱️  Test Duration: {duration:.2f} seconds")
        
        if result.returncode == 0:
            print("✅ Comprehensive tests PASSED!")
            print("\n📊 Test Output:")
            print(result.stdout)
            return True
        else:
            print("❌ Comprehensive tests FAILED!")
            print("\n📊 Test Output:")
            print(result.stdout)
            if result.stderr:
                print("\n🚨 Error Output:")
                print(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ Tests timed out after 5 minutes")
        return False
    except Exception as e:
        print(f"❌ Test execution error: {e}")
        return False

def run_ci_tests():
    """Run CI-friendly tests (no actual email sending)"""
    print("\n🤖 Running CI-Friendly Tests...")
    
    # Run configuration and template tests only
    test_categories = ['config', 'templates']
    all_passed = True
    
    for category in test_categories:
        print(f"\n📋 Testing {category.title()}...")
        if not run_comprehensive_tests(category):
            all_passed = False
    
    return all_passed

def validate_environment():
    """Validate email environment configuration"""
    print("\n🌍 Validating Environment Configuration...")
    
    try:
        exec(open('test_email_system_comprehensive.py').read())
        
        # Run environment validation
        result = validate_email_system_health()
        
        if result:
            print("✅ Environment validation PASSED!")
            return True
        else:
            print("❌ Environment validation FAILED!")
            return False
            
    except Exception as e:
        print(f"❌ Environment validation ERROR: {e}")
        return False

def print_summary(results):
    """Print test execution summary"""
    print("\n" + "=" * 80)
    print("📊 TEST EXECUTION SUMMARY")
    print("=" * 80)
    
    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result)
    failed_tests = total_tests - passed_tests
    
    print(f"📈 Total Test Categories: {total_tests}")
    print(f"✅ Passed: {passed_tests}")
    print(f"❌ Failed: {failed_tests}")
    
    if failed_tests == 0:
        print("\n🎉 ALL TESTS PASSED! Email system is fully operational.")
        success_rate = 100.0
    else:
        success_rate = (passed_tests / total_tests) * 100
        print(f"\n⚠️  {failed_tests} test categories failed.")
    
    print(f"📊 Success Rate: {success_rate:.1f}%")
    
    # Print individual results
    print("\n📋 Detailed Results:")
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {test_name}: {status}")
    
    print("=" * 80)
    print(f"🕐 Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    return failed_tests == 0

def main():
    """Main test runner function"""
    parser = argparse.ArgumentParser(description='Novustell Travel Email Test Runner')
    parser.add_argument('--quick', action='store_true', help='Run quick health check only')
    parser.add_argument('--production', action='store_true', help='Test production environment')
    parser.add_argument('--development', action='store_true', help='Test development environment')
    parser.add_argument('--templates', action='store_true', help='Test email templates only')
    parser.add_argument('--forms', action='store_true', help='Test form integration only')
    parser.add_argument('--config', action='store_true', help='Test configuration only')
    parser.add_argument('--performance', action='store_true', help='Test performance only')
    parser.add_argument('--ci', action='store_true', help='Run CI-friendly tests (no email sending)')
    parser.add_argument('--validate', action='store_true', help='Validate environment only')
    
    args = parser.parse_args()
    
    # Print banner
    print_banner()
    
    # Check prerequisites
    if not check_prerequisites():
        print("\n❌ Prerequisites not met. Please fix the issues above.")
        sys.exit(1)
    
    # Track results
    results = {}
    
    try:
        if args.quick:
            # Quick health check
            results['Quick Health Check'] = run_quick_test()
            
        elif args.validate:
            # Environment validation only
            results['Environment Validation'] = validate_environment()
            
        elif args.ci:
            # CI-friendly tests
            results['CI Tests'] = run_ci_tests()
            
        elif any([args.production, args.development, args.templates, args.forms, args.config, args.performance]):
            # Specific test categories
            if args.production:
                results['Production Tests'] = run_comprehensive_tests('production')
            if args.development:
                results['Development Tests'] = run_comprehensive_tests('development')
            if args.templates:
                results['Template Tests'] = run_comprehensive_tests('templates')
            if args.forms:
                results['Form Tests'] = run_comprehensive_tests('forms')
            if args.config:
                results['Configuration Tests'] = run_comprehensive_tests('config')
            if args.performance:
                results['Performance Tests'] = run_comprehensive_tests('performance')
                
        else:
            # Run all tests
            print("\n🚀 Running All Email System Tests...")
            results['All Tests'] = run_comprehensive_tests()
        
        # Print summary
        success = print_summary(results)
        
        # Exit with appropriate code
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 Unexpected error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
