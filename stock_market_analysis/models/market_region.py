"""
Market region enumeration for stock market analysis.
"""

from enum import Enum


class MarketRegion(Enum):
    """Represents a geographic stock market area."""
    
    CHINA = "china"
    HONG_KONG = "hong_kong"
    USA = "usa"
    # Extensible for additional regions