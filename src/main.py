import os, json, argparse, csv, pathlib, logging
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

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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
    all_records = []
    all_parse_rejects = []
    
    # 1) Fetch from Email Alerts (if enabled)
    if cfg.get("sources", {}).get("email_alerts", {}).get("enabled", True):
        logging.info("📧 Fetching email alerts...")
        
        # For backward compatibility, check old config format too
        imap_label = cfg.get("sources", {}).get("email_alerts", {}).get("imap_label") or cfg.get("imap_label", "biz-acq/alerts")
        lookback_days = cfg.get("sources", {}).get("email_alerts", {}).get("lookback_days") or cfg.get("lookback_days", 7)
        
        records_raw = fetch_alert_emails(
            label=imap_label,
            lookback_days=int(lookback_days)
        )
        records, parse_rejects = parse_emails_to_records(records_raw)
        all_records.extend(records)
        all_parse_rejects.extend(parse_rejects)
        logging.info(f"📧 Email alerts: {len(records)} listings found")
    
    # 2) Fetch from Web Scraping (if enabled)
    if cfg.get("sources", {}).get("web_scraping", {}).get("enabled", False):
        logging.info("🌐 Starting web scraping...")
        try:
            from src.scrapers import scrape_all_platforms
            scraped_listings = scrape_all_platforms(cfg["sources"]["web_scraping"])
            all_records.extend(scraped_listings)
            logging.info(f"🌐 Web scraping: {len(scraped_listings)} listings found")
        except ImportError:
            logging.error("Web scraping modules not available. Install required dependencies.")
        except Exception as e:
            logging.error(f"Error during web scraping: {e}")
    
    # If no records from any source
    if not all_records:
        logging.info("No listings found from any source")
        records = []
    else:
        records = all_records
    
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
    all_rejects = all_parse_rejects + link_rejects + drop_reasons
    write_rejects(all_rejects, cfg["outputs"]["rejects_path"])
    print(f"Parsed: {len(all_records)} | Kept: {len(kept)} | Rejects: {len(all_rejects)}")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", "-c", default="agent_config.yaml")
    args = ap.parse_args()
    main(args.config)
