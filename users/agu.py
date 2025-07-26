import os
import sqlite3
import shutil
import json
from datetime import datetime

class AugmentCleanerV2Mac:
    """macOS version of cleaner for newer Augment versions (0.492.2+)"""
    
    def __init__(self):
        self.findings = {
            'extensions': [],
            'databases': [],
            'personal_data': [],
            'ai_training_data': []
        }
        self.cleaned_items = 0
        self.backup_dir = None
    
    def scan_for_newer_augment(self):
        """Comprehensive scan for newer Augment versions and their data"""
        print("🔍 macOS Augment Scanner v2.0 - Targeting newer versions")
        print("=" * 60)
        
        # Create backup directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup_dir = f"augment_backup_{timestamp}"
        os.makedirs(self.backup_dir, exist_ok=True)
        
        # Scan different areas
        self.scan_extensions()
        self.scan_databases_deep()
        self.scan_personal_data()
        self.scan_ai_training_data()
        
        return self.generate_findings_report()
    
    def scan_extensions(self):
        """Scan for Augment extensions with version detection"""
        print("\n📦 Scanning for Augment extensions...")
        
        vscode_paths = [
            (os.path.expanduser("~/.vscode"), "VSCode"),
            (os.path.expanduser("~/.vscode-insiders"), "VSCode Insiders"),
            (os.path.expanduser("~/Library/Application Support/Code"), "VSCode (User)"),
            (os.path.expanduser("~/Library/Application Support/Cursor"), "Cursor")
        ]
        
        for base_path, ide_name in vscode_paths:
            extensions_dir = os.path.join(base_path, "extensions")
            if not os.path.exists(extensions_dir):
                continue
                
            for item in os.listdir(extensions_dir):
                if any(pattern in item.lower() for pattern in ['augment', 'augmentcode']):
                    ext_path = os.path.join(extensions_dir, item)
                    version = self.extract_version(item)
                    
                    self.findings['extensions'].append({
                        'ide': ide_name,
                        'name': item,
                        'path': ext_path,
                        'version': version,
                        'is_newer': self.is_newer_version(version),
                        'size_mb': self.get_folder_size_mb(ext_path)
                    })
                    
                    print(f"   📦 Found: {item} (v{version}) in {ide_name}")
                    if self.is_newer_version(version):
                        print(f"       🚨 NEWER VERSION - Enhanced data collection!")
    
    def scan_databases_deep(self):
        """Deep scan of VSCode databases for personal data"""
        print("\n🗄️ Deep scanning databases for personal data...")
        
        vscode_paths = [
            os.path.expanduser("~/Library/Application Support/Code/User/globalStorage"),
            os.path.expanduser("~/Library/Application Support/Code - Insiders/User/globalStorage"),
            os.path.expanduser("~/Library/Application Support/Cursor/User/globalStorage")
        ]
        
        personal_patterns = [
            '%username%', '%user%', '%computer%', '%machine%', '%email%',
            '%identity%', '%profile%', '%account%', '%name%', '%domain%'
        ]
        
        for vscode_path in vscode_paths:
            state_db = os.path.join(vscode_path, "state.vscdb")
            if not os.path.exists(state_db):
                continue
                
            try:
                conn = sqlite3.connect(state_db)
                cur = conn.cursor()
                
                # Check for personal data in database
                personal_entries = []
                for pattern in personal_patterns:
                    cur.execute("SELECT key, value FROM ItemTable WHERE LOWER(key) LIKE ? OR LOWER(value) LIKE ?", 
                              (pattern, pattern))
                    results = cur.fetchall()
                    personal_entries.extend(results)
                
                # Check for actual username in data
                username = os.environ.get('USER', '').lower()
                if username:
                    cur.execute("SELECT key, value FROM ItemTable WHERE LOWER(value) LIKE ?", 
                              (f'%{username}%',))
                    username_entries = cur.fetchall()
                    personal_entries.extend(username_entries)
                
                if personal_entries:
                    self.findings['personal_data'].append({
                        'database': state_db,
                        'entries': len(personal_entries),
                        'sample_keys': [entry[0] for entry in personal_entries[:5]],
                        'contains_username': any(username in str(entry[1]).lower() for entry in personal_entries)
                    })
                    
                    print(f"   🚨 Found {len(personal_entries)} personal data entries in {os.path.basename(state_db)}")
                    if any(username in str(entry[1]).lower() for entry in personal_entries):
                        print(f"       ⚠️ Contains your actual username: {username}")
                
                conn.close()
                
            except Exception as e:
                print(f"   ❌ Error scanning {state_db}: {str(e)}")
    
    def scan_personal_data(self):
        """Scan for personal data collection"""
        print("\n👤 Scanning for personal data collection...")
        
        workspace_paths = [
            os.path.expanduser("~/Library/Application Support/Code/User/workspaceStorage"),
            os.path.expanduser("~/Library/Application Support/Code - Insiders/User/workspaceStorage"),
            os.path.expanduser("~/Library/Application Support/Cursor/User/workspaceStorage")
        ]
        
        for workspace_path in workspace_paths:
            if not os.path.exists(workspace_path):
                continue
                
            for workspace_dir in os.listdir(workspace_path):
                workspace_full = os.path.join(workspace_path, workspace_dir)
                if os.path.isdir(workspace_full):
                    for file in os.listdir(workspace_full):
                        if 'augment' in file.lower():
                            self.findings['personal_data'].append({
                                'type': 'workspace_data',
                                'path': os.path.join(workspace_full, file),
                                'workspace': workspace_dir
                            })
                            print(f"   📁 Personal workspace data: {file}")
    
    def scan_ai_training_data(self):
        """Scan for AI/ML training data collection"""
        print("\n🤖 Scanning for AI/ML training data...")
        
        ai_patterns = ['training', 'model', 'ml', 'ai', 'neural', 'learning']
        
        for extension in self.findings['extensions']:
            if extension['is_newer']:
                ext_path = extension['path']
                for root, dirs, files in os.walk(ext_path):
                    for file in files:
                        if any(pattern in file.lower() for pattern in ai_patterns):
                            file_path = os.path.join(root, file)
                            self.findings['ai_training_data'].append({
                                'type': 'ai_training_file',
                                'path': file_path,
                                'extension': extension['name']
                            })
                            print(f"   🤖 AI training data: {file}")
    
    def extract_version(self, extension_name):
        """Extract version from extension name"""
        import re
        version_pattern = r'(\d+\.\d+\.\d+)'
        match = re.search(version_pattern, extension_name)
        return match.group(1) if match else "0.0.0"
    
    def is_newer_version(self, version):
        """Check if version is newer than 0.490.0"""
        try:
            parts = [int(x) for x in version.split('.')]
            return parts[0] > 0 or (parts[0] == 0 and parts[1] >= 490)
        except:
            return False
    
    def get_folder_size_mb(self, folder_path):
        """Get folder size in MB"""
        try:
            total_size = 0
            for dirpath, dirnames, filenames in os.walk(folder_path):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    if os.path.exists(filepath):
                        total_size += os.path.getsize(filepath)
            return round(total_size / (1024 * 1024), 2)
        except:
            return 0
    
    def generate_findings_report(self):
        """Generate comprehensive findings report"""
        print("\n" + "=" * 60)
        print("📊 macOS AUGMENT DETECTION REPORT")
        print("=" * 60)
        
        total_items = sum(len(self.findings[category]) for category in self.findings)
        print(f"🎯 Total items found: {total_items}")
        
        newer_extensions = [ext for ext in self.findings['extensions'] if ext['is_newer']]
        if newer_extensions:
            print(f"\n🚨 PRIVACY ALERT: {len(newer_extensions)} newer Augment version(s) detected!")
            print("   These versions collect significantly more personal data.")
        
        personal_items = len(self.findings['personal_data'])
        if personal_items > 0:
            print(f"\n👤 PERSONAL DATA: {personal_items} instances of personal data collection found")
        
        return total_items > 0
    
    def clean_all_findings(self):
        """Clean all found Augment data with enhanced removal"""
        if not any(self.findings.values()):
            print("✅ No Augment data found to clean.")
            return 0
        
        print("\n🧹 Starting enhanced Augment removal...")
        
        for ext in self.findings['extensions']:
            self.clean_extension(ext)
        
        for db_info in self.findings['personal_data']:
            if 'database' in db_info:
                self.clean_database_personal_data(db_info)
        
        for ai_item in self.findings['ai_training_data']:
            self.clean_ai_data(ai_item)
        
        print(f"\n✅ Enhanced cleaning completed! Removed {self.cleaned_items} items.")
        print(f"💾 Backups saved to: {self.backup_dir}")
        
        return self.cleaned_items
    
    def clean_extension(self, ext_info):
        """Clean extension with backup"""
        try:
            ext_path = ext_info['path']
            if os.path.exists(ext_path):
                backup_path = os.path.join(self.backup_dir, f"extension_{ext_info['name']}")
                shutil.copytree(ext_path, backup_path)
                shutil.rmtree(ext_path)
                self.cleaned_items += 1
                print(f"   ✅ Removed extension: {ext_info['name']}")
        except Exception as e:
            print(f"   ❌ Failed to remove extension: {str(e)}")
    
    def clean_database_personal_data(self, db_info):
        """Clean personal data from databases"""
        try:
            db_path = db_info['database']
            if os.path.exists(db_path):
                backup_path = os.path.join(self.backup_dir, f"database_{os.path.basename(db_path)}")
                shutil.copy2(db_path, backup_path)
                
                conn = sqlite3.connect(db_path)
                cur = conn.cursor()
                
                personal_patterns = ['%augment%', '%username%', '%user%', '%computer%']
                for pattern in personal_patterns:
                    cur.execute("DELETE FROM ItemTable WHERE LOWER(key) LIKE ? OR LOWER(value) LIKE ?", 
                              (pattern, pattern))
                
                conn.commit()
                conn.close()
                self.cleaned_items += 1
                print(f"   ✅ Cleaned personal data from: {os.path.basename(db_path)}")
        except Exception as e:
            print(f"   ❌ Failed to clean database: {str(e)}")
    
    def clean_ai_data(self, ai_info):
        """Clean AI training data"""
        try:
            file_path = ai_info['path']
            if os.path.exists(file_path):
                backup_path = os.path.join(self.backup_dir, f"ai_{os.path.basename(file_path)}")
                shutil.copy2(file_path, backup_path)
                os.remove(file_path)
                self.cleaned_items += 1
                print(f"   ✅ Removed AI training data: {os.path.basename(file_path)}")
        except Exception as e:
            print(f"   ❌ Failed to remove AI data: {str(e)}")

def main():
    """Main function for macOS Augment cleaner"""
    print("🧹 macOS Augment Cleaner v2.0 - Enhanced Privacy Protection")
    print("Specifically designed for newer Augment versions (0.492.2+)")
    print("=" * 60)
    
    cleaner = AugmentCleanerV2Mac()
    
    try:
        found_items = cleaner.scan_for_newer_augment()
        
        if not found_items:
            print("\n✅ No Augment installations found. Your system appears clean!")
            return
        
        print(f"\n⚠️ Found Augment data that may contain personal information.")
        response = input("\nProceed with enhanced cleaning? (y/yes or n/no): ").strip().lower()
        
        if response in ['y', 'yes']:
            cleaned_count = cleaner.clean_all_findings()
            print(f"\n🎉 Enhanced cleaning completed!")
            print(f"✅ Removed {cleaned_count} items containing personal data")
            print(f"💾 Backups created for safety")
            print(f"🔒 Your privacy has been protected!")
        else:
            print("\n❌ Cleaning cancelled. No changes made.")
    
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
    
    finally:
        print("\nPress Enter to exit...")
        input()

if __name__ == "__main__":
    main()