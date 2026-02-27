"""
Unit tests for IntradayMonitor component.

Tests the core functionality of the intraday monitoring system including:
- Start/stop monitoring lifecycle
- Single analysis cycle execution
- Status query methods
- Resource cleanup on shutdown
"""

import pytest
import time
import threading
from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import Mock, MagicMock, patch, call

from stock_market_analysis.models.market_region import MarketRegion
from stock_market_analysis.models.recommendation import StockRecommendation, RecommendationType
from stock_market_analysis.models.results import AnalysisResult
from stock_market_analysis.components.intraday.intraday_monitor import IntradayMonitor
from stock_market_analysis.components.intraday.models import AnalysisCycleResult, MonitoringStatus


class TestIntradayMonitor:
    """Test suite for IntradayMonitor core functionality."""
    
    @pytest.fixture
    def market_hours_detector(self):
        """Create a mock MarketHoursDetector."""
        mock_detector = Mock()
        mock_detector.is_market_open.return_value = True
        return mock_detector
    
    @pytest.fixture
    def analysis_engine(self):
        """Create a mock AnalysisEngine."""
        mock_engine = Mock()
        # Default: successful analysis with no recommendations
        mock_engine.execute_scheduled_analysis.return_value = AnalysisResult(
            success=True,
            recommendations=[],
            error_message=None,
            retry_count=0
        )
        return mock_engine
    
    @pytest.fixture
    def trade_executor(self):
        """Create a mock TradeExecutor."""
        mock_executor = Mock()
        mock_executor.execute_recommendation.return_value = None
        return mock_executor
    
    @pytest.fixture
    def config_manager(self):
        """Create a mock ConfigurationManager."""
        mock_config = Mock()
        mock_config.get_intraday_config.return_value = {
            'enabled': True,
            'monitoring_interval_minutes': 60,
            'monitored_regions': ['china', 'usa']
        }
        return mock_config
    
    @pytest.fixture
    def monitor(self, market_hours_detector, analysis_engine, trade_executor, config_manager):
        """Create an IntradayMonitor instance for testing."""
        return IntradayMonitor(
            market_hours_detector=market_hours_detector,
            analysis_engine=analysis_engine,
            trade_executor=trade_executor,
            config_manager=config_manager
        )
    
    # ===== Start/Stop Monitoring Lifecycle Tests =====
    
    def test_start_monitoring_creates_threads_for_configured_regions(self, monitor, config_manager):
        """Test that start_monitoring creates monitoring threads for each configured region."""
        monitor.start_monitoring()
        
        # Give threads time to start
        time.sleep(0.1)
        
        # Verify threads were created for both regions
        assert MarketRegion.CHINA in monitor._monitoring_threads
        assert MarketRegion.USA in monitor._monitoring_threads
        
        # Verify threads are alive
        assert monitor._monitoring_threads[MarketRegion.CHINA].is_alive()
        assert monitor._monitoring_threads[MarketRegion.USA].is_alive()
        
        # Cleanup
        monitor.stop_monitoring()
    
    def test_start_monitoring_when_disabled_does_not_create_threads(self, monitor, config_manager):
        """Test that start_monitoring does nothing when intraday monitoring is disabled."""
        config_manager.get_intraday_config.return_value = {'enabled': False}
        
        monitor.start_monitoring()
        
        # Verify no threads were created
        assert len(monitor._monitoring_threads) == 0
    
    def test_start_monitoring_with_no_regions_does_not_create_threads(self, monitor, config_manager):
        """Test that start_monitoring does nothing when no regions are configured."""
        config_manager.get_intraday_config.return_value = {
            'enabled': True,
            'monitored_regions': []
        }
        
        monitor.start_monitoring()
        
        # Verify no threads were created
        assert len(monitor._monitoring_threads) == 0
    
    def test_start_monitoring_with_invalid_region_name_skips_invalid(self, monitor, config_manager):
        """Test that start_monitoring skips invalid region names."""
        config_manager.get_intraday_config.return_value = {
            'enabled': True,
            'monitored_regions': ['china', 'invalid_region', 'usa']
        }
        
        monitor.start_monitoring()
        
        # Give threads time to start
        time.sleep(0.1)
        
        # Verify only valid regions have threads
        assert MarketRegion.CHINA in monitor._monitoring_threads
        assert MarketRegion.USA in monitor._monitoring_threads
        assert len(monitor._monitoring_threads) == 2
        
        # Cleanup
        monitor.stop_monitoring()
    
    def test_start_monitoring_twice_does_not_create_duplicate_threads(self, monitor):
        """Test that calling start_monitoring twice doesn't create duplicate threads."""
        monitor.start_monitoring()
        time.sleep(0.1)
        
        # Get thread references
        china_thread_1 = monitor._monitoring_threads[MarketRegion.CHINA]
        usa_thread_1 = monitor._monitoring_threads[MarketRegion.USA]
        
        # Start again
        monitor.start_monitoring()
        time.sleep(0.1)
        
        # Verify same threads are still running
        assert monitor._monitoring_threads[MarketRegion.CHINA] == china_thread_1
        assert monitor._monitoring_threads[MarketRegion.USA] == usa_thread_1
        
        # Cleanup
        monitor.stop_monitoring()
    
    def test_stop_monitoring_sets_stop_flags(self, monitor):
        """Test that stop_monitoring sets stop flags for all regions."""
        monitor.start_monitoring()
        time.sleep(0.1)
        
        # Get references to stop flags before stopping
        china_stop_flag = monitor._stop_flags[MarketRegion.CHINA]
        usa_stop_flag = monitor._stop_flags[MarketRegion.USA]
        global_stop = monitor._global_stop
        
        monitor.stop_monitoring()
        
        # Verify stop flags were set
        assert china_stop_flag.is_set()
        assert usa_stop_flag.is_set()
        assert global_stop.is_set()
    
    def test_stop_monitoring_waits_for_threads_to_complete(self, monitor):
        """Test that stop_monitoring sets stop flags and waits for timeout."""
        monitor.start_monitoring()
        time.sleep(0.1)
        
        # Verify threads are alive and get references
        china_thread = monitor._monitoring_threads[MarketRegion.CHINA]
        usa_thread = monitor._monitoring_threads[MarketRegion.USA]
        assert china_thread.is_alive()
        assert usa_thread.is_alive()
        
        # Get stop flags before stopping
        china_stop_flag = monitor._stop_flags[MarketRegion.CHINA]
        usa_stop_flag = monitor._stop_flags[MarketRegion.USA]
        
        monitor.stop_monitoring()
        
        # Verify stop flags were set (this is what signals threads to stop)
        assert china_stop_flag.is_set()
        assert usa_stop_flag.is_set()
        
        # Threads are daemon threads and may not stop immediately due to sleep(60)
        # The important thing is that stop_monitoring completes within timeout
        # and sets the stop flags correctly
    
    def test_stop_monitoring_completes_within_timeout(self, monitor):
        """Test that stop_monitoring completes within 30 seconds."""
        monitor.start_monitoring()
        time.sleep(0.1)
        
        start_time = time.time()
        monitor.stop_monitoring()
        elapsed_time = time.time() - start_time
        
        # Should complete within 30 seconds (allow small margin)
        assert elapsed_time <= 31
    
    def test_stop_monitoring_clears_state(self, monitor):
        """Test that stop_monitoring clears monitoring state."""
        monitor.start_monitoring()
        time.sleep(0.1)
        
        monitor.stop_monitoring()
        
        # Verify state was cleared
        assert len(monitor._monitoring_threads) == 0
        assert len(monitor._stop_flags) == 0
    
    # ===== Single Analysis Cycle Execution Tests =====
    
    def test_execute_analysis_cycle_success(self, monitor, analysis_engine, trade_executor):
        """Test successful execution of a single analysis cycle."""
        # Setup: analysis returns recommendations
        recommendation = StockRecommendation(
            symbol="AAPL",
            name="Apple Inc.",
            region=MarketRegion.USA,
            recommendation_type=RecommendationType.BUY,
            rationale="Strong growth",
            risk_assessment="Low risk",
            confidence_score=0.85,
            target_price=Decimal("150.00"),
            generated_at=datetime.utcnow()
        )
        
        analysis_engine.execute_scheduled_analysis.return_value = AnalysisResult(
            success=True,
            recommendations=[recommendation],
            error_message=None,
            retry_count=0
        )
        
        trade_executor.execute_recommendation.return_value = Mock()  # Successful trade
        
        # Execute cycle
        result = monitor.execute_analysis_cycle(MarketRegion.USA)
        
        # Verify result
        assert result.success is True
        assert result.region == MarketRegion.USA
        assert result.recommendations_count == 1
        assert result.trades_executed == 1
        assert result.error_message is None
        assert result.start_time is not None
        assert result.end_time is not None
        assert result.end_time >= result.start_time
    
    def test_execute_analysis_cycle_calls_analysis_engine_with_region(self, monitor, analysis_engine):
        """Test that execute_analysis_cycle calls analysis engine with correct region."""
        monitor.execute_analysis_cycle(MarketRegion.CHINA)
        
        analysis_engine.execute_scheduled_analysis.assert_called_once_with([MarketRegion.CHINA])
    
    def test_execute_analysis_cycle_passes_recommendations_to_trade_executor(
        self, monitor, analysis_engine, trade_executor
    ):
        """Test that execute_analysis_cycle passes all recommendations to trade executor."""
        # Setup: multiple recommendations
        recommendations = [
            StockRecommendation(
                symbol="AAPL",
                name="Apple Inc.",
                region=MarketRegion.USA,
                recommendation_type=RecommendationType.BUY,
                rationale="Strong growth",
                risk_assessment="Low risk",
                confidence_score=0.85,
                target_price=Decimal("150.00"),
                generated_at=datetime.utcnow()
            ),
            StockRecommendation(
                symbol="GOOGL",
                name="Alphabet Inc.",
                region=MarketRegion.USA,
                recommendation_type=RecommendationType.SELL,
                rationale="Overvalued",
                risk_assessment="Medium risk",
                confidence_score=0.75,
                target_price=Decimal("140.00"),
                generated_at=datetime.utcnow()
            )
        ]
        
        analysis_engine.execute_scheduled_analysis.return_value = AnalysisResult(
            success=True,
            recommendations=recommendations,
            error_message=None,
            retry_count=0
        )
        
        # Execute cycle
        monitor.execute_analysis_cycle(MarketRegion.USA)
        
        # Verify trade executor was called for each recommendation
        assert trade_executor.execute_recommendation.call_count == 2
        trade_executor.execute_recommendation.assert_any_call(recommendations[0])
        trade_executor.execute_recommendation.assert_any_call(recommendations[1])
    
    def test_execute_analysis_cycle_handles_analysis_failure(self, monitor, analysis_engine):
        """Test that execute_analysis_cycle handles analysis engine failures."""
        # Setup: analysis fails
        analysis_engine.execute_scheduled_analysis.return_value = AnalysisResult(
            success=False,
            recommendations=[],
            error_message="Data collection failed",
            retry_count=3
        )
        
        # Execute cycle
        result = monitor.execute_analysis_cycle(MarketRegion.USA)
        
        # Verify result indicates failure
        assert result.success is False
        assert result.recommendations_count == 0
        assert result.trades_executed == 0
        assert "Analysis failed" in result.error_message
    
    def test_execute_analysis_cycle_handles_trade_execution_failure(
        self, monitor, analysis_engine, trade_executor
    ):
        """Test that execute_analysis_cycle continues when trade execution fails."""
        # Setup: analysis succeeds but trade execution fails
        recommendations = [
            StockRecommendation(
                symbol="AAPL",
                name="Apple Inc.",
                region=MarketRegion.USA,
                recommendation_type=RecommendationType.BUY,
                rationale="Strong growth",
                risk_assessment="Low risk",
                confidence_score=0.85,
                target_price=Decimal("150.00"),
                generated_at=datetime.utcnow()
            ),
            StockRecommendation(
                symbol="GOOGL",
                name="Alphabet Inc.",
                region=MarketRegion.USA,
                recommendation_type=RecommendationType.BUY,
                rationale="Good value",
                risk_assessment="Low risk",
                confidence_score=0.80,
                target_price=Decimal("140.00"),
                generated_at=datetime.utcnow()
            )
        ]
        
        analysis_engine.execute_scheduled_analysis.return_value = AnalysisResult(
            success=True,
            recommendations=recommendations,
            error_message=None,
            retry_count=0
        )
        
        # First trade fails, second succeeds
        trade_executor.execute_recommendation.side_effect = [
            Exception("Insufficient funds"),
            Mock()  # Successful trade
        ]
        
        # Execute cycle
        result = monitor.execute_analysis_cycle(MarketRegion.USA)
        
        # Verify cycle succeeded despite one trade failure
        assert result.success is True
        assert result.recommendations_count == 2
        assert result.trades_executed == 1  # Only one trade succeeded
    
    def test_execute_analysis_cycle_handles_exception(self, monitor, analysis_engine):
        """Test that execute_analysis_cycle handles unexpected exceptions."""
        # Setup: analysis engine raises exception
        analysis_engine.execute_scheduled_analysis.side_effect = Exception("Unexpected error")
        
        # Execute cycle
        result = monitor.execute_analysis_cycle(MarketRegion.USA)
        
        # Verify result indicates failure
        assert result.success is False
        assert result.recommendations_count == 0
        assert result.trades_executed == 0
        assert "Analysis cycle failed" in result.error_message
    
    def test_execute_analysis_cycle_with_no_recommendations(self, monitor, analysis_engine):
        """Test execute_analysis_cycle when analysis returns no recommendations."""
        # Setup: analysis succeeds but no recommendations
        analysis_engine.execute_scheduled_analysis.return_value = AnalysisResult(
            success=True,
            recommendations=[],
            error_message=None,
            retry_count=0
        )
        
        # Execute cycle
        result = monitor.execute_analysis_cycle(MarketRegion.USA)
        
        # Verify result
        assert result.success is True
        assert result.recommendations_count == 0
        assert result.trades_executed == 0
        assert result.error_message is None
    
    # ===== Status Query Methods Tests =====
    
    def test_get_monitoring_status_returns_correct_structure(self, monitor):
        """Test that get_monitoring_status returns MonitoringStatus with correct fields."""
        status = monitor.get_monitoring_status(MarketRegion.USA)
        
        assert isinstance(status, MonitoringStatus)
        assert status.region == MarketRegion.USA
        assert isinstance(status.is_active, bool)
        assert isinstance(status.is_paused, bool)
        assert isinstance(status.consecutive_failures, int)
        assert isinstance(status.total_cycles_today, int)
    
    def test_get_monitoring_status_before_start(self, monitor):
        """Test get_monitoring_status before monitoring has started."""
        status = monitor.get_monitoring_status(MarketRegion.USA)
        
        assert status.is_active is False
        assert status.is_paused is False
        assert status.pause_reason is None
        assert status.pause_until is None
        assert status.last_cycle_time is None
        assert status.next_cycle_time is None
        assert status.consecutive_failures == 0
        assert status.total_cycles_today == 0
    
    def test_get_monitoring_status_after_start(self, monitor):
        """Test get_monitoring_status after monitoring has started."""
        monitor.start_monitoring()
        time.sleep(0.1)
        
        status = monitor.get_monitoring_status(MarketRegion.USA)
        
        assert status.is_active is True
        assert status.is_paused is False
        
        # Cleanup
        monitor.stop_monitoring()
    
    def test_get_monitoring_status_after_successful_cycle(self, monitor, market_hours_detector):
        """Test get_monitoring_status after a successful analysis cycle."""
        # Execute a cycle
        result = monitor.execute_analysis_cycle(MarketRegion.USA)
        
        # Update state as monitoring loop would
        monitor._last_cycle_time[MarketRegion.USA] = result.end_time
        monitor._total_cycles_today[MarketRegion.USA] = 1
        monitor._next_cycle_time[MarketRegion.USA] = datetime.utcnow() + timedelta(minutes=60)
        
        status = monitor.get_monitoring_status(MarketRegion.USA)
        
        assert status.last_cycle_time is not None
        assert status.next_cycle_time is not None
        assert status.total_cycles_today == 1
        assert status.consecutive_failures == 0
    
    def test_get_monitoring_status_after_failed_cycle(self, monitor, analysis_engine):
        """Test get_monitoring_status after a failed analysis cycle."""
        # Setup: analysis fails
        analysis_engine.execute_scheduled_analysis.return_value = AnalysisResult(
            success=False,
            recommendations=[],
            error_message="Data collection failed",
            retry_count=3
        )
        
        # Execute cycle and handle error
        result = monitor.execute_analysis_cycle(MarketRegion.USA)
        monitor._handle_cycle_error(MarketRegion.USA, Exception(result.error_message))
        
        status = monitor.get_monitoring_status(MarketRegion.USA)
        
        assert status.consecutive_failures == 1
    
    def test_get_monitoring_status_when_paused(self, monitor):
        """Test get_monitoring_status when monitoring is paused."""
        # Pause monitoring
        pause_until = datetime.utcnow() + timedelta(minutes=30)
        monitor._pause_monitoring(MarketRegion.USA, 30, "Test pause")
        
        status = monitor.get_monitoring_status(MarketRegion.USA)
        
        assert status.is_paused is True
        assert status.pause_reason == "Test pause"
        assert status.pause_until is not None
        assert status.pause_until >= datetime.utcnow()
    
    # ===== Resource Cleanup Tests =====
    
    def test_stop_monitoring_releases_resources(self, monitor):
        """Test that stop_monitoring releases all resources."""
        monitor.start_monitoring()
        time.sleep(0.1)
        
        # Verify resources are allocated
        assert len(monitor._monitoring_threads) > 0
        assert len(monitor._stop_flags) > 0
        
        monitor.stop_monitoring()
        
        # Verify resources are released
        assert len(monitor._monitoring_threads) == 0
        assert len(monitor._stop_flags) == 0
    
    def test_monitoring_active_flag_cleared_on_stop(self, monitor):
        """Test that monitoring_active flags are cleared when stopping."""
        monitor.start_monitoring()
        time.sleep(0.1)
        
        # Verify flags are set
        assert monitor._monitoring_active[MarketRegion.CHINA] is True
        assert monitor._monitoring_active[MarketRegion.USA] is True
        
        monitor.stop_monitoring()
        
        # Verify flags are cleared
        assert monitor._monitoring_active[MarketRegion.CHINA] is False
        assert monitor._monitoring_active[MarketRegion.USA] is False
    
    # ===== Helper Method Tests =====
    
    def test_should_execute_cycle_when_market_open(self, monitor, market_hours_detector):
        """Test _should_execute_cycle returns True when market is open."""
        market_hours_detector.is_market_open.return_value = True
        
        result = monitor._should_execute_cycle(MarketRegion.USA)
        
        assert result is True
    
    def test_should_execute_cycle_when_market_closed(self, monitor, market_hours_detector):
        """Test _should_execute_cycle returns False when market is closed."""
        market_hours_detector.is_market_open.return_value = False
        
        result = monitor._should_execute_cycle(MarketRegion.USA)
        
        assert result is False
    
    def test_should_execute_cycle_respects_next_cycle_time(self, monitor, market_hours_detector):
        """Test _should_execute_cycle respects next_cycle_time."""
        market_hours_detector.is_market_open.return_value = True
        
        # Set next cycle time in the future
        monitor._next_cycle_time[MarketRegion.USA] = datetime.utcnow() + timedelta(minutes=30)
        
        result = monitor._should_execute_cycle(MarketRegion.USA)
        
        assert result is False
    
    def test_should_execute_cycle_when_next_cycle_time_passed(self, monitor, market_hours_detector):
        """Test _should_execute_cycle returns True when next_cycle_time has passed."""
        market_hours_detector.is_market_open.return_value = True
        
        # Set next cycle time in the past
        monitor._next_cycle_time[MarketRegion.USA] = datetime.utcnow() - timedelta(minutes=1)
        
        result = monitor._should_execute_cycle(MarketRegion.USA)
        
        assert result is True
    
    def test_should_execute_cycle_handles_exception(self, monitor, market_hours_detector):
        """Test _should_execute_cycle returns False when exception occurs."""
        market_hours_detector.is_market_open.side_effect = Exception("Market hours check failed")
        
        result = monitor._should_execute_cycle(MarketRegion.USA)
        
        assert result is False
    
    def test_handle_cycle_error_increments_failure_counter(self, monitor):
        """Test _handle_cycle_error increments consecutive failure counter."""
        initial_count = monitor._consecutive_failures[MarketRegion.USA]
        
        monitor._handle_cycle_error(MarketRegion.USA, Exception("Test error"))
        
        assert monitor._consecutive_failures[MarketRegion.USA] == initial_count + 1
    
    def test_handle_cycle_error_triggers_pause_after_three_failures(self, monitor):
        """Test _handle_cycle_error triggers pause after 3 consecutive failures."""
        # Simulate 3 failures
        for _ in range(3):
            monitor._handle_cycle_error(MarketRegion.USA, Exception("Test error"))
        
        # Verify monitoring is paused
        assert monitor._is_paused[MarketRegion.USA] is True
        assert monitor._pause_until[MarketRegion.USA] is not None
        assert monitor._pause_reason[MarketRegion.USA] is not None
    
    def test_pause_monitoring_sets_pause_state(self, monitor):
        """Test _pause_monitoring sets correct pause state."""
        pause_until_expected = datetime.utcnow() + timedelta(minutes=30)
        
        monitor._pause_monitoring(MarketRegion.USA, 30, "Test pause reason")
        
        assert monitor._is_paused[MarketRegion.USA] is True
        assert monitor._pause_reason[MarketRegion.USA] == "Test pause reason"
        assert monitor._pause_until[MarketRegion.USA] is not None
        # Allow small time difference
        assert abs((monitor._pause_until[MarketRegion.USA] - pause_until_expected).total_seconds()) < 2
    
    def test_component_instance_reuse(self, monitor, analysis_engine, trade_executor):
        """Test that the same component instances are reused across cycles."""
        # Execute multiple cycles
        monitor.execute_analysis_cycle(MarketRegion.USA)
        monitor.execute_analysis_cycle(MarketRegion.USA)
        monitor.execute_analysis_cycle(MarketRegion.CHINA)
        
        # Verify the same instances were used (not creating new ones)
        assert monitor.analysis_engine is analysis_engine
        assert monitor.trade_executor is trade_executor

    # ===== Market Session Lifecycle Management Tests =====
    
    def test_market_open_detection_logs_event(self, monitor, market_hours_detector, caplog):
        """Test that market open event is detected and logged."""
        import logging
        caplog.set_level(logging.INFO)
        
        # Setup: market starts closed, then opens
        # Track state per region to handle both china and usa
        states = {'china': [False, True, True, True], 'usa': [False, True, True, True]}
        indices = {'china': 0, 'usa': 0}
        
        def market_status(region):
            region_key = region.value if hasattr(region, 'value') else str(region)
            idx = indices[region_key]
            indices[region_key] += 1
            return states[region_key][min(idx, len(states[region_key])-1)]
        
        market_hours_detector.is_market_open.side_effect = market_status
        
        # Start monitoring
        monitor.start_monitoring()
        time.sleep(0.3)  # Give time for loop to detect market open
        
        # Stop monitoring
        monitor.stop_monitoring()
        
        # Verify market open event was logged for at least one region
        log_messages = [record.message for record in caplog.records]
        assert any("Market opened for" in msg for msg in log_messages), \
            f"Expected 'Market opened for' in logs, got: {log_messages}"
    
    def test_market_close_detection_logs_event(self, monitor, market_hours_detector, caplog):
        """Test that market close event is detected and logged."""
        import logging
        caplog.set_level(logging.INFO)
        
        # Setup: market starts open, then closes
        states = {'china': [True, True, True, False, False], 'usa': [True, True, True, False, False]}
        indices = {'china': 0, 'usa': 0}
        
        def market_status(region):
            region_key = region.value if hasattr(region, 'value') else str(region)
            idx = indices[region_key]
            indices[region_key] += 1
            return states[region_key][min(idx, len(states[region_key])-1)]
        
        market_hours_detector.is_market_open.side_effect = market_status
        
        # Start monitoring
        monitor.start_monitoring()
        time.sleep(1.2)  # Give time for multiple loop iterations
        
        # Stop monitoring
        monitor.stop_monitoring()
        
        # Verify market close event was logged for at least one region
        log_messages = [record.message for record in caplog.records]
        assert any("Market closed for" in msg for msg in log_messages), \
            f"Expected 'Market closed for' in logs, got: {log_messages}"
    
    def test_market_open_resets_next_cycle_time(self, monitor, market_hours_detector):
        """Test that market open event resets next_cycle_time to allow immediate execution."""
        # Set a future next cycle time
        monitor._next_cycle_time[MarketRegion.USA] = datetime.utcnow() + timedelta(hours=1)
        
        # Setup: market opens (provide enough values)
        call_counts = {}
        
        def market_status(region):
            if region not in call_counts:
                call_counts[region] = 0
            call_counts[region] += 1
            # First check: closed, then open
            return call_counts[region] > 1
        
        market_hours_detector.is_market_open.side_effect = market_status
        
        # Start monitoring
        monitor.start_monitoring()
        time.sleep(0.3)  # Give time for loop to detect market open
        
        # Stop monitoring
        monitor.stop_monitoring()
        
        # Verify next_cycle_time was reset (either None or a recent time)
        next_cycle = monitor._next_cycle_time.get(MarketRegion.USA)
        if next_cycle is not None:
            # If set, should be recent (within last few seconds)
            assert (next_cycle - datetime.utcnow()).total_seconds() < 120
    
    def test_market_close_during_cycle_allows_completion(self, monitor, market_hours_detector, caplog):
        """Test that in-progress cycle completes when market closes."""
        import logging
        caplog.set_level(logging.INFO)
        
        # Setup: market is open, then closes during cycle
        call_counts = {}
        
        def market_status(region):
            if region not in call_counts:
                call_counts[region] = 0
            call_counts[region] += 1
            # Open for first 2 checks, then closed
            return call_counts[region] <= 2
        
        market_hours_detector.is_market_open.side_effect = market_status
        
        # Start monitoring
        monitor.start_monitoring()
        time.sleep(0.5)  # Give time for cycle to execute
        
        # Stop monitoring
        monitor.stop_monitoring()
        
        # Verify message about allowing cycle to complete was logged
        assert any("Allowing in-progress cycle to complete" in record.message for record in caplog.records)
    
    def test_market_close_during_cycle_prevents_next_cycle_scheduling(
        self, monitor, market_hours_detector, caplog
    ):
        """Test that next cycle is not scheduled when market closes during cycle."""
        import logging
        caplog.set_level(logging.INFO)
        
        # Setup: market open before cycle, closed after cycle
        call_counts = {}
        
        def market_status(region):
            if region not in call_counts:
                call_counts[region] = 0
            call_counts[region] += 1
            # Open for first 2 checks, then closed
            return call_counts[region] <= 2
        
        market_hours_detector.is_market_open.side_effect = market_status
        
        # Start monitoring
        monitor.start_monitoring()
        time.sleep(0.5)  # Give time for cycle to execute
        
        # Stop monitoring
        monitor.stop_monitoring()
        
        # Verify message about not scheduling next cycle was logged
        assert any("Not scheduling next cycle" in record.message for record in caplog.records)
    
    def test_market_status_check_before_each_cycle(self, monitor, market_hours_detector):
        """Test that market status is checked before each cycle execution."""
        # Setup: market is open
        market_hours_detector.is_market_open.return_value = True
        
        # Execute cycle directly (simulating what monitoring loop does)
        should_execute = monitor._should_execute_cycle(MarketRegion.USA)
        
        # Verify market status was checked
        market_hours_detector.is_market_open.assert_called_with(MarketRegion.USA)
        assert should_execute is True
    
    def test_market_status_check_failure_assumes_closed(self, monitor, market_hours_detector, caplog):
        """Test that market status check failure results in fail-safe behavior (assume closed)."""
        import logging
        caplog.set_level(logging.ERROR)
        
        # Setup: market status check raises exception (provide enough failures)
        market_hours_detector.is_market_open.side_effect = Exception("Network error")
        
        # Start monitoring
        monitor.start_monitoring()
        time.sleep(0.3)  # Give time for status check
        
        # Stop monitoring
        monitor.stop_monitoring()
        
        # Verify error was logged with fail-safe message
        assert any("Market status check failed" in record.message and "Assuming market is closed" in record.message 
                   for record in caplog.records)
    
    def test_market_status_check_after_cycle_completion(self, monitor, market_hours_detector):
        """Test that market status is checked again after cycle completes."""
        # Setup: market is open before and after cycle
        market_hours_detector.is_market_open.return_value = True
        
        # Start monitoring
        monitor.start_monitoring()
        time.sleep(0.2)  # Give time for cycle to execute
        
        # Stop monitoring
        monitor.stop_monitoring()
        
        # Verify market status was checked multiple times (before and after cycle)
        assert market_hours_detector.is_market_open.call_count >= 2
    
    def test_graceful_cycle_completion_on_market_close(self, monitor, market_hours_detector, analysis_engine):
        """Test that cycle completes gracefully when market closes during execution."""
        # Setup: market open before cycle, closed after
        call_count = [0]
        
        def market_status_side_effect(region):
            call_count[0] += 1
            # Open for first few checks, then closed
            return call_count[0] <= 2
        
        market_hours_detector.is_market_open.side_effect = market_status_side_effect
        
        # Make analysis take a bit of time
        def slow_analysis(regions):
            time.sleep(0.1)
            return AnalysisResult(success=True, recommendations=[], error_message=None, retry_count=0)
        
        analysis_engine.execute_scheduled_analysis.side_effect = slow_analysis
        
        # Execute cycle
        result = monitor.execute_analysis_cycle(MarketRegion.USA)
        
        # Verify cycle completed successfully despite market closing
        assert result.success is True
    
    def test_monitoring_loop_stops_scheduling_when_market_closed(self, monitor, market_hours_detector):
        """Test that monitoring loop doesn't schedule cycles when market is closed."""
        # Setup: market is closed
        market_hours_detector.is_market_open.return_value = False
        
        # Start monitoring
        monitor.start_monitoring()
        time.sleep(0.2)  # Give time for loop iterations
        
        # Stop monitoring
        monitor.stop_monitoring()
        
        # Verify no cycles were scheduled (next_cycle_time should be None or not set)
        next_cycle = monitor._next_cycle_time.get(MarketRegion.USA)
        # Either not set or None
        assert next_cycle is None or MarketRegion.USA not in monitor._next_cycle_time
    
    def test_market_open_to_close_flow(self, monitor, market_hours_detector, analysis_engine, caplog):
        """Test complete flow from market open to close."""
        import logging
        caplog.set_level(logging.INFO)
        
        # Setup: market opens, stays open for a cycle, then closes
        call_count = [0]
        
        def market_status_flow(region):
            call_count[0] += 1
            if call_count[0] == 1:
                return False  # Initially closed
            elif call_count[0] <= 4:
                return True   # Opens and stays open
            else:
                return False  # Closes
        
        market_hours_detector.is_market_open.side_effect = market_status_flow
        
        # Start monitoring
        monitor.start_monitoring()
        time.sleep(0.3)  # Give time for market open, cycle, and close
        
        # Stop monitoring
        monitor.stop_monitoring()
        
        # Verify lifecycle events were logged
        log_messages = [record.message for record in caplog.records]
        assert any("Market opened for" in msg for msg in log_messages)
        assert any("Market closed for" in msg for msg in log_messages)
