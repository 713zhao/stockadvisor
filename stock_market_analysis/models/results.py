"""
Result models for operations in the stock market analysis system.
"""

from dataclasses import dataclass
from typing import List, Optional, Dict

from .recommendation import StockRecommendation


@dataclass
class AnalysisResult:
    """Result of analysis execution."""
    
    success: bool
    recommendations: List[StockRecommendation]
    error_message: Optional[str]
    retry_count: int


@dataclass
class DeliveryResult:
    """Result of report delivery through multiple channels."""
    
    telegram_success: bool
    slack_success: bool
    email_success: bool
    errors: Dict[str, str]  # Channel name -> error message
    
    def all_succeeded(self) -> bool:
        """Returns True if all channels delivered successfully."""
        return self.telegram_success and self.slack_success and self.email_success
    
    def any_succeeded(self) -> bool:
        """Returns True if at least one channel delivered successfully."""
        return self.telegram_success or self.slack_success or self.email_success