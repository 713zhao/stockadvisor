# Logging Infrastructure

## Overview

The Stock Market Analysis system includes a centralized logging infrastructure that provides:

- **Error logging** with timestamps and context (Requirement 8.1)
- **Event logging** for all major operations (Requirements 8.2, 8.3, 8.4)
- **Administrator notification system** for critical errors
- **Structured logging** with JSON output for easy parsing
- **Sensitive data sanitization** for security

## Quick Start

```python
from stock_market_analysis.components.logger import get_logger, EventStatus

# Get the global logger instance
logger = get_logger()

# Log an error
logger.log_error(
    component="MyComponent",
    message="Something went wrong",
    context={"operation": "data_fetch"}
)

# Log a successful report generation
logger.log_report_generation(
    status=EventStatus.SUCCESS,
    report_id="report-123",
    recommendations_count=10
)
```

## Features

### 1. Error Logging (Requirement 8.1)

Log errors with timestamps and context information:

```python
logger.log_error(
    component="AnalysisEngine",
    message="Failed to analyze stock data",
    error=exception_object,  # Optional
    context={"stock": "AAPL", "region": "USA"}
)
```

### 2. Report Generation Logging (Requirement 8.2)

Log all daily report generation events with success/failure status:

```python
# Success
logger.log_report_generation(
    status=EventStatus.SUCCESS,
    report_id="report-2024-01-15",
    recommendations_count=10
)

# Failure
logger.log_report_generation(
    status=EventStatus.FAILURE,
    error_details="Database connection failed"
)
```

### 3. Notification Delivery Logging (Requirement 8.3)

Log all notification delivery attempts:

```python
logger.log_notification_delivery(
    channel="telegram",
    status=EventStatus.SUCCESS,
    report_id="report-123"
)

logger.log_notification_delivery(
    channel="slack",
    status=EventStatus.FAILURE,
    error_details="Invalid webhook URL"
)
```

### 4. Configuration Change Logging (Requirement 8.4)

Log all configuration changes with timestamps and changed values:

```python
logger.log_configuration_change(
    change_type="add_market_region",
    changed_values={
        "region": "USA",
        "enabled": True,
        "api_key": "secret123"  # Automatically sanitized
    }
)
```

### 5. Data Collection Logging

Log market data collection events:

```python
# Full success
logger.log_data_collection(
    status=EventStatus.SUCCESS,
    regions=["USA", "China"],
    successful_regions=["USA", "China"]
)

# Partial success
logger.log_data_collection(
    status=EventStatus.PARTIAL_SUCCESS,
    regions=["USA", "China", "HongKong"],
    successful_regions=["USA", "China"],
    failed_regions=["HongKong"],
    error_details="HongKong API timeout"
)
```

### 6. Analysis Execution Logging

Log analysis execution events:

```python
logger.log_analysis_execution(
    status=EventStatus.SUCCESS,
    recommendations_count=15,
    retry_count=0
)
```

### 7. Administrator Notifications

Set up administrator notifications for critical errors:

```python
from stock_market_analysis.components.logger import initialize_logger

def send_email_alert(message: str):
    # Send email to administrators
    pass

def send_sms_alert(message: str):
    # Send SMS to administrators
    pass

# Initialize with admin notifiers
logger = initialize_logger(
    log_dir=Path("logs"),
    admin_notifiers=[send_email_alert, send_sms_alert]
)
```

When critical errors occur, all registered notifiers will be called automatically.

## Event Types

The system supports the following event types:

- `ERROR` - Error events
- `REPORT_GENERATION` - Daily report generation
- `NOTIFICATION_DELIVERY` - Notification delivery attempts
- `CONFIGURATION_CHANGE` - Configuration changes
- `DATA_COLLECTION` - Market data collection
- `ANALYSIS_EXECUTION` - Analysis execution
- `SYSTEM_STARTUP` - System startup
- `SYSTEM_SHUTDOWN` - System shutdown

## Event Status

Events can have the following statuses:

- `SUCCESS` - Operation completed successfully
- `FAILURE` - Operation failed
- `IN_PROGRESS` - Operation is in progress
- `PARTIAL_SUCCESS` - Operation partially succeeded

## Log Files

The logging infrastructure creates two types of log files:

### 1. Standard Log File

Location: `logs/stock_analysis.log`

Format: Human-readable text with timestamps

```
2024-01-15 10:30:00 - stock_market_analysis - INFO - [report_generation] ReportGenerator: Report generation success (ID: report-123) | Context: {"report_id": "report-123", "recommendations_count": 10}
```

### 2. Structured Event Log

Location: `logs/events.jsonl`

Format: JSON Lines (one JSON object per line)

```json
{"timestamp": "2024-01-15T10:30:00", "event_type": "report_generation", "status": "success", "component": "ReportGenerator", "message": "Report generation success (ID: report-123)", "context": {"report_id": "report-123", "recommendations_count": 10}, "error_details": null}
```

This format is ideal for:
- Log aggregation systems (ELK, Splunk)
- Automated log analysis
- Monitoring and alerting

## Sensitive Data Sanitization

The logging system automatically sanitizes sensitive configuration values:

```python
logger.log_configuration_change(
    change_type="update_credentials",
    changed_values={
        "bot_token": "secret123",      # Sanitized
        "password": "mypassword",       # Sanitized
        "api_key": "key456",           # Sanitized
        "username": "admin"            # Not sanitized
    }
)
```

Sensitive keys include:
- `password`
- `token`
- `secret`
- `api_key`
- `bot_token`
- `webhook_url`
- `smtp_password`

## Best Practices

1. **Use appropriate log levels**: Use `log_error()` for errors, specific methods for events
2. **Include context**: Always provide relevant context information
3. **Don't log sensitive data**: The system sanitizes known sensitive keys, but avoid logging sensitive data
4. **Use structured logging**: Prefer the specialized methods over generic `log_event()`
5. **Set up admin notifications**: Configure admin notifiers for production environments

## Integration with Components

All components should use the centralized logger:

```python
from stock_market_analysis.components.logger import get_logger, EventStatus

class MyComponent:
    def __init__(self):
        self.logger = get_logger()
    
    def do_something(self):
        try:
            # Do work
            result = self.perform_operation()
            
            # Log success
            self.logger.log_event(
                event_type=EventType.CUSTOM,
                status=EventStatus.SUCCESS,
                component="MyComponent",
                message="Operation completed",
                context={"result": result}
            )
        except Exception as e:
            # Log error
            self.logger.log_error(
                component="MyComponent",
                message="Operation failed",
                error=e,
                context={"operation": "do_something"}
            )
```

## Testing

The logging infrastructure includes comprehensive unit tests:

```bash
python -m pytest tests/unit/test_logger.py -v
```

## Examples

See `logger_example.py` for complete usage examples.
