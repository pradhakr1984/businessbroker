# Web scrapers for direct listing access
from .bizbuysell_scraper import scrape_bizbuysell
from .bizquest_scraper import scrape_bizquest
from .dealstream_scraper import scrape_dealstream

def scrape_all_platforms(cfg):
    """Scrape listings from all configured platforms"""
    all_listings = []
    
    if cfg.get("bizbuysell", {}).get("enabled", False):
        listings = scrape_bizbuysell(cfg["bizbuysell"])
        all_listings.extend(listings)
        
    if cfg.get("bizquest", {}).get("enabled", False):
        listings = scrape_bizquest(cfg["bizquest"])
        all_listings.extend(listings)
        
    if cfg.get("dealstream", {}).get("enabled", False):
        listings = scrape_dealstream(cfg["dealstream"])
        all_listings.extend(listings)
    
    return all_listings
