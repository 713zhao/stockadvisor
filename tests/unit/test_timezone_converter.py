"""
Unit tests for TimezoneConverter component.
"""

import pytest
from datetime import datetime, timedelta
import pytz

from stock_market_analysis.components.intraday.timezone_converter import TimezoneConverter


class TestTimezoneConverter:
    """Test suite for TimezoneConverter."""
    
    @pytest.fixture
    def converter(self):
        """Create a TimezoneConverter instance for testing."""
        return TimezoneConverter()
    
    def test_utc_to_china_standard_time(self, converter):
        """Test conversion from UTC to China Standard Time (UTC+8, no DST)."""
        # 2024-06-15 10:00:00 UTC should be 2024-06-15 18:00:00 CST
        utc_time = datetime(2024, 6, 15, 10, 0, 0, tzinfo=pytz.utc)
        local_time = converter.utc_to_local(utc_time, 'Asia/Shanghai')
        
        assert local_time.year == 2024
        assert local_time.month == 6
        assert local_time.day == 15
        assert local_time.hour == 18
        assert local_time.minute == 0
    
    def test_utc_to_hong_kong_time(self, converter):
        """Test conversion from UTC to Hong Kong Time (UTC+8, no DST)."""
        # 2024-06-15 10:00:00 UTC should be 2024-06-15 18:00:00 HKT
        utc_time = datetime(2024, 6, 15, 10, 0, 0, tzinfo=pytz.utc)
        local_time = converter.utc_to_local(utc_time, 'Asia/Hong_Kong')
        
        assert local_time.year == 2024
        assert local_time.month == 6
        assert local_time.day == 15
        assert local_time.hour == 18
        assert local_time.minute == 0
    
    def test_utc_to_eastern_time_winter(self, converter):
        """Test conversion from UTC to Eastern Time during winter (EST, UTC-5)."""
        # 2024-01-15 15:00:00 UTC should be 2024-01-15 10:00:00 EST
        utc_time = datetime(2024, 1, 15, 15, 0, 0, tzinfo=pytz.utc)
        local_time = converter.utc_to_local(utc_time, 'America/New_York')
        
        assert local_time.year == 2024
        assert local_time.month == 1
        assert local_time.day == 15
        assert local_time.hour == 10
        assert local_time.minute == 0
    
    def test_utc_to_eastern_time_summer(self, converter):
        """Test conversion from UTC to Eastern Time during summer (EDT, UTC-4)."""
        # 2024-06-15 14:00:00 UTC should be 2024-06-15 10:00:00 EDT
        utc_time = datetime(2024, 6, 15, 14, 0, 0, tzinfo=pytz.utc)
        local_time = converter.utc_to_local(utc_time, 'America/New_York')
        
        assert local_time.year == 2024
        assert local_time.month == 6
        assert local_time.day == 15
        assert local_time.hour == 10
        assert local_time.minute == 0
    
    def test_dst_transition_spring_forward(self, converter):
        """Test DST transition on March 10, 2024 (spring forward)."""
        # March 10, 2024 at 2:00 AM EST becomes 3:00 AM EDT
        # 2024-03-10 07:00:00 UTC should be 2024-03-10 03:00:00 EDT
        utc_time = datetime(2024, 3, 10, 7, 0, 0, tzinfo=pytz.utc)
        local_time = converter.utc_to_local(utc_time, 'America/New_York')
        
        assert local_time.hour == 3  # Should be 3 AM EDT, not 2 AM
    
    def test_dst_transition_fall_back(self, converter):
        """Test DST transition on November 3, 2024 (fall back)."""
        # November 3, 2024 at 2:00 AM EDT becomes 1:00 AM EST
        # 2024-11-03 06:00:00 UTC should be 2024-11-03 01:00:00 EST
        utc_time = datetime(2024, 11, 3, 6, 0, 0, tzinfo=pytz.utc)
        local_time = converter.utc_to_local(utc_time, 'America/New_York')
        
        assert local_time.hour == 1  # Should be 1 AM EST
    
    def test_local_to_utc_china(self, converter):
        """Test conversion from China Standard Time to UTC."""
        # 2024-06-15 18:00:00 CST should be 2024-06-15 10:00:00 UTC
        cst_tz = pytz.timezone('Asia/Shanghai')
        local_time = cst_tz.localize(datetime(2024, 6, 15, 18, 0, 0))
        utc_time = converter.local_to_utc(local_time, 'Asia/Shanghai')
        
        assert utc_time.hour == 10
        assert utc_time.tzinfo == pytz.utc
    
    def test_local_to_utc_eastern_winter(self, converter):
        """Test conversion from Eastern Time to UTC during winter."""
        # 2024-01-15 10:00:00 EST should be 2024-01-15 15:00:00 UTC
        est_tz = pytz.timezone('America/New_York')
        local_time = est_tz.localize(datetime(2024, 1, 15, 10, 0, 0))
        utc_time = converter.local_to_utc(local_time, 'America/New_York')
        
        assert utc_time.hour == 15
        assert utc_time.tzinfo == pytz.utc
    
    def test_edge_case_midnight(self, converter):
        """Test conversion at midnight."""
        utc_time = datetime(2024, 6, 15, 0, 0, 0, tzinfo=pytz.utc)
        local_time = converter.utc_to_local(utc_time, 'Asia/Shanghai')
        
        assert local_time.hour == 8
        assert local_time.day == 15
    
    def test_edge_case_noon(self, converter):
        """Test conversion at noon."""
        utc_time = datetime(2024, 6, 15, 12, 0, 0, tzinfo=pytz.utc)
        local_time = converter.utc_to_local(utc_time, 'Asia/Shanghai')
        
        assert local_time.hour == 20
        assert local_time.day == 15
    
    def test_edge_case_end_of_day(self, converter):
        """Test conversion at end of day."""
        utc_time = datetime(2024, 6, 15, 23, 59, 59, tzinfo=pytz.utc)
        local_time = converter.utc_to_local(utc_time, 'Asia/Shanghai')
        
        assert local_time.hour == 7
        assert local_time.day == 16  # Next day
    
    def test_invalid_timezone_name(self, converter):
        """Test handling of invalid timezone name."""
        utc_time = datetime(2024, 6, 15, 10, 0, 0, tzinfo=pytz.utc)
        
        with pytest.raises(pytz.exceptions.UnknownTimeZoneError):
            converter.utc_to_local(utc_time, 'Invalid/Timezone')
    
    def test_get_timezone_offset_china(self, converter):
        """Test getting timezone offset for China (always UTC+8)."""
        dt = datetime(2024, 6, 15, 10, 0, 0, tzinfo=pytz.utc)
        offset = converter.get_timezone_offset('Asia/Shanghai', dt)
        
        assert offset == timedelta(hours=8)
    
    def test_get_timezone_offset_eastern_winter(self, converter):
        """Test getting timezone offset for Eastern Time in winter (UTC-5)."""
        dt = datetime(2024, 1, 15, 10, 0, 0, tzinfo=pytz.utc)
        offset = converter.get_timezone_offset('America/New_York', dt)
        
        assert offset == timedelta(hours=-5)
    
    def test_get_timezone_offset_eastern_summer(self, converter):
        """Test getting timezone offset for Eastern Time in summer (UTC-4)."""
        dt = datetime(2024, 6, 15, 10, 0, 0, tzinfo=pytz.utc)
        offset = converter.get_timezone_offset('America/New_York', dt)
        
        assert offset == timedelta(hours=-4)
    
    def test_naive_datetime_handling(self, converter):
        """Test that naive datetimes are handled correctly."""
        # Naive datetime should be assumed as UTC
        naive_time = datetime(2024, 6, 15, 10, 0, 0)
        local_time = converter.utc_to_local(naive_time, 'Asia/Shanghai')
        
        assert local_time.hour == 18
