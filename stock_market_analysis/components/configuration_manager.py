"""
Configuration Manager component for the stock market analysis system.

Manages market region settings and notification channel credentials.
"""

import json
import yaml
import logging
import re
from pathlib import Path
from typing import List, Optional, Union
from dataclasses import asdict

from ..models import (
    MarketRegion,
    TelegramConfig,
    SlackConfig,
    SMTPConfig,
    EmailConfig,
    SystemConfiguration
)


# Result type for operations that can fail
class Result:
    """Simple Result type for operations that can succeed or fail."""
    
    def __init__(self, success: bool, error: Optional[str] = None):
        self._success = success
        self._error = error
    
    def is_ok(self) -> bool:
        """Returns True if operation succeeded."""
        return self._success
    
    def is_err(self) -> bool:
        """Returns True if operation failed."""
        return not self._success
    
    def error(self) -> Optional[str]:
        """Returns error message if operation failed."""
        return self._error
    
    @staticmethod
    def ok() -> 'Result':
        """Creates a successful result."""
        return Result(True, None)
    
    @staticmethod
    def err(message: str) -> 'Result':
        """Creates a failed result with error message."""
        return Result(False, message)


class ConfigurationManager:
    """
    Manages system configuration including market regions and notification credentials.
    
    Responsibilities:
    - Manage market region configuration (add/remove)
    - Store notification channel credentials
    - Validate configuration changes
    - Persist settings across restarts
    - Apply changes to system within 60 seconds
    """
    
    def __init__(self, storage_path: Optional[Path] = None):
        """
        Initialize the Configuration Manager.
        
        Args:
            storage_path: Path to store configuration file. Defaults to config/default.yaml
        """
        self.logger = logging.getLogger(__name__)
        self.storage_path = storage_path or Path("config/default.yaml")
        
        # Initialize with default configuration
        self._configuration = SystemConfiguration(
            market_regions=SystemConfiguration.get_default_regions(),
            telegram=None,
            slack=None,
            email=None,
            custom_schedule=None
        )
        
        # Try to load existing configuration
        if self.storage_path.exists():
            try:
                self.load_configuration()
            except Exception as e:
                self.logger.warning(f"Failed to load configuration from {self.storage_path}: {e}")
                self.logger.info("Using default configuration")
    
    def add_market_region(self, region: MarketRegion) -> Result:
        """
        Adds a market region to monitoring list.
        
        Args:
            region: Market region to add
            
        Returns:
            Result indicating success or error message
        """
        if region in self._configuration.market_regions:
            return Result.err(f"Market region {region.value} is already configured")
        
        self._configuration.market_regions.append(region)
        self.logger.info(f"Added market region: {region.value}")
        
        return Result.ok()
    
    def remove_market_region(self, region: MarketRegion) -> Result:
        """
        Removes a market region from monitoring list.
        
        Args:
            region: Market region to remove
            
        Returns:
            Result with error message if removal would leave zero regions
        """
        if region not in self._configuration.market_regions:
            return Result.err(f"Market region {region.value} is not configured")
        
        # Validate that at least one region remains
        if len(self._configuration.market_regions) <= 1:
            return Result.err("Cannot remove last market region. At least one region must be configured")
        
        self._configuration.market_regions.remove(region)
        self.logger.info(f"Removed market region: {region.value}")
        
        return Result.ok()
    
    def get_configured_regions(self) -> List[MarketRegion]:
        """
        Returns list of configured market regions.
        
        Returns default regions (China, Hong Kong, USA) if none configured.
        """
        if not self._configuration.market_regions:
            return SystemConfiguration.get_default_regions()
        return self._configuration.market_regions.copy()
    
    def set_telegram_config(self, bot_token: str, chat_ids: List[str]) -> Result:
        """
        Validates and stores Telegram configuration.
        
        Args:
            bot_token: Telegram bot token
            chat_ids: List of chat IDs to send messages to
            
        Returns:
            Result indicating success or validation error
        """
        # Validate bot token
        if not bot_token or len(bot_token) < 10:
            return Result.err("Invalid bot token: must be at least 10 characters")
        
        # Validate chat IDs
        if not chat_ids or len(chat_ids) == 0:
            return Result.err("Invalid chat IDs: at least one chat ID required")
        
        for chat_id in chat_ids:
            # Chat IDs can be numeric or start with - for groups
            if not (chat_id.lstrip('-').isdigit()):
                return Result.err(f"Invalid chat ID format: {chat_id}")
        
        self._configuration.telegram = TelegramConfig(bot_token, chat_ids)
        self.logger.info(f"Telegram configuration updated with {len(chat_ids)} chat IDs")
        
        return Result.ok()
    
    def set_slack_config(self, webhook_url: str, channel: str) -> Result:
        """
        Validates and stores Slack configuration.
        
        Args:
            webhook_url: Slack webhook URL
            channel: Slack channel name
            
        Returns:
            Result indicating success or validation error
        """
        # Validate webhook URL
        if not webhook_url or not webhook_url.startswith("https://hooks.slack.com/"):
            return Result.err("Invalid webhook URL: must be a valid Slack webhook URL")
        
        # Validate channel name
        if not channel or len(channel) < 1:
            return Result.err("Invalid channel: channel name required")
        
        # Channel should start with # or be a valid channel name
        if not (channel.startswith('#') or channel.startswith('@') or channel.replace('-', '').replace('_', '').isalnum()):
            return Result.err(f"Invalid channel format: {channel}")
        
        self._configuration.slack = SlackConfig(webhook_url, channel)
        self.logger.info(f"Slack configuration updated for channel: {channel}")
        
        return Result.ok()
    
    def set_email_config(self, smtp_settings: SMTPConfig, recipients: List[str]) -> Result:
        """
        Validates and stores Email configuration.
        
        Args:
            smtp_settings: SMTP server configuration
            recipients: List of recipient email addresses
            
        Returns:
            Result indicating success or validation error
        """
        # Validate SMTP settings
        if not smtp_settings.host or len(smtp_settings.host) < 3:
            return Result.err("Invalid SMTP host: must be at least 3 characters")
        
        if smtp_settings.port < 1 or smtp_settings.port > 65535:
            return Result.err(f"Invalid SMTP port: must be between 1 and 65535, got {smtp_settings.port}")
        
        if not smtp_settings.username:
            return Result.err("Invalid SMTP username: username required")
        
        if not smtp_settings.password:
            return Result.err("Invalid SMTP password: password required")
        
        # Validate recipients
        if not recipients or len(recipients) == 0:
            return Result.err("Invalid recipients: at least one recipient email required")
        
        # Simple email validation
        email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        for recipient in recipients:
            if not email_pattern.match(recipient):
                return Result.err(f"Invalid email format: {recipient}")
        
        # Determine sender address (use username if it's an email, otherwise construct one)
        sender_address = smtp_settings.username
        if not email_pattern.match(sender_address):
            sender_address = f"{smtp_settings.username}@{smtp_settings.host}"
        
        self._configuration.email = EmailConfig(smtp_settings, recipients, sender_address)
        self.logger.info(f"Email configuration updated with {len(recipients)} recipients")
        
        return Result.ok()
    
    def get_telegram_config(self) -> Optional[TelegramConfig]:
        """Returns Telegram configuration if set."""
        return self._configuration.telegram
    
    def get_slack_config(self) -> Optional[SlackConfig]:
        """Returns Slack configuration if set."""
        return self._configuration.slack
    
    def get_email_config(self) -> Optional[EmailConfig]:
        """Returns Email configuration if set."""
        return self._configuration.email
    
    def get_configuration(self) -> SystemConfiguration:
        """Returns the complete system configuration."""
        return self._configuration
    
    def set_configuration(self, config: SystemConfiguration) -> None:
        """
        Sets the complete system configuration.
        
        Args:
            config: System configuration to set
        """
        self._configuration = config
        self.logger.info("System configuration updated")
    
    def persist_configuration(self) -> None:
        """
        Saves configuration to persistent storage.
        
        Configuration is saved as YAML or JSON based on file extension.
        """
        try:
            # Ensure directory exists
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Convert configuration to dictionary
            config_dict = {
                'market_regions': [region.value for region in self._configuration.market_regions],
                'telegram': asdict(self._configuration.telegram) if self._configuration.telegram else None,
                'slack': asdict(self._configuration.slack) if self._configuration.slack else None,
                'email': self._convert_email_config_to_dict(self._configuration.email) if self._configuration.email else None,
                'custom_schedule': self._configuration.custom_schedule
            }
            
            # Determine format based on file extension
            file_extension = self.storage_path.suffix.lower()
            
            # Write to file
            with open(self.storage_path, 'w') as f:
                if file_extension in ['.yaml', '.yml']:
                    yaml.dump(config_dict, f, default_flow_style=False, sort_keys=False)
                else:
                    # Default to JSON
                    json.dump(config_dict, f, indent=2)
            
            self.logger.info(f"Configuration persisted to {self.storage_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to persist configuration: {e}")
            raise
    
    def load_configuration(self) -> None:
        """
        Loads configuration from persistent storage.
        
        Supports both YAML and JSON formats based on file extension.
        If file doesn't exist or is invalid, keeps current configuration.
        """
        try:
            if not self.storage_path.exists():
                self.logger.warning(f"Configuration file not found: {self.storage_path}")
                return
            
            # Determine format based on file extension
            file_extension = self.storage_path.suffix.lower()
            
            with open(self.storage_path, 'r') as f:
                if file_extension in ['.yaml', '.yml']:
                    config_dict = yaml.safe_load(f)
                else:
                    # Default to JSON
                    config_dict = json.load(f)
            
            # Handle empty or None config
            if not config_dict:
                self.logger.warning("Configuration file is empty, using defaults")
                return
            
            # Parse market regions
            market_regions = []
            if config_dict.get('market_regions'):
                market_regions = [
                    MarketRegion(region_str) 
                    for region_str in config_dict['market_regions']
                ]
            
            # Parse telegram config
            telegram = None
            # Support nested notifications structure from YAML
            notifications = config_dict.get('notifications', {})
            telegram_dict = notifications.get('telegram') or config_dict.get('telegram')
            
            if telegram_dict:
                # Support both YAML format (with 'enabled') and direct format (without 'enabled')
                if isinstance(telegram_dict, dict):
                    # Check if this is enabled (YAML format) or always load (direct format)
                    if telegram_dict.get('enabled', True) and telegram_dict.get('bot_token'):
                        # Convert chat_ids to strings if they're integers
                        chat_ids = telegram_dict.get('chat_ids', [])
                        chat_ids = [str(cid) for cid in chat_ids]
                        telegram = TelegramConfig(
                            bot_token=telegram_dict['bot_token'],
                            chat_ids=chat_ids
                        )
            
            # Parse slack config
            slack = None
            slack_dict = notifications.get('slack') or config_dict.get('slack')
            
            if slack_dict:
                # Support both YAML format (with 'enabled') and direct format (without 'enabled')
                if isinstance(slack_dict, dict):
                    if slack_dict.get('enabled', True) and slack_dict.get('webhook_url'):
                        slack = SlackConfig(
                            webhook_url=slack_dict['webhook_url'],
                            channel=slack_dict.get('channel', '')
                        )
            
            # Parse email config
            email = None
            email_dict = notifications.get('email') or config_dict.get('email')
            
            if email_dict:
                # Support both YAML format (with 'enabled') and direct format (without 'enabled')
                if isinstance(email_dict, dict):
                    if email_dict.get('enabled', True) and email_dict.get('smtp'):
                        email = self._parse_email_config_from_dict(email_dict)
            
            # Create configuration
            self._configuration = SystemConfiguration(
                market_regions=market_regions if market_regions else SystemConfiguration.get_default_regions(),
                telegram=telegram,
                slack=slack,
                email=email,
                custom_schedule=config_dict.get('custom_schedule')
            )
            
            self.logger.info(f"Configuration loaded from {self.storage_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
            raise
    
    def _convert_email_config_to_dict(self, email_config: EmailConfig) -> dict:
        """Converts EmailConfig to dictionary for serialization."""
        return {
            'smtp': asdict(email_config.smtp),
            'recipients': email_config.recipients,
            'sender_address': email_config.sender_address
        }
    
    def _parse_email_config_from_dict(self, email_dict: dict) -> EmailConfig:
        """Parses EmailConfig from dictionary."""
        smtp_dict = email_dict['smtp']
        smtp = SMTPConfig(
            host=smtp_dict['host'],
            port=smtp_dict['port'],
            username=smtp_dict['username'],
            password=smtp_dict['password'],
            use_tls=smtp_dict.get('use_tls', True)
        )
        return EmailConfig(
            smtp=smtp,
            recipients=email_dict['recipients'],
            sender_address=email_dict.get('sender_address', smtp_dict['username'])
        )

    def get_trading_config(self) -> dict:
        """
        Returns trading configuration.
        
        Returns:
            Dictionary with trading configuration
        """
        try:
            if not self.storage_path.exists():
                return self._get_default_trading_config()
            
            file_extension = self.storage_path.suffix.lower()
            
            with open(self.storage_path, 'r') as f:
                if file_extension in ['.yaml', '.yml']:
                    config_dict = yaml.safe_load(f)
                else:
                    config_dict = json.load(f)
            
            if not config_dict or 'trading' not in config_dict:
                return self._get_default_trading_config()
            
            trading_config = config_dict['trading']
            
            # Validate configuration
            self._validate_trading_config(trading_config)
            
            return trading_config
            
        except Exception as e:
            self.logger.warning(f"Failed to load trading config: {e}, using defaults")
            return self._get_default_trading_config()
    
    def get_initial_cash_balance(self) -> float:
        """Returns initial cash balance for new portfolios."""
        config = self.get_trading_config()
        return config.get('initial_cash_balance', 100000.00)
    
    def get_confidence_threshold(self) -> float:
        """Returns confidence threshold for trade execution."""
        config = self.get_trading_config()
        return config.get('confidence_threshold', 0.70)
    
    def get_position_sizing_config(self) -> dict:
        """
        Returns position sizing configuration.
        
        Returns:
            Dictionary with 'strategy' and 'value' keys
        """
        config = self.get_trading_config()
        return {
            'strategy': config.get('position_sizing_strategy', 'percentage'),
            'value': config.get('position_size_value', 0.10)
        }
    
    def _get_default_trading_config(self) -> dict:
        """Returns default trading configuration."""
        return {
            'initial_cash_balance': 100000.00,
            'confidence_threshold': 0.70,
            'position_sizing_strategy': 'percentage',
            'position_size_value': 0.10
        }
    
    def _validate_trading_config(self, config: dict) -> None:
        """
        Validates trading configuration.
        
        Args:
            config: Trading configuration dictionary
            
        Raises:
            ValueError: If configuration is invalid
        """
        # Validate confidence threshold
        if 'confidence_threshold' in config:
            threshold = config['confidence_threshold']
            if not isinstance(threshold, (int, float)) or threshold < 0.0 or threshold > 1.0:
                raise ValueError(
                    f"Invalid confidence_threshold: must be between 0.0 and 1.0, got {threshold}"
                )
        
        # Validate position sizing strategy
        if 'position_sizing_strategy' in config:
            strategy = config['position_sizing_strategy']
            if strategy not in ['fixed_amount', 'percentage']:
                raise ValueError(
                    f"Invalid position_sizing_strategy: must be 'fixed_amount' or 'percentage', got {strategy}"
                )
        
        # Validate position size value
        if 'position_size_value' in config:
            value = config['position_size_value']
            if not isinstance(value, (int, float)) or value <= 0:
                raise ValueError(
                    f"Invalid position_size_value: must be positive, got {value}"
                )
            
            # Additional validation for percentage strategy
            strategy = config.get('position_sizing_strategy', 'percentage')
            if strategy == 'percentage' and (value < 0.01 or value > 1.0):
                raise ValueError(
                    f"Invalid position_size_value for percentage strategy: "
                    f"must be between 0.01 and 1.0, got {value}"
                )
