#!/usr/bin/env python3
"""
Quick check script to monitor email activity from all platforms
Run this anytime to see recent email activity
"""
import os
import sys
sys.path.append('src')

from email_imap import fetch_alert_emails
from datetime import datetime

def check_platform_activity():
    print("📧 Platform Email Activity Monitor")
    print("=" * 50)
    print(f"🕒 Checked at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("")
    
    # Check different time periods
    periods = [1, 3, 7]
    
    for days in periods:
        print(f"📅 Last {days} day{'s' if days > 1 else ''}:")
        print("-" * 30)
        
        try:
            emails = fetch_alert_emails(label="biz-acq/alerts", lookback_days=days)
            
            # Categorize emails by platform
            platforms = {
                'bizbuysell': [],
                'bizquest': [],
                'dealstream': [],
                'other': []
            }
            
            for email in emails:
                sender = str(email.get('from', '')).lower()
                subject = str(email.get('subject', '')).lower()
                
                if 'bizbuysell' in sender or 'bizbuysell' in subject:
                    platforms['bizbuysell'].append(email)
                elif 'bizquest' in sender or 'bizquest' in subject:
                    platforms['bizquest'].append(email)
                elif 'dealstream' in sender or 'dealstream' in subject:
                    platforms['dealstream'].append(email)
                else:
                    platforms['other'].append(email)
            
            # Report by platform
            for platform, emails in platforms.items():
                if emails:
                    icon = {'bizbuysell': '🏢', 'bizquest': '🏪', 'dealstream': '💼', 'other': '📨'}[platform]
                    print(f"   {icon} {platform.upper()}: {len(emails)} emails")
                    
                    # Show most recent email
                    recent = emails[0]  # emails are sorted by date, newest first
                    subject = recent.get('subject', 'No subject')[:50]
                    date = recent.get('date', 'Unknown date')
                    print(f"      Latest: {subject}... ({date})")
                else:
                    icon = {'bizbuysell': '🏢', 'bizquest': '🏪', 'dealstream': '💼', 'other': '📨'}[platform]
                    print(f"   {icon} {platform.upper()}: 0 emails")
            
            print(f"   📊 Total: {len(emails)} emails")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print("")
    
    print("💡 Tips:")
    print("- New platform alerts typically start 24-48 hours after setup")
    print("- Long weekends may delay business listing activity")  
    print("- Check your saved searches are 'Active' on each platform")
    print("- Run './daily_workflow.sh' to process any new emails")

if __name__ == "__main__":
    # Load environment variables
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            for line in f:
                if '=' in line and not line.strip().startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
    
    check_platform_activity()
