"""
Unit tests for the Market Monitor component.
"""

import pytest
from datetime import datetime
from decimal import Decimal

from stock_market_analysis.models import MarketRegion, MarketData
from stock_market_analysis.components import MarketMonitor, MockMarketDataAPI


class TestMarketMonitor:
    """Unit tests for MarketMonitor component."""
    
    def test_collect_market_data_single_region(self):
        """Test collecting data from a single region."""
        # Arrange
        api = MockMarketDataAPI()
        monitor = MarketMonitor(api)
        regions = [MarketRegion.USA]
        
        # Act
        result = monitor.collect_market_data(regions)
        
        # Assert
        assert result is not None
        assert result.collection_time is not None
        assert MarketRegion.USA in result.data_by_region
        assert len(result.data_by_region[MarketRegion.USA]) > 0
        assert len(result.failed_regions) == 0
    
    def test_collect_market_data_multiple_regions(self):
        """Test collecting data from multiple regions."""
        # Arrange
        api = MockMarketDataAPI()
        monitor = MarketMonitor(api)
        regions = [MarketRegion.USA, MarketRegion.CHINA, MarketRegion.HONG_KONG]
        
        # Act
        result = monitor.collect_market_data(regions)
        
        # Assert
        assert result is not None
        assert len(result.data_by_region) == 3
        assert MarketRegion.USA in result.data_by_region
        assert MarketRegion.CHINA in result.data_by_region
        assert MarketRegion.HONG_KONG in result.data_by_region
        assert len(result.failed_regions) == 0
    
    def test_collect_market_data_with_region_failure(self):
        """Test graceful handling of region failures."""
        # Arrange
        failing_regions = [MarketRegion.CHINA]
        api = MockMarketDataAPI(failing_regions=failing_regions)
        monitor = MarketMonitor(api)
        regions = [MarketRegion.USA, MarketRegion.CHINA, MarketRegion.HONG_KONG]
        
        # Act
        result = monitor.collect_market_data(regions)
        
        # Assert
        assert result is not None
        # Should have data for USA and HONG_KONG
        assert len(result.data_by_region) == 2
        assert MarketRegion.USA in result.data_by_region
        assert MarketRegion.HONG_KONG in result.data_by_region
        # CHINA should be in failed regions
        assert MarketRegion.CHINA in result.failed_regions
        assert len(result.failed_regions) == 1
    
    def test_collect_market_data_all_regions_fail(self):
        """Test handling when all regions fail."""
        # Arrange
        failing_regions = [MarketRegion.USA, MarketRegion.CHINA, MarketRegion.HONG_KONG]
        api = MockMarketDataAPI(failing_regions=failing_regions)
        monitor = MarketMonitor(api)
        regions = [MarketRegion.USA, MarketRegion.CHINA, MarketRegion.HONG_KONG]
        
        # Act
        result = monitor.collect_market_data(regions)
        
        # Assert
        assert result is not None
        assert len(result.data_by_region) == 0
        assert len(result.failed_regions) == 3
        assert MarketRegion.USA in result.failed_regions
        assert MarketRegion.CHINA in result.failed_regions
        assert MarketRegion.HONG_KONG in result.failed_regions
    
    def test_market_data_has_timestamps(self):
        """Test that all collected market data has timestamps."""
        # Arrange
        api = MockMarketDataAPI()
        monitor = MarketMonitor(api)
        regions = [MarketRegion.USA]
        
        # Act
        result = monitor.collect_market_data(regions)
        
        # Assert
        for region, data_list in result.data_by_region.items():
            for data in data_list:
                assert data.timestamp is not None
                assert isinstance(data.timestamp, datetime)
    
    def test_get_last_collection_time(self):
        """Test tracking of last collection time per region."""
        # Arrange
        api = MockMarketDataAPI()
        monitor = MarketMonitor(api)
        
        # Initially no collection time
        assert monitor.get_last_collection_time(MarketRegion.USA) is None
        
        # Act
        result = monitor.collect_market_data([MarketRegion.USA])
        
        # Assert
        last_time = monitor.get_last_collection_time(MarketRegion.USA)
        assert last_time is not None
        assert isinstance(last_time, datetime)
        assert last_time == result.collection_time
    
    def test_get_last_collection_time_failed_region(self):
        """Test that failed regions don't update last collection time."""
        # Arrange
        failing_regions = [MarketRegion.CHINA]
        api = MockMarketDataAPI(failing_regions=failing_regions)
        monitor = MarketMonitor(api)
        
        # Act
        monitor.collect_market_data([MarketRegion.CHINA])
        
        # Assert
        # Failed region should not have a last collection time
        assert monitor.get_last_collection_time(MarketRegion.CHINA) is None
    
    def test_empty_regions_list(self):
        """Test collecting data with empty regions list."""
        # Arrange
        api = MockMarketDataAPI()
        monitor = MarketMonitor(api)
        
        # Act
        result = monitor.collect_market_data([])
        
        # Assert
        assert result is not None
        assert len(result.data_by_region) == 0
        assert len(result.failed_regions) == 0
        assert result.collection_time is not None
