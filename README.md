# Stock Market Analysis and Recommendation System

A comprehensive stock market analysis system with intraday monitoring, automated trading simulation, and multi-channel notifications. Monitors China, Hong Kong, and USA markets using real Yahoo Finance data.

## Quick Start

```bash
# Start the complete system (analysis + web dashboard)
python start_system.py

# Or use the batch file
start.bat

# Access the dashboard
http://localhost:5000
```

For detailed setup instructions, see **[docs/STARTUP_GUIDE.md](docs/STARTUP_GUIDE.md)**

## Key Features

- **Intraday Market Monitoring**: Hourly analysis during market hours with automatic trading
- **Trading Simulation**: Virtual portfolio with performance tracking and backtesting
- **Web Dashboard**: Real-time portfolio, trades, and recommendations at http://localhost:5000
- **Multi-Market Support**: China, Hong Kong, and USA markets with timezone-aware scheduling
- **Comprehensive Analysis**: Technical, fundamental, volume, sentiment, and pattern recognition
- **Intelligent Recommendations**: Buy/sell/hold with confidence scores and detailed rationale
- **Multi-Channel Notifications**: Telegram, Slack, and Email delivery
- **Automated Scheduling**: Daily analysis and intraday monitoring during market hours

## Documentation

All documentation has been moved to the **[docs/](docs/)** folder:

- **[Startup Guide](docs/STARTUP_GUIDE.md)** - How to run the system
- **[Algorithm Guide](docs/ALGORITHM_README.md)** - Analysis algorithm details
- **[Comprehensive Guide](docs/COMPREHENSIVE_ANALYSIS_GUIDE.md)** - Complete feature documentation
- **[Web Dashboard](docs/WEB_DASHBOARD_README.md)** - Dashboard usage
- **[Trading Guide](docs/TRADING_TRIGGER_GUIDE.md)** - Manual trading
- **[Report Formatting](docs/REPORT_FORMATTING_GUIDE.md)** - Report configuration

## Architecture

The system follows a pipeline architecture with core components:

1. **Market_Monitor**: Collects stock market data from configured regions
2. **Analysis_Engine**: Performs stock analysis and generates recommendations
3. **Report_Generator**: Compiles daily reports with all recommendations
4. **Notification_Service**: Delivers reports through multiple channels
5. **Configuration_Manager**: Manages system settings and credentials

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy the example configuration:
   ```bash
   cp config/example.yaml config/production.yaml
   ```
4. Edit `config/production.yaml` with your credentials and preferences

## Configuration

The system uses YAML configuration files in the `config/` directory:

- `default.yaml`: Default settings and structure
- `example.yaml`: Example configuration with sample values
- `production.yaml`: Your actual configuration (create from example)

See [config/README.md](config/README.md) for detailed configuration documentation.

### Key Configuration Options

#### Stock Scanning
```yaml
stock_scanning:
  # Maximum number of stocks to scan per region (0 = scan all)
  max_stocks_per_region: 0
```

#### Report Formatting
```yaml
report_formatting:
  # Number of top recommendations to show full rationale (0 = all)
  full_rationale_count: 3
  
  # Maximum length for truncated rationale (characters)
  truncated_rationale_length: 80
  
  # Maximum recommendations to send to Telegram (0 = all)
  # Full report always saved to disk regardless of this setting
  max_telegram_recommendations: 10
```

#### Stock Symbols
Configure which stocks to monitor per region with focus on specific industries:
```yaml
stock_symbols:
  usa:
    - NVDA      # NVIDIA - AI chips
    - MSFT      # Microsoft - AI software
    - GOOGL     # Alphabet - AI research
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

See [config/STOCK_CONFIGURATION_GUIDE.md](config/STOCK_CONFIGURATION_GUIDE.md) for stock configuration details.
See [REPORT_FORMATTING_GUIDE.md](REPORT_FORMATTING_GUIDE.md) for report formatting details.

### Quick Setup

Use the interactive configuration helper:
```bash
python config/setup_config.py create
```

Or validate an existing configuration:
```bash
python config/setup_config.py validate config/production.yaml
```

### Market Regions

Configure which markets to monitor:
```yaml
market_regions:
  - china
  - hong_kong
  - usa
```

### Notification Channels

Configure delivery channels:
```yaml
notifications:
  telegram:
    enabled: true
    bot_token: "YOUR_BOT_TOKEN"
    chat_ids: ["CHAT_ID"]
  
  slack:
    enabled: true
    webhook_url: "YOUR_WEBHOOK_URL"
    channel: "#stock-alerts"
  
  email:
    enabled: true
    smtp:
      host: "smtp.gmail.com"
      port: 587
      username: "your-email@gmail.com"
      password: "your-app-password"
      use_tls: true
    recipients: ["recipient@example.com"]
```

## Usage

Run the system:
```bash
python -m stock_market_analysis.main
```

The system will:
1. Load configuration from `config/default.yaml`
2. Fetch real market data from Yahoo Finance for configured stocks
3. Perform comprehensive analysis (technical, fundamental, volume, sentiment, pattern)
4. Generate recommendations with confidence scores and risk assessments
5. Create daily report in multiple formats (JSON, HTML, TXT)
6. Deliver report through configured channels (Telegram, Slack, Email)
7. Save full report to `reports/YYYY-MM-DD/` directory

### Report Output

Reports are saved in three formats:
- **JSON**: Machine-readable format with all data
- **HTML**: Formatted email-ready report
- **TXT**: Plain text Telegram-ready report

Location: `reports/YYYY-MM-DD/REPORT-YYYYMMDD-{id}.{json,html,txt}`

### Telegram Message Format

With default settings (`max_telegram_recommendations: 10`):
- Shows top 5 BUY and top 5 SELL recommendations
- Top 3 of each type show full rationale + Yahoo Finance URL
- Remaining 2 of each type show truncated rationale (80 chars)
- HOLD recommendations excluded from Telegram (available in disk report)
- Message includes note: "Full report with all X recommendations saved to disk"

Example:
```
📊 Market Report 02/27

📋 Showing top 5 BUY and top 5 SELL recommendations
   (Full report with all 30 recommendations saved to disk)

🟢 BUY (5):
• Tencent Holdings Limited
  0700.HK | $570.900 | 93%
  📊 RSI at 33.9 shows potential upside; moderate upward trend...
  ⚠️ Low risk: stable price action, limited downside risk
  https://finance.yahoo.com/quote/0700.HK
...
```

## Testing

Run all tests:
```bash
pytest
```

Run specific test types:
```bash
# Unit tests only
pytest tests/unit/

# Property-based tests only
pytest tests/property/

# Integration tests only
pytest tests/integration/
```

Run tests with coverage:
```bash
pytest --cov=stock_market_analysis --cov-report=html
```

## Development

The project uses:
- **pytest** for unit and integration testing
- **Hypothesis** for property-based testing
- **black** for code formatting
- **flake8** for linting
- **mypy** for type checking

Run development tools:
```bash
# Format code
black stock_market_analysis/ tests/

# Lint code
flake8 stock_market_analysis/ tests/

# Type check
mypy stock_market_analysis/
```

## Project Structure

```
stock_market_analysis/
├── stock_market_analysis/          # Main package
│   ├── models/                     # Data models
│   ├── components/                 # Core components
│   │   ├── market_monitor.py      # Market data collection
│   │   ├── yahoo_finance_api.py   # Yahoo Finance integration
│   │   ├── analysis_engine.py     # Stock analysis
│   │   ├── technical_indicators.py # RSI, MACD calculations
│   │   ├── fundamental_analysis.py # P/E, earnings, revenue
│   │   ├── volume_analysis.py     # Volume patterns
│   │   ├── sentiment_analysis.py  # Market sentiment
│   │   ├── pattern_recognition.py # Chart patterns
│   │   ├── report_generator.py    # Report creation
│   │   ├── notification_service.py # Multi-channel delivery
│   │   └── configuration_manager.py # Config management
│   └── main.py                     # Application entry point
├── tests/                          # Test suite
│   ├── unit/                       # Unit tests (153 tests)
│   ├── property/                   # Property-based tests
│   └── integration/                # Integration tests
├── config/                         # Configuration files
│   ├── default.yaml                # Default configuration
│   ├── example.yaml                # Example configuration
│   ├── README.md                   # Config documentation
│   └── STOCK_CONFIGURATION_GUIDE.md # Stock selection guide
├── reports/                        # Generated reports (YYYY-MM-DD/)
├── logs/                           # Log files
├── REPORT_FORMATTING_GUIDE.md      # Report formatting documentation
├── COMPREHENSIVE_ANALYSIS_GUIDE.md # Analysis methodology
├── ALGORITHM_README.md             # Algorithm details
└── requirements.txt                # Dependencies
```

## Documentation

- [Configuration Guide](config/README.md) - System configuration
- [Stock Configuration Guide](config/STOCK_CONFIGURATION_GUIDE.md) - Stock selection and scanning
- [Report Formatting Guide](REPORT_FORMATTING_GUIDE.md) - Report formatting options
- [Comprehensive Analysis Guide](COMPREHENSIVE_ANALYSIS_GUIDE.md) - Analysis methodology
- [Algorithm Documentation](ALGORITHM_README.md) - Technical details

## License

This project is licensed under the MIT License.