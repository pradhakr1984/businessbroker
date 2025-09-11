import re
from bs4 import BeautifulSoup

def parse_dealstream(email):
    subj = (email.get("subject") or "").lower()
    froms = email.get("from") or []
    if ("dealstream" not in subj and "mergernetwork" not in subj
        and not any(("dealstream" in (x[1] or "").lower() or "mergernetwork" in (x[1] or "").lower()) for x in froms)):
        return []

    html = email.get("text_html") or email.get("text_plain") or ""
    if not html:
        return []

    soup = BeautifulSoup(html, "lxml")
    text = soup.get_text("\n", strip=True)

    price_re  = re.compile(r'Price[:\s]*\$\s?([\d,]+)', re.I)
    cf_re     = re.compile(r'(?:EBITDA|Cash\s*Flow|SDE)[:\s]*\$\s?([\d,]+)', re.I)
    reason_re = re.compile(r'(?:Reason\s*for\s*Sale)[:\s]*(.+)', re.I)
    a = soup.find("a", string=re.compile(r"(View|See)\s+(Listing|Details)", re.I))
    url = a.get("href") if a else None

    m_price  = price_re.search(text)
    m_cf     = cf_re.search(text)
    m_reason = reason_re.search(text)
    if not (url and m_price):
        return []

    rec = {
        "source_site": "dealstream",
        "source_url": url,
        "name": (email.get("subject") or "Listing").strip(),
        "address": "",
        "price": float(str(m_price.group(1)).replace(",", "")),
        "earnings_multiple": None,
        "ownership_structure": None,
        "visit_frequency": None,
        "reason_for_sale": m_reason.group(1).strip() if m_reason else "",
        "ai_disruptability": "",
        "labor_intensity": "",
        "partial_match_explanation": None,
    }
    if m_cf:
        try:
            cf = float(str(m_cf.group(1)).replace(",", ""))
            if cf > 0:
                rec["earnings_multiple"] = round(rec["price"] / cf, 2)
        except Exception:
            pass
    if rec["earnings_multiple"] is None:
        rec["partial_match_explanation"] = "multiple not disclosed"
    return [rec]
