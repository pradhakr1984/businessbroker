#!/usr/bin/env python3
"""
Debug script to examine the actual content of BizBuySell emails
"""
import os
import sys
sys.path.append('src')

from email_imap import fetch_alert_emails
from parsers.bizbuysell import parse_bizbuysell

def debug_bizbuysell_emails():
    print("🔍 Debugging BizBuySell Email Content")
    print("=" * 50)
    
    # Fetch emails from the last 30 days to get that BizBuySell email
    emails = fetch_alert_emails(label="biz-acq/alerts", lookback_days=30)
    print(f"📧 Found {len(emails)} total emails")
    
    # Find BizBuySell emails
    bizbuysell_emails = []
    for email in emails:
        sender = str(email.get('from', ''))
        subject = email.get('subject', '')
        if 'bizbuysell' in sender.lower() or 'bizbuysell' in subject.lower():
            bizbuysell_emails.append(email)
    
    print(f"🏢 Found {len(bizbuysell_emails)} BizBuySell emails")
    
    for i, email in enumerate(bizbuysell_emails):
        print(f"\n📨 Email {i+1}:")
        print(f"   Subject: {email.get('subject', 'No subject')}")
        print(f"   From: {email.get('from', 'Unknown')}")
        print(f"   Date: {email.get('date', 'Unknown')}")
        
        # Show first 500 chars of text content
        text_plain = email.get('text_plain', '')
        text_html = email.get('text_html', '')
        
        print(f"   Text length: {len(text_plain)} chars")
        print(f"   HTML length: {len(text_html)} chars")
        
        if text_plain:
            print(f"   Text preview: {text_plain[:500]}...")
        elif text_html:
            print(f"   HTML preview: {text_html[:500]}...")
        
        # Test if our parser recognizes it
        try:
            parsed_result = parse_bizbuysell(email)
            print(f"   ✅ Parser result: {len(parsed_result)} listings found")
            if parsed_result:
                for j, listing in enumerate(parsed_result):
                    print(f"      Listing {j+1}: {listing.get('name', 'No name')} - ${listing.get('price', 'No price')}")
        except Exception as e:
            print(f"   ❌ Parser error: {e}")
        
        print("-" * 50)

if __name__ == "__main__":
    # Load environment variables
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            for line in f:
                if '=' in line and not line.strip().startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
    
    debug_bizbuysell_emails()
