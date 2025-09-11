# Multi-Platform Integration

## Overview
The acquisition agent now includes support for filtering deal flow emails from multiple platforms using the same criteria. Supported platforms include:

- **BizBuySell** - Business marketplace
- **BizQuest** - Business marketplace  
- **DealStream** - Investment opportunities
- **LoopNet** - Business listings
- **BusinessBroker** - Broker listings
- **Axial** - Deal flow platform

All platforms use the same filtering criteria defined in `agent_config.yaml`.

## How It Works

### Email Parsing
Each platform has a dedicated parser that automatically detects and parses emails:

**BizBuySell** (`src/parsers/bizbuysell.py`):
- Emails from `bizbuysell.com` domains
- Subject lines containing "bizbuysell"

**BizQuest** (`src/parsers/bizquest.py`):
- Emails from `bizquest.com` domains  
- Subject lines containing "bizquest"

**DealStream** (`src/parsers/dealstream.py`):
- Emails from `dealstream.com` or `mergernetwork.com` domains
- Subject lines containing "dealstream" or "mergernetwork"

**LoopNet** (`src/parsers/loopnet.py`):
- Emails from `loopnet.com` domains
- Subject lines containing "loopnet" + business/listing keywords

**BusinessBroker** (`src/parsers/businessbroker.py`):
- Emails from `businessbroker.com` domains
- Subject lines containing "businessbroker"

**Axial** (`src/parsers/axial.py`):
- Subject lines with "deal alert", "deal opportunity", "new opportunity", or "investment opportunity"
- Emails from Axial domains (axial.net, etc.)

### Data Extraction
The parser extracts:
- **Business Name**: From subject line or email content
- **Price**: Asking price, enterprise value, or valuation
- **EBITDA**: TTM EBITDA, cash flow, or earnings
- **Location**: Business location/geography
- **Industry**: Business category/sector
- **Reason for Sale**: Seller motivation

### Filtering Criteria
All Axial deals are filtered using your existing criteria from `agent_config.yaml`:
- ✅ Price max: $5M
- ✅ Earnings multiple max: 5.0x
- ✅ Reason for sale: retirement/succession focused
- ✅ Excluded categories: restaurants, bars, cleaning, retail, salons/spas, gyms
- ✅ Geographic radius: 50 miles from NYC

## Usage

### Automatic Processing
The Axial parser is automatically included when you run the main email processing:

```bash
python3 src/main.py agent_config.yaml
```

### Manual Testing
Test the Axial parser specifically:

```bash
python3 test_axial_parser.py
```

## Email Setup

### Gmail Labels
Make sure your Gmail account has a label for Axial emails:
- Create a label like "biz-acq/axial" or "biz-acq/alerts"
- Set up Gmail filters to automatically label Axial emails

### Configuration
Update `agent_config.yaml` to include Axial in your email processing:

```yaml
sources:
  email_alerts:
    enabled: true
    imap_label: "biz-acq/alerts"  # Include Axial emails in this label
    lookback_days: 7
```

## Example Output

When an Axial deal passes your filters, it will appear in your results with:

```json
{
  "source_site": "axial",
  "source_url": "https://axial.net/deal/12345",
  "name": "Premium Manufacturing Co.",
  "address": "Albany, NY",
  "price": 3200000.0,
  "earnings_multiple": 3.76,
  "reason_for_sale": "Owner retirement after 25 years",
  "category": "Manufacturing"
}
```

## Supported Formats

The parser handles various Axial email formats:
- `Asking Price: $3.2M`
- `TTM EBITDA: $850K`
- `Enterprise Value: $5.5 Million`
- `Cash Flow: $1.2M`

Both HTML and plain text emails are supported.
