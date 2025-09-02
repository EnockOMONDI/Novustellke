#!/usr/bin/env python3
"""
Environment Switcher for Novustell Travel Django Project

This script helps switch between development and production environments
by copying the appropriate .env file.

Usage:
    python switch_env.py dev     # Switch to development environment
    python switch_env.py prod    # Switch to production environment
    python switch_env.py status  # Show current environment status
"""

import os
import shutil
import sys
from pathlib import Path

# Define file paths
BASE_DIR = Path(__file__).parent
ENV_FILE = BASE_DIR / '.env'
DEV_ENV_FILE = BASE_DIR / '.env.development'
PROD_ENV_FILE = BASE_DIR / '.env.production'

def get_current_environment():
    """Detect current environment based on .env file content"""
    if not ENV_FILE.exists():
        return "unknown"
    
    try:
        with open(ENV_FILE, 'r') as f:
            content = f.read()
            if 'DEBUG=True' in content:
                return "development"
            elif 'DEBUG=False' in content:
                return "production"
            else:
                return "unknown"
    except Exception:
        return "unknown"

def switch_to_development():
    """Switch to development environment"""
    if not DEV_ENV_FILE.exists():
        print(f"❌ Development environment file not found: {DEV_ENV_FILE}")
        return False
    
    try:
        # Backup current .env if it exists
        if ENV_FILE.exists():
            backup_file = BASE_DIR / '.env.backup'
            shutil.copy2(ENV_FILE, backup_file)
            print(f"📁 Backed up current .env to {backup_file}")
        
        # Copy development environment
        shutil.copy2(DEV_ENV_FILE, ENV_FILE)
        print("✅ Switched to DEVELOPMENT environment")
        print("🔧 Configuration:")
        print("   - DEBUG=True")
        print("   - Database: Supabase (shared with production)")
        print("   - Admin environment indicator: Development")
        print("   - Security settings: Relaxed for local development")
        print("   - Site URL: http://127.0.0.1:8005")
        return True
    except Exception as e:
        print(f"❌ Failed to switch to development: {e}")
        return False

def switch_to_production():
    """Switch to production environment"""
    # Use the current .env as production (it's already configured for production)
    current_env = get_current_environment()
    if current_env == "production":
        print("✅ Already in PRODUCTION environment")
        return True
    
    # If we have a production backup, use it
    if PROD_ENV_FILE.exists():
        try:
            shutil.copy2(PROD_ENV_FILE, ENV_FILE)
            print("✅ Switched to PRODUCTION environment")
        except Exception as e:
            print(f"❌ Failed to switch to production: {e}")
            return False
    else:
        # Create production env file from current .env
        try:
            # Read current .env and modify for production
            with open(ENV_FILE, 'r') as f:
                content = f.read()
            
            # Ensure production settings
            content = content.replace('DEBUG=True', 'DEBUG=False')
            content = content.replace('PRODUCTION_ENVIRONMENT=False', 'PRODUCTION_ENVIRONMENT=True')
            
            with open(ENV_FILE, 'w') as f:
                f.write(content)
            
            print("✅ Switched to PRODUCTION environment")
        except Exception as e:
            print(f"❌ Failed to switch to production: {e}")
            return False
    
    print("🚀 Configuration:")
    print("   - DEBUG=False")
    print("   - Database: Supabase (production)")
    print("   - Admin environment indicator: Production")
    print("   - Security settings: Production-ready")
    print("   - Site URL: https://novustelltravel.com")
    return True

def show_status():
    """Show current environment status"""
    current_env = get_current_environment()
    
    print("🌍 Novustell Travel Environment Status")
    print("=" * 40)
    print(f"Current Environment: {current_env.upper()}")
    
    if ENV_FILE.exists():
        print(f"Environment file: {ENV_FILE}")
        
        # Read some key settings
        try:
            with open(ENV_FILE, 'r') as f:
                content = f.read()
                
            debug = "True" if "DEBUG=True" in content else "False"
            site_url = ""
            for line in content.split('\n'):
                if line.startswith('SITE_URL='):
                    site_url = line.split('=', 1)[1]
                    break
            
            print(f"DEBUG: {debug}")
            print(f"Site URL: {site_url}")
            
            if "127.0.0.1" in site_url or "localhost" in site_url:
                print("🔧 Local development configuration detected")
            else:
                print("🚀 Production configuration detected")
                
        except Exception as e:
            print(f"❌ Error reading environment file: {e}")
    else:
        print("❌ No .env file found")
    
    print("\nAvailable commands:")
    print("  python switch_env.py dev     # Switch to development")
    print("  python switch_env.py prod    # Switch to production")
    print("  python switch_env.py status  # Show this status")

def main():
    """Main function"""
    if len(sys.argv) != 2:
        show_status()
        return
    
    command = sys.argv[1].lower()
    
    if command in ['dev', 'development']:
        success = switch_to_development()
        if success:
            print("\n🔄 Next steps:")
            print("1. Restart your Django development server")
            print("2. Run: python manage.py runserver 8005")
            print("3. Access admin at: http://127.0.0.1:8005/admin/")
    
    elif command in ['prod', 'production']:
        success = switch_to_production()
        if success:
            print("\n🔄 Next steps:")
            print("1. Deploy to production server")
            print("2. Restart production services")
            print("3. Verify at: https://novustelltravel.com/admin/")
    
    elif command in ['status', 'info']:
        show_status()
    
    else:
        print(f"❌ Unknown command: {command}")
        print("Available commands: dev, prod, status")
        sys.exit(1)

if __name__ == "__main__":
    main()
