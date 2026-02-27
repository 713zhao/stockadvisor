# Stock Configuration Guide

This guide explains how to configure the stock symbols and scanning behavior for the Stock Market Analysis system.

## Configuration File

The main configuration file is located at `config/default.yaml`.

## Stock Scanning Configuration

### Maximum Stocks Per Region

Control how many stocks to scan per region:

```yaml
stock_scanning:
  max_stocks_per_region: 0  # 0 = scan all stocks, >0 = limit to that number
```

**Examples:**
- `max_stocks_per_region: 0` - Scan ALL stocks in the list (default)
- `max_stocks_per_region: 10` - Scan only the first 10 stocks per region
- `max_stocks_per_region: 5` - Scan only the first 5 stocks per region

### Focus Industries

Define which industries to focus on:

```yaml
stock_scanning:
  focus_industries:
    - AI              # Artificial Intelligence
    - semiconductors  # Chip manufacturing
    - power           # Energy and utilities
    - resources       # Natural resources
```

## Stock Symbol Lists

### Current Configuration (AI & Resources Focus)

The system is currently configured to focus on:
1. **AI Companies** - NVIDIA, AMD, Microsoft, Google, Meta, Tesla, Palantir
2. **Semiconductors** - TSMC, Intel, Qualcomm, Broadcom, Micron
3. **Power & Energy** - NextEra Energy, Duke Energy, Southern Company
4. **Resources** - Oil, gas, and renewable energy companies

### USA Market (15 stocks)

```yaml
stock_symbols:
  usa:
    # AI Leaders
    - NVDA      # NVIDIA - AI chips
    - AMD       # AMD - AI/GPU chips
    - MSFT      # Microsoft - AI software
    - GOOGL     # Alphabet - AI research
    - META      # Meta - AI applications
    - TSLA      # Tesla - AI/autonomous driving
    - PLTR      # Palantir - AI analytics
    # Power & Resources
    - NEE       # NextEra Energy - renewable power
    - DUK       # Duke Energy - power utility
    - SO        # Southern Company - power utility
    # Semiconductors
    - TSM       # TSMC - chip manufacturing
    - INTC      # Intel - semiconductors
    - QCOM      # Qualcomm - mobile chips
    - AVGO      # Broadcom - semiconductors
    - MU        # Micron - memory chips
```

### Hong Kong Market (8 stocks)

```yaml
stock_symbols:
  hong_kong:
    # AI & Tech
    - 0700.HK   # Tencent - AI/cloud
    - 9988.HK   # Alibaba - AI/cloud
    - 1810.HK   # Xiaomi - AI devices
    - 2382.HK   # Sunny Optical - AI cameras
    # Resources & Power
    - 0002.HK   # CLP Holdings - power utility
    - 0003.HK   # Hong Kong & China Gas - energy
    - 0386.HK   # China Petroleum - oil/gas
    - 0883.HK   # CNOOC - offshore oil
```

### China Market (9 stocks)

```yaml
stock_symbols:
  china:
    # AI & Tech (Shanghai)
    - 688981.SS # iFlytek - AI voice
    - 688036.SS # Cambricon - AI chips
    - 600588.SS # Yonyou Network - AI software
    # Resources & Power (Shanghai)
    - 600900.SS # China Yangtze Power - hydropower
    - 601088.SS # China Shenhua Energy - coal/power
    - 600028.SS # China Petroleum - oil/gas
    # Semiconductors (Shenzhen)
    - 002371.SZ # NAURA - semiconductor equipment
    - 300782.SZ # Maxscend - RF chips
    - 002049.SZ # Unigroup Guoxin - semiconductors
```

## Total Stocks

With `max_stocks_per_region: 0`, the system will scan:
- **USA**: 15 stocks
- **Hong Kong**: 8 stocks
- **China**: 9 stocks
- **Total**: 32 stocks

## How to Customize

### 1. Limit Number of Stocks

To scan only the top 5 stocks per region:

```yaml
stock_scanning:
  max_stocks_per_region: 5
```

This will scan:
- USA: First 5 stocks (NVDA, AMD, MSFT, GOOGL, META)
- Hong Kong: First 5 stocks (0700.HK, 9988.HK, 1810.HK, 2382.HK, 0002.HK)
- China: First 5 stocks (688981.SS, 688036.SS, 600588.SS, 600900.SS, 601088.SS)

### 2. Add More Stocks

Simply add more symbols to the list:

```yaml
stock_symbols:
  usa:
    - NVDA
    - AMD
    - AAPL      # Add Apple
    - NFLX      # Add Netflix
    # ... more stocks
```

### 3. Change Focus Industries

To focus on different industries, replace the stock lists:

**Example: Finance Focus**
```yaml
stock_symbols:
  usa:
    - JPM       # JPMorgan Chase
    - BAC       # Bank of America
    - WFC       # Wells Fargo
    - GS        # Goldman Sachs
    - MS        # Morgan Stanley
```

**Example: Healthcare Focus**
```yaml
stock_symbols:
  usa:
    - JNJ       # Johnson & Johnson
    - UNH       # UnitedHealth
    - PFE       # Pfizer
    - ABBV      # AbbVie
    - TMO       # Thermo Fisher
```

### 4. Disable a Region

To skip a region, remove it from `market_regions`:

```yaml
market_regions:
  - usa         # Only scan USA
  # - hong_kong  # Commented out
  # - china      # Commented out
```

## Stock Symbol Formats

- **USA**: Simple ticker (e.g., `AAPL`, `MSFT`)
- **Hong Kong**: 4-digit code + `.HK` (e.g., `0700.HK`, `9988.HK`)
- **China Shanghai**: 6-digit code + `.SS` (e.g., `600000.SS`, `601398.SS`)
- **China Shenzhen**: 6-digit code + `.SZ` (e.g., `000001.SZ`, `002371.SZ`)

## Performance Considerations

- Each stock requires 1-2 seconds to fetch data from Yahoo Finance
- Scanning 32 stocks takes approximately 30-60 seconds
- Consider using `max_stocks_per_region` to limit scan time during testing
- For production, set `max_stocks_per_region: 0` to scan all stocks

## Example Configurations

### Quick Test (5 stocks total)
```yaml
stock_scanning:
  max_stocks_per_region: 2
market_regions:
  - usa
```

### Balanced (15 stocks total)
```yaml
stock_scanning:
  max_stocks_per_region: 5
market_regions:
  - usa
  - hong_kong
  - china
```

### Comprehensive (32 stocks total)
```yaml
stock_scanning:
  max_stocks_per_region: 0  # Scan all
market_regions:
  - usa
  - hong_kong
  - china
```

## Troubleshooting

### Stock Not Found
If a stock symbol is invalid, the system will log a warning and skip it:
```
WARNING - No data available for INVALID
```

### Slow Performance
If scanning is too slow:
1. Reduce `max_stocks_per_region`
2. Remove regions you don't need
3. Remove stocks from the lists

### Missing Data
Some stocks may have incomplete fundamental data. The system will use available data and note missing metrics in the analysis.
