# Report Formatting Configuration Guide

This guide explains how to configure the report formatting to control the level of detail and number of recommendations shown in Telegram messages.

## Configuration

Edit `config/default.yaml`:

```yaml
report_formatting:
  # Number of top recommendations to show full rationale for (0 = show full rationale for all)
  full_rationale_count: 3
  
  # Maximum length for truncated rationale (characters)
  truncated_rationale_length: 80
  
  # Maximum number of recommendations to send to Telegram (0 = send all)
  # Full report is ALWAYS saved to disk regardless of this setting
  max_telegram_recommendations: 10
```

## Key Features

### 1. Limit Total Recommendations (`max_telegram_recommendations`)

Controls how many recommendations are sent to Telegram:
- `0` = Send ALL recommendations (default for small lists)
- `10` = Send only top 10 (5 BUY + 5 SELL)
- `20` = Send only top 20 (10 BUY + 10 SELL)

**Important:** The full report with ALL recommendations is ALWAYS saved to disk in `reports/YYYY-MM-DD/`. This setting only affects the Telegram message.

### 2. Full vs Truncated Rationale (`full_rationale_count`)

Controls how many of the sent recommendations show full analysis:
- `0` = Show full rationale for all sent recommendations
- `3` = Show full rationale for top 3 BUY and top 3 SELL
- `5` = Show full rationale for top 5 BUY and top 5 SELL

### 3. Truncation Length (`truncated_rationale_length`)

Controls how much text to show for truncated recommendations:
- `60` = Very brief
- `80` = Balanced (recommended)
- `100` = More context

## How It Works

### Full Rationale (Top N Recommendations)

The top N BUY and top N SELL recommendations (sorted by confidence score) will show:
- ✅ Full comprehensive rationale with all analysis details
- ✅ Complete risk assessment
- ✅ Yahoo Finance URL link
- ✅ All technical, fundamental, volume, sentiment, and pattern analysis

**Example (Top 3 BUY):**
```
🟢 BUY (11):
• Tencent Holdings Limited
  0700.HK | $566.500 | 87%
  📊 RSI at 31.6 shows potential upside; P/E ratio at 20.4; earnings growth of 20.1%; 
      revenue growth of 15.4%; low volume suggests weak conviction; volume declining; 
      price bouncing off support; trading range $512.00-$548.00; low volatility indicates stability.
  ⚠️ Low risk: stable price action, limited downside risk in current conditions.
  https://finance.yahoo.com/quote/0700.HK
```

### Truncated Rationale (Remaining Recommendations)

Recommendations beyond the top N will show:
- ✅ Stock name, symbol, price, confidence
- ✅ Truncated rationale (first 80 characters + "...")
- ✅ Risk assessment
- ❌ No URL link (to save space)

**Example (Beyond Top 3):**
```
• NextEra Energy, Inc.
  NEE | $101.1890 | 70%
  📊 RSI at 59.1 suggests caution; moderate downward trend with 2.78% change; P/E...
  ⚠️ Low risk: stable price action, limited downside risk in current conditions.
```

### HOLD Recommendations

HOLD recommendations are ALWAYS truncated (regardless of `full_rationale_count` setting) since they are lower priority.

## Configuration Examples

### Minimal Telegram Message (Top 10 Only) - RECOMMENDED

```yaml
report_formatting:
  full_rationale_count: 3
  truncated_rationale_length: 80
  max_telegram_recommendations: 10  # Only top 5 BUY + 5 SELL
```

**Result:**
- Telegram: Top 10 stocks only (5 BUY + 5 SELL)
- Disk: Full report with all 30+ stocks
- Message size: 1 Telegram message (very fast to read)

**Use when:**
- You scan 20+ stocks
- You want quick, actionable insights on mobile
- You only care about the best opportunities

### Moderate Telegram Message (Top 20)

```yaml
report_formatting:
  full_rationale_count: 5
  truncated_rationale_length: 80
  max_telegram_recommendations: 20  # Top 10 BUY + 10 SELL
```

**Result:**
- Telegram: Top 20 stocks (10 BUY + 10 SELL)
- Disk: Full report with all stocks
- Message size: 1-2 Telegram messages

**Use when:**
- You scan 30-50 stocks
- You want more options to choose from
- You have time to review more recommendations

### Send Everything to Telegram

```yaml
report_formatting:
  full_rationale_count: 3
  truncated_rationale_length: 80
  max_telegram_recommendations: 0  # Send all recommendations
```

**Result:**
- Telegram: ALL recommendations
- Disk: Full report (same as Telegram)
- Message size: 2-4 Telegram messages

**Use when:**
- You scan < 20 stocks
- You want to see everything on mobile
- Message length is not a concern

## Truncation Length

The `truncated_rationale_length` controls how much of the rationale to show for non-top recommendations:

- **60 characters**: Very brief, just the first key point
- **80 characters**: Balanced (recommended)
- **100 characters**: More context
- **120 characters**: Almost full, but still saves space

## Benefits

### Shorter Telegram Messages
- Reduces message splitting (Telegram has 4096 character limit)
- Faster to read on mobile
- Focuses attention on best opportunities

### Better Signal-to-Noise Ratio
- Top recommendations get full attention
- Lower confidence recommendations don't clutter the report
- Easier to make quick decisions

### Flexible Detail Level
- Adjust based on your portfolio size
- Change based on market conditions
- Customize for different notification channels

## Report File Storage

Note: The full reports saved to disk (`reports/YYYY-MM-DD/REPORT-*.txt`) always contain FULL rationale for all recommendations, regardless of this setting. This configuration only affects the Telegram/Slack/Email delivery format.

## Current Configuration

With the current settings (`full_rationale_count: 3`):
- **32 stocks scanned** → ~30 recommendations
- **Top 3 BUY**: Full details with URLs
- **Top 3 SELL**: Full details with URLs
- **Remaining BUY/SELL**: Truncated to 80 characters
- **All HOLD**: Truncated to 80 characters

This keeps Telegram messages concise while highlighting the most important opportunities.

## Testing Different Settings

To test different configurations:

1. Edit `config/default.yaml`
2. Change `full_rationale_count` value
3. Run: `python -m stock_market_analysis.main`
4. Check your Telegram for the formatted report

## Recommendations by Stock Count

| Stocks Scanned | Recommended `max_telegram_recommendations` | Recommended `full_rationale_count` | Rationale |
|----------------|-------------------------------------------|-----------------------------------|-----------|
| 1-15 | `0` (send all) | `0` (full for all) | Show everything |
| 16-30 | `10` (top 10) | `3` (top 3) | Focus on best |
| 31-50 | `10` (top 10) | `3` (top 3) | Keep concise |
| 51-100 | `10` (top 10) | `3` (top 3) | Only the best |
| 100+ | `6` (top 6) | `2` (top 2) | Ultra-focused |

## Current Configuration (Recommended)

With 32 stocks scanned and current settings:

```yaml
max_telegram_recommendations: 10  # Top 5 BUY + 5 SELL
full_rationale_count: 3           # Full details for top 3 of each
truncated_rationale_length: 80    # 80 chars for others
```

**Result:**
- **Telegram**: 10 stocks (5 BUY + 5 SELL)
  - Top 3 BUY: Full rationale + URL
  - Remaining 2 BUY: Truncated rationale
  - Top 3 SELL: Full rationale + URL
  - Remaining 2 SELL: Truncated rationale
- **Disk**: Full report with all 30 stocks
- **Message size**: 1 Telegram message (~2000 characters)

## Where to Find Full Reports

All reports are saved to disk with complete details:
- **Location**: `reports/YYYY-MM-DD/REPORT-*.txt`
- **Format**: Plain text, JSON, and HTML
- **Content**: ALL recommendations with full rationale
- **Always saved**: Regardless of Telegram settings

## Benefits of Limiting Telegram Recommendations

### Faster to Read
- Single message instead of 2-4
- Loads instantly on mobile
- Quick decision making

### Better Focus
- Only see the best opportunities
- Less information overload
- Higher signal-to-noise ratio

### Reduced Notification Fatigue
- Shorter messages are less overwhelming
- More likely to be read immediately
- Better for daily notifications

### Full Data Still Available
- Complete analysis saved to disk
- Can review full report anytime
- Nothing is lost
