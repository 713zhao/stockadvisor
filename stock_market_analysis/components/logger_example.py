"""
Example usage of the logging infrastructure.

This file demonstrates how to use the centralized logging system
in the stock market analysis application.
"""

from pathlib import Path
from stock_market_analysis.components.logger import (
    get_logger,
    initialize_logger,
    EventType,
    EventStatus
)


def example_basic_usage():
    """Example: Basic logging usage."""
    # Get the global logger instance
    logger = get_logger()
    
    # Log an error
    logger.log_error(
        component="MyComponent",
        message="Something went wrong",
        context={"operation": "data_fetch", "retry_count": 1}
    )
    
    # Log a successful report generation
    logger.log_report_generation(
        status=EventStatus.SUCCESS,
        report_id="report-2024-01-15",
        recommendations_count=10
    )
    
    # Log a notification delivery
    logger.log_notification_delivery(
        channel="telegram",
        status=EventStatus.SUCCESS,
        report_id="report-2024-01-15"
    )


def example_with_exception():
    """Example: Logging with exception handling."""
    logger = get_logger()
    
    try:
        # Some operation that might fail
        result = 10 / 0
    except Exception as e:
        # Log the error with exception details
        logger.log_error(
            component="Calculator",
            message="Division operation failed",
            error=e,
            context={"operation": "divide", "numerator": 10, "denominator": 0}
        )


def example_configuration_logging():
    """Example: Logging configuration changes."""
    logger = get_logger()
    
    # Log a configuration change
    logger.log_configuration_change(
        change_type="add_market_region",
        changed_values={
            "region": "USA",
            "enabled": True,
            "api_key": "secret123"  # Will be automatically sanitized
        }
    )


def example_with_admin_notifications():
    """Example: Setting up administrator notifications."""
    
    def send_email_notification(message: str):
        """Send email to administrators."""
        print(f"EMAIL TO ADMIN: {message}")
    
    def send_sms_notification(message: str):
        """Send SMS to administrators."""
        print(f"SMS TO ADMIN: {message}")
    
    # Initialize logger with admin notifiers
    logger = initialize_logger(
        log_dir=Path("logs"),
        admin_notifiers=[send_email_notification, send_sms_notification]
    )
    
    # This error will trigger admin notifications
    logger.log_error(
        component="CriticalSystem",
        message="Critical system failure detected",
        context={"severity": "critical"}
    )


def example_data_collection_logging():
    """Example: Logging data collection events."""
    logger = get_logger()
    
    # Log successful data collection
    logger.log_data_collection(
        status=EventStatus.SUCCESS,
        regions=["USA", "China", "HongKong"],
        successful_regions=["USA", "China", "HongKong"]
    )
    
    # Log partial success (some regions failed)
    logger.log_data_collection(
        status=EventStatus.PARTIAL_SUCCESS,
        regions=["USA", "China", "HongKong"],
        successful_regions=["USA", "China"],
        failed_regions=["HongKong"],
        error_details="HongKong API timeout after 30 seconds"
    )


def example_analysis_logging():
    """Example: Logging analysis execution."""
    logger = get_logger()
    
    # Log successful analysis
    logger.log_analysis_execution(
        status=EventStatus.SUCCESS,
        recommendations_count=15,
        retry_count=0
    )
    
    # Log failed analysis with retries
    logger.log_analysis_execution(
        status=EventStatus.FAILURE,
        retry_count=3,
        error_details="Analysis failed after 3 retry attempts"
    )


def example_custom_event():
    """Example: Logging custom events."""
    logger = get_logger()
    
    # Log a custom event using the generic log_event method
    logger.log_event(
        event_type=EventType.SYSTEM_STARTUP,
        status=EventStatus.SUCCESS,
        component="Application",
        message="System started successfully",
        context={
            "version": "1.0.0",
            "environment": "production",
            "startup_time_ms": 1234
        }
    )


if __name__ == "__main__":
    print("Running logging examples...\n")
    
    print("1. Basic usage:")
    example_basic_usage()
    
    print("\n2. With exception:")
    example_with_exception()
    
    print("\n3. Configuration logging:")
    example_configuration_logging()
    
    print("\n4. Data collection logging:")
    example_data_collection_logging()
    
    print("\n5. Analysis logging:")
    example_analysis_logging()
    
    print("\n6. Custom event:")
    example_custom_event()
    
    print("\n7. With admin notifications:")
    example_with_admin_notifications()
    
    print("\nCheck logs/events.jsonl for structured event logs")
