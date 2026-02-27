# Intraday Market Monitoring

Hourly market monitoring and automated trading during market hours across multiple regional markets.

## Overview

The intraday monitoring system enables real-time market analysis and automated trading throughout the trading day. It monitors stocks across China, Hong Kong, and USA markets, respecting each market's trading hours, holidays, and timezones.

## Features

- **Hourly Analysis**: Configurable monitoring intervals (15-240 minutes)
- **Multi-Region Support**: Concurrent monitoring of China, Hong Kong, and USA markets
- **Market Hours Awareness**: Only operates during market trading hours
- **Holiday Detection**: Respects market holidays for each region
- **Timezone Handling**: Accurate timezone conversions with DST support
- **Automatic Trading**: Executes trades based on analysis results
- **Error Recovery**: Circuit breaker pattern with automatic pause/resume
- **Independent Operation**: Runs alongside daily analysis without interference

## Architecture

### Components

1. **IntradayMonitor**: Main coordinator for hourly monitoring
2. **MarketHoursDetector**: Determines if markets are open
3. **TimezoneConverter**: Handles timezone conversions with DST
4. **AnalysisEngine**: Performs stock analysis (shared with daily system)
5. **TradeExecutor**: Executes trades (shared with daily system)

### Market Hours

| Region | Market | Trading Hours (Local) | Timezone | UTC Offset |
|--------|--------|----------------------|----------|------------|
| China | SSE/SZSE | 09:30 - 15:00 | CST | UTC+8 (no DST) |
| Hong Kong | HKEX | 09:30 - 16:00 | HKT | UTC+8 (no DST) |
| USA | NYSE/NASDAQ | 09:30 - 16:00 | ET | UTC-5 (winter) / UTC-4 (summer) |

## Configuration

Edit `config/default.yaml`:

```yaml
intraday_monitoring:
  # Enable/disable intraday monitoring
  enabled: true
  
  # Monitoring interval in minutes (15-240)
  monitoring_interval_minutes: 60
  
  # Markets to monitor
  monitored_regions:
    - china
    - hong_kong
    - usa
  
  # Market holidays (markets closed on these dates)
  market_holidays:
    china:
      - "2024-01-01"  # New Year's Day
      - "2024-02-10"  # Spring Festival
      # ... more holidays
    hong_kong:
      - "2024-01-01"  # New Year's Day
      - "2024-02-10"  # Lunar New Year
      # ... more holidays
    usa:
      - "2024-01-01"  # New Year's Day
      - "2024-07-04"  # Independence Day
      # ... more holidays
```

## Usage

### Basic Usage

```python
from stock_market_analysis.components.intraday import (
    IntradayMonitor,
    TimezoneConverter,
    MarketHoursDetector
)
from stock_market_analysis.components.configuration_manager import ConfigurationManager
from stock_market_analysis.components.analysis_engine import AnalysisEngine
from stock_market_analysis.trading.trade_executor import TradeExecutor

# Initialize components
config_manager = ConfigurationManager()
timezone_converter = TimezoneConverter()
market_hours_detector = MarketHoursDetector(timezone_converter, config_manager)

# Create intraday monitor
monitor = IntradayMonitor(
    market_hours_detector=market_hours_detector,
    analysis_engine=analysis_engine,
    trade_executor=trade_executor,
    config_manager=config_manager
)

# Start monitoring
monitor.start_monitoring()

# Check status
status = monitor.get_monitoring_status(MarketRegion.USA)
print(f"Active: {status.is_active}")
print(f"Cycles today: {status.total_cycles_today}")

# Stop monitoring
monitor.stop_monitoring()
```

### Enable/Disable Programmatically

```python
from stock_market_analysis.models.market_region import MarketRegion

# Enable intraday monitoring
result = config_manager.set_intraday_config(
    enabled=True,
    interval_minutes=60,
    regions=[MarketRegion.CHINA, MarketRegion.USA]
)

if result.is_ok():
    print("Intraday monitoring enabled")
else:
    print(f"Error: {result.error()}")
```

### Check Market Status

```python
from datetime import datetime

# Check if market is currently open
is_open = market_hours_detector.is_market_open(MarketRegion.USA)
print(f"USA market open: {is_open}")

# Check at specific time
check_time = datetime(2024, 6, 17, 14, 30, 0)  # UTC
is_open = market_hours_detector.is_market_open(MarketRegion.USA, check_time)
```

## Monitoring Status

The `MonitoringStatus` object provides detailed information:

```python
status = monitor.get_monitoring_status(MarketRegion.CHINA)

# Status fields
status.region                  # Market region
status.is_active              # Is monitoring active?
status.is_paused              # Is monitoring paused?
status.pause_reason           # Reason for pause (if paused)
status.pause_until            # When monitoring will resume
status.last_cycle_time        # Last analysis cycle time
status.next_cycle_time        # Next scheduled cycle time
status.consecutive_failures   # Number of consecutive failures
status.total_cycles_today     # Total cycles executed today
```

## Error Handling

### Circuit Breaker

After 3 consecutive failures, monitoring is automatically paused for 30 minutes:

```
2024-06-17 10:30:00 - ERROR - Analysis cycle error for china (consecutive failures: 3)
2024-06-17 10:30:00 - WARNING - Paused monitoring for china until 2024-06-17T11:00:00
```

Monitoring automatically resumes after the pause period if the market is still open.

### Error Recovery

- **Data Collection Errors**: Skip cycle, retry on next interval
- **Analysis Errors**: Log error, continue with next cycle
- **Trade Execution Errors**: Log error, continue processing other recommendations
- **Market Hours Detection Errors**: Assume market closed (fail-safe)

## Logging

All monitoring events are logged with structured information:

```
2024-06-17 09:30:00 - INFO - Starting analysis cycle for usa
2024-06-17 09:30:15 - INFO - Analysis completed for usa: 5 recommendations
2024-06-17 09:30:20 - INFO - Analysis cycle completed for usa: 2 trades executed in 20.3s
```

## Performance

- **Resource Usage**: Reuses Analysis Engine and Trade Executor instances
- **Concurrent Monitoring**: Separate threads for each regional market
- **Graceful Shutdown**: Completes in-progress cycles within 30 seconds
- **Memory Efficient**: Minimal state tracking per region

## Integration with Daily Analysis

Intraday monitoring operates independently from the daily scheduler:

- Both can run concurrently without interference
- Shared Analysis Engine and Trade Executor components
- Daily analysis continues to run at configured times
- Separate logging and error handling

## Troubleshooting

### Monitoring Not Starting

1. Check if enabled in configuration: `intraday_monitoring.enabled: true`
2. Verify regions are configured: `monitored_regions: [china, hong_kong, usa]`
3. Check logs for configuration errors

### No Trades Executing

1. Verify confidence threshold: `trading.confidence_threshold`
2. Check if market is open: Use `market_hours_detector.is_market_open()`
3. Review analysis results in logs
4. Verify sufficient cash balance in portfolio

### Monitoring Paused

1. Check status: `monitor.get_monitoring_status(region)`
2. Review `pause_reason` for details
3. Wait for automatic resume or restart monitoring
4. Check for underlying issues (network, API limits, etc.)

## Example Scripts

See `examples/intraday_monitoring_example.py` for a complete working example.

## Testing

Run unit tests:

```bash
python -m pytest tests/unit/test_timezone_converter.py -v
python -m pytest tests/unit/test_market_hours_detector.py -v
python -m pytest tests/unit/test_configuration_manager_intraday.py -v
```

## Requirements

- Python 3.8+
- pytz (for timezone handling)
- All dependencies from main stock market analysis system

## License

Same as main project.
