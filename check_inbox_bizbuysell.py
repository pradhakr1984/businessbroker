#!/usr/bin/env python3
"""
Check INBOX directly for any BizBuySell emails that might be unlabeled
"""
import os
import sys
sys.path.append('src')

from email_imap import fetch_alert_emails

def check_inbox_for_bizbuysell():
    print("🔍 Checking INBOX for BizBuySell emails (last 3 days)")
    print("=" * 50)
    
    # Check INBOX directly for recent BizBuySell emails
    try:
        emails = fetch_alert_emails(label="INBOX", lookback_days=3)
        print(f"📧 Checked {len(emails)} emails in INBOX")
        
        bizbuysell_emails = []
        for email in emails:
            sender = str(email.get('from', '')).lower()
            subject = str(email.get('subject', '')).lower()
            
            if ('bizbuysell' in sender or 'bizbuysell' in subject):
                bizbuysell_emails.append(email)
        
        print(f"🏢 Found {len(bizbuysell_emails)} BizBuySell emails in INBOX:")
        
        for i, email in enumerate(bizbuysell_emails):
            print(f"\n📨 Email {i+1}:")
            print(f"   Subject: {email.get('subject', 'No subject')}")
            print(f"   From: {email.get('from', 'Unknown')}")
            print(f"   Date: {email.get('date', 'Unknown')}")
            
            # Check if it looks like a search alert
            subject = email.get('subject', '').lower()
            if any(word in subject for word in ['alert', 'new listing', 'saved search', 'match']):
                print("   🎯 This looks like a SEARCH ALERT!")
            elif 'newsletter' in subject or 'top' in subject:
                print("   📰 This looks like a newsletter")
            else:
                print("   ❓ Email type unclear")
        
        if not bizbuysell_emails:
            print("\n💡 No BizBuySell emails found in INBOX from last 3 days")
            print("   This suggests:")
            print("   1. Search alerts haven't triggered yet (normal)")
            print("   2. Need to wait 24-48 hours for first alerts")
            print("   3. Check your BizBuySell account settings")
        
    except Exception as e:
        print(f"❌ Error checking INBOX: {e}")

if __name__ == "__main__":
    # Load environment variables
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            for line in f:
                if '=' in line and not line.strip().startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
    
    check_inbox_for_bizbuysell()
