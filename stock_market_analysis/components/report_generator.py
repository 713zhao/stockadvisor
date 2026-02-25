"""
Report Generator component for the stock market analysis system.

Compiles daily reports from recommendations and market summaries.
"""

import logging
import uuid
from datetime import datetime, date
from typing import List, Dict

from ..models import (
    StockRecommendation,
    MarketSummary,
    DailyReport,
    MarketRegion
)


class ReportGenerator:
    """
    Generates comprehensive daily reports from analysis results.
    
    Responsibilities:
    - Compile daily reports from recommendations
    - Include market summaries
    - Add generation timestamps
    - Handle zero-recommendation scenarios
    """
    
    def __init__(self):
        """Initialize the Report Generator."""
        self.logger = logging.getLogger(__name__)
    
    def generate_daily_report(
        self, 
        recommendations: List[StockRecommendation], 
        market_summaries: Dict[MarketRegion, MarketSummary]
    ) -> DailyReport:
        """
        Generates a comprehensive daily report.
        
        Args:
            recommendations: List of stock recommendations for the day
            market_summaries: Summary information for each market region
            
        Returns:
            DailyReport with all recommendations and summaries
            
        Note:
            Creates report even when recommendations list is empty
        """
        generation_time = datetime.now()
        trading_date = date.today()
        report_id = self._generate_report_id(trading_date)
        
        self.logger.info(
            f"Generating daily report for {trading_date} with "
            f"{len(recommendations)} recommendations and "
            f"{len(market_summaries)} market summaries"
        )
        
        # Log if no recommendations
        if len(recommendations) == 0:
            self.logger.info("Report contains no recommendations")
        
        # Create the daily report
        report = DailyReport(
            report_id=report_id,
            generation_time=generation_time,
            trading_date=trading_date,
            recommendations=recommendations,
            market_summaries=market_summaries
        )
        
        self.logger.info(f"Daily report generated successfully: {report_id}")
        
        return report
    
    def _generate_report_id(self, trading_date: date) -> str:
        """
        Generates a unique report identifier.
        
        Args:
            trading_date: The trading date for the report
            
        Returns:
            Unique report ID string
        """
        # Format: REPORT-YYYYMMDD-UUID
        date_str = trading_date.strftime("%Y%m%d")
        unique_id = str(uuid.uuid4())[:8]
        return f"REPORT-{date_str}-{unique_id}"
