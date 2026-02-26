"""
Market data models for stock market analysis.
"""

from dataclasses import dataclass
from datetime import datetime, date
from decimal import Decimal
from typing import Dict, List, Any, Optional

from .market_region import MarketRegion


@dataclass
class MarketData:
    """Raw market data for a single stock."""
    
    symbol: str
    name: str  # Full company name
    region: MarketRegion
    timestamp: datetime
    open_price: Decimal
    close_price: Decimal
    high_price: Decimal
    low_price: Decimal
    volume: int
    additional_metrics: Dict[str, Any]  # Extensible for technical indicators


@dataclass
class MarketDataCollection:
    """Collection of market data from multiple regions."""
    
    collection_time: datetime
    data_by_region: Dict[MarketRegion, List[MarketData]]
    failed_regions: List[MarketRegion]  # Regions that failed to collect


@dataclass
class MarketSummary:
    """Summary information for a market region."""
    
    region: MarketRegion
    trading_date: date
    total_stocks_analyzed: int
    market_trend: str  # "bullish", "bearish", "neutral"
    notable_events: List[str]
    index_performance: Dict[str, Decimal]  # Index name -> performance percentage