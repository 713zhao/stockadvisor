"""
Market Monitor component for the stock market analysis system.

Collects stock market data from configured regions with graceful failure handling.
"""

import logging
from datetime import datetime
from typing import List, Optional, Dict
from decimal import Decimal

from ..models import (
    MarketRegion,
    MarketData,
    MarketDataCollection
)


class MarketDataAPI:
    """
    Interface for external market data APIs.
    
    This is a mock implementation that can be replaced with real API integrations.
    """
    
    def fetch_market_data(self, region: MarketRegion) -> List[MarketData]:
        """
        Fetches market data for a specific region.
        
        Args:
            region: Market region to fetch data for
            
        Returns:
            List of MarketData for stocks in the region
            
        Raises:
            Exception: If data fetching fails
        """
        # Mock implementation - replace with real API calls
        # This would integrate with services like Alpha Vantage, Yahoo Finance, etc.
        raise NotImplementedError("Market data API integration not yet implemented")


class MarketMonitor:
    """
    Monitors and collects stock market data from configured regions.
    
    Responsibilities:
    - Collect stock market data from configured regions
    - Handle data source unavailability gracefully
    - Timestamp collected data
    - Track last collection time per region
    """
    
    def __init__(self, api: Optional[MarketDataAPI] = None):
        """
        Initialize the Market Monitor.
        
        Args:
            api: Market data API instance. If None, creates default instance.
        """
        self.logger = logging.getLogger(__name__)
        self.api = api or MarketDataAPI()
        self._last_collection_times: Dict[MarketRegion, datetime] = {}
    
    def collect_market_data(self, regions: List[MarketRegion]) -> MarketDataCollection:
        """
        Collects market data from specified regions.
        
        Args:
            regions: List of market regions to monitor
            
        Returns:
            MarketDataCollection containing data from all available regions
            
        Note:
            Does not raise exceptions - logs errors and continues with available regions.
            Failed regions are tracked in the failed_regions list.
        """
        collection_time = datetime.now()
        data_by_region: Dict[MarketRegion, List[MarketData]] = {}
        failed_regions: List[MarketRegion] = []
        
        self.logger.info(f"Starting market data collection for {len(regions)} regions")
        
        for region in regions:
            try:
                self.logger.debug(f"Collecting data for region: {region.value}")
                
                # Fetch data from API
                market_data = self.api.fetch_market_data(region)
                
                # Ensure all data has timestamps
                for data in market_data:
                    if data.timestamp is None:
                        data.timestamp = collection_time
                
                data_by_region[region] = market_data
                self._last_collection_times[region] = collection_time
                
                self.logger.info(
                    f"Successfully collected {len(market_data)} stocks from {region.value}"
                )
                
            except Exception as e:
                # Log error but continue with other regions
                self.logger.error(
                    f"Failed to collect data for region {region.value}: {e}",
                    exc_info=True
                )
                failed_regions.append(region)
        
        # Log summary
        success_count = len(data_by_region)
        failure_count = len(failed_regions)
        self.logger.info(
            f"Market data collection completed: {success_count} regions succeeded, "
            f"{failure_count} regions failed"
        )
        
        return MarketDataCollection(
            collection_time=collection_time,
            data_by_region=data_by_region,
            failed_regions=failed_regions
        )
    
    def get_last_collection_time(self, region: MarketRegion) -> Optional[datetime]:
        """
        Returns the timestamp of the last successful data collection for a region.
        
        Args:
            region: Market region to query
            
        Returns:
            Datetime of last collection, or None if never collected
        """
        return self._last_collection_times.get(region)
