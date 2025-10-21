#!/usr/bin/env python3
"""
Simple Mailtrap SMTP Connection Test
Tests different ports and configurations to find working setup
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Mailtrap configuration
MAILTRAP_HOST = 'live.smtp.mailtrap.io'
MAILTRAP_USER = 'api'
MAILTRAP_PASSWORD = 'd766975d57a7ef1acf2f750a36247a37'

def test_mailtrap_connection(port, use_tls=True, use_ssl=False):
    """Test Mailtrap connection with different configurations"""
    print(f"\n🔍 Testing Mailtrap connection:")
    print(f"   Host: {MAILTRAP_HOST}")
    print(f"   Port: {port}")
    print(f"   TLS: {use_tls}")
    print(f"   SSL: {use_ssl}")
    print(f"   User: {MAILTRAP_USER}")
    
    try:
        if use_ssl:
            # SSL connection
            context = ssl.create_default_context()
            server = smtplib.SMTP_SSL(MAILTRAP_HOST, port, context=context)
        else:
            # Regular connection
            server = smtplib.SMTP(MAILTRAP_HOST, port)
            
            if use_tls:
                # Start TLS
                server.starttls()
        
        # Login
        server.login(MAILTRAP_USER, MAILTRAP_PASSWORD)
        
        # Create test email
        msg = MIMEMultipart()
        msg['From'] = 'Novustell Travel <info@novustelltravel.com>'
        msg['To'] = 'test@novustelltravel.com'
        msg['Subject'] = f'Mailtrap Test - Port {port}'
        
        body = f"""
        This is a test email from Novustell Travel.
        
        Configuration:
        - Host: {MAILTRAP_HOST}
        - Port: {port}
        - TLS: {use_tls}
        - SSL: {use_ssl}
        - User: {MAILTRAP_USER}
        
        If you receive this email, the Mailtrap configuration is working correctly!
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email
        text = msg.as_string()
        server.sendmail(msg['From'], [msg['To']], text)
        server.quit()
        
        print(f"✅ SUCCESS: Email sent successfully via port {port}")
        return True
        
    except Exception as e:
        print(f"❌ FAILED: Port {port} - {str(e)}")
        return False

def test_all_configurations():
    """Test all common Mailtrap configurations"""
    print("🚀 MAILTRAP SMTP CONNECTION TESTING")
    print("=" * 50)
    
    configurations = [
        # (port, use_tls, use_ssl, description)
        (587, True, False, "Standard TLS (recommended)"),
        (2525, True, False, "Alternative TLS port"),
        (25, True, False, "Standard SMTP with TLS"),
        (465, False, True, "SSL/TLS"),
        (2525, False, False, "Plain SMTP (no encryption)"),
    ]
    
    successful_configs = []
    
    for port, use_tls, use_ssl, description in configurations:
        print(f"\n📡 Testing: {description}")
        if test_mailtrap_connection(port, use_tls, use_ssl):
            successful_configs.append((port, use_tls, use_ssl, description))
    
    print("\n" + "=" * 50)
    print("📊 RESULTS SUMMARY")
    print("=" * 50)
    
    if successful_configs:
        print(f"✅ {len(successful_configs)} working configuration(s) found:")
        for port, use_tls, use_ssl, description in successful_configs:
            print(f"   - Port {port}: {description}")
            print(f"     TLS: {use_tls}, SSL: {use_ssl}")
        
        # Recommend best configuration
        print(f"\n🎯 RECOMMENDED CONFIGURATION:")
        best_config = successful_configs[0]  # First working config
        port, use_tls, use_ssl, description = best_config
        print(f"   EMAIL_HOST = 'live.smtp.mailtrap.io'")
        print(f"   EMAIL_PORT = {port}")
        print(f"   EMAIL_USE_TLS = {use_tls}")
        print(f"   EMAIL_USE_SSL = {use_ssl}")
        print(f"   EMAIL_HOST_USER = 'api'")
        print(f"   EMAIL_HOST_PASSWORD = 'd766975d57a7ef1acf2f750a36247a37'")
        
    else:
        print("❌ No working configurations found!")
        print("   This could indicate:")
        print("   - Incorrect Mailtrap credentials")
        print("   - Network connectivity issues")
        print("   - Firewall blocking SMTP ports")
        print("   - Mailtrap service issues")

if __name__ == "__main__":
    test_all_configurations()
