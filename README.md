# Stock Market Analysis and Recommendation System

A scheduled service that monitors multiple stock markets, performs analysis, and delivers actionable investment recommendations through multiple communication channels including Telegram, Slack, and Email.

## Features

- **Multi-Market Monitoring**: Supports China, Hong Kong, and USA markets by default
- **Intelligent Analysis**: Generates buy/sell/hold recommendations with rationale and risk assessment
- **Multi-Channel Delivery**: Delivers reports via Telegram, Slack, and Email
- **Configurable Scheduling**: Automated daily analysis with customizable timing
- **Graceful Error Handling**: Continues operation even when individual components fail
- **Comprehensive Logging**: Full audit trail of all operations

## Architecture

The system follows a pipeline architecture with five core components:

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
│   └── main.py                     # Application entry point
├── tests/                          # Test suite
│   ├── unit/                       # Unit tests
│   ├── property/                   # Property-based tests
│   └── integration/                # Integration tests
├── config/                         # Configuration files
├── logs/                           # Log files
└── requirements.txt                # Dependencies
```

## License

This project is licensed under the MIT License.