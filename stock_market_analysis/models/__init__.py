"""
Core data models for the Stock Market Analysis system.
"""

from .market_region import MarketRegion
from .market_data import MarketData, MarketDataCollection, MarketSummary
from .recommendation import StockRecommendation, RecommendationType
from .report import DailyReport
from .configuration import (
    TelegramConfig,
    SlackConfig,
    SMTPConfig,
    EmailConfig,
    SystemConfiguration
)
from .results import AnalysisResult, DeliveryResult

__all__ = [
    "MarketRegion",
    "MarketData",
    "MarketDataCollection", 
    "MarketSummary",
    "StockRecommendation",
    "RecommendationType",
    "DailyReport",
    "TelegramConfig",
    "SlackConfig",
    "SMTPConfig",
    "EmailConfig",
    "SystemConfiguration",
    "AnalysisResult",
    "DeliveryResult"
]