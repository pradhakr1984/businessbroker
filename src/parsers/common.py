# Conservative fallback parser using simple patterns; won't fabricate fields.
import re
from bs4 import BeautifulSoup

URL_RE = re.compile(r'https?://\S+')
PRICE_RE = re.compile(r'\$\s?([\d,]+(?:\.\d{2})?)')
EBITDA_RE = re.compile(r'(?:EBITDA|Cash\s*Flow|SDE)[:\s]*\$\s?([\d,]+(?:\.\d{2})?)', re.I)
REASON_RE = re.compile(r'(?:Reason\s*for\s*Sale|Owner\s*Reason)[:\s]*(.+)', re.I)
ADDR_RE = re.compile(r'Address[:\s]*(.+)', re.I)

def extract_urls(text):
    return URL_RE.findall(text)

def parse_generic_blocks(email):
    body = email.get("text_html") or email.get("text_plain") or ""
    if not body: return []
    soup = BeautifulSoup(body, "lxml")
    text = soup.get_text("\n", strip=True)

    urls = extract_urls(text)
    m_price = PRICE_RE.search(text)
    m_eb = EBITDA_RE.search(text)
    m_reason = REASON_RE.search(text)
    m_addr = ADDR_RE.search(text)

    if not urls or not m_price:
        return []

    rec = {
        "source_site": "unknown",
        "source_url": urls[0],
        "name": email.get("subject","").strip() or "Listing",
        "address": m_addr.group(1).strip() if m_addr else "",
        "price": float(str(m_price.group(1)).replace(",","")) if m_price else None,
        "earnings_multiple": None,
        "ownership_structure": None,
        "visit_frequency": None,
        "reason_for_sale": m_reason.group(1).strip() if m_reason else "",
        "ai_disruptability": "",
        "labor_intensity": "",
        "partial_match_explanation": None,
    }
    if m_eb:
        try:
            eb = float(str(m_eb.group(1)).replace(",",""))
            if eb > 0:
                rec["earnings_multiple"] = round(rec["price"]/eb, 2)
        except Exception:
            pass
    if rec["earnings_multiple"] is None:
        rec["partial_match_explanation"] = "multiple not disclosed"
    return [rec]
