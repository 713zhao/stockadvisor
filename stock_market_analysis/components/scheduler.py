"""
Scheduler component for the stock market analysis system.

This module provides scheduling functionality for automated daily analysis execution.
"""

import logging
from datetime import datetime, time
from typing import List, Optional, Callable
from croniter import croniter

from ..models.market_region import MarketRegion
from ..models.results import AnalysisResult


class Scheduler:
    """
    Scheduler for automated analysis execution.
    
    Responsibilities:
    - Trigger daily analysis execution
    - Respect market close times
    - Support custom schedules (cron expressions)
    """
    
    # Default market close times (in UTC)
    MARKET_CLOSE_TIMES = {
        MarketRegion.CHINA: time(7, 0),      # 15:00 CST = 07:00 UTC
        MarketRegion.HONG_KONG: time(8, 0),  # 16:00 HKT = 08:00 UTC
        MarketRegion.USA: time(21, 0),       # 16:00 EST = 21:00 UTC (winter)
    }
    
    def __init__(
        self,
        analysis_executor: Optional[Callable[[Optional[List[MarketRegion]]], AnalysisResult]] = None,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize the Scheduler.
        
        Args:
            analysis_executor: Callable that executes analysis (typically Analysis_Engine.execute_scheduled_analysis)
            logger: Optional logger instance
        """
        self.analysis_executor = analysis_executor
        self.logger = logger or logging.getLogger(__name__)
        self.custom_schedule: Optional[str] = None
        self._scheduled_regions: List[MarketRegion] = []
    
    def schedule_daily_analysis(self, market_regions: List[MarketRegion]) -> None:
        """
        Schedules analysis to run after market close for each region.
        
        This method configures the scheduler to execute analysis after the latest
        market close time among the configured regions.
        
        Args:
            market_regions: Regions to consider for scheduling
            
        Note:
            In a production system, this would integrate with a task scheduler
            like APScheduler, Celery, or system cron. For this implementation,
            it stores the configuration for later execution.
        """
        if not market_regions:
            self.logger.warning("No market regions provided for scheduling")
            return
        
        self._scheduled_regions = market_regions
        
        # Find the latest market close time
        latest_close_time = self._get_latest_close_time(market_regions)
        
        self.logger.info(
            f"Scheduled daily analysis for regions: {[r.value for r in market_regions]}, "
            f"execution time: {latest_close_time}"
        )
    
    def set_custom_schedule(self, cron_expression: str) -> 'Result':
        """
        Sets a custom schedule for analysis execution.
        
        Args:
            cron_expression: Cron-style schedule expression
            
        Returns:
            Result indicating success or validation error
            
        Example cron expressions:
            "0 21 * * *" - Daily at 21:00 UTC
            "0 9,21 * * *" - Daily at 9:00 and 21:00 UTC
            "0 21 * * 1-5" - Weekdays at 21:00 UTC
        """
        # Import Result here to avoid circular imports
        from .configuration_manager import Result
        
        if not cron_expression or not cron_expression.strip():
            return Result.err("Cron expression cannot be empty")
        
        # Validate cron expression
        try:
            # Test if croniter can parse the expression
            base_time = datetime.now()
            cron = croniter(cron_expression, base_time)
            # Try to get next execution time to validate
            next_time = cron.get_next(datetime)
            
            self.custom_schedule = cron_expression
            self.logger.info(
                f"Custom schedule set: {cron_expression}, "
                f"next execution: {next_time}"
            )
            
            return Result.ok()
            
        except (ValueError, KeyError) as e:
            error_msg = f"Invalid cron expression: {str(e)}"
            self.logger.error(error_msg)
            return Result.err(error_msg)
    
    def get_next_execution_time(self) -> Optional[datetime]:
        """
        Gets the next scheduled execution time.
        
        Returns:
            Next execution datetime, or None if no schedule is configured
        """
        if self.custom_schedule:
            try:
                cron = croniter(self.custom_schedule, datetime.now())
                return cron.get_next(datetime)
            except Exception as e:
                self.logger.error(f"Error calculating next execution time: {e}")
                return None
        
        if self._scheduled_regions:
            # Calculate next execution based on market close times
            latest_close_time = self._get_latest_close_time(self._scheduled_regions)
            now = datetime.now()
            next_execution = datetime.combine(now.date(), latest_close_time)
            
            # If the time has passed today, schedule for tomorrow
            if next_execution <= now:
                from datetime import timedelta
                next_execution += timedelta(days=1)
            
            return next_execution
        
        return None
    
    def execute_now(self, regions: Optional[List[MarketRegion]] = None) -> AnalysisResult:
        """
        Executes analysis immediately.
        
        Args:
            regions: Optional list of regions to analyze. If None, uses scheduled regions.
            
        Returns:
            AnalysisResult from the analysis execution
            
        Raises:
            ValueError: If no analysis executor is configured
        """
        if self.analysis_executor is None:
            raise ValueError("No analysis executor configured")
        
        regions_to_analyze = regions or self._scheduled_regions
        
        if not regions_to_analyze:
            self.logger.warning("No regions specified for analysis execution")
            # Return empty result
            return AnalysisResult(
                success=True,
                recommendations=[],
                error_message="No regions specified",
                retry_count=0
            )
        
        self.logger.info(f"Executing analysis for regions: {[r.value for r in regions_to_analyze]}")
        
        try:
            result = self.analysis_executor(regions_to_analyze)
            
            if result.success:
                self.logger.info(
                    f"Analysis completed successfully: "
                    f"{len(result.recommendations)} recommendations generated"
                )
            else:
                self.logger.error(f"Analysis failed: {result.error_message}")
            
            return result
            
        except Exception as e:
            error_msg = f"Analysis execution failed with exception: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            
            return AnalysisResult(
                success=False,
                recommendations=[],
                error_message=error_msg,
                retry_count=0
            )
    
    def _get_latest_close_time(self, regions: List[MarketRegion]) -> time:
        """
        Gets the latest market close time among the given regions.
        
        Args:
            regions: List of market regions
            
        Returns:
            Latest close time as a time object
        """
        close_times = [
            self.MARKET_CLOSE_TIMES.get(region, time(21, 0))
            for region in regions
        ]
        
        # Return the latest time
        return max(close_times)
    
    def get_market_close_time(self, region: MarketRegion) -> time:
        """
        Gets the market close time for a specific region.
        
        Args:
            region: Market region
            
        Returns:
            Market close time for the region
        """
        return self.MARKET_CLOSE_TIMES.get(region, time(21, 0))
