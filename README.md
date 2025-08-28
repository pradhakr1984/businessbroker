# Acquisition Agent (Email-Driven, No Listing-Site APIs)

Deterministic daily pipeline that ingests **saved-search alert emails** from business-for-sale marketplaces, parses listings,
**never fabricates fields**, validates links, dedupes across sources, filters to your criteria, and exports JSON + Markdown.

> This repo is a starter template. You will likely tweak the per-site parsers in `src/parsers/` to match the email formats you receive.

## Quick Start (local)
1. Create a Gmail app password (if using 2FA). Enable IMAP in Gmail.
2. Copy `.env.example` to `.env` and fill in credentials.
3. Install deps:
   ```bash
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```
4. Run:
   ```bash
   python -m src.main --config agent_config.yaml
   ```
5. Open outputs:
   - `data/results.json` (machine-readable, sorted by price asc)
   - `data/results.md` (digest)
   - `data/rejects.csv` (why some were dropped)

## GitHub Actions (daily)
- Add repo secrets `IMAP_USERNAME`, `IMAP_APP_PASSWORD`.
- The workflow `.github/workflows/daily.yml` runs daily and commits artifacts back to the repo.

## Important
- The parsers only extract fields that **actually exist** in the emails; missing fields are left blank and (optionally) recorded in `partial_match_explanation`.
- No scraping of listing sites; this ingests **your emails**.
- Tune `agent_config.yaml` filters to your needs.
