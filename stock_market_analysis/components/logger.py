"""
Centralized logging infrastructure for the stock market analysis system.

Provides error logging with timestamps and context, event logging for major operations,
and administrator notification system.
"""

import logging
import json
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass, asdict


class EventType(Enum):
    """Types of events that can be logged."""
    ERROR = "error"
    REPORT_GENERATION = "report_generation"
    NOTIFICATION_DELIVERY = "notification_delivery"
    CONFIGURATION_CHANGE = "configuration_change"
    DATA_COLLECTION = "data_collection"
    ANALYSIS_EXECUTION = "analysis_execution"
    SYSTEM_STARTUP = "system_startup"
    SYSTEM_SHUTDOWN = "system_shutdown"


class EventStatus(Enum):
    """Status of logged events."""
    SUCCESS = "success"
    FAILURE = "failure"
    IN_PROGRESS = "in_progress"
    PARTIAL_SUCCESS = "partial_success"


@dataclass
class LogEvent:
    """Structured log event with timestamp and context."""
    timestamp: datetime
    event_type: EventType
    status: EventStatus
    component: str
    message: str
    context: Dict[str, Any]
    error_details: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert log event to dictionary."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        data['event_type'] = self.event_type.value
        data['status'] = self.status.value
        return data
    
    def to_json(self) -> str:
        """Convert log event to JSON string."""
        return json.dumps(self.to_dict())


class SystemLogger:
    """
    Centralized logging system for the stock market analysis application.
    
    Provides:
    - Error logging with timestamps and context
    - Event logging for all major operations
    - Administrator notification system
    - Structured logging with JSON output
    """
    
    def __init__(
        self,
        log_dir: Path = Path("logs"),
        admin_notifiers: Optional[List[Callable[[str], None]]] = None
    ):
        """
        Initialize the system logger.
        
        Args:
            log_dir: Directory for log files
            admin_notifiers: List of callback functions for administrator notifications
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.admin_notifiers = admin_notifiers or []
        
        # Set up Python logging
        self.logger = logging.getLogger("stock_market_analysis")
        
        # Set up structured event log file
        self.event_log_path = self.log_dir / "events.jsonl"
        
    def log_event(
        self,
        event_type: EventType,
        status: EventStatus,
        component: str,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        error_details: Optional[str] = None
    ) -> None:
        """
        Log a structured event.
        
        Args:
            event_type: Type of event being logged
            status: Status of the event
            component: Component that generated the event
            message: Human-readable message
            context: Additional context information
            error_details: Error details if status is FAILURE
        """
        event = LogEvent(
            timestamp=datetime.now(),
            event_type=event_type,
            status=status,
            component=component,
            message=message,
            context=context or {},
            error_details=error_details
        )
        
        # Write to structured log file
        with open(self.event_log_path, 'a') as f:
            f.write(event.to_json() + '\n')
        
        # Also log to standard Python logger
        log_level = logging.ERROR if status == EventStatus.FAILURE else logging.INFO
        log_message = f"[{event_type.value}] {component}: {message}"
        if context:
            log_message += f" | Context: {json.dumps(context)}"
        if error_details:
            log_message += f" | Error: {error_details}"
        
        self.logger.log(log_level, log_message)
        
        # Notify administrators for critical errors
        if status == EventStatus.FAILURE and event_type == EventType.ERROR:
            self._notify_administrators(event)
    
    def log_error(
        self,
        component: str,
        message: str,
        error: Optional[Exception] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log an error with timestamp and context.
        
        Args:
            component: Component where error occurred
            message: Error message
            error: Exception object if available
            context: Additional context information
            
        Validates: Requirements 8.1
        """
        error_details = str(error) if error else None
        if error and hasattr(error, '__traceback__'):
            import traceback
            error_details = ''.join(traceback.format_exception(
                type(error), error, error.__traceback__
            ))
        
        self.log_event(
            event_type=EventType.ERROR,
            status=EventStatus.FAILURE,
            component=component,
            message=message,
            context=context,
            error_details=error_details
        )
    
    def log_report_generation(
        self,
        status: EventStatus,
        report_id: Optional[str] = None,
        recommendations_count: Optional[int] = None,
        error_details: Optional[str] = None
    ) -> None:
        """
        Log a daily report generation event.
        
        Args:
            status: Success or failure status
            report_id: ID of the generated report
            recommendations_count: Number of recommendations in report
            error_details: Error details if generation failed
            
        Validates: Requirements 8.2
        """
        context = {}
        if report_id:
            context['report_id'] = report_id
        if recommendations_count is not None:
            context['recommendations_count'] = recommendations_count
        
        message = f"Report generation {status.value}"
        if report_id:
            message += f" (ID: {report_id})"
        
        self.log_event(
            event_type=EventType.REPORT_GENERATION,
            status=status,
            component="ReportGenerator",
            message=message,
            context=context,
            error_details=error_details
        )
    
    def log_notification_delivery(
        self,
        channel: str,
        status: EventStatus,
        report_id: Optional[str] = None,
        error_details: Optional[str] = None
    ) -> None:
        """
        Log a notification delivery attempt.
        
        Args:
            channel: Delivery channel (telegram, slack, email)
            status: Success or failure status
            report_id: ID of the report being delivered
            error_details: Error details if delivery failed
            
        Validates: Requirements 8.3
        """
        context = {
            'channel': channel
        }
        if report_id:
            context['report_id'] = report_id
        
        message = f"Notification delivery via {channel}: {status.value}"
        
        self.log_event(
            event_type=EventType.NOTIFICATION_DELIVERY,
            status=status,
            component="NotificationService",
            message=message,
            context=context,
            error_details=error_details
        )
    
    def log_configuration_change(
        self,
        change_type: str,
        changed_values: Dict[str, Any],
        component: str = "ConfigurationManager"
    ) -> None:
        """
        Log a configuration change.
        
        Args:
            change_type: Type of configuration change
            changed_values: Dictionary of changed configuration values
            component: Component that made the change
            
        Validates: Requirements 8.4
        """
        # Sanitize sensitive values
        sanitized_values = self._sanitize_config_values(changed_values)
        
        self.log_event(
            event_type=EventType.CONFIGURATION_CHANGE,
            status=EventStatus.SUCCESS,
            component=component,
            message=f"Configuration change: {change_type}",
            context={
                'change_type': change_type,
                'changed_values': sanitized_values
            }
        )
    
    def log_data_collection(
        self,
        status: EventStatus,
        regions: List[str],
        successful_regions: Optional[List[str]] = None,
        failed_regions: Optional[List[str]] = None,
        error_details: Optional[str] = None
    ) -> None:
        """
        Log a market data collection event.
        
        Args:
            status: Success, failure, or partial success status
            regions: List of regions attempted
            successful_regions: List of regions that succeeded
            failed_regions: List of regions that failed
            error_details: Error details if collection failed
        """
        context = {
            'regions': regions
        }
        if successful_regions:
            context['successful_regions'] = successful_regions
        if failed_regions:
            context['failed_regions'] = failed_regions
        
        self.log_event(
            event_type=EventType.DATA_COLLECTION,
            status=status,
            component="MarketMonitor",
            message=f"Market data collection {status.value}",
            context=context,
            error_details=error_details
        )
    
    def log_analysis_execution(
        self,
        status: EventStatus,
        recommendations_count: Optional[int] = None,
        retry_count: Optional[int] = None,
        error_details: Optional[str] = None
    ) -> None:
        """
        Log an analysis execution event.
        
        Args:
            status: Success or failure status
            recommendations_count: Number of recommendations generated
            retry_count: Number of retry attempts made
            error_details: Error details if analysis failed
        """
        context = {}
        if recommendations_count is not None:
            context['recommendations_count'] = recommendations_count
        if retry_count is not None:
            context['retry_count'] = retry_count
        
        self.log_event(
            event_type=EventType.ANALYSIS_EXECUTION,
            status=status,
            component="AnalysisEngine",
            message=f"Analysis execution {status.value}",
            context=context,
            error_details=error_details
        )
    
    def add_admin_notifier(self, notifier: Callable[[str], None]) -> None:
        """
        Add an administrator notification callback.
        
        Args:
            notifier: Callback function that takes a message string
        """
        self.admin_notifiers.append(notifier)
    
    def _notify_administrators(self, event: LogEvent) -> None:
        """
        Send notification to administrators for critical events.
        
        Args:
            event: Log event to notify about
        """
        if not self.admin_notifiers:
            return
        
        notification_message = (
            f"CRITICAL ERROR in {event.component}\n"
            f"Time: {event.timestamp.isoformat()}\n"
            f"Message: {event.message}\n"
        )
        
        if event.context:
            notification_message += f"Context: {json.dumps(event.context, indent=2)}\n"
        
        if event.error_details:
            notification_message += f"Error Details:\n{event.error_details}\n"
        
        for notifier in self.admin_notifiers:
            try:
                notifier(notification_message)
            except Exception as e:
                # Don't let notification failures break the logging system
                self.logger.error(f"Failed to notify administrator: {e}")
    
    def _sanitize_config_values(self, values: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize sensitive configuration values for logging.
        
        Args:
            values: Configuration values to sanitize
            
        Returns:
            Sanitized configuration values
        """
        sensitive_keys = {
            'password', 'token', 'secret', 'api_key', 'bot_token',
            'webhook_url', 'smtp_password'
        }
        
        sanitized = {}
        for key, value in values.items():
            key_lower = key.lower()
            if any(sensitive in key_lower for sensitive in sensitive_keys):
                sanitized[key] = "***REDACTED***"
            elif isinstance(value, dict):
                sanitized[key] = self._sanitize_config_values(value)
            else:
                sanitized[key] = value
        
        return sanitized


# Global logger instance
_global_logger: Optional[SystemLogger] = None


def get_logger() -> SystemLogger:
    """
    Get the global system logger instance.
    
    Returns:
        Global SystemLogger instance
    """
    global _global_logger
    if _global_logger is None:
        _global_logger = SystemLogger()
    return _global_logger


def initialize_logger(
    log_dir: Path = Path("logs"),
    admin_notifiers: Optional[List[Callable[[str], None]]] = None
) -> SystemLogger:
    """
    Initialize the global system logger.
    
    Args:
        log_dir: Directory for log files
        admin_notifiers: List of callback functions for administrator notifications
        
    Returns:
        Initialized SystemLogger instance
    """
    global _global_logger
    _global_logger = SystemLogger(log_dir=log_dir, admin_notifiers=admin_notifiers)
    return _global_logger
