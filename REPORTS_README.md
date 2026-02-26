# Stock Market Analysis Reports

## Report Storage Location

All generated reports are automatically saved to the `reports/` directory, organized by date.

### Directory Structure

```
reports/
└── YYYY-MM-DD/
    ├── REPORT-YYYYMMDD-xxxxxxxx.json    # Full report data
    ├── REPORT-YYYYMMDD-xxxxxxxx.html    # HTML formatted report
    └── REPORT-YYYYMMDD-xxxxxxxx.txt     # Plain text report
```

### Report Formats

Each report is saved in three formats:

1. **JSON** (`.json`) - Complete structured data including:
   - Stock symbol and full company name
   - Recommendation type (BUY/SELL/HOLD)
   - Rationale and risk assessment
   - Confidence score and target price
   - Direct link to view stock on Yahoo Finance
   - Market summaries for each region

2. **HTML** (`.html`) - Formatted report suitable for:
   - Email delivery
   - Web viewing
   - Archival purposes

3. **Plain Text** (`.txt`) - Compact format used for:
   - Telegram delivery
   - Quick reference
   - Terminal viewing

## Stock Information

Each recommendation includes:

- **Symbol**: Stock ticker symbol (e.g., AAPL, 0700.HK, 600000.SS)
- **Name**: Full company name (e.g., Apple Inc., Tencent Holdings Limited)
- **Region**: Market region (USA, Hong Kong, China)
- **Type**: BUY, SELL, or HOLD recommendation
- **Target Price**: Projected price target
- **Confidence**: Confidence score (0-100%)
- **Rationale**: Explanation of why the recommendation was made
- **Risk Assessment**: Risk level and factors
- **URL**: Direct link to view stock details on Yahoo Finance

## Stock Links

The system generates proper Yahoo Finance links for each stock:

- **USA stocks**: `https://finance.yahoo.com/quote/AAPL`
- **Hong Kong stocks**: `https://finance.yahoo.com/quote/0700.HK`
- **China stocks**: `https://finance.yahoo.com/quote/600000.SS`

## Example Report Entry

```json
{
  "symbol": "AAPL",
  "name": "Apple Inc.",
  "region": "usa",
  "type": "buy",
  "rationale": "Strong upward momentum with 3.26% price movement...",
  "risk_assessment": "Medium risk: moderate price volatility...",
  "confidence_score": 0.7,
  "target_price": "457.80",
  "url": "https://finance.yahoo.com/quote/AAPL"
}
```

## Accessing Reports

### Via File System
Navigate to `reports/YYYY-MM-DD/` to find today's reports.

### Via Telegram
Reports are automatically delivered to your configured Telegram chat with:
- Stock names and symbols
- Recommendations grouped by type (BUY/SELL/HOLD)
- Direct links to view each stock
- Rationale summaries

### Via Email (when configured)
HTML-formatted reports with complete details including:
- Full rationale and risk assessment
- Clickable stock links
- Professional formatting

## Report Retention

Reports are stored indefinitely in the `reports/` directory. You can:
- Archive old reports manually
- Set up automated cleanup scripts
- Use the JSON format for data analysis and backtesting

## Note on Stock Data

Currently using mock data for development. To connect to real market data:
1. Replace `MockMarketDataAPI` with a real API implementation
2. Configure API credentials in `config/default.yaml`
3. Supported APIs: Yahoo Finance, Alpha Vantage, IEX Cloud, etc.
