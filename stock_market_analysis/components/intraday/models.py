"""
Data models for intraday market monitoring.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from stock_market_analysis.models.market_region import MarketRegion


@dataclass
class AnalysisCycleResult:
    """Result of an analysis cycle execution."""
    
    success: bool
    region: MarketRegion
    start_time: datetime
    end_time: datetime
    recommendations_count: int
    trades_executed: int
    error_message: Optional[str] = None
    
    @property
    def duration_seconds(self) -> float:
        """Calculate cycle duration in seconds."""
        return (self.end_time - self.start_time).total_seconds()


@dataclass
class MonitoringStatus:
    """Current status of intraday monitoring for a region."""
    
    region: MarketRegion
    is_active: bool
    is_paused: bool
    pause_reason: Optional[str]
    pause_until: Optional[datetime]
    last_cycle_time: Optional[datetime]
    next_cycle_time: Optional[datetime]
    consecutive_failures: int
    total_cycles_today: int
