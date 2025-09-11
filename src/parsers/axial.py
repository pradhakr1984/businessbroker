import re
from bs4 import BeautifulSoup

def parse_axial(email):
    """
    Parser for Axial deal flow emails.
    Axial typically sends deal notifications with subject lines like "New Deal Alert" or "Deal Opportunity"
    and includes deal details in structured format.
    """
    subj = (email.get("subject") or "").lower()
    froms = email.get("from") or []
    
    # Check if this is an Axial email - be more permissive
    is_axial_domain = any("axial" in (x[1] or "").lower() for x in froms)
    
    # Axial keywords that commonly appear in their emails
    axial_keywords = ["deal alert", "deal opportunity", "new opportunity", "investment opportunity", "axial"]
    
    # Check if this looks like an Axial email
    has_axial_keywords = any(keyword in subj for keyword in axial_keywords)
    
    # If it's not from Axial domain and doesn't have Axial keywords, skip
    if not is_axial_domain and not has_axial_keywords:
        return []

    html = email.get("text_html") or email.get("text_plain") or ""
    if not html:
        return []

    soup = BeautifulSoup(html, "lxml")
    text = soup.get_text("\n", strip=True)

    # Axial-specific regex patterns
    # Common patterns for business details in Axial emails
    price_patterns = [
        r'(?:Asking\s*Price|Price|Valuation)[:\s]*\$\s?([\d,]+(?:\.\d{1,2})?)\s*(?:M|Million)',
        r'(?:Asking\s*Price|Price|Valuation)[:\s]*\$\s?([\d,]+(?:\.\d{2})?)',
        r'(?:Enterprise\s*Value|EV)[:\s]*\$\s?([\d,]+(?:\.\d{1,2})?)\s*(?:M|Million)',
        r'(?:Enterprise\s*Value|EV)[:\s]*\$\s?([\d,]+(?:\.\d{2})?)',
    ]
    
    ebitda_patterns = [
        r'(?:EBITDA|TTM\s*EBITDA)[:\s]*\$\s*([\d,]+(?:\.\d{1,2})?)\s*[Kk]',
        r'(?:EBITDA|TTM\s*EBITDA)[:\s]*\$\s*([\d,]+(?:\.\d{1,2})?)\s*(?:M|Million)',
        r'(?:EBITDA|TTM\s*EBITDA)[:\s]*\$\s*([\d,]+(?:\.\d{2})?)',
        r'(?:Cash\s*Flow|SDE)[:\s]*\$\s*([\d,]+(?:\.\d{1,2})?)\s*[Kk]',
        r'(?:Cash\s*Flow|SDE)[:\s]*\$\s*([\d,]+(?:\.\d{1,2})?)\s*(?:M|Million)',
        r'(?:Cash\s*Flow|SDE)[:\s]*\$\s*([\d,]+(?:\.\d{2})?)',
        r'(?:Earnings)[:\s]*\$\s*([\d,]+(?:\.\d{2})?)',
    ]
    
    revenue_patterns = [
        r'(?:Revenue|Sales|TTM\s*Revenue)[:\s]*\$\s?([\d,]+(?:\.\d{2})?)',
    ]
    
    reason_patterns = [
        r'(?:Reason\s*for\s*Sale|Seller\s*Motivation)[:\s]*(.+?)(?:\n|$)',
        r'(?:Why\s*Selling|Sale\s*Rationale)[:\s]*(.+?)(?:\n|$)',
    ]
    
    location_patterns = [
        r'(?:Location|Geography|Headquarters)[:\s]*(.+?)(?:\n|$)',
        r'(?:Based\s*in|Located\s*in)[:\s]*(.+?)(?:\n|$)',
    ]
    
    industry_patterns = [
        r'(?:Industry|Sector|Business\s*Type)[:\s]*(.+?)(?:\n|$)',
        r'(?:Category|Vertical)[:\s]*(.+?)(?:\n|$)',
    ]

    # Extract information using patterns
    price = None
    ebitda = None
    revenue = None
    reason = ""
    location = ""
    industry = ""
    
    for pattern in price_patterns:
        m = re.search(pattern, text, re.I)
        if m:
            try:
                price_str = m.group(1).replace(",", "")
                price = float(price_str)
                # Convert millions to actual value if needed
                if "M" in m.group(0) or "Million" in m.group(0):
                    price = price * 1000000
                break
            except:
                continue
    
    for pattern in ebitda_patterns:
        m = re.search(pattern, text, re.I)
        if m:
            try:
                ebitda_str = m.group(1).replace(",", "")
                ebitda = float(ebitda_str)
                # Check for K first (thousands), then M (millions)
                if "K" in m.group(0) or "k" in m.group(0):
                    ebitda = ebitda * 1000
                elif "M" in m.group(0) or "Million" in m.group(0):
                    ebitda = ebitda * 1000000
                break
            except Exception as e:
                continue
    
    for pattern in reason_patterns:
        m = re.search(pattern, text, re.I)
        if m:
            reason = m.group(1).strip()
            break
    
    for pattern in location_patterns:
        m = re.search(pattern, text, re.I)
        if m:
            location = m.group(1).strip()
            break
    
    for pattern in industry_patterns:
        m = re.search(pattern, text, re.I)
        if m:
            industry = m.group(1).strip()
            break

    # Look for URLs (deal links)
    url_pattern = r'https?://(?:www\.)?axial\.net/[^\s]+|https?://[^\s]*deal[^\s]*|https?://[^\s]*opportunity[^\s]*'
    urls = re.findall(url_pattern, text, re.I)
    
    # Fallback to any URL if no specific deal URL found
    if not urls:
        url_pattern = r'https?://\S+'
        urls = re.findall(url_pattern, text)
    
    # Require at least a price to create a record
    if not price:
        return []

    # Extract business name from subject or email content
    business_name = email.get("subject", "").strip()
    if "deal alert" in business_name.lower():
        # Try to extract business name from content
        name_patterns = [
            r'(?:Company|Business|Target)[:\s]*(.+?)(?:\n|$)',
            r'(?:Name)[:\s]*(.+?)(?:\n|$)',
        ]
        for pattern in name_patterns:
            m = re.search(pattern, text, re.I)
            if m:
                potential_name = m.group(1).strip()
                if len(potential_name) > 3 and len(potential_name) < 100:
                    business_name = potential_name
                    break
    
    if not business_name or business_name.lower() in ["listing", "deal alert", "new opportunity"]:
        business_name = f"Axial Deal - {industry}" if industry else "Axial Deal"

    rec = {
        "source_site": "axial",
        "source_url": urls[0] if urls else "",
        "name": business_name,
        "address": location,
        "price": price,
        "earnings_multiple": None,
        "ownership_structure": None,
        "visit_frequency": None,
        "reason_for_sale": reason,
        "category": industry,
        "ai_disruptability": "",
        "labor_intensity": "",
        "partial_match_explanation": None,
    }
    
    # Calculate earnings multiple if both price and EBITDA are available
    if ebitda and ebitda > 0:
        try:
            rec["earnings_multiple"] = round(price / ebitda, 2)
        except:
            pass
    
    if rec["earnings_multiple"] is None:
        rec["partial_match_explanation"] = "multiple not disclosed"
    
    return [rec]
