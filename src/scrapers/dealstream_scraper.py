import requests
from bs4 import BeautifulSoup
import time
import re
from urllib.parse import urljoin
import logging

def scrape_dealstream(scraper_cfg):
    """
    Scrape DealStream.com search results
    
    scraper_cfg format:
    {
        "search_url": "https://www.dealstream.com/opportunities/...",
        "max_pages": 5,
        "delay_seconds": 2
    }
    """
    logging.info("Starting DealStream scraping...")
    
    base_url = "https://www.dealstream.com"
    search_url = scraper_cfg["search_url"]
    max_pages = scraper_cfg.get("max_pages", 5)
    delay = scraper_cfg.get("delay_seconds", 2)
    
    listings = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    for page in range(1, max_pages + 1):
        logging.info(f"Scraping DealStream page {page}...")
        
        # DealStream pagination
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
            
            # Find listing cards (adjust selectors based on DealStream's HTML structure)
            listing_cards = soup.find_all('div', class_=['opportunity-card', 'deal-card', 'listing-item'])
            
            if not listing_cards:
                # Try alternative selectors
                listing_cards = soup.find_all('div', class_=re.compile(r'opportunity|deal|listing|business'))
            
            if not listing_cards:
                logging.warning(f"No listings found on DealStream page {page}, stopping pagination")
                break
                
            for card in listing_cards:
                listing = parse_dealstream_card(card, base_url)
                if listing:
                    listings.append(listing)
            
            # Respectful delay
            time.sleep(delay)
            
        except Exception as e:
            logging.error(f"Error scraping DealStream page {page}: {e}")
            continue
    
    logging.info(f"DealStream scraping complete: {len(listings)} listings found")
    return listings

def parse_dealstream_card(card, base_url):
    """Parse individual DealStream listing card"""
    try:
        listing = {
            "source_site": "dealstream",
            "source_method": "web_scrape"
        }
        
        # Title/Name
        title_elem = card.find('h3') or card.find('h2') or card.find('a', class_=re.compile(r'title|name|opportunity'))
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
        
        # Price/Valuation
        price_elem = card.find(text=re.compile(r'Valuation|Price|Seeking')) or card.find('span', class_=re.compile(r'price|valuation'))
        if price_elem:
            price_text = price_elem if isinstance(price_elem, str) else price_elem.get_text(strip=True)
            price_match = re.search(r'\$?([\d,]+)', price_text.replace(',', ''))
            if price_match:
                listing["price"] = int(price_match.group(1))
        
        # Revenue/EBITDA
        revenue_elem = card.find(text=re.compile(r'Revenue|EBITDA|Earnings'))
        if revenue_elem:
            revenue_text = revenue_elem if isinstance(revenue_elem, str) else revenue_elem.get_text(strip=True)
            revenue_match = re.search(r'\$?([\d,]+)', revenue_text.replace(',', ''))
            if revenue_match:
                listing["cash_flow"] = int(revenue_match.group(1))
                if listing.get("price") and listing["cash_flow"]:
                    listing["earnings_multiple"] = round(listing["price"] / listing["cash_flow"], 1)
        
        # Industry/Category
        industry_elem = card.find(text=re.compile(r'Industry|Category|Sector'))
        if industry_elem:
            industry_text = industry_elem if isinstance(industry_elem, str) else industry_elem.get_text(strip=True)
            listing["category"] = industry_text.strip()
        
        # Location
        location_elem = card.find(text=re.compile(r'Location:|[A-Z]{2}\s*$')) or card.find('span', class_=re.compile(r'location'))
        if location_elem:
            location_text = location_elem if isinstance(location_elem, str) else location_elem.get_text(strip=True)
            listing["location"] = location_text.strip()
        
        # Only return if we have essential fields
        if listing.get("name") and listing.get("source_url"):
            return listing
        
    except Exception as e:
        logging.error(f"Error parsing DealStream card: {e}")
    
    return None

def build_dealstream_search_url(cfg):
    """Build DealStream search URL from config parameters"""
    base = "https://www.dealstream.com/opportunities/"
    
    params = []
    
    # Price range
    if cfg.get("price_usd_max"):
        params.append(f"price_max={cfg['price_usd_max']}")
    
    # Industry exclusions
    if cfg.get("exclude_categories"):
        for category in cfg["exclude_categories"]:
            params.append(f"exclude_industry={category}")
    
    # Build URL
    if params:
        return base + "?" + "&".join(params)
    else:
        return base
