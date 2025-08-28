from typing import List, Tuple, Dict
from .common import parse_generic_blocks
from .bizbuysell import parse_bizbuysell

PARSERS = [
    parse_bizbuysell,     # site-specific
    parse_generic_blocks, # conservative fallback
]

def parse_emails_to_records(emails) -> Tuple[List[Dict], List[Dict]]:
    records = []
    rejects = []
    for em in emails:
        parsed_any = False
        for fn in PARSERS:
            try:
                recs = fn(em)
                if recs:
                    records.extend(recs)
                    parsed_any = True
                    break
            except Exception:
                continue
        if not parsed_any:
            rejects.append({
                "source_site": "unknown",
                "source_url": "",
                "reason": "no parser matched"
            })
    return records, rejects
