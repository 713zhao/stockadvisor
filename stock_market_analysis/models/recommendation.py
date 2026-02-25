"""
Stock recommendation models.
"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional

from .market_region import MarketRegion


class RecommendationType(Enum):
    """Type of stock recommendation."""
    
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"


@dataclass
class StockRecommendation:
    """A buy/sell/hold recommendation with supporting analysis."""
    
    symbol: str
    region: MarketRegion
    recommendation_type: RecommendationType
    rationale: str  # Human-readable explanation
    risk_assessment: str  # Risk level and factors
    confidence_score: float  # 0.0 to 1.0
    target_price: Optional[Decimal]
    generated_at: datetime