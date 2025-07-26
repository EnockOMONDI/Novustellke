#!/usr/bin/env python
"""
Pre-deployment checklist for Novustell Travel
Validates all requirements before production deployment
"""

import os
import sys
import django
import subprocess
from pathlib import Path

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tours_travels.settings_prod')
django.setup()

from django.conf import settings
from django.core.management import call_command
from django.test.utils import get_runner
from django.db import connection
from django.contrib.auth.models import User
from adminside.models import Package, Destination, Accommodation
from users.models import Booking


class DeploymentChecker:
    """Comprehensive deployment readiness checker"""
    
    def __init__(self):
        self.checks_passed = 0
        self.checks_failed = 0
        self.warnings = 0
        self.errors = []
        self.warnings_list = []
    
    def print_header(self, title):
        """Print section header"""
        print(f"\n{'='*60}")
        print(f"🔍 {title}")
        print('='*60)
    
    def print_check(self, description, status, message=""):
        """Print individual check result"""
        if status == "PASS":
            print(f"✅ {description}")
            self.checks_passed += 1
        elif status == "FAIL":
            print(f"❌ {description} - {message}")
            self.checks_failed += 1
            self.errors.append(f"{description}: {message}")
        elif status == "WARN":
            print(f"⚠️  {description} - {message}")
            self.warnings += 1
            self.warnings_list.append(f"{description}: {message}")
    
    def check_environment_variables(self):
        """Check required environment variables"""
        self.print_header("Environment Variables")
        
        required_vars = [
            'SECRET_KEY',
            'DATABASE_URL',
            'EMAIL_HOST_USER',
            'EMAIL_HOST_PASSWORD',
            'UPLOADCARE_PUBLIC_KEY',
            'UPLOADCARE_SECRET_KEY',
        ]
        
        for var in required_vars:
            if os.getenv(var):
                self.print_check(f"Environment variable {var}", "PASS")
            else:
                self.print_check(f"Environment variable {var}", "FAIL", "Not set")
        
        # Check optional but recommended variables
        optional_vars = [
            'SENTRY_DSN',
            'RENDER_EXTERNAL_HOSTNAME',
            'SITE_URL',
        ]
        
        for var in optional_vars:
            if os.getenv(var):
                self.print_check(f"Optional variable {var}", "PASS")
            else:
                self.print_check(f"Optional variable {var}", "WARN", "Not set (recommended)")
    
    def check_django_settings(self):
        """Check Django settings configuration"""
        self.print_header("Django Settings")
        
        # Check DEBUG is False
        if not settings.DEBUG:
            self.print_check("DEBUG is False", "PASS")
        else:
            self.print_check("DEBUG is False", "FAIL", "DEBUG should be False in production")
        
        # Check ALLOWED_HOSTS
        if settings.ALLOWED_HOSTS and settings.ALLOWED_HOSTS != ['*']:
            self.print_check("ALLOWED_HOSTS configured", "PASS")
        else:
            self.print_check("ALLOWED_HOSTS configured", "FAIL", "ALLOWED_HOSTS not properly configured")
        
        # Check SECRET_KEY
        if settings.SECRET_KEY and len(settings.SECRET_KEY) > 20:
            self.print_check("SECRET_KEY configured", "PASS")
        else:
            self.print_check("SECRET_KEY configured", "FAIL", "SECRET_KEY not properly configured")
        
        # Check database configuration
        if 'postgresql' in settings.DATABASES['default']['ENGINE']:
            self.print_check("PostgreSQL database configured", "PASS")
        else:
            self.print_check("PostgreSQL database configured", "WARN", "Using non-PostgreSQL database")
        
        # Check email configuration
        if settings.EMAIL_BACKEND == 'django.core.mail.backends.smtp.EmailBackend':
            self.print_check("SMTP email backend configured", "PASS")
        else:
            self.print_check("SMTP email backend configured", "WARN", "Not using SMTP backend")
        
        # Check security settings
        security_checks = [
            ('SECURE_SSL_REDIRECT', True),
            ('SESSION_COOKIE_SECURE', True),
            ('CSRF_COOKIE_SECURE', True),
            ('SECURE_HSTS_SECONDS', lambda x: x > 0),
        ]
        
        for setting_name, expected in security_checks:
            value = getattr(settings, setting_name, None)
            if callable(expected):
                if expected(value):
                    self.print_check(f"Security setting {setting_name}", "PASS")
                else:
                    self.print_check(f"Security setting {setting_name}", "FAIL", f"Value: {value}")
            else:
                if value == expected:
                    self.print_check(f"Security setting {setting_name}", "PASS")
                else:
                    self.print_check(f"Security setting {setting_name}", "FAIL", f"Expected: {expected}, Got: {value}")
    
    def check_database_connectivity(self):
        """Check database connectivity and migrations"""
        self.print_header("Database Connectivity")
        
        try:
            # Test database connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            self.print_check("Database connection", "PASS")
        except Exception as e:
            self.print_check("Database connection", "FAIL", str(e))
            return
        
        # Check migrations
        try:
            from django.db.migrations.executor import MigrationExecutor
            executor = MigrationExecutor(connection)
            plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
            
            if not plan:
                self.print_check("Database migrations", "PASS")
            else:
                self.print_check("Database migrations", "FAIL", f"{len(plan)} unapplied migrations")
        except Exception as e:
            self.print_check("Database migrations", "FAIL", str(e))
        
        # Check essential models
        try:
            Package.objects.exists()
            self.print_check("Package model accessible", "PASS")
        except Exception as e:
            self.print_check("Package model accessible", "FAIL", str(e))
        
        try:
            Destination.objects.exists()
            self.print_check("Destination model accessible", "PASS")
        except Exception as e:
            self.print_check("Destination model accessible", "FAIL", str(e))
    
    def check_static_files(self):
        """Check static files configuration"""
        self.print_header("Static Files")
        
        # Check STATIC_ROOT
        if settings.STATIC_ROOT:
            self.print_check("STATIC_ROOT configured", "PASS")
            
            # Check if static files exist
            static_root = Path(settings.STATIC_ROOT)
            if static_root.exists() and any(static_root.iterdir()):
                self.print_check("Static files collected", "PASS")
            else:
                self.print_check("Static files collected", "WARN", "Run collectstatic")
        else:
            self.print_check("STATIC_ROOT configured", "FAIL", "STATIC_ROOT not set")
        
        # Check STATIC_URL
        if settings.STATIC_URL:
            self.print_check("STATIC_URL configured", "PASS")
        else:
            self.print_check("STATIC_URL configured", "FAIL", "STATIC_URL not set")
    
    def check_email_configuration(self):
        """Check email configuration"""
        self.print_header("Email Configuration")
        
        # Check email settings
        email_settings = [
            'EMAIL_HOST',
            'EMAIL_PORT',
            'EMAIL_HOST_USER',
            'EMAIL_HOST_PASSWORD',
            'DEFAULT_FROM_EMAIL',
        ]
        
        for setting in email_settings:
            value = getattr(settings, setting, None)
            if value:
                self.print_check(f"Email setting {setting}", "PASS")
            else:
                self.print_check(f"Email setting {setting}", "FAIL", "Not configured")
        
        # Test email backend
        try:
            from django.core.mail import get_connection
            connection = get_connection()
            self.print_check("Email backend connection", "PASS")
        except Exception as e:
            self.print_check("Email backend connection", "FAIL", str(e))
    
    def check_uploadcare_configuration(self):
        """Check Uploadcare configuration"""
        self.print_header("Uploadcare Configuration")
        
        uploadcare_config = getattr(settings, 'UPLOADCARE', {})
        
        if uploadcare_config.get('pub_key'):
            self.print_check("Uploadcare public key", "PASS")
        else:
            self.print_check("Uploadcare public key", "FAIL", "Not configured")
        
        if uploadcare_config.get('secret'):
            self.print_check("Uploadcare secret key", "PASS")
        else:
            self.print_check("Uploadcare secret key", "FAIL", "Not configured")
    
    def check_dependencies(self):
        """Check Python dependencies"""
        self.print_header("Dependencies")
        
        # Check if requirements.txt exists
        requirements_file = Path('requirements.txt')
        if requirements_file.exists():
            self.print_check("requirements.txt exists", "PASS")
        else:
            self.print_check("requirements.txt exists", "FAIL", "File not found")
            return
        
        # Check critical packages
        critical_packages = [
            'django',
            'psycopg2-binary',
            'gunicorn',
            'whitenoise',
            'django-unfold',
        ]
        
        for package in critical_packages:
            try:
                __import__(package.replace('-', '_'))
                self.print_check(f"Package {package}", "PASS")
            except ImportError:
                self.print_check(f"Package {package}", "FAIL", "Not installed")
    
    def check_security(self):
        """Check security configuration"""
        self.print_header("Security Configuration")
        
        # Check for common security issues
        if hasattr(settings, 'SECURE_SSL_REDIRECT') and settings.SECURE_SSL_REDIRECT:
            self.print_check("SSL redirect enabled", "PASS")
        else:
            self.print_check("SSL redirect enabled", "FAIL", "SSL redirect not enabled")
        
        if hasattr(settings, 'SECURE_HSTS_SECONDS') and settings.SECURE_HSTS_SECONDS > 0:
            self.print_check("HSTS configured", "PASS")
        else:
            self.print_check("HSTS configured", "WARN", "HSTS not configured")
        
        # Check for debug toolbar in production
        if 'debug_toolbar' not in settings.INSTALLED_APPS:
            self.print_check("Debug toolbar disabled", "PASS")
        else:
            self.print_check("Debug toolbar disabled", "FAIL", "Debug toolbar should not be in production")
    
    def run_tests(self):
        """Run the test suite"""
        self.print_header("Test Suite")
        
        try:
            # Run tests with test settings
            result = subprocess.run([
                sys.executable, 'manage.py', 'test', 
                '--settings=tours_travels.test_settings',
                '--verbosity=1'
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                self.print_check("Test suite", "PASS")
            else:
                self.print_check("Test suite", "FAIL", "Some tests failed")
                print(f"Test output: {result.stdout}")
                print(f"Test errors: {result.stderr}")
        except subprocess.TimeoutExpired:
            self.print_check("Test suite", "FAIL", "Tests timed out")
        except Exception as e:
            self.print_check("Test suite", "FAIL", str(e))
    
    def generate_summary(self):
        """Generate deployment readiness summary"""
        self.print_header("Deployment Readiness Summary")
        
        total_checks = self.checks_passed + self.checks_failed + self.warnings
        
        print(f"📊 Total Checks: {total_checks}")
        print(f"✅ Passed: {self.checks_passed}")
        print(f"⚠️  Warnings: {self.warnings}")
        print(f"❌ Failed: {self.checks_failed}")
        
        if self.checks_failed == 0:
            print(f"\n🎉 DEPLOYMENT READY!")
            print("All critical checks passed. The application is ready for production deployment.")
            
            if self.warnings > 0:
                print(f"\n⚠️  Note: {self.warnings} warnings found. Consider addressing these for optimal performance.")
        else:
            print(f"\n🚫 DEPLOYMENT NOT READY!")
            print(f"❌ {self.checks_failed} critical issues must be resolved before deployment.")
            
            print("\n🔧 Issues to resolve:")
            for error in self.errors:
                print(f"   • {error}")
        
        if self.warnings_list:
            print(f"\n⚠️  Warnings:")
            for warning in self.warnings_list:
                print(f"   • {warning}")
        
        return self.checks_failed == 0
    
    def run_all_checks(self):
        """Run all deployment checks"""
        print("🚀 Novustell Travel - Pre-Deployment Checklist")
        print("=" * 60)
        
        self.check_environment_variables()
        self.check_django_settings()
        self.check_database_connectivity()
        self.check_static_files()
        self.check_email_configuration()
        self.check_uploadcare_configuration()
        self.check_dependencies()
        self.check_security()
        self.run_tests()
        
        return self.generate_summary()


if __name__ == '__main__':
    checker = DeploymentChecker()
    is_ready = checker.run_all_checks()
    
    # Exit with appropriate code
    sys.exit(0 if is_ready else 1)
