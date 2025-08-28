RETIREMENT_HINTS = ("retire","succession","aging","after","long tenure","transition")
EXCLUDED_HINTS = ("restaurant","bar","cleaning","retail","salon","spa","gym")

def standardize_reason(text:str) -> str:
    t = (text or "").lower()
    if any(h in t for h in RETIREMENT_HINTS):
        return "retirement"
    if "relocat" in t:
        return "owner relocation"
    return "other"

def postprocess_reason(text:str) -> str:
    return standardize_reason(text)

def policy_filter(r, cfg):
    if r.get("price") is None:
        return False, "missing price"
    if r["price"] > cfg["price_usd_max"]:
        return False, "price > max"
    rs = standardize_reason(r.get("reason_for_sale",""))
    if rs != "retirement":
        return False, "reason not retirement"
    em = r.get("earnings_multiple")
    if em is not None and em > cfg["earnings_multiple_max"]:
        return False, "multiple > max"
    cat = (r.get("category") or "").lower()
    if any(h in cat for h in cfg.get("exclude_categories", [])) or any(h in (r.get("name","").lower()+" "+cat) for h in EXCLUDED_HINTS):
        return False, "excluded category"
    return True, ""
