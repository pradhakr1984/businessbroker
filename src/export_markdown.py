import pathlib, json

def write_markdown(listings, path, prev_json_path=None):
    out = []
    out.append("# Daily Results\n")
    prev_urls = set()
    p = pathlib.Path(prev_json_path) if prev_json_path else None
    if p and p.exists():
        try:
            prev = json.loads(p.read_text())
            prev_urls = {r.get("source_url","") for r in prev}
        except Exception:
            prev_urls = set()

    new = [r for r in listings if r.get("source_url","") and r["source_url"] not in prev_urls]
    if new:
        out.append("## New Today\n")
        for r in new:
            out.append(f"- **{r.get('name','')}** — ${r.get('price','')} — {r.get('reason_for_sale','')} — [{r.get('source_site','')}]({r.get('final_url', r.get('source_url',''))})")
        out.append("\n")

    out.append("## All (sorted by price)\n")
    out.append("| Name | Price | Multiple | Reason | URL |")
    out.append("|---|---:|---:|---|---|")
    for r in listings:
        url = r.get("final_url") or r.get("source_url","")
        out.append(f"| {r.get('name','')} | ${r.get('price','')} | {r.get('earnings_multiple','')} | {r.get('reason_for_sale','')} | [link]({url}) |")
    content = "\n".join(out) + "\n"
    pathlib.Path(path).parent.mkdir(parents=True, exist_ok=True)
    pathlib.Path(path).write_text(content, encoding="utf-8")
