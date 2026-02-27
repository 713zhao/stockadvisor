"""
Unit tests for MarketHoursDetector component.
"""

import pytest
from datetime import datetime, date, time
from unittest.mock import Mock, MagicMock
import pytz

from stock_market_analysis.models.market_region import MarketRegion
from stock_market_analysis.components.intraday.market_hours_detector import MarketHoursDetector
from stock_market_analysis.components.intraday.timezone_converter import TimezoneConverter
from stock_market_analysis.components.configuration_manager import ConfigurationManager


class TestMarketHoursDetector:
    """Test suite for MarketHoursDetector."""
    
    @pytest.fixture
    def timezone_converter(self):
        """Create a real TimezoneConverter instance."""
        return TimezoneConverter()
    
    @pytest.fixture
    def config_manager(self):
        """Create a mock ConfigurationManager."""
        mock_config = Mock(spec=ConfigurationManager)
        # Default: no holidays
        mock_config.get_market_holidays.return_value = []
        return mock_config
    
    @pytest.fixture
    def detector(self, timezone_converter, config_manager):
        """Create a MarketHoursDetector instance for testing."""
        return MarketHoursDetector(timezone_converter, config_manager)
    
    def test_china_market_hours_open(self, detector):
        """Test China market is open during trading hours (09:30-15:00 CST)."""
        # 2024-06-17 (Monday) 10:00 CST = 02:00 UTC
        check_time = datetime(2024, 6, 17, 2, 0, 0, tzinfo=pytz.utc)
        assert detector.is_market_open(MarketRegion.CHINA, check_time) is True
    
    def test_china_market_hours_closed_before_open(self, detector):
        """Test China market is closed before 09:30 CST."""
        # 2024-06-17 (Monday) 09:00 CST = 01:00 UTC
        check_time = datetime(2024, 6, 17, 1, 0, 0, tzinfo=pytz.utc)
        assert detector.is_market_open(MarketRegion.CHINA, check_time) is False
    
    def test_china_market_hours_closed_after_close(self, detector):
        """Test China market is closed after 15:00 CST."""
        # 2024-06-17 (Monday) 16:00 CST = 08:00 UTC
        check_time = datetime(2024, 6, 17, 8, 0, 0, tzinfo=pytz.utc)
        assert detector.is_market_open(MarketRegion.CHINA, check_time) is False
    
    def test_hong_kong_market_hours_open(self, detector):
        """Test Hong Kong market is open during trading hours (09:30-16:00 HKT)."""
        # 2024-06-17 (Monday) 10:00 HKT = 02:00 UTC
        check_time = datetime(2024, 6, 17, 2, 0, 0, tzinfo=pytz.utc)
        assert detector.is_market_open(MarketRegion.HONG_KONG, check_time) is True
    
    def test_hong_kong_market_hours_closed_after_close(self, detector):
        """Test Hong Kong market is closed after 16:00 HKT."""
        # 2024-06-17 (Monday) 17:00 HKT = 09:00 UTC
        check_time = datetime(2024, 6, 17, 9, 0, 0, tzinfo=pytz.utc)
        assert detector.is_market_open(MarketRegion.HONG_KONG, check_time) is False
    
    def test_usa_market_hours_open_winter(self, detector):
        """Test USA market is open during trading hours in winter (09:30-16:00 EST)."""
        # 2024-01-15 (Monday) 10:00 EST = 15:00 UTC
        check_time = datetime(2024, 1, 15, 15, 0, 0, tzinfo=pytz.utc)
        assert detector.is_market_open(MarketRegion.USA, check_time) is True
    
    def test_usa_market_hours_open_summer(self, detector):
        """Test USA market is open during trading hours in summer (09:30-16:00 EDT)."""
        # 2024-06-17 (Monday) 10:00 EDT = 14:00 UTC
        check_time = datetime(2024, 6, 17, 14, 0, 0, tzinfo=pytz.utc)
        assert detector.is_market_open(MarketRegion.USA, check_time) is True
    
    def test_usa_market_hours_closed_after_close(self, detector):
        """Test USA market is closed after 16:00 ET."""
        # 2024-06-17 (Monday) 17:00 EDT = 21:00 UTC
        check_time = datetime(2024, 6, 17, 21, 0, 0, tzinfo=pytz.utc)
        assert detector.is_market_open(MarketRegion.USA, check_time) is False
    
    def test_weekend_saturday(self, detector):
        """Test market is closed on Saturday."""
        # 2024-06-15 (Saturday) 10:00 CST = 02:00 UTC
        check_time = datetime(2024, 6, 15, 2, 0, 0, tzinfo=pytz.utc)
        assert detector.is_market_open(MarketRegion.CHINA, check_time) is False
    
    def test_weekend_sunday(self, detector):
        """Test market is closed on Sunday."""
        # 2024-06-16 (Sunday) 10:00 CST = 02:00 UTC
        check_time = datetime(2024, 6, 16, 2, 0, 0, tzinfo=pytz.utc)
        assert detector.is_market_open(MarketRegion.CHINA, check_time) is False
    
    def test_weekend_edge_friday_2359(self, detector):
        """Test market status at Friday 23:59."""
        # 2024-06-14 (Friday) 23:59 CST = 15:59 UTC
        check_time = datetime(2024, 6, 14, 15, 59, 0, tzinfo=pytz.utc)
        # Market closes at 15:00 CST, so should be closed
        assert detector.is_market_open(MarketRegion.CHINA, check_time) is False
    
    def test_weekend_edge_saturday_0000(self, detector):
        """Test market status at Saturday 00:00."""
        # 2024-06-15 (Saturday) 00:00 CST = 16:00 UTC (previous day)
        check_time = datetime(2024, 6, 14, 16, 0, 0, tzinfo=pytz.utc)
        # This is actually Friday 16:00 UTC = Saturday 00:00 CST
        # Need to check Saturday in CST
        check_time = datetime(2024, 6, 15, 0, 0, 0, tzinfo=pytz.utc)  # Saturday 08:00 CST
        assert detector.is_market_open(MarketRegion.CHINA, check_time) is False
    
    def test_weekend_edge_sunday_2359(self, detector):
        """Test market status at Sunday 23:59."""
        # 2024-06-16 (Sunday) 23:59 CST
        check_time = datetime(2024, 6, 16, 15, 59, 0, tzinfo=pytz.utc)
        assert detector.is_market_open(MarketRegion.CHINA, check_time) is False
    
    def test_weekend_edge_monday_0000(self, detector):
        """Test market status at Monday 00:00."""
        # 2024-06-17 (Monday) 00:00 CST = 16:00 UTC (previous day)
        check_time = datetime(2024, 6, 16, 16, 0, 0, tzinfo=pytz.utc)
        # Market not open yet (opens at 09:30)
        assert detector.is_market_open(MarketRegion.CHINA, check_time) is False
    
    def test_holiday_new_year(self, detector, config_manager):
        """Test market is closed on New Year's Day (2024-01-01)."""
        config_manager.get_market_holidays.return_value = ['2024-01-01']
        detector._holidays_cache = {}  # Clear cache
        
        # 2024-01-01 (Monday) 10:00 CST = 02:00 UTC
        check_time = datetime(2024, 1, 1, 2, 0, 0, tzinfo=pytz.utc)
        assert detector.is_market_open(MarketRegion.CHINA, check_time) is False
    
    def test_holiday_independence_day(self, detector, config_manager):
        """Test USA market is closed on Independence Day (2024-07-04)."""
        config_manager.get_market_holidays.return_value = ['2024-07-04']
        detector._holidays_cache = {}  # Clear cache
        
        # 2024-07-04 (Thursday) 10:00 EDT = 14:00 UTC
        check_time = datetime(2024, 7, 4, 14, 0, 0, tzinfo=pytz.utc)
        assert detector.is_market_open(MarketRegion.USA, check_time) is False
    
    def test_invalid_holiday_date_format(self, detector, config_manager):
        """Test handling of invalid holiday date format."""
        config_manager.get_market_holidays.return_value = ['2024/01/01', 'invalid-date']
        detector._holidays_cache = {}  # Clear cache
        
        holidays = detector.load_holidays(MarketRegion.CHINA)
        # Should return empty list or skip invalid dates
        assert len(holidays) == 0
    
    def test_get_market_hours_china(self, detector):
        """Test getting market hours for China."""
        open_time, close_time = detector.get_market_hours(MarketRegion.CHINA)
        assert open_time == time(9, 30)
        assert close_time == time(15, 0)
    
    def test_get_market_hours_hong_kong(self, detector):
        """Test getting market hours for Hong Kong."""
        open_time, close_time = detector.get_market_hours(MarketRegion.HONG_KONG)
        assert open_time == time(9, 30)
        assert close_time == time(16, 0)
    
    def test_get_market_hours_usa(self, detector):
        """Test getting market hours for USA."""
        open_time, close_time = detector.get_market_hours(MarketRegion.USA)
        assert open_time == time(9, 30)
        assert close_time == time(16, 0)
    
    def test_is_weekend_method(self, detector):
        """Test is_weekend method."""
        # Saturday
        saturday = datetime(2024, 6, 15, 10, 0, 0)
        assert detector.is_weekend(saturday) is True
        
        # Sunday
        sunday = datetime(2024, 6, 16, 10, 0, 0)
        assert detector.is_weekend(sunday) is True
        
        # Monday
        monday = datetime(2024, 6, 17, 10, 0, 0)
        assert detector.is_weekend(monday) is False
        
        # Friday
        friday = datetime(2024, 6, 14, 10, 0, 0)
        assert detector.is_weekend(friday) is False
    
    def test_is_market_holiday_method(self, detector, config_manager):
        """Test is_market_holiday method."""
        config_manager.get_market_holidays.return_value = ['2024-01-01', '2024-07-04']
        detector._holidays_cache = {}  # Clear cache
        
        # Holiday
        assert detector.is_market_holiday(MarketRegion.USA, date(2024, 1, 1)) is True
        assert detector.is_market_holiday(MarketRegion.USA, date(2024, 7, 4)) is True
        
        # Not a holiday
        assert detector.is_market_holiday(MarketRegion.USA, date(2024, 6, 17)) is False
    
    def test_default_check_time_uses_current_time(self, detector):
        """Test that is_market_open uses current time when check_time is None."""
        # This test just verifies it doesn't crash
        result = detector.is_market_open(MarketRegion.CHINA)
        assert isinstance(result, bool)
