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
    name: str  # Full company name
    region: MarketRegion
    recommendation_type: RecommendationType
    rationale: str  # Human-readable explanation
    risk_assessment: str  # Risk level and factors
    confidence_score: float  # 0.0 to 1.0
    target_price: Optional[Decimal]
    generated_at: datetime
    
    def get_stock_url(self) -> str:
        """Generate URL to view stock details based on region."""
        if self.region == MarketRegion.USA:
            return f"https://finance.yahoo.com/quote/{self.symbol}"
        elif self.region == MarketRegion.HONG_KONG:
            # Remove .HK suffix for Yahoo Finance
            clean_symbol = self.symbol.replace('.HK', '')
            return f"https://finance.yahoo.com/quote/{clean_symbol}.HK"
        elif self.region == MarketRegion.CHINA:
            # Remove .SS suffix for Yahoo Finance
            clean_symbol = self.symbol.replace('.SS', '')
            return f"https://finance.yahoo.com/quote/{clean_symbol}.SS"
        else:
            return f"https://finance.yahoo.com/quote/{self.symbol}"