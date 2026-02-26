"""
Mock market data API for testing and development.

This module provides a mock implementation of the MarketDataAPI interface
that generates realistic-looking test data without requiring external API calls.
"""

import random
from datetime import datetime
from decimal import Decimal
from typing import List

from ..models import MarketRegion, MarketData
from .market_monitor import MarketDataAPI


class MockMarketDataAPI(MarketDataAPI):
    """
    Mock implementation of MarketDataAPI for testing.
    
    Generates realistic-looking market data without external API calls.
    Can be configured to simulate failures for specific regions.
    """
    
    def __init__(self, failing_regions: List[MarketRegion] = None):
        """
        Initialize the mock API.
        
        Args:
            failing_regions: List of regions that should fail when fetched.
                           Used to test error handling.
        """
        self.failing_regions = failing_regions or []
        
        # Sample stock symbols and names by region
        self._stocks_by_region = {
            MarketRegion.CHINA: [
                ("600000.SS", "Shanghai Pudong Development Bank"),
                ("600036.SS", "China Merchants Bank"),
                ("601398.SS", "Industrial and Commercial Bank of China"),
                ("601857.SS", "PetroChina Company Limited"),
                ("601988.SS", "Bank of China")
            ],
            MarketRegion.HONG_KONG: [
                ("0001.HK", "CK Hutchison Holdings Limited"),
                ("0005.HK", "HSBC Holdings plc"),
                ("0011.HK", "Hang Seng Bank Limited"),
                ("0388.HK", "Hong Kong Exchanges and Clearing Limited"),
                ("0700.HK", "Tencent Holdings Limited")
            ],
            MarketRegion.USA: [
                ("AAPL", "Apple Inc."),
                ("GOOGL", "Alphabet Inc."),
                ("MSFT", "Microsoft Corporation"),
                ("AMZN", "Amazon.com Inc."),
                ("TSLA", "Tesla Inc.")
            ]
        }
    
    def fetch_market_data(self, region: MarketRegion) -> List[MarketData]:
        """
        Fetches mock market data for a specific region.
        
        Args:
            region: Market region to fetch data for
            
        Returns:
            List of MarketData for stocks in the region
            
        Raises:
            Exception: If region is in failing_regions list
        """
        # Simulate failure for configured regions
        if region in self.failing_regions:
            raise Exception(f"Simulated API failure for region {region.value}")
        
        # Get stocks for this region
        stocks = self._stocks_by_region.get(region, [])
        
        # Generate mock data for each stock
        market_data_list = []
        timestamp = datetime.now()
        
        for symbol, name in stocks:
            # Generate realistic-looking prices
            base_price = random.uniform(50, 500)
            open_price = Decimal(str(round(base_price, 2)))
            close_price = Decimal(str(round(base_price * random.uniform(0.95, 1.05), 2)))
            high_price = Decimal(str(round(max(float(open_price), float(close_price)) * random.uniform(1.0, 1.03), 2)))
            low_price = Decimal(str(round(min(float(open_price), float(close_price)) * random.uniform(0.97, 1.0), 2)))
            volume = random.randint(1000000, 100000000)
            
            market_data = MarketData(
                symbol=symbol,
                name=name,
                region=region,
                timestamp=timestamp,
                open_price=open_price,
                close_price=close_price,
                high_price=high_price,
                low_price=low_price,
                volume=volume,
                additional_metrics={
                    "rsi": random.uniform(30, 70),
                    "macd": random.uniform(-5, 5),
                    "volume_avg": random.randint(500000, 50000000),
                    # Fundamental metrics
                    "pe_ratio": random.uniform(10, 35),
                    "earnings_growth": random.uniform(-15, 25),
                    "revenue_growth": random.uniform(-10, 20),
                    "debt_to_equity": random.uniform(0.2, 1.5),
                    # Volume history (simulated)
                    "volume_history": [random.randint(1000000, 100000000) for _ in range(10)],
                    # Price history (simulated)
                    "price_history": [Decimal(str(round(base_price * random.uniform(0.9, 1.1), 2))) for _ in range(20)]
                }
            )
            market_data_list.append(market_data)
        
        return market_data_list
