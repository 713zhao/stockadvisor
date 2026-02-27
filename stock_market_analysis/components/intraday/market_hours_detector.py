"""
Market hours detection for regional stock markets.
"""

import logging
from datetime import datetime, time, date
from typing import Optional, List, Tuple

from stock_market_analysis.models.market_region import MarketRegion
from stock_market_analysis.components.configuration_manager import ConfigurationManager
from .timezone_converter import TimezoneConverter


class MarketHoursDetector:
    """
    Determines if regional markets are currently open for trading.
    
    Supports:
    - China markets (SSE, SZSE): 09:30-15:00 CST (UTC+8)
    - Hong Kong market (HKEX): 09:30-16:00 HKT (UTC+8)
    - USA markets (NYSE, NASDAQ): 09:30-16:00 ET (UTC-5/UTC-4 with DST)
    """
    
    # Market trading hours in local timezone
    MARKET_HOURS = {
        MarketRegion.CHINA: {
            'open': time(9, 30),
            'close': time(15, 0),
            'timezone': 'Asia/Shanghai'  # UTC+8, no DST
        },
        MarketRegion.HONG_KONG: {
            'open': time(9, 30),
            'close': time(16, 0),
            'timezone': 'Asia/Hong_Kong'  # UTC+8, no DST
        },
        MarketRegion.USA: {
            'open': time(9, 30),
            'close': time(16, 0),
            'timezone': 'America/New_York'  # UTC-5/UTC-4 with DST
        }
    }
    
    def __init__(
        self,
        timezone_converter: TimezoneConverter,
        config_manager: ConfigurationManager,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize market hours detector.
        
        Args:
            timezone_converter: TimezoneConverter instance for time conversions
            config_manager: ConfigurationManager instance for holiday configuration
            logger: Optional logger instance
        """
        self.timezone_converter = timezone_converter
        self.config_manager = config_manager
        self.logger = logger or logging.getLogger(__name__)
        
        # Cache for loaded holidays
        self._holidays_cache = {}
    
    def is_market_open(
        self,
        region: MarketRegion,
        check_time: Optional[datetime] = None
    ) -> bool:
        """
        Check if a regional market is currently open.
        
        Args:
            region: Market region to check
            check_time: Time to check (defaults to current UTC time)
            
        Returns:
            True if market is open, False otherwise
        """
        try:
            # Use current UTC time if not specified
            if check_time is None:
                check_time = datetime.utcnow()
            
            # Ensure check_time is timezone-aware (UTC)
            if check_time.tzinfo is None:
                import pytz
                check_time = pytz.utc.localize(check_time)
            
            # Get market timezone
            market_info = self.MARKET_HOURS.get(region)
            if not market_info:
                self.logger.error(f"Unknown market region: {region}")
                return False
            
            # Convert to local market time
            local_time = self.timezone_converter.utc_to_local(
                check_time,
                market_info['timezone']
            )
            
            # Check if weekend
            if self.is_weekend(local_time):
                self.logger.debug(f"{region.value} market closed: weekend")
                return False
            
            # Check if holiday
            if self.is_market_holiday(region, local_time.date()):
                self.logger.debug(f"{region.value} market closed: holiday")
                return False
            
            # Check if within trading hours
            current_time = local_time.time()
            open_time = market_info['open']
            close_time = market_info['close']
            
            is_open = open_time <= current_time < close_time
            
            self.logger.debug(
                f"{region.value} market {'open' if is_open else 'closed'} at "
                f"{local_time.strftime('%Y-%m-%d %H:%M:%S %Z')}"
            )
            
            return is_open
            
        except Exception as e:
            self.logger.error(f"Error checking market status for {region.value}: {e}")
            return False
    
    def is_weekend(self, local_time: datetime) -> bool:
        """
        Check if the given time falls on a weekend.
        
        Args:
            local_time: Datetime in local timezone
            
        Returns:
            True if Saturday (5) or Sunday (6), False otherwise
        """
        return local_time.weekday() >= 5
    
    def is_market_holiday(self, region: MarketRegion, check_date: date) -> bool:
        """
        Check if the given date is a market holiday for the region.
        
        Args:
            region: Market region to check
            check_date: Date to check
            
        Returns:
            True if the date is a market holiday, False otherwise
        """
        try:
            # Load holidays for this region if not cached
            if region not in self._holidays_cache:
                self._holidays_cache[region] = self.load_holidays(region)
            
            holidays = self._holidays_cache[region]
            return check_date in holidays
            
        except Exception as e:
            self.logger.error(f"Error checking holiday for {region.value}: {e}")
            return False
    
    def get_market_hours(self, region: MarketRegion) -> Tuple[time, time]:
        """
        Get market open and close times in local timezone.
        
        Args:
            region: Market region
            
        Returns:
            Tuple of (open_time, close_time)
            
        Raises:
            ValueError: If region is not supported
        """
        market_info = self.MARKET_HOURS.get(region)
        if not market_info:
            raise ValueError(f"Unsupported market region: {region}")
        
        return market_info['open'], market_info['close']
    
    def load_holidays(self, region: MarketRegion) -> List[date]:
        """
        Load market holidays from configuration.
        
        Args:
            region: Market region
            
        Returns:
            List of holiday dates
        """
        try:
            # Get holidays from configuration
            holiday_strings = self.config_manager.get_market_holidays(region)
            
            # Parse date strings (YYYY-MM-DD format)
            holidays = []
            for holiday_str in holiday_strings:
                try:
                    # Parse YYYY-MM-DD format
                    holiday_date = datetime.strptime(holiday_str, '%Y-%m-%d').date()
                    holidays.append(holiday_date)
                except ValueError as e:
                    self.logger.warning(
                        f"Invalid holiday date format for {region.value}: {holiday_str}. "
                        f"Expected YYYY-MM-DD format."
                    )
            
            self.logger.info(f"Loaded {len(holidays)} holidays for {region.value}")
            return holidays
            
        except Exception as e:
            self.logger.error(f"Error loading holidays for {region.value}: {e}")
            return []
