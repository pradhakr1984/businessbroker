#!/usr/bin/env python3
"""
Manual listing check - bypass automated scraping issues
This script helps you manually input listings you find while browsing
"""

import json
import sys
from datetime import datetime

def manual_listing_entry():
    """Allow manual entry of listings found while browsing"""
    print("🎯 Manual Business Listing Entry")
    print("=" * 40)
    print()
    print("💡 Since automated scraping can be blocked, you can manually")
    print("   enter interesting listings you find while browsing!")
    print()
    
    listings = []
    
    while True:
        print(f"\n📝 Listing #{len(listings) + 1}")
        print("-" * 20)
        
        # Get listing details
        name = input("Business Name: ").strip()
        if not name:
            break
            
        price_str = input("Price (numbers only, e.g., 1500000): ").strip()
        try:
            price = int(price_str) if price_str else None
        except ValueError:
            price = None
            
        cash_flow_str = input("Cash Flow/Earnings (numbers only): ").strip()
        try:
            cash_flow = int(cash_flow_str) if cash_flow_str else None
        except ValueError:
            cash_flow = None
            
        reason = input("Reason for Sale: ").strip()
        location = input("Location: ").strip()
        category = input("Category/Industry: ").strip()
        url = input("URL: ").strip()
        source = input("Source (bizbuysell/bizquest/dealstream): ").strip() or "manual"
        
        # Calculate multiple
        earnings_multiple = None
        if price and cash_flow and cash_flow > 0:
            earnings_multiple = round(price / cash_flow, 1)
        
        # Create listing object
        listing = {
            "name": name,
            "price": price,
            "cash_flow": cash_flow,
            "earnings_multiple": earnings_multiple,
            "reason_for_sale": reason,
            "location": location,
            "category": category,
            "source_url": url,
            "source_site": source,
            "source_method": "manual_entry",
            "date_added": datetime.now().isoformat()
        }
        
        listings.append(listing)
        print(f"✅ Added: {name}")
        
        # Ask if they want to add another
        another = input("\nAdd another listing? (y/n): ").strip().lower()
        if another not in ['y', 'yes']:
            break
    
    if listings:
        # Save to file
        filename = f"data/manual_listings_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(listings, f, indent=2)
        
        print(f"\n✅ Saved {len(listings)} listings to {filename}")
        print("\n💡 To process these through your filters:")
        print(f"   python process_manual_listings.py {filename}")
        
        # Show summary
        print(f"\n📊 Summary:")
        for i, listing in enumerate(listings, 1):
            price_str = f"${listing['price']:,}" if listing['price'] else "Price TBD"
            multiple_str = f" ({listing['earnings_multiple']}x)" if listing['earnings_multiple'] else ""
            print(f"   {i}. {listing['name']} - {price_str}{multiple_str}")
    else:
        print("\nNo listings entered.")

def quick_market_check():
    """Guide for manual market research"""
    print("🔍 Quick Market Research Guide")
    print("=" * 35)
    print()
    print("Since automated scraping is blocked, here's how to manually check:")
    print()
    print("1. 🌐 BizBuySell.com:")
    print("   • Go to https://www.bizbuysell.com/businesses-for-sale/")
    print("   • Filter: New York area, under $5M")
    print("   • Look for 'retirement' in reason for sale")
    print()
    print("2. 🌐 BizQuest.com:")
    print("   • Go to https://www.bizquest.com/businesses-for-sale/")
    print("   • Use location and price filters")
    print("   • Check recent listings")
    print()
    print("3. 🌐 DealStream.com:")
    print("   • Go to https://www.dealstream.com/opportunities/")
    print("   • Filter by location and price range")
    print("   • Look for acquisition opportunities")
    print()
    print("💡 Copy interesting listings and run manual_listing_entry() to add them!")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "research":
        quick_market_check()
    else:
        manual_listing_entry()
