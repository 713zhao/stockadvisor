# Stock Scanning Configuration Summary

## Current Configuration

The Stock Market Analysis system is now configured to focus on **AI and Resources** industries with **configurable scanning limits**.

### Scanning Statistics

With `max_stocks_per_region: 0` (scan all):
- **China**: 9 stocks (AI, semiconductors, power)
- **Hong Kong**: 8 stocks (AI/tech, resources)
- **USA**: 15 stocks (AI leaders, semiconductors, power)
- **Total**: 32 stocks scanned
- **Scan Time**: ~7 seconds (with real Yahoo Finance data)

### Stock Distribution by Industry

#### AI & Technology (16 stocks)
**USA:**
- NVDA (NVIDIA) - AI chips
- AMD - AI/GPU chips
- MSFT (Microsoft) - AI software
- GOOGL (Alphabet) - AI research
- META - AI applications
- TSLA (Tesla) - AI/autonomous driving
- PLTR (Palantir) - AI analytics

**Hong Kong:**
- 0700.HK (Tencent) - AI/cloud
- 9988.HK (Alibaba) - AI/cloud
- 1810.HK (Xiaomi) - AI devices
- 2382.HK (Sunny Optical) - AI cameras

**China:**
- 688981.SS (iFlytek) - AI voice
- 688036.SS (Cambricon) - AI chips
- 600588.SS (Yonyou Network) - AI software

#### Semiconductors (8 stocks)
**USA:**
- TSM (TSMC) - chip manufacturing
- INTC (Intel) - semiconductors
- QCOM (Qualcomm) - mobile chips
- AVGO (Broadcom) - semiconductors
- MU (Micron) - memory chips

**China:**
- 002371.SZ (NAURA) - semiconductor equipment
- 300782.SZ (Maxscend) - RF chips
- 002049.SZ (Unigroup Guoxin) - semiconductors

#### Power & Resources (8 stocks)
**USA:**
- NEE (NextEra Energy) - renewable power
- DUK (Duke Energy) - power utility
- SO (Southern Company) - power utility

**Hong Kong:**
- 0002.HK (CLP Holdings) - power utility
- 0003.HK (Hong Kong & China Gas) - energy
- 0386.HK (China Petroleum) - oil/gas
- 0883.HK (CNOOC) - offshore oil

**China:**
- 600900.SS (China Yangtze Power) - hydropower
- 601088.SS (China Shenhua Energy) - coal/power
- 600028.SS (China Petroleum) - oil/gas

## Configuration Options

### 1. Scan All Stocks (Current Setting)
```yaml
stock_scanning:
  max_stocks_per_region: 0  # Scan all 32 stocks
```
- **Pros**: Comprehensive analysis, no stocks missed
- **Cons**: Longer scan time (~7 seconds)
- **Best for**: Daily scheduled reports

### 2. Limit to Top Stocks
```yaml
stock_scanning:
  max_stocks_per_region: 5  # Scan top 5 per region (15 total)
```
- **Pros**: Faster scanning (~3 seconds)
- **Cons**: May miss opportunities in lower-priority stocks
- **Best for**: Quick testing, frequent updates

### 3. Focus on Single Region
```yaml
stock_scanning:
  max_stocks_per_region: 0
market_regions:
  - usa  # Only scan USA (15 stocks)
```
- **Pros**: Very fast, focused analysis
- **Cons**: Limited geographic diversification
- **Best for**: US-focused portfolios

## How to Customize

### Change Number of Stocks
Edit `config/default.yaml`:
```yaml
stock_scanning:
  max_stocks_per_region: 10  # Scan 10 stocks per region
```

### Add More Stocks
Add symbols to the lists in `config/default.yaml`:
```yaml
stock_symbols:
  usa:
    - NVDA
    - AMD
    - ORCL      # Add Oracle
    - CRM       # Add Salesforce
```

### Change Focus Industries
Replace the stock lists with different industries:
- **Finance**: JPM, BAC, WFC, GS, MS
- **Healthcare**: JNJ, UNH, PFE, ABBV, TMO
- **Consumer**: AMZN, WMT, HD, NKE, SBUX
- **Energy**: XOM, CVX, COP, SLB, EOG

## Performance Metrics

| Configuration | Stocks | Scan Time | Recommendations |
|--------------|--------|-----------|-----------------|
| All regions, no limit | 32 | ~7 sec | 30 |
| All regions, limit 5 | 15 | ~3 sec | 15 |
| USA only, no limit | 15 | ~3 sec | 15 |
| USA only, limit 5 | 5 | ~1 sec | 5 |

## Latest Report Summary

From the most recent scan (32 stocks):
- **BUY**: 9 recommendations
- **SELL**: 7 recommendations
- **HOLD**: 14 recommendations

**Top BUY Recommendations:**
1. Tencent (0700.HK) - 87% confidence
2. Alphabet (GOOGL) - 80% confidence
3. Xiaomi (1810.HK) - 77% confidence

**Top SELL Recommendations:**
1. Tesla (TSLA) - 81% confidence (overvalued P/E)
2. Southern Company (SO) - 77% confidence (overbought)
3. Duke Energy (DUK) - 75% confidence (overbought)

## Documentation

For detailed configuration instructions, see:
- `config/STOCK_CONFIGURATION_GUIDE.md` - Complete configuration guide
- `config/default.yaml` - Main configuration file
- `COMPREHENSIVE_ANALYSIS_GUIDE.md` - Analysis methodology

## Quick Start

1. **Test with limited stocks** (fast):
   ```yaml
   max_stocks_per_region: 3
   ```

2. **Run the system**:
   ```bash
   python -m stock_market_analysis.main
   ```

3. **Check the report**:
   - Telegram: Delivered automatically
   - Files: `reports/YYYY-MM-DD/REPORT-*.txt`

4. **Adjust to full scan**:
   ```yaml
   max_stocks_per_region: 0
   ```
