import os, json, argparse, csv, pathlib
from datetime import datetime, timezone
import yaml
from src.email_imap import fetch_alert_emails
from src.parsers import parse_emails_to_records
from src.normalize import normalize_records
from src.linkcheck import link_check_records
from src.dedupe import dedupe_records
from src.filters import policy_filter, postprocess_reason
from src.export_json import write_json
from src.export_markdown import write_markdown

def load_cfg(path:str):
    with open(path, "r") as f:
        return yaml.safe_load(f)

def write_rejects(rejects, path):
    if not rejects: return
    pathlib.Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["source_site","source_url","reason"])
        for r in rejects:
            w.writerow([r.get("source_site",""), r.get("source_url",""), r.get("reason","")])

def main(cfg_path:str):
    cfg = load_cfg(cfg_path)
    # 1) fetch emails
    records_raw = fetch_alert_emails(
        label=cfg["imap_label"],
        lookback_days=int(cfg.get("lookback_days",2))
    )
    # 2) parse emails -> listing dicts
    records, parse_rejects = parse_emails_to_records(records_raw)
    # 3) normalize
    records = normalize_records(records)
    # 4) link check
    records, link_rejects = link_check_records(records)
    # 5) dedupe
    records = dedupe_records(records)
    # 6) filtering
    kept, drop_reasons = [], []
    for r in records:
        ok, why = policy_filter(r, cfg)
        if ok:
            r["reason_for_sale"] = postprocess_reason(r.get("reason_for_sale"))
            kept.append(r)
        else:
            drop_reasons.append({"source_site": r.get("source_site",""), "source_url": r.get("source_url",""), "reason": why})
    # 7) sort by price asc
    kept.sort(key=lambda x: (x.get("price") is None, x.get("price") or 10**12))
    # 8) exports
    write_json(kept, cfg["outputs"]["json_path"])
    write_markdown(kept, cfg["outputs"]["markdown_path"], prev_json_path=cfg["outputs"]["json_path"])
    # 9) rejects
    all_rejects = parse_rejects + link_rejects + drop_reasons
    write_rejects(all_rejects, cfg["outputs"]["rejects_path"])
    print(f"Parsed: {len(records)} | Kept: {len(kept)} | Rejects: {len(all_rejects)}")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", "-c", default="agent_config.yaml")
    args = ap.parse_args()
    main(args.config)
