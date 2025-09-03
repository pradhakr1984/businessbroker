#!/usr/bin/env python3
"""
Process manually entered listings through the same filters and pipeline
"""

import json
import sys
import yaml
from src.normalize import normalize_records
from src.linkcheck import link_check_records
from src.dedupe import dedupe_records
from src.filters import policy_filter, postprocess_reason
from src.export_json import write_json
from src.export_markdown import write_markdown

def process_manual_listings(manual_file, config_file="agent_config.yaml"):
    """Process manual listings through the same pipeline as scraped ones"""
    print(f"🔄 Processing manual listings from {manual_file}")
    print("=" * 50)
    
    # Load manual listings
    with open(manual_file, 'r') as f:
        manual_listings = json.load(f)
    
    print(f"📥 Loaded {len(manual_listings)} manual listings")
    
    # Load config
    with open(config_file, 'r') as f:
        cfg = yaml.safe_load(f)
    
    # Process through same pipeline as automated scraping
    records = manual_listings
    
    # 1) normalize
    print("🔧 Normalizing records...")
    records = normalize_records(records)
    
    # 2) link check (if URLs provided)
    print("🔗 Checking links...")
    records, link_rejects = link_check_records(records)
    
    # 3) dedupe
    print("🔄 Deduplicating...")
    records = dedupe_records(records)
    
    # 4) filtering
    print("🎯 Applying filters...")
    kept, drop_reasons = [], []
    for r in records:
        ok, why = policy_filter(r, cfg)
        if ok:
            r["reason_for_sale"] = postprocess_reason(r.get("reason_for_sale"))
            kept.append(r)
        else:
            drop_reasons.append({
                "source_site": r.get("source_site", ""),
                "source_url": r.get("source_url", ""),
                "reason": why
            })
    
    # 5) sort by price asc
    kept.sort(key=lambda x: (x.get("price") is None, x.get("price") or 10**12))
    
    # 6) exports
    output_prefix = manual_file.replace('.json', '')
    json_path = f"{output_prefix}_filtered.json"
    md_path = f"{output_prefix}_filtered.md"
    
    write_json(kept, json_path)
    write_markdown(kept, md_path, prev_json_path=json_path)
    
    # 7) summary
    print(f"\n📊 Results:")
    print(f"   📥 Input: {len(manual_listings)} listings")
    print(f"   🔗 After link check: {len(records)} listings")
    print(f"   🎯 After filters: {len(kept)} listings")
    print(f"   ❌ Rejected: {len(drop_reasons)} listings")
    
    if drop_reasons:
        print(f"\n❌ Rejection reasons:")
        for reject in drop_reasons:
            print(f"   • {reject['reason']}")
    
    print(f"\n📄 Files created:")
    print(f"   📊 Filtered JSON: {json_path}")
    print(f"   📋 Report: {md_path}")
    
    if kept:
        print(f"\n🎉 {len(kept)} opportunities match your criteria!")
        print(f"📖 Open {md_path} to see the full report")
        
        # Show top opportunities
        print(f"\n🏆 Top opportunities:")
        for i, listing in enumerate(kept[:3], 1):
            name = listing.get('name', 'Unnamed')
            price = f"${listing.get('price', 0):,}" if listing.get('price') else 'TBD'
            multiple = f" ({listing.get('earnings_multiple')}x)" if listing.get('earnings_multiple') else ''
            reason = listing.get('reason_for_sale', 'Not specified')
            print(f"   {i}. {name} - {price}{multiple} - {reason}")
    else:
        print(f"\n😔 No listings matched your criteria")
        print(f"💡 Consider adjusting filters in {config_file}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python process_manual_listings.py <manual_listings.json>")
        sys.exit(1)
    
    manual_file = sys.argv[1]
    config_file = sys.argv[2] if len(sys.argv) > 2 else "agent_config.yaml"
    
    try:
        process_manual_listings(manual_file, config_file)
    except FileNotFoundError as e:
        print(f"❌ File not found: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
