"""
Unit tests for Configuration_Manager component.
"""

import pytest
import json
from pathlib import Path
from stock_market_analysis.components import ConfigurationManager, Result
from stock_market_analysis.models import (
    MarketRegion,
    TelegramConfig,
    SlackConfig,
    SMTPConfig,
    EmailConfig,
    SystemConfiguration
)


class TestConfigurationManager:
    """Unit tests for ConfigurationManager."""
    
    def test_initialization_with_defaults(self):
        """Test that ConfigurationManager initializes with default regions."""
        manager = ConfigurationManager()
        regions = manager.get_configured_regions()
        
        assert len(regions) == 3
        assert MarketRegion.CHINA in regions
        assert MarketRegion.HONG_KONG in regions
        assert MarketRegion.USA in regions
    
    def test_add_market_region_success(self):
        """Test successfully adding a new market region."""
        manager = ConfigurationManager()
        
        # Remove all default regions first
        for region in [MarketRegion.CHINA, MarketRegion.HONG_KONG]:
            manager.remove_market_region(region)
        
        # Now add a region back
        result = manager.add_market_region(MarketRegion.CHINA)
        
        assert result.is_ok()
        assert MarketRegion.CHINA in manager.get_configured_regions()
    
    def test_add_duplicate_market_region(self):
        """Test that adding a duplicate region returns an error."""
        manager = ConfigurationManager()
        
        # Try to add a region that's already in defaults
        result = manager.add_market_region(MarketRegion.USA)
        
        assert result.is_err()
        assert "already configured" in result.error()
    
    def test_remove_market_region_success(self):
        """Test successfully removing a market region."""
        manager = ConfigurationManager()
        
        result = manager.remove_market_region(MarketRegion.USA)
        
        assert result.is_ok()
        assert MarketRegion.USA not in manager.get_configured_regions()
        assert len(manager.get_configured_regions()) == 2
    
    def test_cannot_remove_last_market_region(self):
        """
        Test that removing the last market region is prevented.
        Validates: Requirement 5.3
        """
        manager = ConfigurationManager()
        
        # Remove all but one region
        manager.remove_market_region(MarketRegion.CHINA)
        manager.remove_market_region(MarketRegion.HONG_KONG)
        
        # Try to remove the last region
        result = manager.remove_market_region(MarketRegion.USA)
        
        assert result.is_err()
        assert "at least one" in result.error().lower()
        assert MarketRegion.USA in manager.get_configured_regions()
    
    def test_remove_nonexistent_region(self):
        """Test that removing a non-configured region returns an error."""
        manager = ConfigurationManager()
        
        # Remove a region first
        manager.remove_market_region(MarketRegion.USA)
        
        # Try to remove it again
        result = manager.remove_market_region(MarketRegion.USA)
        
        assert result.is_err()
        assert "not configured" in result.error()
    
    def test_set_telegram_config_success(self):
        """Test successfully setting Telegram configuration."""
        manager = ConfigurationManager()
        
        result = manager.set_telegram_config(
            bot_token="1234567890:ABCdefGHIjklMNOpqrsTUVwxyz",
            chat_ids=["123456789", "-987654321"]
        )
        
        assert result.is_ok()
        
        config = manager.get_telegram_config()
        assert config is not None
        assert config.bot_token == "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
        assert len(config.chat_ids) == 2
    
    def test_set_telegram_config_invalid_token(self):
        """Test that invalid bot token is rejected."""
        manager = ConfigurationManager()
        
        result = manager.set_telegram_config(
            bot_token="short",
            chat_ids=["123456789"]
        )
        
        assert result.is_err()
        assert "bot token" in result.error().lower()
    
    def test_set_telegram_config_empty_chat_ids(self):
        """Test that empty chat IDs list is rejected."""
        manager = ConfigurationManager()
        
        result = manager.set_telegram_config(
            bot_token="1234567890:ABCdefGHIjklMNOpqrsTUVwxyz",
            chat_ids=[]
        )
        
        assert result.is_err()
        assert "chat id" in result.error().lower()
    
    def test_set_telegram_config_invalid_chat_id_format(self):
        """Test that invalid chat ID format is rejected."""
        manager = ConfigurationManager()
        
        result = manager.set_telegram_config(
            bot_token="1234567890:ABCdefGHIjklMNOpqrsTUVwxyz",
            chat_ids=["invalid_chat_id"]
        )
        
        assert result.is_err()
        assert "invalid chat id format" in result.error().lower()
    
    def test_set_slack_config_success(self):
        """Test successfully setting Slack configuration."""
        manager = ConfigurationManager()
        
        result = manager.set_slack_config(
            webhook_url="https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXX",
            channel="#general"
        )
        
        assert result.is_ok()
        
        config = manager.get_slack_config()
        assert config is not None
        assert config.webhook_url.startswith("https://hooks.slack.com/")
        assert config.channel == "#general"
    
    def test_set_slack_config_invalid_webhook(self):
        """Test that invalid webhook URL is rejected."""
        manager = ConfigurationManager()
        
        result = manager.set_slack_config(
            webhook_url="https://invalid.com/webhook",
            channel="#general"
        )
        
        assert result.is_err()
        assert "webhook" in result.error().lower()
    
    def test_set_slack_config_invalid_channel(self):
        """Test that invalid channel name is rejected."""
        manager = ConfigurationManager()
        
        result = manager.set_slack_config(
            webhook_url="https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXX",
            channel=""
        )
        
        assert result.is_err()
        assert "channel" in result.error().lower()
    
    def test_set_email_config_success(self):
        """Test successfully setting Email configuration."""
        manager = ConfigurationManager()
        
        smtp = SMTPConfig(
            host="smtp.gmail.com",
            port=587,
            username="test@example.com",
            password="password123",
            use_tls=True
        )
        
        result = manager.set_email_config(
            smtp_settings=smtp,
            recipients=["recipient1@example.com", "recipient2@example.com"]
        )
        
        assert result.is_ok()
        
        config = manager.get_email_config()
        assert config is not None
        assert config.smtp.host == "smtp.gmail.com"
        assert len(config.recipients) == 2
    
    def test_set_email_config_invalid_smtp_host(self):
        """Test that invalid SMTP host is rejected."""
        manager = ConfigurationManager()
        
        smtp = SMTPConfig(
            host="ab",
            port=587,
            username="test@example.com",
            password="password123",
            use_tls=True
        )
        
        result = manager.set_email_config(
            smtp_settings=smtp,
            recipients=["recipient@example.com"]
        )
        
        assert result.is_err()
        assert "smtp host" in result.error().lower()
    
    def test_set_email_config_invalid_port(self):
        """Test that invalid SMTP port is rejected."""
        manager = ConfigurationManager()
        
        smtp = SMTPConfig(
            host="smtp.gmail.com",
            port=99999,
            username="test@example.com",
            password="password123",
            use_tls=True
        )
        
        result = manager.set_email_config(
            smtp_settings=smtp,
            recipients=["recipient@example.com"]
        )
        
        assert result.is_err()
        assert "port" in result.error().lower()
    
    def test_set_email_config_empty_recipients(self):
        """Test that empty recipients list is rejected."""
        manager = ConfigurationManager()
        
        smtp = SMTPConfig(
            host="smtp.gmail.com",
            port=587,
            username="test@example.com",
            password="password123",
            use_tls=True
        )
        
        result = manager.set_email_config(
            smtp_settings=smtp,
            recipients=[]
        )
        
        assert result.is_err()
        assert "recipient" in result.error().lower()
    
    def test_set_email_config_invalid_email_format(self):
        """Test that invalid email format is rejected."""
        manager = ConfigurationManager()
        
        smtp = SMTPConfig(
            host="smtp.gmail.com",
            port=587,
            username="test@example.com",
            password="password123",
            use_tls=True
        )
        
        result = manager.set_email_config(
            smtp_settings=smtp,
            recipients=["invalid-email"]
        )
        
        assert result.is_err()
        assert "email format" in result.error().lower()
    
    def test_persist_and_load_configuration(self, tmp_path):
        """
        Test that configuration can be persisted and loaded.
        Validates: Requirement 5.5
        """
        config_file = tmp_path / "test_config.json"
        manager = ConfigurationManager(storage_path=config_file)
        
        # Configure the manager
        manager.add_market_region(MarketRegion.CHINA)
        manager.set_telegram_config(
            bot_token="1234567890:ABCdefGHIjklMNOpqrsTUVwxyz",
            chat_ids=["123456789"]
        )
        
        # Persist configuration
        manager.persist_configuration()
        
        # Create new manager and load
        new_manager = ConfigurationManager(storage_path=config_file)
        new_manager.load_configuration()
        
        # Verify configuration was loaded
        regions = new_manager.get_configured_regions()
        assert MarketRegion.CHINA in regions
        
        telegram = new_manager.get_telegram_config()
        assert telegram is not None
        assert telegram.bot_token == "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
    
    def test_load_nonexistent_configuration(self, tmp_path):
        """Test that loading from nonexistent file keeps defaults."""
        config_file = tmp_path / "nonexistent.json"
        manager = ConfigurationManager(storage_path=config_file)
        
        # Should have default regions
        regions = manager.get_configured_regions()
        assert len(regions) == 3
    
    def test_configuration_round_trip_with_all_settings(self, tmp_path):
        """Test complete configuration persistence round-trip."""
        config_file = tmp_path / "full_config.json"
        manager = ConfigurationManager(storage_path=config_file)
        
        # Configure all settings
        manager.set_telegram_config(
            bot_token="1234567890:ABCdefGHIjklMNOpqrsTUVwxyz",
            chat_ids=["123456789"]
        )
        manager.set_slack_config(
            webhook_url="https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXX",
            channel="#trading"
        )
        smtp = SMTPConfig(
            host="smtp.gmail.com",
            port=587,
            username="test@example.com",
            password="password123",
            use_tls=True
        )
        manager.set_email_config(
            smtp_settings=smtp,
            recipients=["trader@example.com"]
        )
        
        # Persist and reload
        manager.persist_configuration()
        
        new_manager = ConfigurationManager(storage_path=config_file)
        new_manager.load_configuration()
        
        # Verify all settings
        assert new_manager.get_telegram_config() is not None
        assert new_manager.get_slack_config() is not None
        assert new_manager.get_email_config() is not None
        assert len(new_manager.get_configured_regions()) == 3
