"""
Yahoo Finance API implementation for real market data.

This module provides a real implementation of the MarketDataAPI interface
using the yfinance library to fetch live market data from Yahoo Finance.
"""

import logging
import yfinance as yf
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Dict, Optional

from ..models import MarketRegion, MarketData
from .market_monitor import MarketDataAPI


class YahooFinanceAPI(MarketDataAPI):
    """
    Real implementation of MarketDataAPI using Yahoo Finance.
    
    Fetches live market data from Yahoo Finance using the yfinance library.
    Includes technical indicators, fundamental metrics, and historical data.
    """
    
    def __init__(self, config_manager=None):
        """
        Initialize the Yahoo Finance API.
        
        Args:
            config_manager: Optional ConfigurationManager to load stock symbols from config
        """
        self.logger = logging.getLogger(__name__)
        self.config_manager = config_manager
        
        # Default stock symbols by region (fallback if no config provided)
        self._default_stocks_by_region = {
            MarketRegion.CHINA: [
                "600000.SS",  # Shanghai Pudong Development Bank
                "600036.SS",  # China Merchants Bank
                "601398.SS",  # Industrial and Commercial Bank of China
                "601857.SS",  # PetroChina Company Limited
                "601988.SS"   # Bank of China
            ],
            MarketRegion.HONG_KONG: [
                "0001.HK",    # CK Hutchison Holdings Limited
                "0005.HK",    # HSBC Holdings plc
                "0011.HK",    # Hang Seng Bank Limited
                "0388.HK",    # Hong Kong Exchanges and Clearing Limited
                "0700.HK"     # Tencent Holdings Limited
            ],
            MarketRegion.USA: [
                "AAPL",       # Apple Inc.
                "GOOGL",      # Alphabet Inc.
                "MSFT",       # Microsoft Corporation
                "AMZN",       # Amazon.com Inc.
                "TSLA"        # Tesla Inc.
            ]
        }
    
    def _get_stocks_for_region(self, region: MarketRegion) -> List[str]:
        """
        Get stock symbols for a region from config or defaults.
        
        Args:
            region: Market region
            
        Returns:
            List of stock symbols (limited by max_stocks_per_region if configured)
        """
        symbols = []
        max_stocks = None
        
        # Try to load from config first
        if self.config_manager and self.config_manager.storage_path.exists():
            try:
                # Read the config file directly
                with open(self.config_manager.storage_path, 'r') as f:
                    import yaml
                    config_data = yaml.safe_load(f)
                
                # Get max stocks per region setting
                stock_scanning = config_data.get('stock_scanning', {})
                max_stocks = stock_scanning.get('max_stocks_per_region', None)
                
                stock_symbols = config_data.get('stock_symbols', {})
                
                # Map region to config key
                region_key_map = {
                    MarketRegion.USA: 'usa',
                    MarketRegion.HONG_KONG: 'hong_kong',
                    MarketRegion.CHINA: 'china'
                }
                
                region_key = region_key_map.get(region)
                if region_key and region_key in stock_symbols:
                    symbols = stock_symbols[region_key]
                    if symbols:
                        self.logger.info(f"Loaded {len(symbols)} stock symbols for {region.value} from config")
            except Exception as e:
                self.logger.warning(f"Failed to load stock symbols from config: {e}")
        
        # Fall back to defaults if no symbols loaded
        if not symbols:
            symbols = self._default_stocks_by_region.get(region, [])
        
        # Apply max_stocks_per_region limit
        if max_stocks is not None and max_stocks > 0 and len(symbols) > max_stocks:
            self.logger.info(f"Limiting {region.value} stocks from {len(symbols)} to {max_stocks}")
            symbols = symbols[:max_stocks]
        elif max_stocks == 0:
            self.logger.info(f"Scanning all {len(symbols)} stocks for {region.value} (max_stocks_per_region=0)")
        
        return symbols
    
    def fetch_market_data(self, region: MarketRegion) -> List[MarketData]:
        """
        Fetches real market data from Yahoo Finance for a specific region.
        
        Args:
            region: Market region to fetch data for
            
        Returns:
            List of MarketData for stocks in the region
            
        Raises:
            Exception: If data fetching fails
        """
        self.logger.info(f"Fetching real market data from Yahoo Finance for {region.value}")
        
        # Get stocks for this region
        symbols = self._get_stocks_for_region(region)
        
        if not symbols:
            self.logger.warning(f"No symbols configured for region {region.value}")
            return []
        
        market_data_list = []
        timestamp = datetime.now()
        
        for symbol in symbols:
            try:
                # Fetch stock data
                stock_data = self._fetch_stock_data(symbol, region)
                if stock_data:
                    market_data_list.append(stock_data)
                else:
                    self.logger.warning(f"No data available for {symbol}")
            except Exception as e:
                self.logger.error(f"Failed to fetch data for {symbol}: {e}")
                # Continue with other stocks even if one fails
                continue
        
        self.logger.info(f"Successfully fetched data for {len(market_data_list)}/{len(symbols)} stocks in {region.value}")
        return market_data_list
    
    def _fetch_stock_data(self, symbol: str, region: MarketRegion) -> Optional[MarketData]:
        """
        Fetches data for a single stock from Yahoo Finance.
        
        Args:
            symbol: Stock symbol
            region: Market region
            
        Returns:
            MarketData object or None if fetch fails
        """
        try:
            # Create ticker object
            ticker = yf.Ticker(symbol)
            
            # Get stock info
            info = ticker.info
            
            # Get historical data (last 30 days for technical analysis)
            hist = ticker.history(period="1mo")
            
            if hist.empty:
                self.logger.warning(f"No historical data available for {symbol}")
                return None
            
            # Get latest day's data
            latest = hist.iloc[-1]
            
            # Extract basic price data
            open_price = Decimal(str(round(latest['Open'], 2)))
            close_price = Decimal(str(round(latest['Close'], 2)))
            high_price = Decimal(str(round(latest['High'], 2)))
            low_price = Decimal(str(round(latest['Low'], 2)))
            volume = int(latest['Volume'])
            
            # Calculate technical indicators
            rsi = self._calculate_rsi(hist['Close'])
            macd = self._calculate_macd(hist['Close'])
            
            # Extract fundamental metrics
            pe_ratio = info.get('trailingPE', 0) or info.get('forwardPE', 0) or 0
            earnings_growth = info.get('earningsGrowth', 0) or 0
            revenue_growth = info.get('revenueGrowth', 0) or 0
            debt_to_equity = info.get('debtToEquity', 0) or 0
            
            # Convert percentages to actual percentages
            if earnings_growth != 0:
                earnings_growth = earnings_growth * 100
            if revenue_growth != 0:
                revenue_growth = revenue_growth * 100
            if debt_to_equity != 0:
                debt_to_equity = debt_to_equity / 100
            
            # Get volume history
            volume_history = hist['Volume'].tail(10).tolist()
            
            # Get price history
            price_history = [Decimal(str(round(p, 2))) for p in hist['Close'].tail(20).tolist()]
            
            # Get stock name
            name = info.get('longName', symbol)
            
            # Create MarketData object
            market_data = MarketData(
                symbol=symbol,
                name=name,
                region=region,
                timestamp=datetime.now(),
                open_price=open_price,
                close_price=close_price,
                high_price=high_price,
                low_price=low_price,
                volume=volume,
                additional_metrics={
                    "rsi": rsi,
                    "macd": macd,
                    "volume_avg": int(hist['Volume'].mean()),
                    # Fundamental metrics
                    "pe_ratio": pe_ratio,
                    "earnings_growth": earnings_growth,
                    "revenue_growth": revenue_growth,
                    "debt_to_equity": debt_to_equity,
                    # Historical data
                    "volume_history": volume_history,
                    "price_history": price_history
                }
            )
            
            return market_data
            
        except Exception as e:
            self.logger.error(f"Error fetching data for {symbol}: {e}", exc_info=True)
            return None
    
    def _calculate_rsi(self, prices, period: int = 14) -> float:
        """
        Calculate Relative Strength Index (RSI).
        
        Args:
            prices: Series of closing prices
            period: RSI period (default 14)
            
        Returns:
            RSI value (0-100)
        """
        try:
            if len(prices) < period + 1:
                return 50.0  # Default neutral value
            
            # Calculate price changes
            delta = prices.diff()
            
            # Separate gains and losses
            gains = delta.where(delta > 0, 0)
            losses = -delta.where(delta < 0, 0)
            
            # Calculate average gains and losses
            avg_gain = gains.rolling(window=period).mean().iloc[-1]
            avg_loss = losses.rolling(window=period).mean().iloc[-1]
            
            if avg_loss == 0:
                return 100.0
            
            # Calculate RS and RSI
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            
            return float(rsi)
        except Exception as e:
            self.logger.warning(f"Error calculating RSI: {e}")
            return 50.0
    
    def _calculate_macd(self, prices, fast: int = 12, slow: int = 26, signal: int = 9) -> float:
        """
        Calculate MACD (Moving Average Convergence Divergence).
        
        Args:
            prices: Series of closing prices
            fast: Fast EMA period (default 12)
            slow: Slow EMA period (default 26)
            signal: Signal line period (default 9)
            
        Returns:
            MACD value
        """
        try:
            if len(prices) < slow + signal:
                return 0.0  # Default neutral value
            
            # Calculate EMAs
            ema_fast = prices.ewm(span=fast, adjust=False).mean()
            ema_slow = prices.ewm(span=slow, adjust=False).mean()
            
            # Calculate MACD line
            macd_line = ema_fast - ema_slow
            
            # Calculate signal line
            signal_line = macd_line.ewm(span=signal, adjust=False).mean()
            
            # Return MACD histogram (MACD - Signal)
            macd_histogram = macd_line.iloc[-1] - signal_line.iloc[-1]
            
            return float(macd_histogram)
        except Exception as e:
            self.logger.warning(f"Error calculating MACD: {e}")
            return 0.0
