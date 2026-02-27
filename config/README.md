# Stock Market Analysis System - Configuration Guide

This directory contains configuration files for the Stock Market Analysis and Recommendation System.

## Configuration Files

### `default.yaml`
The default configuration file used when no other configuration is specified. This file contains safe defaults and is loaded automatically on system startup.

### `example.yaml`
An example configuration showing all available options with sample values. Copy this file to create your own configuration.

### `production.yaml` (create this)
Your production configuration with real credentials. This file should be created by copying `example.yaml` and filling in your actual values.

**IMPORTANT:** Never commit `production.yaml` to version control as it contains sensitive credentials!

## Configuration Structure

### Data Source

Configure whether to use real Yahoo Finance data or simulated data:

```yaml
data_source:
  # Set to true for testing, false for real Yahoo Finance data
  use_mock_data: false
```

### Stock Scanning

Configure how many stocks to scan per region:

```yaml
stock_scanning:
  # Maximum number of stocks to scan per region (0 = scan all)
  # This setting applies GLOBALLY to ALL regions
  # Examples:
  #   0 = scan all stocks (default)
  #   5 = scan 5 stocks per region
  #   10 = scan 10 stocks per region
  max_stocks_per_region: 0
```

See [STOCK_CONFIGURATION_GUIDE.md](STOCK_CONFIGURATION_GUIDE.md) for details on stock selection.

### Report Formatting

Configure how reports are formatted for delivery:

```yaml
report_formatting:
  # Number of top recommendations to show full rationale (0 = all)
  # Top recommendations are sorted by confidence score
  full_rationale_count: 3
  
  # Maximum length for truncated rationale (characters)
  truncated_rationale_length: 80
  
  # Maximum recommendations to send to Telegram (0 = all)
  # Full report is ALWAYS saved to disk regardless of this setting
  # Examples:
  #   0 = send all recommendations
  #   10 = send top 10 (5 BUY + 5 SELL)
  #   20 = send top 20 (10 BUY + 10 SELL)
  max_telegram_recommendations: 10
  
  # Focus industries for stock selection
  focus_industries:
    - AI              # Artificial Intelligence
    - semiconductors  # Chip manufacturing
    - power           # Energy and utilities
    - resources       # Natural resources
```

See [REPORT_FORMATTING_GUIDE.md](../REPORT_FORMATTING_GUIDE.md) for detailed formatting options.

### Stock Symbols

Configure which stocks to monitor per region:

```yaml
stock_symbols:
  usa:
    - NVDA      # NVIDIA - AI chips
    - AMD       # AMD - AI/GPU chips
    - MSFT      # Microsoft - AI software
    # ... more stocks
  
  hong_kong:
    - 0700.HK   # Tencent - AI/cloud
    - 9988.HK   # Alibaba - AI/cloud
    # ... more stocks
  
  china:
    - 688981.SS # iFlytek - AI voice
    - 688036.SS # Cambricon - AI chips
    # ... more stocks
```

**Default Configuration:** The system includes 32 stocks focused on AI and Resources:
- USA: 15 stocks (NVIDIA, AMD, Microsoft, Google, Meta, Tesla, Palantir, TSMC, Intel, Qualcomm, Broadcom, Micron, NextEra Energy, Duke Energy, Southern Company)
- Hong Kong: 8 stocks (Tencent, Alibaba, Xiaomi, Sunny Optical, CLP Holdings, HK Gas, China Petroleum, CNOOC)
- China: 9 stocks (iFlytek, Cambricon, Yonyou, Yangtze Power, Shenhua Energy, China Petroleum, NAURA, Maxscend, Unigroup Guoxin)

### Market Regions

Configure which stock markets to monitor:

```yaml
market_regions:
  - china        # Shanghai and Shenzhen exchanges
  - hong_kong    # Hong Kong Stock Exchange
  - usa          # NYSE and NASDAQ
```

**Default:** If not specified, the system monitors China, Hong Kong, and USA markets.

**Requirements:** At least one market region must be configured.

### Notification Channels

The system supports three notification channels: Telegram, Slack, and Email.

#### Telegram Configuration

```yaml
notifications:
  telegram:
    enabled: true
    bot_token: "YOUR_TELEGRAM_BOT_TOKEN"
    chat_ids:
      - "CHAT_ID_1"
      - "CHAT_ID_2"
```

**How to get credentials:**
1. Create a bot using [@BotFather](https://t.me/botfather) on Telegram
2. Copy the bot token provided by BotFather
3. Get your chat ID by messaging [@userinfobot](https://t.me/userinfobot)
4. For group chats, add the bot to the group and use the group's chat ID (starts with `-`)

#### Slack Configuration

```yaml
notifications:
  slack:
    enabled: true
    webhook_url: "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
    channel: "#stock-alerts"
```

**How to get credentials:**
1. Go to [Slack API](https://api.slack.com/apps)
2. Create a new app or select an existing one
3. Enable "Incoming Webhooks"
4. Create a new webhook for your desired channel
5. Copy the webhook URL

#### Email Configuration

```yaml
notifications:
  email:
    enabled: true
    smtp:
      host: "smtp.gmail.com"
      port: 587
      username: "your-email@gmail.com"
      password: "your-app-password"
      use_tls: true
    sender_address: "your-email@gmail.com"
    recipients:
      - "recipient1@example.com"
      - "recipient2@example.com"
```

**Gmail Setup:**
1. Enable 2-factor authentication on your Google account
2. Generate an [App Password](https://myaccount.google.com/apppasswords)
3. Use the app password (not your regular password) in the configuration

**Other SMTP Providers:**
- **Outlook/Office365:** `smtp.office365.com`, port 587
- **Yahoo:** `smtp.mail.yahoo.com`, port 587
- **Custom SMTP:** Use your provider's SMTP settings

### Analysis Schedule

Configure when the system runs analysis:

```yaml
schedule: "0 18 * * 1-5"
```

The schedule uses cron expression format:

```
┌───────────── minute (0 - 59)
│ ┌───────────── hour (0 - 23)
│ │ ┌───────────── day of month (1 - 31)
│ │ │ ┌───────────── month (1 - 12)
│ │ │ │ ┌───────────── day of week (0 - 6) (Sunday to Saturday)
│ │ │ │ │
│ │ │ │ │
* * * * *
```

**Common Examples:**
- `0 18 * * 1-5` - Weekdays at 6 PM
- `0 9,21 * * *` - Daily at 9 AM and 9 PM
- `30 16 * * 1-5` - Weekdays at 4:30 PM
- `0 0 * * *` - Daily at midnight

**Default:** `0 18 * * 1-5` (6 PM EST on weekdays, after US market close)

### Logging Configuration

```yaml
logging:
  level: INFO              # DEBUG, INFO, WARNING, ERROR, CRITICAL
  file: logs/stock_analysis.log
  max_size_mb: 100        # Maximum log file size before rotation
  backup_count: 5         # Number of backup log files to keep
```

## Using Configuration Files

### Method 1: Default Configuration

The system automatically loads `config/default.yaml` on startup:

```bash
python -m stock_market_analysis.main
```

### Method 2: Custom Configuration

Specify a custom configuration file:

```python
from stock_market_analysis.main import StockMarketAnalysisSystem
from pathlib import Path

system = StockMarketAnalysisSystem(config_path=Path("config/production.yaml"))
system.initialize()
system.start()
```

### Method 3: Programmatic Configuration

Configure the system programmatically:

```python
from stock_market_analysis.components import ConfigurationManager
from stock_market_analysis.models import MarketRegion, SMTPConfig

config_manager = ConfigurationManager()

# Add market regions
config_manager.add_market_region(MarketRegion.CHINA)
config_manager.add_market_region(MarketRegion.USA)

# Configure Telegram
config_manager.set_telegram_config(
    bot_token="YOUR_BOT_TOKEN",
    chat_ids=["YOUR_CHAT_ID"]
)

# Configure Email
smtp = SMTPConfig(
    host="smtp.gmail.com",
    port=587,
    username="your-email@gmail.com",
    password="your-app-password",
    use_tls=True
)
config_manager.set_email_config(smtp, ["recipient@example.com"])

# Save configuration
config_manager.persist_configuration()
```

## Configuration Validation

The system validates all configuration changes:

- **Market Regions:** At least one region must be configured
- **Telegram:** Bot token must be at least 10 characters, chat IDs must be valid
- **Slack:** Webhook URL must be a valid Slack webhook
- **Email:** Email addresses must be valid, SMTP port must be 1-65535
- **Schedule:** Cron expression must be valid

Invalid configurations will be rejected with descriptive error messages.

## Configuration Persistence

Configuration changes are automatically persisted to disk and survive system restarts. The system applies configuration changes within 60 seconds.

## Security Best Practices

1. **Never commit credentials** to version control
2. **Use environment variables** for sensitive values in production
3. **Restrict file permissions** on configuration files containing credentials
4. **Use app-specific passwords** instead of main account passwords
5. **Rotate credentials regularly**
6. **Use separate credentials** for development and production

## Troubleshooting

### Configuration Not Loading

- Check file path is correct
- Verify YAML syntax is valid (use a YAML validator)
- Check file permissions (must be readable)
- Review logs for error messages

### Notification Delivery Failures

- Verify credentials are correct
- Check network connectivity
- Ensure notification channel is enabled (`enabled: true`)
- Review logs for specific error messages

### Schedule Not Working

- Verify cron expression is valid
- Check system timezone matches expected schedule
- Ensure system is running during scheduled times

## Support

For issues or questions:
1. Check the logs in `logs/stock_analysis.log`
2. Review the [main README](../README.md)
3. Verify configuration against this guide
