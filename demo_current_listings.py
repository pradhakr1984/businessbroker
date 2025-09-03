#!/usr/bin/env python3
"""
Demo what current listings would look like after filtering
(skips link checking since these are example URLs)
"""

import json
import yaml
from src.normalize import normalize_records
from src.dedupe import dedupe_records
from src.filters import policy_filter, postprocess_reason
from src.export_json import write_json
from src.export_markdown import write_markdown

def demo_current_listings():
    """Show what current listings would look like"""
    print("🎯 DEMO: Current Market Listings")
    print("=" * 35)
    
    # Sample current listings (realistic data)
    current_listings = [
        {
            "name": "Established Manufacturing Company - 25 Years",
            "price": 2850000,
            "cash_flow": 475000,
            "earnings_multiple": 6.0,
            "reason_for_sale": "retirement",
            "location": "Westchester County, NY",
            "category": "Manufacturing",
            "source_url": "https://example.com/listing1",
            "source_site": "bizbuysell",
            "source_method": "web_scrape"
        },
        {
            "name": "Professional Services Firm",
            "price": 1200000,
            "cash_flow": 280000,
            "earnings_multiple": 4.3,
            "reason_for_sale": "retirement",
            "location": "Manhattan, NY",
            "category": "Professional Services",
            "source_url": "https://example.com/listing2",
            "source_site": "bizquest",
            "source_method": "web_scrape"
        },
        {
            "name": "Tech Distribution Business",
            "price": 3200000,
            "cash_flow": 580000,
            "earnings_multiple": 5.5,
            "reason_for_sale": "retirement",
            "location": "Long Island, NY",
            "category": "Technology Distribution",
            "source_url": "https://example.com/listing3",
            "source_site": "dealstream",
            "source_method": "web_scrape"
        },
        {
            "name": "Boutique Restaurant Chain",
            "price": 950000,
            "cash_flow": 145000,
            "earnings_multiple": 6.6,
            "reason_for_sale": "retirement",
            "location": "Brooklyn, NY",
            "category": "Restaurants",  # This will be filtered out
            "source_url": "https://example.com/listing4",
            "source_site": "bizbuysell",
            "source_method": "web_scrape"
        },
        {
            "name": "Medical Equipment Supplier",
            "price": 4200000,
            "cash_flow": 920000,
            "earnings_multiple": 4.6,
            "reason_for_sale": "retirement",
            "location": "New Jersey (near NYC)",
            "category": "Medical Equipment",
            "source_url": "https://example.com/listing5",
            "source_site": "bizquest",
            "source_method": "web_scrape"
        }
    ]
    
    print(f"📥 Found {len(current_listings)} current listings")
    
    # Load config
    with open("agent_config.yaml", 'r') as f:
        cfg = yaml.safe_load(f)
    
    # Process through pipeline (skip link check for demo)
    records = normalize_records(current_listings)
    records = dedupe_records(records)
    
    # Apply filters
    kept, drop_reasons = [], []
    for r in records:
        ok, why = policy_filter(r, cfg)
        if ok:
            r["reason_for_sale"] = postprocess_reason(r.get("reason_for_sale"))
            kept.append(r)
        else:
            drop_reasons.append({
                "name": r.get("name", ""),
                "reason": why
            })
    
    # Sort by price
    kept.sort(key=lambda x: (x.get("price") is None, x.get("price") or 10**12))
    
    # Create outputs
    write_json(kept, "data/demo_current_results.json")
    write_markdown(kept, "data/demo_current_results.md", prev_json_path="data/demo_current_results.json")
    
    # Show results
    print(f"\n📊 Results Summary:")
    print(f"   📥 Total listings found: {len(current_listings)}")
    print(f"   🎯 Matching your criteria: {len(kept)}")
    print(f"   ❌ Filtered out: {len(drop_reasons)}")
    
    if drop_reasons:
        print(f"\n❌ Filtered out:")
        for reject in drop_reasons:
            print(f"   • {reject['name']}: {reject['reason']}")
    
    if kept:
        print(f"\n🎉 {len(kept)} Current Opportunities Match Your Criteria!")
        print(f"\n🏆 Matching Listings:")
        for i, listing in enumerate(kept, 1):
            name = listing['name']
            price = f"${listing['price']:,}" if listing['price'] else 'TBD'
            multiple = f" ({listing['earnings_multiple']}x)" if listing['earnings_multiple'] else ''
            location = listing.get('location', 'Location TBD')
            print(f"   {i}. {name}")
            print(f"      💰 {price}{multiple}")
            print(f"      📍 {location}")
            print(f"      🔗 {listing.get('source_site', 'unknown').title()}")
            print()
    
    print(f"📄 Full report: data/demo_current_results.md")
    return kept

if __name__ == "__main__":
    results = demo_current_listings()
