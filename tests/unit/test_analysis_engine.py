"""
Unit tests for the Analysis Engine component.
"""

import pytest
from datetime import datetime, date
from decimal import Decimal

from stock_market_analysis.models import (
    MarketData,
    MarketDataCollection,
    MarketRegion,
    RecommendationType
)
from stock_market_analysis.components import AnalysisEngine


class TestAnalysisEngine:
    """Test suite for Analysis Engine component."""
    
    def test_analyze_with_valid_data(self):
        """Test that analysis generates recommendations for valid market data."""
        # Create test market data
        stock = MarketData(
            symbol="AAPL",
            name="Apple Inc.",
            region=MarketRegion.USA,
            timestamp=datetime.now(),
            open_price=Decimal("150.00"),
            close_price=Decimal("155.00"),  # 3.33% increase
            high_price=Decimal("156.00"),
            low_price=Decimal("149.00"),
            volume=1000000,
            additional_metrics={}
        )
        
        market_data = MarketDataCollection(
            collection_time=datetime.now(),
            data_by_region={MarketRegion.USA: [stock]},
            failed_regions=[]
        )
        
        # Analyze
        engine = AnalysisEngine()
        recommendations = engine.analyze_and_recommend(market_data)
        
        # Verify
        assert len(recommendations) == 1
        rec = recommendations[0]
        assert rec.symbol == "AAPL"
        assert rec.region == MarketRegion.USA
        assert rec.recommendation_type == RecommendationType.BUY
        assert rec.rationale != ""
        assert rec.risk_assessment != ""
        assert 0.0 <= rec.confidence_score <= 1.0
        assert rec.target_price is not None
        assert rec.generated_at is not None
    
    def test_insufficient_data_filtering(self):
        """Test that stocks with insufficient data are excluded."""
        # Create stock with insufficient volume
        low_volume_stock = MarketData(
            symbol="LOW",
            name="Low Volume Stock",
            region=MarketRegion.USA,
            timestamp=datetime.now(),
            open_price=Decimal("100.00"),
            close_price=Decimal("105.00"),
            high_price=Decimal("106.00"),
            low_price=Decimal("99.00"),
            volume=500,  # Below minimum
            additional_metrics={}
        )
        
        # Create stock with invalid price
        low_price_stock = MarketData(
            symbol="PENNY",
            name="Penny Stock",
            region=MarketRegion.USA,
            timestamp=datetime.now(),
            open_price=Decimal("0.005"),  # Below minimum
            close_price=Decimal("0.006"),
            high_price=Decimal("0.007"),
            low_price=Decimal("0.004"),
            volume=100000,
            additional_metrics={}
        )
        
        market_data = MarketDataCollection(
            collection_time=datetime.now(),
            data_by_region={MarketRegion.USA: [low_volume_stock, low_price_stock]},
            failed_regions=[]
        )
        
        # Analyze
        engine = AnalysisEngine()
        recommendations = engine.analyze_and_recommend(market_data)
        
        # Verify both stocks were filtered out
        assert len(recommendations) == 0
    
    def test_buy_recommendation_generation(self):
        """Test that strong upward momentum generates BUY recommendation."""
        stock = MarketData(
            symbol="BULL",
            name="Bullish Stock",
            region=MarketRegion.USA,
            timestamp=datetime.now(),
            open_price=Decimal("100.00"),
            close_price=Decimal("105.00"),  # 5% increase
            high_price=Decimal("106.00"),
            low_price=Decimal("99.00"),
            volume=500000,
            additional_metrics={}
        )
        
        market_data = MarketDataCollection(
            collection_time=datetime.now(),
            data_by_region={MarketRegion.USA: [stock]},
            failed_regions=[]
        )
        
        engine = AnalysisEngine()
        recommendations = engine.analyze_and_recommend(market_data)
        
        assert len(recommendations) == 1
        assert recommendations[0].recommendation_type == RecommendationType.BUY
        assert recommendations[0].target_price > stock.close_price
    
    def test_sell_recommendation_generation(self):
        """Test that strong downward momentum generates SELL recommendation."""
        stock = MarketData(
            symbol="BEAR",
            name="Bearish Stock",
            region=MarketRegion.USA,
            timestamp=datetime.now(),
            open_price=Decimal("100.00"),
            close_price=Decimal("95.00"),  # 5% decrease
            high_price=Decimal("101.00"),
            low_price=Decimal("94.00"),
            volume=50000000,  # High volume to confirm trend
            additional_metrics={
                'rsi': 75,  # Overbought
                'macd': -1.5,  # Bearish momentum
                'pe_ratio': 45,  # Overvalued
                'earnings_growth': -15,  # Declining earnings
                'volume_history': [30000000, 35000000, 40000000, 45000000, 48000000]
            }
        )
        
        market_data = MarketDataCollection(
            collection_time=datetime.now(),
            data_by_region={MarketRegion.USA: [stock]},
            failed_regions=[]
        )
        
        engine = AnalysisEngine()
        recommendations = engine.analyze_and_recommend(market_data)
        
        assert len(recommendations) == 1
        assert recommendations[0].recommendation_type == RecommendationType.SELL
        assert recommendations[0].target_price < stock.close_price
    
    def test_hold_recommendation_generation(self):
        """Test that minimal price movement generates HOLD recommendation."""
        stock = MarketData(
            symbol="STABLE",
            name="Stable Stock",
            region=MarketRegion.USA,
            timestamp=datetime.now(),
            open_price=Decimal("100.00"),
            close_price=Decimal("100.50"),  # 0.5% increase
            high_price=Decimal("101.00"),
            low_price=Decimal("99.50"),
            volume=500000,
            additional_metrics={}
        )
        
        market_data = MarketDataCollection(
            collection_time=datetime.now(),
            data_by_region={MarketRegion.USA: [stock]},
            failed_regions=[]
        )
        
        engine = AnalysisEngine()
        recommendations = engine.analyze_and_recommend(market_data)
        
        assert len(recommendations) == 1
        assert recommendations[0].recommendation_type == RecommendationType.HOLD
        assert recommendations[0].target_price is None
    
    def test_multiple_regions_analysis(self):
        """Test analysis across multiple market regions."""
        usa_stock = MarketData(
            symbol="AAPL",
            name="Apple Inc.",
            region=MarketRegion.USA,
            timestamp=datetime.now(),
            open_price=Decimal("150.00"),
            close_price=Decimal("155.00"),
            high_price=Decimal("156.00"),
            low_price=Decimal("149.00"),
            volume=1000000,
            additional_metrics={}
        )
        
        china_stock = MarketData(
            symbol="BABA",
            name="Alibaba Group",
            region=MarketRegion.CHINA,
            timestamp=datetime.now(),
            open_price=Decimal("80.00"),
            close_price=Decimal("76.00"),  # Downward
            high_price=Decimal("81.00"),
            low_price=Decimal("75.00"),
            volume=800000,
            additional_metrics={}
        )
        
        market_data = MarketDataCollection(
            collection_time=datetime.now(),
            data_by_region={
                MarketRegion.USA: [usa_stock],
                MarketRegion.CHINA: [china_stock]
            },
            failed_regions=[]
        )
        
        engine = AnalysisEngine()
        recommendations = engine.analyze_and_recommend(market_data)
        
        assert len(recommendations) == 2
        # Verify both regions are represented
        regions = {rec.region for rec in recommendations}
        assert MarketRegion.USA in regions
        assert MarketRegion.CHINA in regions
    
    def test_empty_market_data(self):
        """Test analysis with empty market data."""
        market_data = MarketDataCollection(
            collection_time=datetime.now(),
            data_by_region={},
            failed_regions=[]
        )
        
        engine = AnalysisEngine()
        recommendations = engine.analyze_and_recommend(market_data)
        
        assert len(recommendations) == 0
    
    def test_recommendation_completeness(self):
        """Test that all recommendations have required fields populated."""
        stock = MarketData(
            symbol="TEST",
            name="Test Stock",
            region=MarketRegion.USA,
            timestamp=datetime.now(),
            open_price=Decimal("100.00"),
            close_price=Decimal("104.00"),
            high_price=Decimal("105.00"),
            low_price=Decimal("99.00"),
            volume=500000,
            additional_metrics={}
        )
        
        market_data = MarketDataCollection(
            collection_time=datetime.now(),
            data_by_region={MarketRegion.USA: [stock]},
            failed_regions=[]
        )
        
        engine = AnalysisEngine()
        recommendations = engine.analyze_and_recommend(market_data)
        
        assert len(recommendations) == 1
        rec = recommendations[0]
        
        # Verify all required fields are present and valid
        assert rec.symbol is not None and rec.symbol != ""
        assert rec.region is not None
        assert rec.recommendation_type in [RecommendationType.BUY, RecommendationType.SELL, RecommendationType.HOLD]
        assert rec.rationale is not None and rec.rationale != ""
        assert rec.risk_assessment is not None and rec.risk_assessment != ""
        assert rec.confidence_score >= 0.0 and rec.confidence_score <= 1.0
        assert rec.generated_at is not None
    
    def test_invalid_price_consistency(self):
        """Test that stocks with inconsistent prices are filtered out."""
        # High price less than low price
        invalid_stock = MarketData(
            symbol="INVALID",
            name="Invalid Stock",
            region=MarketRegion.USA,
            timestamp=datetime.now(),
            open_price=Decimal("100.00"),
            close_price=Decimal("100.00"),
            high_price=Decimal("95.00"),  # Invalid: high < low
            low_price=Decimal("105.00"),
            volume=500000,
            additional_metrics={}
        )
        
        market_data = MarketDataCollection(
            collection_time=datetime.now(),
            data_by_region={MarketRegion.USA: [invalid_stock]},
            failed_regions=[]
        )
        
        engine = AnalysisEngine()
        recommendations = engine.analyze_and_recommend(market_data)
        
        assert len(recommendations) == 0


class TestScheduledAnalysis:
    """Test suite for scheduled analysis with retry logic."""
    
    def test_execute_scheduled_analysis_success(self):
        """Test successful scheduled analysis execution."""
        from stock_market_analysis.components import MarketMonitor
        
        # Setup
        market_monitor = MarketMonitor()
        engine = AnalysisEngine(market_monitor=market_monitor)
        
        # Execute with explicit regions
        result = engine.execute_scheduled_analysis(regions=[MarketRegion.USA])
        
        # Verify
        assert result.success is True
        assert result.error_message is None
        assert result.retry_count == 0
        assert isinstance(result.recommendations, list)
    
    def test_execute_scheduled_analysis_with_regions(self):
        """Test scheduled analysis with specific regions."""
        from stock_market_analysis.components import MarketMonitor
        
        # Setup
        market_monitor = MarketMonitor()
        engine = AnalysisEngine(market_monitor=market_monitor)
        
        # Execute with specific regions
        result = engine.execute_scheduled_analysis(regions=[MarketRegion.USA])
        
        # Verify
        assert result.success is True
        assert result.retry_count == 0
    
    def test_execute_scheduled_analysis_retry_on_failure(self):
        """Test that analysis retries on failure."""
        from unittest.mock import Mock, patch
        from stock_market_analysis.components import MarketMonitor
        
        # Setup
        market_monitor = MarketMonitor()
        engine = AnalysisEngine(market_monitor=market_monitor)
        
        # Mock collect_market_data to fail twice then succeed
        call_count = 0
        original_collect = market_monitor.collect_market_data
        
        def failing_collect(regions):
            nonlocal call_count
            call_count += 1
            if call_count <= 2:
                raise Exception("Temporary failure")
            return original_collect(regions)
        
        market_monitor.collect_market_data = failing_collect
        
        # Execute with mocked sleep to avoid delays
        with patch('time.sleep'):
            result = engine.execute_scheduled_analysis(regions=[MarketRegion.USA])
        
        # Verify retry happened
        assert result.success is True
        assert result.retry_count == 2  # Failed twice, succeeded on third attempt
        assert call_count == 3
    
    def test_execute_scheduled_analysis_all_retries_fail(self):
        """Test that analysis fails after exhausting all retries."""
        from unittest.mock import Mock, patch
        from stock_market_analysis.components import MarketMonitor
        
        # Setup
        market_monitor = MarketMonitor()
        
        # Track admin notifications
        admin_messages = []
        
        def mock_admin_notifier(message: str):
            admin_messages.append(message)
        
        engine = AnalysisEngine(
            market_monitor=market_monitor,
            admin_notifier=mock_admin_notifier
        )
        
        # Mock collect_market_data to always fail
        def always_fail(regions):
            raise Exception("Persistent failure")
        
        market_monitor.collect_market_data = always_fail
        
        # Execute with mocked sleep to avoid delays
        with patch('time.sleep'):
            result = engine.execute_scheduled_analysis(regions=[MarketRegion.USA])
        
        # Verify failure after all retries
        assert result.success is False
        assert result.retry_count == 3
        assert result.error_message is not None
        assert "failed after 3 retry attempts" in result.error_message.lower()
        assert len(result.recommendations) == 0
        
        # Verify administrator was notified
        assert len(admin_messages) == 1
        assert "failed after 3 retry attempts" in admin_messages[0].lower()
    
    def test_execute_scheduled_analysis_retry_interval(self):
        """Test that retry interval is respected."""
        from unittest.mock import Mock, patch
        from stock_market_analysis.components import MarketMonitor
        
        # Setup
        market_monitor = MarketMonitor()
        engine = AnalysisEngine(market_monitor=market_monitor)
        
        # Mock to fail twice
        call_count = 0
        
        def failing_collect(regions):
            nonlocal call_count
            call_count += 1
            if call_count <= 2:
                raise Exception("Temporary failure")
            return MarketDataCollection(
                collection_time=datetime.now(),
                data_by_region={},
                failed_regions=[]
            )
        
        market_monitor.collect_market_data = failing_collect
        
        # Track sleep calls
        sleep_calls = []
        
        def mock_sleep(seconds):
            sleep_calls.append(seconds)
        
        # Execute with mocked sleep
        with patch('time.sleep', side_effect=mock_sleep):
            result = engine.execute_scheduled_analysis(regions=[MarketRegion.USA])
        
        # Verify sleep was called with correct interval (5 minutes = 300 seconds)
        assert len(sleep_calls) == 2  # Two retries, so two sleeps
        assert all(s == 300 for s in sleep_calls)
    
    def test_execute_scheduled_analysis_no_market_monitor(self):
        """Test that analysis fails gracefully without market monitor."""
        from unittest.mock import patch
        
        engine = AnalysisEngine()  # No market monitor
        
        # Execute with mocked sleep
        with patch('time.sleep'):
            result = engine.execute_scheduled_analysis(regions=[MarketRegion.USA])
        
        # Verify failure
        assert result.success is False
        assert result.retry_count == 3
        assert "market monitor not configured" in result.error_message.lower()
    
    def test_execute_scheduled_analysis_no_admin_notifier(self):
        """Test that analysis handles missing admin notifier gracefully."""
        from unittest.mock import patch
        from stock_market_analysis.components import MarketMonitor
        
        # Setup without admin notifier
        market_monitor = MarketMonitor()
        engine = AnalysisEngine(market_monitor=market_monitor)  # No admin_notifier
        
        # Mock to always fail
        def always_fail(regions):
            raise Exception("Persistent failure")
        
        market_monitor.collect_market_data = always_fail
        
        # Execute with mocked sleep - should not raise exception
        with patch('time.sleep'):
            result = engine.execute_scheduled_analysis(regions=[MarketRegion.USA])
        
        # Verify failure was handled
        assert result.success is False
        assert result.retry_count == 3
    
    def test_execute_scheduled_analysis_admin_notifier_fails(self):
        """Test that analysis continues even if admin notification fails."""
        from unittest.mock import patch
        from stock_market_analysis.components import MarketMonitor
        
        # Setup with failing admin notifier
        market_monitor = MarketMonitor()
        
        def failing_notifier(message: str):
            raise Exception("Notification system down")
        
        engine = AnalysisEngine(
            market_monitor=market_monitor,
            admin_notifier=failing_notifier
        )
        
        # Mock to always fail
        def always_fail(regions):
            raise Exception("Persistent failure")
        
        market_monitor.collect_market_data = always_fail
        
        # Execute with mocked sleep - should not raise exception
        with patch('time.sleep'):
            result = engine.execute_scheduled_analysis(regions=[MarketRegion.USA])
        
        # Verify analysis failure was still recorded
        assert result.success is False
        assert result.retry_count == 3
    
    def test_retry_count_in_successful_result(self):
        """Test that retry count is correctly recorded in successful result."""
        from unittest.mock import patch
        from stock_market_analysis.components import MarketMonitor
        
        # Setup
        market_monitor = MarketMonitor()
        engine = AnalysisEngine(market_monitor=market_monitor)
        
        # Mock to fail once then succeed
        call_count = 0
        original_collect = market_monitor.collect_market_data
        
        def failing_once(regions):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise Exception("First attempt fails")
            return original_collect(regions)
        
        market_monitor.collect_market_data = failing_once
        
        # Execute with mocked sleep
        with patch('time.sleep'):
            result = engine.execute_scheduled_analysis(regions=[MarketRegion.USA])
        
        # Verify success with correct retry count
        assert result.success is True
        assert result.retry_count == 1  # One retry before success
