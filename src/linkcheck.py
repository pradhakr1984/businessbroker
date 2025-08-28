import requests

def link_check_records(records, timeout=12):
    kept, rejects = [], []
    for r in records:
        url = r.get("source_url")
        if not url:
            rejects.append({"source_site": r.get("source_site",""), "source_url": "", "reason": "missing url"})
            continue
        try:
            resp = requests.head(url, allow_redirects=True, timeout=timeout)
            if resp.status_code >= 400:
                resp = requests.get(url, allow_redirects=True, timeout=timeout, stream=True)
            if resp.status_code < 400:
                r["final_url"] = resp.url
                kept.append(r)
            else:
                rejects.append({"source_site": r.get("source_site",""), "source_url": url, "reason": f"http {resp.status_code}"})
        except Exception:
            rejects.append({"source_site": r.get("source_site",""), "source_url": url, "reason": "link check failed"})
    return kept, rejects
