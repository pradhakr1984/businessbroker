#!/usr/bin/env python3
"""
Test script for web scraping functionality
Run this to test the new web scraping features
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from src.scrapers.bizbuysell_scraper import scrape_bizbuysell, build_bizbuysell_search_url
from src.scrapers.bizquest_scraper import scrape_bizquest, build_bizquest_search_url

def test_url_builders():
    """Test the URL building functions"""
    print("🔗 Testing URL builders...")
    
    test_config = {
        "center_address": "37 Warren Street, New York, NY 10007",
        "price_usd_max": 5000000,
        "exclude_categories": ["restaurants", "bars"]
    }
    
    bizbuysell_url = build_bizbuysell_search_url(test_config)
    bizquest_url = build_bizquest_search_url(test_config)
    
    print(f"   BizBuySell URL: {bizbuysell_url}")
    print(f"   BizQuest URL: {bizquest_url}")
    print()

def test_single_scraper():
    """Test a single scraper with minimal pages"""
    print("🕷️  Testing BizBuySell scraper (1 page)...")
    
    scraper_config = {
        "search_url": "https://www.bizbuysell.com/businesses-for-sale/",
        "max_pages": 1,
        "delay_seconds": 1
    }
    
    try:
        listings = scrape_bizbuysell(scraper_config)
        print(f"   Found {len(listings)} listings")
        
        if listings:
            print("   Sample listing:")
            sample = listings[0]
            for key, value in sample.items():
                print(f"     {key}: {value}")
        print()
        
    except Exception as e:
        print(f"   Error: {e}")
        print()

def test_full_pipeline():
    """Test the full pipeline with web scraping"""
    print("🎯 Testing full pipeline with web scraping...")
    
    try:
        from src.main import main
        main("web_scraping_config.yaml")
        print("   ✅ Full pipeline completed successfully!")
        
        # Show results
        print("\n📄 Results summary:")
        if os.path.exists("data/web_scraping_results.json"):
            import json
            with open("data/web_scraping_results.json", "r") as f:
                results = json.load(f)
            print(f"   📊 Total opportunities: {len(results)}")
            
            if results:
                print("   💰 Price range:")
                prices = [r.get("price") for r in results if r.get("price")]
                if prices:
                    print(f"     Min: ${min(prices):,}")
                    print(f"     Max: ${max(prices):,}")
                    print(f"     Avg: ${sum(prices)//len(prices):,}")
        else:
            print("   ❌ No results file found")
            
    except Exception as e:
        print(f"   Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🎯 Business Acquisition Agent - Web Scraping Test")
    print("=" * 50)
    print()
    
    test_url_builders()
    test_single_scraper()
    test_full_pipeline()
    
    print("🎉 Testing complete!")
    print()
    print("💡 To enable web scraping in your main agent:")
    print("   1. Edit agent_config.yaml")
    print("   2. Set sources.web_scraping.enabled: true")
    print("   3. Enable individual platforms as needed")
    print("   4. Run: python -m src.main --config agent_config.yaml")
