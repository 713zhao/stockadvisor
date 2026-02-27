"""
Timezone conversion utilities with daylight saving time support.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional
import pytz


class TimezoneConverter:
    """
    Handles timezone conversions with daylight saving time support.
    
    Supports:
    - China Standard Time (UTC+8, no DST)
    - Hong Kong Time (UTC+8, no DST)
    - USA Eastern Time (UTC-5/UTC-4 with DST)
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize timezone converter.
        
        Args:
            logger: Optional logger instance for logging conversion operations
        """
        self.logger = logger or logging.getLogger(__name__)
    
    def utc_to_local(self, utc_time: datetime, timezone_name: str) -> datetime:
        """
        Convert UTC time to local timezone.
        
        Args:
            utc_time: Time in UTC (must be timezone-aware or will be assumed UTC)
            timezone_name: Target timezone (e.g., 'America/New_York', 'Asia/Shanghai')
            
        Returns:
            Time in local timezone
            
        Raises:
            pytz.exceptions.UnknownTimeZoneError: If timezone_name is invalid
        """
        try:
            # Ensure utc_time is timezone-aware
            if utc_time.tzinfo is None:
                utc_time = pytz.utc.localize(utc_time)
            elif utc_time.tzinfo != pytz.utc:
                # Convert to UTC if it's in a different timezone
                utc_time = utc_time.astimezone(pytz.utc)
            
            # Get target timezone
            target_tz = pytz.timezone(timezone_name)
            
            # Convert to target timezone
            local_time = utc_time.astimezone(target_tz)
            
            self.logger.debug(
                f"Converted {utc_time} UTC to {local_time} {timezone_name}"
            )
            
            return local_time
            
        except pytz.exceptions.UnknownTimeZoneError as e:
            self.logger.error(f"Unknown timezone: {timezone_name}")
            raise
        except Exception as e:
            self.logger.error(f"Error converting UTC to local time: {e}")
            raise
    
    def local_to_utc(self, local_time: datetime, timezone_name: str) -> datetime:
        """
        Convert local time to UTC.
        
        Args:
            local_time: Time in local timezone (naive or aware)
            timezone_name: Source timezone (e.g., 'America/New_York', 'Asia/Shanghai')
            
        Returns:
            Time in UTC
            
        Raises:
            pytz.exceptions.UnknownTimeZoneError: If timezone_name is invalid
        """
        try:
            # Get source timezone
            source_tz = pytz.timezone(timezone_name)
            
            # If local_time is naive, localize it
            if local_time.tzinfo is None:
                local_time = source_tz.localize(local_time)
            
            # Convert to UTC
            utc_time = local_time.astimezone(pytz.utc)
            
            self.logger.debug(
                f"Converted {local_time} {timezone_name} to {utc_time} UTC"
            )
            
            return utc_time
            
        except pytz.exceptions.UnknownTimeZoneError as e:
            self.logger.error(f"Unknown timezone: {timezone_name}")
            raise
        except Exception as e:
            self.logger.error(f"Error converting local time to UTC: {e}")
            raise
    
    def get_timezone_offset(self, timezone_name: str, dt: datetime) -> timedelta:
        """
        Get UTC offset for a timezone at a specific datetime.
        Handles daylight saving time transitions.
        
        Args:
            timezone_name: Timezone name (e.g., 'America/New_York')
            dt: Datetime to check offset for
            
        Returns:
            UTC offset as timedelta
            
        Raises:
            pytz.exceptions.UnknownTimeZoneError: If timezone_name is invalid
        """
        try:
            tz = pytz.timezone(timezone_name)
            
            # Ensure dt is timezone-aware
            if dt.tzinfo is None:
                dt = pytz.utc.localize(dt)
            
            # Convert to target timezone to get the offset
            local_dt = dt.astimezone(tz)
            offset = local_dt.utcoffset()
            
            self.logger.debug(
                f"Timezone {timezone_name} offset at {dt}: {offset}"
            )
            
            return offset
            
        except pytz.exceptions.UnknownTimeZoneError as e:
            self.logger.error(f"Unknown timezone: {timezone_name}")
            raise
        except Exception as e:
            self.logger.error(f"Error getting timezone offset: {e}")
            raise
