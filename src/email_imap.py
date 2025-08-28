import os
from datetime import datetime, timedelta, timezone
from imapclient import IMAPClient
from mailparser import parse_from_bytes

def _env(key, default=None):
    v = os.getenv(key)
    return v if v is not None else default

def fetch_alert_emails(label:str, lookback_days:int=2):
    host = _env("IMAP_HOST","imap.gmail.com")
    port = int(_env("IMAP_PORT","993"))
    user = _env("IMAP_USERNAME")
    pwd  = _env("IMAP_APP_PASSWORD")
    if not (user and pwd):
        raise RuntimeError("IMAP_USERNAME / IMAP_APP_PASSWORD missing (see .env.example)")

    since = (datetime.now(timezone.utc) - timedelta(days=lookback_days)).strftime("%d-%b-%Y")
    emails = []

    with IMAPClient(host, port=port, ssl=True) as server:
        server.login(user, pwd)
        # Gmail "All Mail" holds labeled mail as well
        server.select_folder("[Gmail]/All Mail", readonly=True)
        ids = []
        try:
            # Gmail fast path: label + recent
            ids = server.gmail_search(f'label:{label} newer_than:{lookback_days}d')
        except Exception:
            # Generic IMAP fallback: SINCE date (may include extra)
            ids = server.search(['SINCE', since])
        if not ids:
            return []
        response = server.fetch(ids, ["RFC822", "ENVELOPE"])
        for uid, data in response.items():
            raw = data[b"RFC822"]
            mail = parse_from_bytes(raw)
            emails.append({
                "uid": uid,
                "from": mail.from_,
                "subject": mail.subject or "",
                "date": mail.date.isoformat() if mail.date else "",
                "text_plain": "\n".join(mail.text_plain) if mail.text_plain else "",
                "text_html": "\n".join(mail.text_html) if mail.text_html else "",
                "attachments": [att["payload"] for att in (mail.attachments or [])]
            })
    return emails
