#!/usr/bin/env python3
"""
Test script to verify Gmail label setup and IMAP connection
"""
import os
import sys
from datetime import datetime, timedelta, timezone

# Add src to path so we can import our modules
sys.path.append('src')

from email_imap import fetch_alert_emails

def test_gmail_connection():
    """Test Gmail IMAP connection and label setup"""
    print("🔧 Testing Gmail IMAP Connection...")
    print("-" * 50)
    
    # Check environment variables
    username = os.getenv("IMAP_USERNAME")
    password = os.getenv("IMAP_APP_PASSWORD")
    
    print(f"📧 IMAP Username: {username}")
    print(f"🔑 App Password: {'✅ Set' if password else '❌ Missing'}")
    
    if not username or not password:
        print("\n❌ Missing credentials!")
        print("Please set your environment variables:")
        print("export IMAP_USERNAME=your-email@gmail.com")
        print("export IMAP_APP_PASSWORD=your-app-password")
        return False
    
    # Test different lookback periods and labels
    test_configs = [
        {"label": "biz-acq/alerts", "days": 7},
        {"label": "biz-acq/alerts", "days": 14},
        {"label": "biz-acq/alerts", "days": 30},
        {"label": "INBOX", "days": 7},  # Test if we can read inbox
    ]
    
    for config in test_configs:
        print(f"\n🔍 Testing label: '{config['label']}' (last {config['days']} days)")
        try:
            emails = fetch_alert_emails(
                label=config['label'], 
                lookback_days=config['days']
            )
            print(f"   ✅ Found {len(emails)} emails")
            
            # Show sample subjects if any emails found
            if emails:
                print("   📋 Sample subjects:")
                for i, email in enumerate(emails[:3]):  # Show first 3
                    subject = email.get('subject', 'No subject')[:60]
                    sender = email.get('from', ['Unknown'])[0] if email.get('from') else 'Unknown'
                    print(f"      {i+1}. {subject}... (from: {sender})")
                
                # Check for BizBuySell emails specifically
                bizbuysell_count = sum(1 for email in emails 
                                     if 'bizbuysell' in str(email.get('from', '')).lower() 
                                     or 'bizbuysell' in email.get('subject', '').lower())
                print(f"   🏢 BizBuySell emails: {bizbuysell_count}")
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
    
    return True

def check_label_suggestions():
    """Provide suggestions for Gmail label setup"""
    print("\n📝 Gmail Label Setup Guide:")
    print("-" * 50)
    print("1. 🏷️  Create the label 'biz-acq/alerts' in Gmail:")
    print("   - Go to Gmail → Settings → Labels")
    print("   - Click 'Create new label'")
    print("   - Name: biz-acq/alerts")
    print("   - Make sure 'Show in IMAP' is checked ✅")
    
    print("\n2. 📧 Set up email filters:")
    print("   - Go to Gmail → Settings → Filters and Blocked Addresses")
    print("   - Create filter for BizBuySell emails:")
    print("     From: contains 'bizbuysell.com'")
    print("     Action: Apply label 'biz-acq/alerts'")
    
    print("\n3. 🔍 Alternative label names to try:")
    print("   - INBOX (to test basic connectivity)")
    print("   - [Gmail]/All Mail")
    print("   - bizbuysell (if you created a simpler label)")
    
    print("\n4. 🛠️  Troubleshooting:")
    print("   - Make sure IMAP is enabled in Gmail")
    print("   - Check that your app password is correct")
    print("   - Verify the label shows in IMAP settings")

if __name__ == "__main__":
    print("🎯 Gmail Label & IMAP Test")
    print("=" * 50)
    
    # Load environment variables from .env if available
    if os.path.exists('.env'):
        print("📄 Loading .env file...")
        with open('.env', 'r') as f:
            for line in f:
                if '=' in line and not line.strip().startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
    
    success = test_gmail_connection()
    
    if success:
        check_label_suggestions()
    
    print(f"\n⏰ Test completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
