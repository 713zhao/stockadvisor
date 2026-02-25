"""
Unit tests for Scheduler component.
"""

import pytest
from datetime import datetime, time, timedelta
from unittest.mock import Mock, MagicMock

from stock_market_analysis.components import Scheduler
from stock_market_analysis.models import MarketRegion, AnalysisResult, StockRecommendation


class TestScheduler:
    """Unit tests for Scheduler."""
    
    def test_initialization(self):
        """Test that Scheduler initializes correctly."""
        scheduler = Scheduler()
        
        assert scheduler.analysis_executor is None
        assert scheduler.custom_schedule is None
        assert scheduler._scheduled_regions == []
    
    def test_initialization_with_executor(self):
        """Test that Scheduler initializes with an analysis executor."""
        mock_executor = Mock()
        scheduler = Scheduler(analysis_executor=mock_executor)
        
        assert scheduler.analysis_executor is mock_executor
    
    def test_schedule_daily_analysis_single_region(self):
        """
        Test scheduling daily analysis for a single region.
        Validates: Requirement 7.1
        """
        scheduler = Scheduler()
        regions = [MarketRegion.USA]
        
        scheduler.schedule_daily_analysis(regions)
        
        assert scheduler._scheduled_regions == regions
    
    def test_schedule_daily_analysis_multiple_regions(self):
        """
        Test scheduling daily analysis for multiple regions.
        Validates: Requirement 7.2
        """
        scheduler = Scheduler()
        regions = [MarketRegion.CHINA, MarketRegion.HONG_KONG, MarketRegion.USA]
        
        scheduler.schedule_daily_analysis(regions)
        
        assert scheduler._scheduled_regions == regions
    
    def test_schedule_daily_analysis_empty_regions(self):
        """Test scheduling with empty regions list."""
        scheduler = Scheduler()
        
        scheduler.schedule_daily_analysis([])
        
        assert scheduler._scheduled_regions == []
    
    def test_get_market_close_time_china(self):
        """Test getting market close time for China."""
        scheduler = Scheduler()
        
        close_time = scheduler.get_market_close_time(MarketRegion.CHINA)
        
        assert close_time == time(7, 0)
    
    def test_get_market_close_time_hong_kong(self):
        """Test getting market close time for Hong Kong."""
        scheduler = Scheduler()
        
        close_time = scheduler.get_market_close_time(MarketRegion.HONG_KONG)
        
        assert close_time == time(8, 0)
    
    def test_get_market_close_time_usa(self):
        """Test getting market close time for USA."""
        scheduler = Scheduler()
        
        close_time = scheduler.get_market_close_time(MarketRegion.USA)
        
        assert close_time == time(21, 0)
    
    def test_set_custom_schedule_valid_cron(self):
        """
        Test setting a valid custom schedule.
        Validates: Requirement 7.3
        """
        scheduler = Scheduler()
        
        # Valid cron expression: daily at 21:00
        result = scheduler.set_custom_schedule("0 21 * * *")
        
        assert result.is_ok()
        assert scheduler.custom_schedule == "0 21 * * *"
    
    def test_set_custom_schedule_valid_cron_multiple_times(self):
        """
        Test setting a custom schedule with multiple execution times.
        Validates: Requirement 7.3
        """
        scheduler = Scheduler()
        
        # Valid cron expression: daily at 9:00 and 21:00
        result = scheduler.set_custom_schedule("0 9,21 * * *")
        
        assert result.is_ok()
        assert scheduler.custom_schedule == "0 9,21 * * *"
    
    def test_set_custom_schedule_valid_cron_weekdays(self):
        """
        Test setting a custom schedule for weekdays only.
        Validates: Requirement 7.3
        """
        scheduler = Scheduler()
        
        # Valid cron expression: weekdays at 21:00
        result = scheduler.set_custom_schedule("0 21 * * 1-5")
        
        assert result.is_ok()
        assert scheduler.custom_schedule == "0 21 * * 1-5"
    
    def test_set_custom_schedule_invalid_cron(self):
        """
        Test that invalid cron expression is rejected.
        Validates: Requirement 7.3
        """
        scheduler = Scheduler()
        
        # Invalid cron expression
        result = scheduler.set_custom_schedule("invalid cron")
        
        assert result.is_err()
        assert "invalid" in result.error().lower()
    
    def test_set_custom_schedule_empty_string(self):
        """Test that empty cron expression is rejected."""
        scheduler = Scheduler()
        
        result = scheduler.set_custom_schedule("")
        
        assert result.is_err()
        assert "empty" in result.error().lower()
    
    def test_set_custom_schedule_whitespace_only(self):
        """Test that whitespace-only cron expression is rejected."""
        scheduler = Scheduler()
        
        result = scheduler.set_custom_schedule("   ")
        
        assert result.is_err()
        assert "empty" in result.error().lower()
    
    def test_get_next_execution_time_with_custom_schedule(self):
        """Test getting next execution time with custom schedule."""
        scheduler = Scheduler()
        scheduler.set_custom_schedule("0 21 * * *")
        
        next_time = scheduler.get_next_execution_time()
        
        assert next_time is not None
        assert isinstance(next_time, datetime)
        assert next_time > datetime.now()
    
    def test_get_next_execution_time_with_scheduled_regions(self):
        """Test getting next execution time with scheduled regions."""
        scheduler = Scheduler()
        scheduler.schedule_daily_analysis([MarketRegion.USA])
        
        next_time = scheduler.get_next_execution_time()
        
        assert next_time is not None
        assert isinstance(next_time, datetime)
        # Should be at 21:00 (USA market close)
        assert next_time.time() == time(21, 0)
    
    def test_get_next_execution_time_no_schedule(self):
        """Test getting next execution time when no schedule is configured."""
        scheduler = Scheduler()
        
        next_time = scheduler.get_next_execution_time()
        
        assert next_time is None
    
    def test_execute_now_with_executor(self):
        """
        Test executing analysis immediately with configured executor.
        Validates: Requirement 7.1
        """
        mock_executor = Mock()
        mock_result = AnalysisResult(
            success=True,
            recommendations=[],
            error_message=None,
            retry_count=0
        )
        mock_executor.return_value = mock_result
        
        scheduler = Scheduler(analysis_executor=mock_executor)
        scheduler.schedule_daily_analysis([MarketRegion.USA])
        
        result = scheduler.execute_now()
        
        assert result.success
        mock_executor.assert_called_once_with([MarketRegion.USA])
    
    def test_execute_now_with_specific_regions(self):
        """Test executing analysis with specific regions."""
        mock_executor = Mock()
        mock_result = AnalysisResult(
            success=True,
            recommendations=[],
            error_message=None,
            retry_count=0
        )
        mock_executor.return_value = mock_result
        
        scheduler = Scheduler(analysis_executor=mock_executor)
        
        result = scheduler.execute_now(regions=[MarketRegion.CHINA])
        
        assert result.success
        mock_executor.assert_called_once_with([MarketRegion.CHINA])
    
    def test_execute_now_without_executor(self):
        """Test that executing without executor raises error."""
        scheduler = Scheduler()
        
        with pytest.raises(ValueError, match="No analysis executor configured"):
            scheduler.execute_now()
    
    def test_execute_now_no_regions(self):
        """Test executing analysis with no regions specified."""
        mock_executor = Mock()
        scheduler = Scheduler(analysis_executor=mock_executor)
        
        result = scheduler.execute_now()
        
        assert result.success
        assert len(result.recommendations) == 0
        assert "No regions specified" in result.error_message
        # Executor should not be called when no regions
        mock_executor.assert_not_called()
    
    def test_execute_now_executor_exception(self):
        """Test handling of executor exceptions."""
        mock_executor = Mock()
        mock_executor.side_effect = Exception("Executor error")
        
        scheduler = Scheduler(analysis_executor=mock_executor)
        scheduler.schedule_daily_analysis([MarketRegion.USA])
        
        result = scheduler.execute_now()
        
        assert not result.success
        assert "Executor error" in result.error_message
    
    def test_execute_now_with_failed_analysis(self):
        """Test executing analysis that fails."""
        mock_executor = Mock()
        mock_result = AnalysisResult(
            success=False,
            recommendations=[],
            error_message="Analysis failed",
            retry_count=3
        )
        mock_executor.return_value = mock_result
        
        scheduler = Scheduler(analysis_executor=mock_executor)
        scheduler.schedule_daily_analysis([MarketRegion.USA])
        
        result = scheduler.execute_now()
        
        assert not result.success
        assert result.error_message == "Analysis failed"
        assert result.retry_count == 3
    
    def test_latest_close_time_single_region(self):
        """Test getting latest close time for single region."""
        scheduler = Scheduler()
        
        latest = scheduler._get_latest_close_time([MarketRegion.CHINA])
        
        assert latest == time(7, 0)
    
    def test_latest_close_time_multiple_regions(self):
        """Test getting latest close time for multiple regions."""
        scheduler = Scheduler()
        
        # USA has the latest close time (21:00)
        latest = scheduler._get_latest_close_time([
            MarketRegion.CHINA,
            MarketRegion.HONG_KONG,
            MarketRegion.USA
        ])
        
        assert latest == time(21, 0)
    
    def test_custom_schedule_overrides_region_schedule(self):
        """Test that custom schedule takes precedence over region-based schedule."""
        scheduler = Scheduler()
        scheduler.schedule_daily_analysis([MarketRegion.USA])
        scheduler.set_custom_schedule("0 9 * * *")
        
        next_time = scheduler.get_next_execution_time()
        
        assert next_time is not None
        # Should use custom schedule (9:00), not USA close time (21:00)
        assert next_time.time() == time(9, 0)
    
    def test_integration_with_analysis_engine(self):
        """
        Test integration with Analysis_Engine execution.
        Validates: Requirements 7.1, 7.2, 7.3
        """
        # Create a mock that simulates Analysis_Engine.execute_scheduled_analysis
        mock_executor = Mock()
        mock_recommendations = [
            Mock(spec=StockRecommendation),
            Mock(spec=StockRecommendation)
        ]
        mock_result = AnalysisResult(
            success=True,
            recommendations=mock_recommendations,
            error_message=None,
            retry_count=0
        )
        mock_executor.return_value = mock_result
        
        scheduler = Scheduler(analysis_executor=mock_executor)
        scheduler.schedule_daily_analysis([
            MarketRegion.CHINA,
            MarketRegion.HONG_KONG,
            MarketRegion.USA
        ])
        
        result = scheduler.execute_now()
        
        assert result.success
        assert len(result.recommendations) == 2
        mock_executor.assert_called_once()
