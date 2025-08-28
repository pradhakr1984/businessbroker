from rapidfuzz import fuzz

BAD = {"inc","llc","corp","co","ltd",".",","}

def key(name, address):
    parts = []
    for w in f"{name} {address}".split():
        w = w.lower().strip(".,")
        if w and w not in BAD:
            parts.append(w)
    return " ".join(parts)

def is_dup(a,b,th=92):
    return fuzz.token_set_ratio(key(a.get("name",""),a.get("address","")),
                                key(b.get("name",""),b.get("address",""))) >= th

def prefer(a,b):
    score = lambda r: sum(bool(r.get(k)) for k in ["earnings_multiple","reason_for_sale","ownership_structure","visit_frequency"]) + int(bool(r.get("final_url")))
    return a if score(a) >= score(b) else b

def dedupe_records(items):
    out = []
    for it in items:
        for i, ex in enumerate(out):
            if is_dup(it, ex):
                out[i] = prefer(ex, it)
                break
        else:
            out.append(it)
    return out
