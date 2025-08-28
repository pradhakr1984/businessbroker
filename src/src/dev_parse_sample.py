import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from bizquest import parse_bizquest  # swap for the parser you want
sample = {
    "subject": "BizQuest Saved Search Results – New Listing",
    "from": [("BizQuest Alerts", "alerts@bizquest.com")],
    "text_html": """<html><body>
      <h1>New Listing</h1>
      <div>Price: $1,250,000</div>
      <div>Cash Flow: $310,000</div>
      <div>Reason for Sale: Owner retiring after 25 years</div>
      <a href="https://www.bizquest.com/listings/abc123">View Listing</a>
    </body></html>"""
}
print(parse_bizquest(sample))
