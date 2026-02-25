"""
Unit tests for the logging infrastructure.

Tests error logging, event logging, and administrator notification system.
"""

import json
import pytest
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch, call

from stock_market_analysis.components.logger import (
    SystemLogger,
    EventType,
    EventStatus,
    LogEvent,
    get_logger,
    initialize_logger
)


class TestLogEvent:
    """Tests for LogEvent data class."""
    
    def test_log_event_to_dict(self):
        """Test converting log event to dictionary."""
        event = LogEvent(
            timestamp=datetime(2024, 1, 15, 10, 30, 0),
            event_type=EventType.ERROR,
            status=EventStatus.FAILURE,
            component="TestComponent",
            message="Test error message",
            context={"key": "value"},
            error_details="Error details"
        )
        
        result = event.to_dict()
        
        assert result['timestamp'] == "2024-01-15T10:30:00"
        assert result['event_type'] == "error"
        assert result['status'] == "failure"
        assert result['component'] == "TestComponent"
        assert result['message'] == "Test error message"
        assert result['context'] == {"key": "value"}
        assert result['error_details'] == "Error details"
    
    def test_log_event_to_json(self):
        """Test converting log event to JSON string."""
        event = LogEvent(
            timestamp=datetime(2024, 1, 15, 10, 30, 0),
            event_type=EventType.REPORT_GENERATION,
            status=EventStatus.SUCCESS,
            component="ReportGenerator",
            message="Report generated",
            context={"report_id": "123"}
        )
        
        result = event.to_json()
        parsed = json.loads(result)
        
        assert parsed['event_type'] == "report_generation"
        assert parsed['status'] == "success"
        assert parsed['context']['report_id'] == "123"


class TestSystemLogger:
    """Tests for SystemLogger class."""
    
    @pytest.fixture
    def temp_log_dir(self, tmp_path):
        """Create temporary log directory."""
        log_dir = tmp_path / "logs"
        log_dir.mkdir()
        return log_dir
    
    @pytest.fixture
    def logger(self, temp_log_dir):
        """Create SystemLogger instance with temporary directory."""
        return SystemLogger(log_dir=temp_log_dir)
    
    def test_logger_initialization(self, temp_log_dir):
        """Test logger initialization creates log directory."""
        logger = SystemLogger(log_dir=temp_log_dir)
        
        assert logger.log_dir.exists()
        assert logger.event_log_path == temp_log_dir / "events.jsonl"
        assert logger.admin_notifiers == []
    
    def test_log_event_writes_to_file(self, logger, temp_log_dir):
        """Test that log_event writes to structured log file."""
        logger.log_event(
            event_type=EventType.ERROR,
            status=EventStatus.FAILURE,
            component="TestComponent",
            message="Test error",
            context={"key": "value"}
        )
        
        event_log_path = temp_log_dir / "events.jsonl"
        assert event_log_path.exists()
        
        with open(event_log_path, 'r') as f:
            lines = f.readlines()
        
        assert len(lines) == 1
        event_data = json.loads(lines[0])
        assert event_data['event_type'] == "error"
        assert event_data['status'] == "failure"
        assert event_data['component'] == "TestComponent"
        assert event_data['message'] == "Test error"
        assert event_data['context'] == {"key": "value"}
    
    def test_log_error_with_exception(self, logger, temp_log_dir):
        """Test logging error with exception object."""
        try:
            raise ValueError("Test exception")
        except ValueError as e:
            logger.log_error(
                component="TestComponent",
                message="An error occurred",
                error=e,
                context={"operation": "test"}
            )
        
        event_log_path = temp_log_dir / "events.jsonl"
        with open(event_log_path, 'r') as f:
            event_data = json.loads(f.read())
        
        assert event_data['event_type'] == "error"
        assert event_data['status'] == "failure"
        assert event_data['message'] == "An error occurred"
        assert "ValueError: Test exception" in event_data['error_details']
        assert event_data['context']['operation'] == "test"
    
    def test_log_error_without_exception(self, logger, temp_log_dir):
        """Test logging error without exception object."""
        logger.log_error(
            component="TestComponent",
            message="Error without exception",
            context={"info": "test"}
        )
        
        event_log_path = temp_log_dir / "events.jsonl"
        with open(event_log_path, 'r') as f:
            event_data = json.loads(f.read())
        
        assert event_data['event_type'] == "error"
        assert event_data['message'] == "Error without exception"
        assert event_data['error_details'] is None
    
    def test_log_report_generation_success(self, logger, temp_log_dir):
        """Test logging successful report generation."""
        logger.log_report_generation(
            status=EventStatus.SUCCESS,
            report_id="report-123",
            recommendations_count=5
        )
        
        event_log_path = temp_log_dir / "events.jsonl"
        with open(event_log_path, 'r') as f:
            event_data = json.loads(f.read())
        
        assert event_data['event_type'] == "report_generation"
        assert event_data['status'] == "success"
        assert event_data['component'] == "ReportGenerator"
        assert "report-123" in event_data['message']
        assert event_data['context']['report_id'] == "report-123"
        assert event_data['context']['recommendations_count'] == 5
    
    def test_log_report_generation_failure(self, logger, temp_log_dir):
        """Test logging failed report generation."""
        logger.log_report_generation(
            status=EventStatus.FAILURE,
            error_details="Database connection failed"
        )
        
        event_log_path = temp_log_dir / "events.jsonl"
        with open(event_log_path, 'r') as f:
            event_data = json.loads(f.read())
        
        assert event_data['event_type'] == "report_generation"
        assert event_data['status'] == "failure"
        assert event_data['error_details'] == "Database connection failed"
    
    def test_log_notification_delivery_success(self, logger, temp_log_dir):
        """Test logging successful notification delivery."""
        logger.log_notification_delivery(
            channel="telegram",
            status=EventStatus.SUCCESS,
            report_id="report-123"
        )
        
        event_log_path = temp_log_dir / "events.jsonl"
        with open(event_log_path, 'r') as f:
            event_data = json.loads(f.read())
        
        assert event_data['event_type'] == "notification_delivery"
        assert event_data['status'] == "success"
        assert event_data['component'] == "NotificationService"
        assert "telegram" in event_data['message']
        assert event_data['context']['channel'] == "telegram"
        assert event_data['context']['report_id'] == "report-123"
    
    def test_log_notification_delivery_failure(self, logger, temp_log_dir):
        """Test logging failed notification delivery."""
        logger.log_notification_delivery(
            channel="slack",
            status=EventStatus.FAILURE,
            report_id="report-456",
            error_details="Invalid webhook URL"
        )
        
        event_log_path = temp_log_dir / "events.jsonl"
        with open(event_log_path, 'r') as f:
            event_data = json.loads(f.read())
        
        assert event_data['event_type'] == "notification_delivery"
        assert event_data['status'] == "failure"
        assert event_data['context']['channel'] == "slack"
        assert event_data['error_details'] == "Invalid webhook URL"
    
    def test_log_configuration_change(self, logger, temp_log_dir):
        """Test logging configuration changes."""
        logger.log_configuration_change(
            change_type="add_region",
            changed_values={"region": "USA", "enabled": True}
        )
        
        event_log_path = temp_log_dir / "events.jsonl"
        with open(event_log_path, 'r') as f:
            event_data = json.loads(f.read())
        
        assert event_data['event_type'] == "configuration_change"
        assert event_data['status'] == "success"
        assert event_data['component'] == "ConfigurationManager"
        assert event_data['context']['change_type'] == "add_region"
        assert event_data['context']['changed_values']['region'] == "USA"
    
    def test_log_configuration_change_sanitizes_sensitive_data(self, logger, temp_log_dir):
        """Test that sensitive configuration values are sanitized."""
        logger.log_configuration_change(
            change_type="update_credentials",
            changed_values={
                "bot_token": "secret123",
                "password": "mypassword",
                "api_key": "key456",
                "username": "admin"
            }
        )
        
        event_log_path = temp_log_dir / "events.jsonl"
        with open(event_log_path, 'r') as f:
            event_data = json.loads(f.read())
        
        changed_values = event_data['context']['changed_values']
        assert changed_values['bot_token'] == "***REDACTED***"
        assert changed_values['password'] == "***REDACTED***"
        assert changed_values['api_key'] == "***REDACTED***"
        assert changed_values['username'] == "admin"  # Not sensitive
    
    def test_log_data_collection_success(self, logger, temp_log_dir):
        """Test logging successful data collection."""
        logger.log_data_collection(
            status=EventStatus.SUCCESS,
            regions=["USA", "China"],
            successful_regions=["USA", "China"]
        )
        
        event_log_path = temp_log_dir / "events.jsonl"
        with open(event_log_path, 'r') as f:
            event_data = json.loads(f.read())
        
        assert event_data['event_type'] == "data_collection"
        assert event_data['status'] == "success"
        assert event_data['component'] == "MarketMonitor"
        assert event_data['context']['regions'] == ["USA", "China"]
        assert event_data['context']['successful_regions'] == ["USA", "China"]
    
    def test_log_data_collection_partial_success(self, logger, temp_log_dir):
        """Test logging partial data collection success."""
        logger.log_data_collection(
            status=EventStatus.PARTIAL_SUCCESS,
            regions=["USA", "China", "HongKong"],
            successful_regions=["USA", "China"],
            failed_regions=["HongKong"],
            error_details="HongKong API timeout"
        )
        
        event_log_path = temp_log_dir / "events.jsonl"
        with open(event_log_path, 'r') as f:
            event_data = json.loads(f.read())
        
        assert event_data['status'] == "partial_success"
        assert event_data['context']['successful_regions'] == ["USA", "China"]
        assert event_data['context']['failed_regions'] == ["HongKong"]
        assert event_data['error_details'] == "HongKong API timeout"
    
    def test_log_analysis_execution_success(self, logger, temp_log_dir):
        """Test logging successful analysis execution."""
        logger.log_analysis_execution(
            status=EventStatus.SUCCESS,
            recommendations_count=10,
            retry_count=0
        )
        
        event_log_path = temp_log_dir / "events.jsonl"
        with open(event_log_path, 'r') as f:
            event_data = json.loads(f.read())
        
        assert event_data['event_type'] == "analysis_execution"
        assert event_data['status'] == "success"
        assert event_data['component'] == "AnalysisEngine"
        assert event_data['context']['recommendations_count'] == 10
        assert event_data['context']['retry_count'] == 0
    
    def test_log_analysis_execution_with_retries(self, logger, temp_log_dir):
        """Test logging analysis execution with retries."""
        logger.log_analysis_execution(
            status=EventStatus.FAILURE,
            retry_count=3,
            error_details="Analysis failed after all retries"
        )
        
        event_log_path = temp_log_dir / "events.jsonl"
        with open(event_log_path, 'r') as f:
            event_data = json.loads(f.read())
        
        assert event_data['status'] == "failure"
        assert event_data['context']['retry_count'] == 3
        assert event_data['error_details'] == "Analysis failed after all retries"
    
    def test_add_admin_notifier(self, logger):
        """Test adding administrator notifier."""
        notifier = Mock()
        
        logger.add_admin_notifier(notifier)
        
        assert notifier in logger.admin_notifiers
    
    def test_admin_notification_on_error(self, logger):
        """Test that administrators are notified on critical errors."""
        notifier = Mock()
        logger.add_admin_notifier(notifier)
        
        logger.log_error(
            component="TestComponent",
            message="Critical error occurred",
            context={"severity": "high"}
        )
        
        notifier.assert_called_once()
        call_args = notifier.call_args[0][0]
        assert "CRITICAL ERROR" in call_args
        assert "TestComponent" in call_args
        assert "Critical error occurred" in call_args
    
    def test_admin_notification_not_sent_for_non_errors(self, logger):
        """Test that administrators are not notified for non-error events."""
        notifier = Mock()
        logger.add_admin_notifier(notifier)
        
        logger.log_report_generation(
            status=EventStatus.SUCCESS,
            report_id="report-123"
        )
        
        notifier.assert_not_called()
    
    def test_admin_notification_failure_does_not_break_logging(self, logger, temp_log_dir):
        """Test that notification failures don't break the logging system."""
        failing_notifier = Mock(side_effect=Exception("Notification failed"))
        logger.add_admin_notifier(failing_notifier)
        
        # Should not raise exception
        logger.log_error(
            component="TestComponent",
            message="Test error"
        )
        
        # Event should still be logged
        event_log_path = temp_log_dir / "events.jsonl"
        assert event_log_path.exists()
    
    def test_multiple_events_logged(self, logger, temp_log_dir):
        """Test logging multiple events."""
        logger.log_report_generation(status=EventStatus.SUCCESS, report_id="r1")
        logger.log_notification_delivery(channel="telegram", status=EventStatus.SUCCESS)
        logger.log_configuration_change(change_type="test", changed_values={})
        
        event_log_path = temp_log_dir / "events.jsonl"
        with open(event_log_path, 'r') as f:
            lines = f.readlines()
        
        assert len(lines) == 3
        
        event1 = json.loads(lines[0])
        event2 = json.loads(lines[1])
        event3 = json.loads(lines[2])
        
        assert event1['event_type'] == "report_generation"
        assert event2['event_type'] == "notification_delivery"
        assert event3['event_type'] == "configuration_change"


class TestGlobalLogger:
    """Tests for global logger functions."""
    
    def test_get_logger_creates_instance(self):
        """Test that get_logger creates a global instance."""
        # Reset global logger
        import stock_market_analysis.components.logger as logger_module
        logger_module._global_logger = None
        
        logger = get_logger()
        
        assert logger is not None
        assert isinstance(logger, SystemLogger)
    
    def test_get_logger_returns_same_instance(self):
        """Test that get_logger returns the same instance."""
        logger1 = get_logger()
        logger2 = get_logger()
        
        assert logger1 is logger2
    
    def test_initialize_logger_sets_global_instance(self, tmp_path):
        """Test that initialize_logger sets the global instance."""
        log_dir = tmp_path / "logs"
        notifier = Mock()
        
        logger = initialize_logger(log_dir=log_dir, admin_notifiers=[notifier])
        
        assert logger is not None
        assert logger.log_dir == log_dir
        assert notifier in logger.admin_notifiers
        
        # get_logger should return the same instance
        assert get_logger() is logger


class TestSensitiveDataSanitization:
    """Tests for sensitive data sanitization."""
    
    @pytest.fixture
    def logger(self, tmp_path):
        """Create SystemLogger instance."""
        return SystemLogger(log_dir=tmp_path / "logs")
    
    def test_sanitize_password(self, logger):
        """Test that passwords are sanitized."""
        values = {"password": "secret123", "username": "admin"}
        result = logger._sanitize_config_values(values)
        
        assert result['password'] == "***REDACTED***"
        assert result['username'] == "admin"
    
    def test_sanitize_token(self, logger):
        """Test that tokens are sanitized."""
        values = {"bot_token": "abc123", "api_token": "xyz789"}
        result = logger._sanitize_config_values(values)
        
        assert result['bot_token'] == "***REDACTED***"
        assert result['api_token'] == "***REDACTED***"
    
    def test_sanitize_nested_values(self, logger):
        """Test that nested sensitive values are sanitized."""
        values = {
            "smtp": {
                "host": "smtp.example.com",
                "password": "secret",
                "username": "user"
            }
        }
        result = logger._sanitize_config_values(values)
        
        assert result['smtp']['password'] == "***REDACTED***"
        assert result['smtp']['host'] == "smtp.example.com"
        assert result['smtp']['username'] == "user"
    
    def test_sanitize_case_insensitive(self, logger):
        """Test that sanitization is case-insensitive."""
        values = {"PASSWORD": "secret", "Bot_Token": "token123"}
        result = logger._sanitize_config_values(values)
        
        assert result['PASSWORD'] == "***REDACTED***"
        assert result['Bot_Token'] == "***REDACTED***"
