"""
Unit tests for the Notification Service component.

Tests notification delivery through Telegram, Slack, and Email channels
with graceful failure handling.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, date
from decimal import Decimal

from stock_market_analysis.components import NotificationService, ConfigurationManager
from stock_market_analysis.models import (
    DailyReport,
    StockRecommendation,
    RecommendationType,
    MarketRegion,
    MarketSummary,
    TelegramConfig,
    SlackConfig,
    SMTPConfig,
    EmailConfig
)


@pytest.fixture
def config_manager():
    """Create a configuration manager for testing without loading from file."""
    from stock_market_analysis.models import SystemConfiguration
    # Create a fresh ConfigurationManager with empty configuration
    manager = ConfigurationManager.__new__(ConfigurationManager)
    manager.logger = Mock()
    manager.storage_path = None
    manager._configuration = SystemConfiguration(
        market_regions=[MarketRegion.CHINA, MarketRegion.HONG_KONG, MarketRegion.USA],
        telegram=None,
        slack=None,
        email=None,
        custom_schedule=None
    )
    manager.market_regions = manager._configuration.market_regions
    manager.telegram_config = None
    manager.slack_config = None
    manager.email_config = None
    return manager


@pytest.fixture
def notification_service(config_manager):
    """Create a notification service for testing."""
    return NotificationService(config_manager)


@pytest.fixture
def sample_report():
    """Create a sample daily report for testing."""
    recommendation = StockRecommendation(
        symbol="AAPL",
        region=MarketRegion.USA,
        recommendation_type=RecommendationType.BUY,
        rationale="Strong earnings growth",
        risk_assessment="Low risk",
        confidence_score=0.85,
        target_price=Decimal("150.00"),
        generated_at=datetime.now()
    )
    
    market_summary = MarketSummary(
        region=MarketRegion.USA,
        trading_date=date.today(),
        total_stocks_analyzed=100,
        market_trend="bullish",
        notable_events=["Fed rate decision"],
        index_performance={"S&P 500": Decimal("1.5")}
    )
    
    return DailyReport(
        report_id="test-report-001",
        generation_time=datetime.now(),
        trading_date=date.today(),
        recommendations=[recommendation],
        market_summaries={MarketRegion.USA: market_summary}
    )


class TestNotificationServiceDelivery:
    """Tests for multi-channel notification delivery."""
    
    @patch('stock_market_analysis.components.notification_service.requests.post')
    def test_telegram_delivery_success(self, mock_post, notification_service, config_manager, sample_report):
        """
        Test successful Telegram delivery.
        Validates: Requirements 4.1
        """
        # Configure Telegram
        config_manager.set_telegram_config("test_bot_token_123456", ["123456789"])
        
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        # Deliver report
        success = notification_service.deliver_to_telegram(sample_report)
        
        assert success is True
        assert mock_post.called
        
        # Verify API call
        call_args = mock_post.call_args
        assert "api.telegram.org" in call_args[0][0]
        assert call_args[1]['json']['chat_id'] == "123456789"
        assert 'text' in call_args[1]['json']
    
    @patch('stock_market_analysis.components.notification_service.requests.post')
    def test_telegram_delivery_multiple_chats(self, mock_post, notification_service, config_manager, sample_report):
        """
        Test Telegram delivery to multiple chat IDs.
        Validates: Requirements 4.1
        """
        # Configure Telegram with multiple chats
        config_manager.set_telegram_config("test_bot_token_123456", ["123456789", "987654321"])
        
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        # Deliver report
        success = notification_service.deliver_to_telegram(sample_report)
        
        assert success is True
        assert mock_post.call_count == 2
    
    @patch('stock_market_analysis.components.notification_service.requests.post')
    def test_slack_delivery_success(self, mock_post, notification_service, config_manager, sample_report):
        """
        Test successful Slack delivery.
        Validates: Requirements 4.2
        """
        # Configure Slack
        config_manager.set_slack_config("https://hooks.slack.com/services/TEST/WEBHOOK", "#trading")
        
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        # Deliver report
        success = notification_service.deliver_to_slack(sample_report)
        
        assert success is True
        assert mock_post.called
        
        # Verify webhook call
        call_args = mock_post.call_args
        assert "hooks.slack.com" in call_args[0][0]
        assert call_args[1]['json']['channel'] == "#trading"
        assert 'text' in call_args[1]['json']
    
    @patch('stock_market_analysis.components.notification_service.smtplib.SMTP')
    def test_email_delivery_success(self, mock_smtp, notification_service, config_manager, sample_report):
        """
        Test successful Email delivery.
        Validates: Requirements 4.3
        """
        # Configure Email
        smtp_config = SMTPConfig(
            host="smtp.gmail.com",
            port=587,
            username="test@example.com",
            password="test_password",
            use_tls=True
        )
        config_manager.set_email_config(smtp_config, ["recipient@example.com"])
        
        # Mock SMTP server
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        
        # Deliver report
        success = notification_service.deliver_to_email(sample_report)
        
        assert success is True
        assert mock_server.starttls.called
        assert mock_server.login.called
        assert mock_server.sendmail.called
        assert mock_server.quit.called


class TestChannelFailureHandling:
    """Tests for graceful channel failure handling."""
    
    def test_no_configuration_returns_false(self, notification_service, sample_report):
        """
        Test that delivery returns False when no configuration exists.
        Validates: Requirements 4.4
        """
        # No configuration set
        telegram_success = notification_service.deliver_to_telegram(sample_report)
        slack_success = notification_service.deliver_to_slack(sample_report)
        email_success = notification_service.deliver_to_email(sample_report)
        
        assert telegram_success is False
        assert slack_success is False
        assert email_success is False
    
    @patch('stock_market_analysis.components.notification_service.requests.post')
    def test_telegram_failure_isolation(self, mock_post, notification_service, config_manager, sample_report):
        """
        Test that Telegram failure doesn't affect other channels.
        Validates: Requirements 4.4, 8.3
        """
        # Configure all channels
        config_manager.set_telegram_config("test_bot_token_123456", ["123456789"])
        config_manager.set_slack_config("https://hooks.slack.com/services/TEST/WEBHOOK", "#trading")
        
        # Mock Telegram failure, Slack success
        def mock_post_side_effect(url, *args, **kwargs):
            response = Mock()
            if "telegram" in url:
                response.status_code = 400
                response.text = "Bad Request"
            else:
                response.status_code = 200
            return response
        
        mock_post.side_effect = mock_post_side_effect
        
        # Deliver report
        result = notification_service.deliver_report(sample_report)
        
        # Telegram should fail, Slack should succeed
        assert result.telegram_success is False
        assert result.slack_success is True
        assert 'telegram' in result.errors
        assert 'slack' not in result.errors
    
    @patch('stock_market_analysis.components.notification_service.smtplib.SMTP')
    @patch('stock_market_analysis.components.notification_service.requests.post')
    def test_all_channels_attempted_on_partial_failure(self, mock_post, mock_smtp, 
                                                       notification_service, config_manager, sample_report):
        """
        Test that all channels are attempted even when some fail.
        Validates: Requirements 4.4
        """
        # Configure all channels
        config_manager.set_telegram_config("test_bot_token_123456", ["123456789"])
        config_manager.set_slack_config("https://hooks.slack.com/services/TEST/WEBHOOK", "#trading")
        smtp_config = SMTPConfig(
            host="smtp.gmail.com",
            port=587,
            username="test@example.com",
            password="test_password",
            use_tls=True
        )
        config_manager.set_email_config(smtp_config, ["recipient@example.com"])
        
        # Mock Telegram and Slack failure, Email success
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Server Error"
        mock_post.return_value = mock_response
        
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        
        # Deliver report
        result = notification_service.deliver_report(sample_report)
        
        # All channels should be attempted
        assert mock_post.call_count == 2  # Telegram and Slack
        assert mock_smtp.called  # Email
        
        # Telegram and Slack should fail, Email should succeed
        assert result.telegram_success is False
        assert result.slack_success is False
        assert result.email_success is True
        assert result.any_succeeded() is True
        assert result.all_succeeded() is False
    
    @patch('stock_market_analysis.components.notification_service.requests.post')
    def test_telegram_partial_chat_failure(self, mock_post, notification_service, config_manager, sample_report):
        """
        Test handling when some Telegram chats fail.
        Validates: Requirements 4.4
        """
        # Configure Telegram with multiple chats
        config_manager.set_telegram_config("test_bot_token_123456", ["123456789", "987654321"])
        
        # Mock one success, one failure
        call_count = [0]
        def mock_post_side_effect(*args, **kwargs):
            response = Mock()
            if call_count[0] == 0:
                response.status_code = 200
            else:
                response.status_code = 400
                response.text = "Bad Request"
            call_count[0] += 1
            return response
        
        mock_post.side_effect = mock_post_side_effect
        
        # Deliver report
        success = notification_service.deliver_to_telegram(sample_report)
        
        # Should fail because not all chats succeeded
        assert success is False
        assert mock_post.call_count == 2


class TestChannelFormatting:
    """Tests for channel-specific report formatting."""
    
    def test_telegram_format_contains_key_info(self, sample_report):
        """
        Test that Telegram format contains key report information.
        Validates: Requirements 4.5
        """
        formatted = sample_report.format_for_telegram()
        
        assert formatted is not None
        assert len(formatted) > 0
        assert str(sample_report.trading_date) in formatted
        assert "AAPL" in formatted
        assert "BUY" in formatted.upper()
    
    def test_slack_format_contains_key_info(self, sample_report):
        """
        Test that Slack format contains key report information.
        Validates: Requirements 4.5
        """
        formatted = sample_report.format_for_slack()
        
        assert formatted is not None
        assert len(formatted) > 0
        assert str(sample_report.trading_date) in formatted
        assert "AAPL" in formatted
        assert "BUY" in formatted.upper()
    
    def test_email_format_contains_key_info(self, sample_report):
        """
        Test that Email format contains key report information.
        Validates: Requirements 4.5
        """
        formatted = sample_report.format_for_email()
        
        assert formatted is not None
        assert len(formatted) > 0
        assert "<html>" in formatted.lower()
        assert str(sample_report.trading_date) in formatted
        assert "AAPL" in formatted
        assert "BUY" in formatted.upper()
    
    def test_empty_report_formatting(self):
        """
        Test formatting of report with no recommendations.
        Validates: Requirements 4.5
        """
        empty_report = DailyReport(
            report_id="empty-001",
            generation_time=datetime.now(),
            trading_date=date.today(),
            recommendations=[],
            market_summaries={}
        )
        
        telegram_format = empty_report.format_for_telegram()
        slack_format = empty_report.format_for_slack()
        email_format = empty_report.format_for_email()
        
        # All formats should handle empty reports gracefully
        assert telegram_format is not None and len(telegram_format) > 0
        assert slack_format is not None and len(slack_format) > 0
        assert email_format is not None and len(email_format) > 0


class TestDeliveryLogging:
    """Tests for delivery attempt logging."""
    
    @patch('stock_market_analysis.components.notification_service.requests.post')
    def test_successful_delivery_logged(self, mock_post, notification_service, config_manager, sample_report, caplog):
        """
        Test that successful deliveries are logged.
        Validates: Requirements 8.3
        """
        # Configure Telegram
        config_manager.set_telegram_config("test_bot_token_123456", ["123456789"])
        
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        # Deliver report
        with caplog.at_level('INFO'):
            notification_service.deliver_to_telegram(sample_report)
        
        # Check logs
        assert any("Telegram delivery successful" in record.message for record in caplog.records)
    
    @patch('stock_market_analysis.components.notification_service.requests.post')
    def test_failed_delivery_logged(self, mock_post, notification_service, config_manager, sample_report, caplog):
        """
        Test that failed deliveries are logged.
        Validates: Requirements 8.3
        """
        # Configure Telegram
        config_manager.set_telegram_config("test_bot_token_123456", ["123456789"])
        
        # Mock failed response
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_post.return_value = mock_response
        
        # Deliver report
        with caplog.at_level('ERROR'):
            notification_service.deliver_to_telegram(sample_report)
        
        # Check logs
        assert any("Telegram delivery failed" in record.message for record in caplog.records)
    
    @patch('stock_market_analysis.components.notification_service.smtplib.SMTP')
    @patch('stock_market_analysis.components.notification_service.requests.post')
    def test_delivery_result_summary_logged(self, mock_post, mock_smtp, notification_service, config_manager, sample_report, caplog):
        """
        Test that overall delivery result is logged.
        Validates: Requirements 8.3
        """
        # Configure all three channels
        config_manager.set_telegram_config("test_bot_token_123456", ["123456789"])
        config_manager.set_slack_config("https://hooks.slack.com/services/TEST/WEBHOOK", "#trading")
        smtp_config = SMTPConfig(
            host="smtp.gmail.com",
            port=587,
            username="test@example.com",
            password="test_password",
            use_tls=True
        )
        config_manager.set_email_config(smtp_config, ["recipient@example.com"])
        
        # Mock all successful
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        
        # Deliver report
        with caplog.at_level('INFO'):
            result = notification_service.deliver_report(sample_report)
        
        # Check logs for summary
        assert any("delivered successfully to all channels" in record.message for record in caplog.records)
