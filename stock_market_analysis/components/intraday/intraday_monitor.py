"""
Intraday market monitoring coordinator.

Schedules and executes hourly analysis cycles during market hours
across multiple regional markets.
"""

import logging
import threading
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from collections import defaultdict

from stock_market_analysis.models.market_region import MarketRegion
from stock_market_analysis.components.analysis_engine import AnalysisEngine
from stock_market_analysis.components.configuration_manager import ConfigurationManager
from stock_market_analysis.trading.trade_executor import TradeExecutor
from .market_hours_detector import MarketHoursDetector
from .models import AnalysisCycleResult, MonitoringStatus


class IntradayMonitor:
    """
    Coordinates hourly market monitoring and analysis during trading hours.
    
    Manages separate monitoring loops for each regional market, executes
    analysis cycles at configured intervals, and handles errors with
    circuit breaker logic.
    """
    
    def __init__(
        self,
        market_hours_detector: MarketHoursDetector,
        analysis_engine: AnalysisEngine,
        trade_executor: TradeExecutor,
        config_manager: ConfigurationManager,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize the intraday monitor.
        
        Args:
            market_hours_detector: Detector for market hours and holidays
            analysis_engine: Engine for stock analysis
            trade_executor: Executor for trade operations
            config_manager: Configuration manager
            logger: Optional logger instance
        """
        self.market_hours_detector = market_hours_detector
        self.analysis_engine = analysis_engine
        self.trade_executor = trade_executor
        self.config_manager = config_manager
        self.logger = logger or logging.getLogger(__name__)
        
        # Monitoring state per region
        self._monitoring_threads: Dict[MarketRegion, threading.Thread] = {}
        self._stop_flags: Dict[MarketRegion, threading.Event] = {}
        self._monitoring_active: Dict[MarketRegion, bool] = {}
        self._is_paused: Dict[MarketRegion, bool] = {}
        self._pause_until: Dict[MarketRegion, Optional[datetime]] = {}
        self._pause_reason: Dict[MarketRegion, Optional[str]] = {}
        self._consecutive_failures: Dict[MarketRegion, int] = defaultdict(int)
        self._last_cycle_time: Dict[MarketRegion, Optional[datetime]] = {}
        self._next_cycle_time: Dict[MarketRegion, Optional[datetime]] = {}
        self._total_cycles_today: Dict[MarketRegion, int] = defaultdict(int)
        
        # Global stop flag
        self._global_stop = threading.Event()
    
    def start_monitoring(self) -> None:
        """
        Start intraday monitoring for configured markets.
        Creates separate monitoring loops for each regional market.
        """
        try:
            # Get configuration
            config = self.config_manager.get_intraday_config()
            
            if not config.get('enabled', False):
                self.logger.info("Intraday monitoring is disabled in configuration")
                return
            
            # Get monitored regions
            region_names = config.get('monitored_regions', [])
            if not region_names:
                self.logger.warning("No regions configured for intraday monitoring")
                return
            
            # Convert region names to MarketRegion enums
            regions = []
            for region_name in region_names:
                try:
                    region = MarketRegion(region_name)
                    regions.append(region)
                except ValueError:
                    self.logger.error(f"Invalid region name: {region_name}")
            
            if not regions:
                self.logger.error("No valid regions to monitor")
                return
            
            self.logger.info(f"Starting intraday monitoring for regions: {[r.value for r in regions]}")
            
            # Start monitoring thread for each region
            for region in regions:
                if region in self._monitoring_threads and self._monitoring_threads[region].is_alive():
                    self.logger.warning(f"Monitoring already active for {region.value}")
                    continue
                
                # Create stop flag for this region
                self._stop_flags[region] = threading.Event()
                self._monitoring_active[region] = True
                self._is_paused[region] = False
                self._pause_until[region] = None
                self._pause_reason[region] = None
                
                # Create and start monitoring thread
                thread = threading.Thread(
                    target=self._monitoring_loop,
                    args=(region,),
                    name=f"IntradayMonitor-{region.value}",
                    daemon=True
                )
                self._monitoring_threads[region] = thread
                thread.start()
                
                self.logger.info(f"Started monitoring thread for {region.value}")
            
        except Exception as e:
            self.logger.error(f"Error starting intraday monitoring: {e}", exc_info=True)
    
    def stop_monitoring(self) -> None:
        """
        Stop all monitoring activities.
        Allows in-progress cycles to complete.
        Completes cleanup within 30 seconds.
        """
        self.logger.info("Stopping intraday monitoring...")
        
        # Set global stop flag
        self._global_stop.set()
        
        # Signal all threads to stop
        for region, stop_flag in self._stop_flags.items():
            stop_flag.set()
            self._monitoring_active[region] = False
        
        # Wait for threads to complete (with timeout)
        timeout = 30  # seconds
        start_time = time.time()
        
        for region, thread in self._monitoring_threads.items():
            if thread.is_alive():
                remaining_time = timeout - (time.time() - start_time)
                if remaining_time > 0:
                    thread.join(timeout=remaining_time)
                    if thread.is_alive():
                        self.logger.warning(
                            f"Monitoring thread for {region.value} did not stop within timeout"
                        )
                    else:
                        self.logger.info(f"Stopped monitoring thread for {region.value}")
        
        # Clear state
        self._monitoring_threads.clear()
        self._stop_flags.clear()
        
        self.logger.info("Intraday monitoring stopped")
    
    def _monitoring_loop(self, region: MarketRegion) -> None:
        """
        Main monitoring loop for a regional market.

        Implements market session lifecycle management:
        - Detects market open and starts scheduling cycles
        - Detects market close and stops scheduling new cycles
        - Allows in-progress cycles to complete gracefully
        - Checks market status before each cycle

        Args:
            region: Market region to monitor
        """
        stop_flag = self._stop_flags[region]
        config = self.config_manager.get_intraday_config()
        interval_minutes = config.get('monitoring_interval_minutes', 60)

        # Track market state for lifecycle events
        was_market_open = False
        cycle_in_progress = False

        self.logger.info(
            f"Monitoring loop started for {region.value} "
            f"(interval: {interval_minutes} minutes)"
        )

        while not stop_flag.is_set() and not self._global_stop.is_set():
            try:
                # Check if monitoring is paused
                if self._is_paused.get(region, False):
                    pause_until = self._pause_until.get(region)
                    if pause_until and datetime.utcnow() >= pause_until:
                        # Resume monitoring
                        self._is_paused[region] = False
                        self._pause_until[region] = None
                        self._pause_reason[region] = None
                        self._consecutive_failures[region] = 0
                        self.logger.info(f"Resumed monitoring for {region.value}")
                    else:
                        # Still paused, wait
                        time.sleep(60)  # Check every minute
                        continue

                # Check current market status
                try:
                    is_market_open = self.market_hours_detector.is_market_open(region)
                except Exception as e:
                    # Fail-safe: assume market is closed if status check fails
                    self.logger.error(
                        f"Market status check failed for {region.value}: {e}. "
                        f"Assuming market is closed."
                    )
                    is_market_open = False

                # Detect market open event (transition from closed to open)
                if is_market_open and not was_market_open:
                    self.logger.info(f"Market opened for {region.value}")
                    # Reset next cycle time to allow immediate execution
                    self._next_cycle_time[region] = None

                # Detect market close event (transition from open to closed)
                if not is_market_open and was_market_open:
                    self.logger.info(f"Market closed for {region.value}")
                    if cycle_in_progress:
                        self.logger.info(
                            f"Allowing in-progress cycle to complete for {region.value}"
                        )

                # Update market state tracking
                was_market_open = is_market_open

                # Check if should execute cycle (includes market status check)
                if self._should_execute_cycle(region):
                    # Mark cycle as in progress
                    cycle_in_progress = True

                    # Execute analysis cycle
                    result = self.execute_analysis_cycle(region)

                    # Mark cycle as complete
                    cycle_in_progress = False

                    # Update state based on result
                    if result.success:
                        self._consecutive_failures[region] = 0
                        self._last_cycle_time[region] = result.end_time
                        self._total_cycles_today[region] += 1
                    else:
                        self._handle_cycle_error(region, Exception(result.error_message or "Unknown error"))

                    # Check market status again after cycle completion
                    # If market closed during cycle, don't schedule next cycle
                    try:
                        is_market_still_open = self.market_hours_detector.is_market_open(region)
                    except Exception as e:
                        self.logger.error(
                            f"Market status check failed after cycle for {region.value}: {e}. "
                            f"Assuming market is closed."
                        )
                        is_market_still_open = False

                    if is_market_still_open:
                        # Calculate next cycle time
                        self._next_cycle_time[region] = datetime.utcnow() + timedelta(minutes=interval_minutes)
                    else:
                        # Market closed during cycle, don't schedule next cycle
                        self.logger.info(
                            f"Market closed during cycle for {region.value}. "
                            f"Not scheduling next cycle."
                        )
                        self._next_cycle_time[region] = None
                        was_market_open = False

                # Sleep for a short interval before checking again
                time.sleep(60)  # Check every minute

            except Exception as e:
                self.logger.error(
                    f"Error in monitoring loop for {region.value}: {e}",
                    exc_info=True
                )
                cycle_in_progress = False
                self._handle_cycle_error(region, e)
                time.sleep(60)

        self.logger.info(f"Monitoring loop stopped for {region.value}")

    
    def _should_execute_cycle(self, region: MarketRegion) -> bool:
        """
        Check if analysis cycle should execute for the given region.
        
        Args:
            region: Market region to check
            
        Returns:
            True if cycle should execute, False otherwise
        """
        try:
            # Check if market is open
            if not self.market_hours_detector.is_market_open(region):
                return False
            
            # Check if enough time has passed since last cycle
            next_cycle_time = self._next_cycle_time.get(region)
            if next_cycle_time and datetime.utcnow() < next_cycle_time:
                return False
            
            # Check if a cycle is already in progress (simple check)
            # In a more robust implementation, we'd track cycle execution state
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking if cycle should execute for {region.value}: {e}")
            return False
    
    def execute_analysis_cycle(self, region: MarketRegion) -> AnalysisCycleResult:
        """
        Execute a single analysis cycle for a regional market.
        
        Args:
            region: Market region to analyze
            
        Returns:
            AnalysisCycleResult with success status, trade count, and errors
        """
        start_time = datetime.utcnow()
        
        try:
            self.logger.info(f"Starting analysis cycle for {region.value}")
            
            # Execute analysis
            analysis_result = self.analysis_engine.execute_scheduled_analysis([region])
            
            if not analysis_result.success:
                error_msg = f"Analysis failed: {analysis_result.error_message}"
                self.logger.error(error_msg)
                return AnalysisCycleResult(
                    success=False,
                    region=region,
                    start_time=start_time,
                    end_time=datetime.utcnow(),
                    recommendations_count=0,
                    trades_executed=0,
                    error_message=error_msg
                )
            
            recommendations = analysis_result.recommendations
            recommendations_count = len(recommendations)
            
            self.logger.info(
                f"Analysis completed for {region.value}: {recommendations_count} recommendations"
            )
            
            # Execute trades based on recommendations
            trades_executed = 0
            for recommendation in recommendations:
                try:
                    trade_result = self.trade_executor.execute_recommendation(recommendation)
                    if trade_result:
                        trades_executed += 1
                except Exception as e:
                    self.logger.error(
                        f"Error executing trade for {recommendation.symbol}: {e}"
                    )
            
            end_time = datetime.utcnow()
            
            self.logger.info(
                f"Analysis cycle completed for {region.value}: "
                f"{trades_executed} trades executed in {(end_time - start_time).total_seconds():.1f}s"
            )
            
            return AnalysisCycleResult(
                success=True,
                region=region,
                start_time=start_time,
                end_time=end_time,
                recommendations_count=recommendations_count,
                trades_executed=trades_executed,
                error_message=None
            )
            
        except Exception as e:
            error_msg = f"Analysis cycle failed: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            
            return AnalysisCycleResult(
                success=False,
                region=region,
                start_time=start_time,
                end_time=datetime.utcnow(),
                recommendations_count=0,
                trades_executed=0,
                error_message=error_msg
            )
    
    def _handle_cycle_error(self, region: MarketRegion, error: Exception) -> None:
        """
        Handle errors during analysis cycle execution.
        
        Args:
            region: Market region where error occurred
            error: Exception that occurred
        """
        self._consecutive_failures[region] += 1
        failure_count = self._consecutive_failures[region]
        
        self.logger.error(
            f"Analysis cycle error for {region.value} "
            f"(consecutive failures: {failure_count}): {error}"
        )
        
        # Circuit breaker: pause after 3 consecutive failures
        if failure_count >= 3:
            self._pause_monitoring(
                region,
                duration_minutes=30,
                reason=f"3 consecutive failures: {str(error)}"
            )
    
    def _pause_monitoring(self, region: MarketRegion, duration_minutes: int, reason: str) -> None:
        """
        Pause monitoring for a region due to repeated failures.
        
        Args:
            region: Market region to pause
            duration_minutes: Duration to pause in minutes
            reason: Reason for pausing
        """
        pause_until = datetime.utcnow() + timedelta(minutes=duration_minutes)
        
        self._is_paused[region] = True
        self._pause_until[region] = pause_until
        self._pause_reason[region] = reason
        
        self.logger.warning(
            f"Paused monitoring for {region.value} until {pause_until.isoformat()} "
            f"(duration: {duration_minutes} minutes). Reason: {reason}"
        )
    
    def get_monitoring_status(self, region: MarketRegion) -> MonitoringStatus:
        """
        Query current monitoring status for a regional market.
        
        Args:
            region: Market region to query
            
        Returns:
            MonitoringStatus with active/paused state, last cycle time, next cycle time
        """
        return MonitoringStatus(
            region=region,
            is_active=self._monitoring_active.get(region, False),
            is_paused=self._is_paused.get(region, False),
            pause_reason=self._pause_reason.get(region),
            pause_until=self._pause_until.get(region),
            last_cycle_time=self._last_cycle_time.get(region),
            next_cycle_time=self._next_cycle_time.get(region),
            consecutive_failures=self._consecutive_failures.get(region, 0),
            total_cycles_today=self._total_cycles_today.get(region, 0)
        )
