"""
Configuration models for the stock market analysis system.
"""

from dataclasses import dataclass
from typing import List, Optional

from .market_region import MarketRegion


@dataclass
class TelegramConfig:
    """Telegram bot configuration."""
    
    bot_token: str
    chat_ids: List[str]


@dataclass
class SlackConfig:
    """Slack webhook configuration."""
    
    webhook_url: str
    channel: str


@dataclass
class SMTPConfig:
    """SMTP server configuration."""
    
    host: str
    port: int
    username: str
    password: str
    use_tls: bool


@dataclass
class EmailConfig:
    """Email delivery configuration."""
    
    smtp: SMTPConfig
    recipients: List[str]
    sender_address: str


@dataclass
class SystemConfiguration:
    """Complete system configuration."""
    
    market_regions: List[MarketRegion]
    telegram: Optional[TelegramConfig]
    slack: Optional[SlackConfig]
    email: Optional[EmailConfig]
    custom_schedule: Optional[str]  # Cron expression
    
    @staticmethod
    def get_default_regions() -> List[MarketRegion]:
        """Returns default regions: China, Hong Kong, USA."""
        return [MarketRegion.CHINA, MarketRegion.HONG_KONG, MarketRegion.USA]