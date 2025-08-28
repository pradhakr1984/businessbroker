from datetime import datetime, timezone

def normalize_records(records):
    out = []
    now = datetime.now(timezone.utc).isoformat()
    for r in records:
        r = dict(r)
        for k,v in list(r.items()):
            if isinstance(v, str):
                r[k] = v.strip()
        # types
        if r.get("price") is not None:
            try: r["price"] = float(r["price"])
            except: r["price"] = None
        if r.get("earnings_multiple") is not None:
            try: r["earnings_multiple"] = float(r["earnings_multiple"])
            except: r["earnings_multiple"] = None
        r["fetched_at_iso"] = now
        out.append(r)
    return out
