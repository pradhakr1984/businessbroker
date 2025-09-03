import requests
from bs4 import BeautifulSoup
import time
import re
from urllib.parse import urljoin
import logging

def scrape_bizquest(scraper_cfg):
    """
    Scrape BizQuest.com search results
    
    scraper_cfg format:
    {
        "search_url": "https://www.bizquest.com/businesses-for-sale/...",
        "max_pages": 5,
        "delay_seconds": 2
    }
    """
    logging.info("Starting BizQuest scraping...")
    
    base_url = "https://www.bizquest.com"
    search_url = scraper_cfg["search_url"]
    max_pages = scraper_cfg.get("max_pages", 5)
    delay = scraper_cfg.get("delay_seconds", 2)
    
    listings = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    for page in range(1, max_pages + 1):
        logging.info(f"Scraping BizQuest page {page}...")
        
        # BizQuest uses different pagination format
        if page > 1:
            if '?' in search_url:
                page_url = f"{search_url}&page={page}"
            else:
                page_url = f"{search_url}?page={page}"
        else:
            page_url = search_url
        
        try:
            response = requests.get(page_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find listing cards (adjust selectors based on BizQuest's HTML structure)
            listing_cards = soup.find_all('div', class_=['business-listing', 'listing-card', 'search-result'])
            
            if not listing_cards:
                # Try alternative selectors
                listing_cards = soup.find_all('article') or soup.find_all('div', class_=re.compile(r'listing|business|result'))
            
            if not listing_cards:
                logging.warning(f"No listings found on BizQuest page {page}, stopping pagination")
                break
                
            for card in listing_cards:
                listing = parse_bizquest_card(card, base_url)
                if listing:
                    listings.append(listing)
            
            # Respectful delay
            time.sleep(delay)
            
        except Exception as e:
            logging.error(f"Error scraping BizQuest page {page}: {e}")
            continue
    
    logging.info(f"BizQuest scraping complete: {len(listings)} listings found")
    return listings

def parse_bizquest_card(card, base_url):
    """Parse individual BizQuest listing card"""
    try:
        listing = {
            "source_site": "bizquest",
            "source_method": "web_scrape"
        }
        
        # Title/Name
        title_elem = card.find('h3') or card.find('h2') or card.find('a', class_=re.compile(r'title|name|heading'))
        if title_elem:
            listing["name"] = title_elem.get_text(strip=True)
        
        # URL
        link_elem = card.find('a', href=True)
        if link_elem:
            href = link_elem['href']
            if href.startswith('/'):
                listing["source_url"] = urljoin(base_url, href)
            else:
                listing["source_url"] = href
        
        # Price
        price_elem = card.find(text=re.compile(r'Asking Price|Price')) or card.find('span', class_=re.compile(r'price'))
        if price_elem:
            price_text = price_elem if isinstance(price_elem, str) else price_elem.get_text(strip=True)
            price_match = re.search(r'\$?([\d,]+)', price_text.replace(',', ''))
            if price_match:
                listing["price"] = int(price_match.group(1))
        
        # Cash Flow
        cash_flow_elem = card.find(text=re.compile(r'Cash Flow|Net Income'))
        if cash_flow_elem:
            cash_flow_text = cash_flow_elem if isinstance(cash_flow_elem, str) else cash_flow_elem.get_text(strip=True)
            cash_match = re.search(r'\$?([\d,]+)', cash_flow_text.replace(',', ''))
            if cash_match:
                listing["cash_flow"] = int(cash_match.group(1))
                if listing.get("price") and listing["cash_flow"]:
                    listing["earnings_multiple"] = round(listing["price"] / listing["cash_flow"], 1)
        
        # Location
        location_elem = card.find(text=re.compile(r'Location:|[A-Z]{2}\s*$')) or card.find('span', class_=re.compile(r'location'))
        if location_elem:
            location_text = location_elem if isinstance(location_elem, str) else location_elem.get_text(strip=True)
            listing["location"] = location_text.strip()
        
        # Reason for sale (if available)
        reason_elem = card.find(text=re.compile(r'Reason|Selling|Retirement'))
        if reason_elem:
            reason_text = reason_elem if isinstance(reason_elem, str) else reason_elem.get_text(strip=True)
            listing["reason_for_sale"] = reason_text.strip()
        
        # Only return if we have essential fields
        if listing.get("name") and listing.get("source_url"):
            return listing
        
    except Exception as e:
        logging.error(f"Error parsing BizQuest card: {e}")
    
    return None

def build_bizquest_search_url(cfg):
    """Build BizQuest search URL from config parameters"""
    base = "https://www.bizquest.com/businesses-for-sale/"
    
    params = []
    
    # Price range
    if cfg.get("price_usd_max"):
        params.append(f"price_max={cfg['price_usd_max']}")
    
    # Location (simplified)
    if cfg.get("center_address"):
        location_parts = cfg["center_address"].split(",")
        if len(location_parts) >= 2:
            state = location_parts[-1].strip().split()[-1]
            params.append(f"state={state}")
    
    # Build URL
    if params:
        return base + "?" + "&".join(params)
    else:
        return base
