# Design Document: Stock Market Analysis and Recommendation System

## Overview

The Stock Market Analysis and Recommendation System is a scheduled service that monitors multiple stock markets, performs technical and fundamental analysis, and delivers actionable investment recommendations through multiple communication channels. The system operates autonomously on a daily schedule, collecting market data after trading hours, generating analysis-driven recommendations, and distributing comprehensive reports via Telegram, Slack, and Email.

The architecture follows a pipeline pattern with five core components:
1. **Market_Monitor**: Data collection from configured market regions
2. **Analysis_Engine**: Stock analysis and recommendation generation
3. **Report_Generator**: Daily report compilation and formatting
4. **Notification_Service**: Multi-channel report delivery
5. **Configuration_Manager**: System settings and credentials management

The system is designed for reliability with graceful degradation - failures in individual market regions or notification channels do not prevent the system from continuing operations for unaffected components.

## Architecture

### System Architecture

The system follows a pipeline architecture with clear separation of concerns:

```mermaid
graph TD
    A[Scheduler] -->|Triggers Daily| B[Market_Monitor]
    B -->|Uses| K[MarketDataAPI Interface]
    K -->|Mock Mode| L[MockMarketDataAPI]
    K -->|Real Mode| M[YahooFinanceAPI]
    M -->|Fetches from| N[Yahoo Finance]
    B -->|Market Data| C[Analysis_Engine]
    C -->|Recommendations| D[Report_Generator]
    D -->|Daily Report| E[Notification_Service]
    E -->|Deliver| F[Telegram]
    E -->|Deliver| G[Slack]
    E -->|Deliver| H[Email]
    I[Configuration_Manager] -.->|Config| B
    I -.->|Config| C
    I -.->|Credentials| E
    I -.->|Data Source Config| K
    J[Logger] -.->|Logs| B
    J -.->|Logs| C
    J -.->|Logs| D
    J -.->|Logs| E
    J -.->|Logs| I
    J -.->|Logs| M
```

### Component Responsibilities

**Market_Monitor**
- Collects stock market data from configured regions (China, Hong Kong, USA by default)
- Uses MarketDataAPI interface to support both mock and real data sources
- Handles data source failures gracefully
- Timestamps all collected data
- Executes once per trading day per region

**MarketDataAPI Interface**
- Defines the contract for market data fetching
- Implemented by both MockMarketDataAPI and YahooFinanceAPI
- Allows seamless switching between mock and real data sources

**YahooFinanceAPI**
- Fetches real end-of-day market data from Yahoo Finance using yfinance library
- Supports multiple stock symbol formats (US: AAPL, HK: 0700.HK, China: 601398.SS)
- Implements rate limiting and exponential backoff retry logic
- Validates data completeness before returning
- Caches data to minimize API calls
- No API key required (free access)

**MockMarketDataAPI**
- Generates simulated market data for testing purposes
- Maintains consistent data patterns for reproducible tests
- Used when use_mock_data configuration is set to true

**Analysis_Engine**
- Processes market data to identify investment opportunities
- Generates buy/sell/hold recommendations with rationale
- Includes risk assessment for each recommendation
- Filters out stocks with insufficient data
- Executes after market close times
- Implements retry logic (3 attempts, 5-minute intervals)

**Report_Generator**
- Compiles all recommendations into a structured daily report
- Includes market summaries for each region
- Adds generation timestamp
- Handles days with no recommendations

**Notification_Service**
- Delivers reports through three channels: Telegram, Slack, Email
- Formats reports appropriately for each channel
- Continues delivery on individual channel failures
- Logs all delivery attempts

**Configuration_Manager**
- Manages market region settings (add/remove regions)
- Stores notification channel credentials
- Validates configuration changes
- Persists settings across restarts
- Applies changes within 60 seconds

### Data Flow

1. **Scheduled Trigger**: Daily scheduler initiates the pipeline after market close
2. **Configuration Check**: Market_Monitor checks use_mock_data configuration setting
3. **Data Source Selection**: Market_Monitor selects either MockMarketDataAPI or YahooFinanceAPI based on configuration
4. **Data Collection**: 
   - If real mode: YahooFinanceAPI fetches data from Yahoo Finance with proper symbol formatting
   - If mock mode: MockMarketDataAPI generates simulated data
   - Data is validated for completeness and cached
5. **Analysis**: Analysis_Engine processes data and generates recommendations
6. **Report Generation**: Report_Generator compiles recommendations into formatted report
7. **Distribution**: Notification_Service delivers report through all channels
8. **Logging**: All operations log success/failure status

### Error Handling Strategy

The system implements graceful degradation:
- Market region failures don't stop monitoring of other regions
- Notification channel failures don't prevent delivery through other channels
- Analysis failures trigger automatic retry (3 attempts)
- All errors are logged with context
- Critical errors don't cascade to unaffected components

## Components and Interfaces

### Market_Monitor

**Responsibilities:**
- Collect stock market data from configured regions
- Handle data source unavailability
- Timestamp collected data

**Public Interface:**
```python
class MarketMonitor:
    def collect_market_data(self, regions: List[MarketRegion]) -> MarketDataCollection:
        """
        Collects market data from specified regions.
        
        Args:
            regions: List of market regions to monitor
            
        Returns:
            MarketDataCollection containing data from all available regions
            
        Raises:
            No exceptions - logs errors and continues with available regions
        """
        pass
    
    def get_last_collection_time(self, region: MarketRegion) -> Optional[datetime]:
        """Returns the timestamp of the last successful data collection for a region."""
        pass
```

**Dependencies:**
- Configuration_Manager (for region list)
- Logger (for error logging)
- MarketDataAPI (for data fetching)

### MarketDataAPI Interface

**Responsibilities:**
- Define the contract for market data fetching
- Enable switching between mock and real data sources

**Public Interface:**
```python
from abc import ABC, abstractmethod
from typing import List, Dict
from datetime import datetime, date

class MarketDataAPI(ABC):
    @abstractmethod
    def fetch_stock_data(self, symbol: str, region: MarketRegion, 
                        start_date: date, end_date: date) -> Optional[MarketData]:
        """
        Fetches market data for a single stock.
        
        Args:
            symbol: Stock symbol (format varies by region)
            region: Market region for the stock
            start_date: Start date for data fetch
            end_date: End date for data fetch
            
        Returns:
            MarketData if successful, None if data unavailable or invalid
            
        Raises:
            No exceptions - returns None on errors
        """
        pass
    
    @abstractmethod
    def fetch_multiple_stocks(self, symbols: List[str], region: MarketRegion,
                             start_date: date, end_date: date) -> Dict[str, MarketData]:
        """
        Fetches market data for multiple stocks.
        
        Args:
            symbols: List of stock symbols
            region: Market region for the stocks
            start_date: Start date for data fetch
            end_date: End date for data fetch
            
        Returns:
            Dictionary mapping symbols to MarketData (excludes failed fetches)
        """
        pass
    
    @abstractmethod
    def validate_symbol_format(self, symbol: str, region: MarketRegion) -> bool:
        """
        Validates that a stock symbol matches the expected format for the region.
        
        Args:
            symbol: Stock symbol to validate
            region: Market region
            
        Returns:
            True if symbol format is valid for the region
        """
        pass
```

**Implementations:**
- MockMarketDataAPI: Generates simulated data
- YahooFinanceAPI: Fetches real data from Yahoo Finance

### YahooFinanceAPI

**Responsibilities:**
- Fetch real end-of-day market data from Yahoo Finance
- Support multiple stock symbol formats (US, Hong Kong, China)
- Implement rate limiting and retry logic
- Validate data completeness
- Cache data to minimize API calls

**Public Interface:**
```python
import yfinance as yf
from typing import Optional, Dict, List
from datetime import date, datetime, timedelta
import time

class YahooFinanceAPI(MarketDataAPI):
    def __init__(self, cache_ttl_hours: int = 24):
        """
        Initializes the Yahoo Finance API client.
        
        Args:
            cache_ttl_hours: Time-to-live for cached data in hours
        """
        self.cache: Dict[str, tuple[MarketData, datetime]] = {}
        self.cache_ttl = timedelta(hours=cache_ttl_hours)
        self.rate_limit_delay = 0.5  # seconds between requests
        self.last_request_time = None
    
    def fetch_stock_data(self, symbol: str, region: MarketRegion, 
                        start_date: date, end_date: date) -> Optional[MarketData]:
        """
        Fetches market data for a single stock from Yahoo Finance.
        
        Implements:
        - Symbol format validation
        - Rate limiting with delays
        - Exponential backoff retry (3 attempts)
        - Data completeness validation
        - Caching with TTL
        
        Returns None if:
        - Symbol format is invalid
        - API is unavailable after retries
        - Data is incomplete or invalid
        """
        # Check cache first
        cached_data = self._get_from_cache(symbol)
        if cached_data:
            return cached_data
        
        # Validate symbol format
        if not self.validate_symbol_format(symbol, region):
            logger.error(f"Invalid symbol format: {symbol} for region {region}")
            return None
        
        # Format symbol for Yahoo Finance
        yf_symbol = self._format_symbol_for_yfinance(symbol, region)
        
        # Implement rate limiting
        self._apply_rate_limit()
        
        # Fetch with retry logic
        max_retries = 3
        retry_delay = 1  # Start with 1 second
        
        for attempt in range(max_retries):
            try:
                ticker = yf.Ticker(yf_symbol)
                hist = ticker.history(start=start_date, end=end_date)
                
                if hist.empty:
                    logger.warning(f"No data returned for {yf_symbol}")
                    return None
                
                # Get the most recent day's data
                latest = hist.iloc[-1]
                
                # Validate completeness
                if not self._validate_data_completeness(latest):
                    logger.warning(f"Incomplete data for {yf_symbol}")
                    return None
                
                # Create MarketData object
                market_data = MarketData(
                    symbol=symbol,
                    region=region,
                    timestamp=datetime.now(),
                    open_price=Decimal(str(latest['Open'])),
                    close_price=Decimal(str(latest['Close'])),
                    high_price=Decimal(str(latest['High'])),
                    low_price=Decimal(str(latest['Low'])),
                    volume=int(latest['Volume']),
                    additional_metrics={}
                )
                
                # Cache the result
                self._add_to_cache(symbol, market_data)
                
                return market_data
                
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed for {yf_symbol}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
        
        logger.error(f"All retry attempts failed for {yf_symbol}")
        return None
    
    def fetch_multiple_stocks(self, symbols: List[str], region: MarketRegion,
                             start_date: date, end_date: date) -> Dict[str, MarketData]:
        """
        Fetches market data for multiple stocks.
        
        Implements batch fetching with individual error handling.
        Failed fetches are excluded from results.
        """
        results = {}
        
        for symbol in symbols:
            data = self.fetch_stock_data(symbol, region, start_date, end_date)
            if data:
                results[symbol] = data
        
        return results
    
    def validate_symbol_format(self, symbol: str, region: MarketRegion) -> bool:
        """
        Validates stock symbol format for the region.
        
        Format rules:
        - US: Simple ticker (e.g., AAPL, MSFT, GOOGL)
        - Hong Kong: Ticker with .HK suffix (e.g., 0700.HK, 9988.HK)
        - China: Ticker with .SS (Shanghai) or .SZ (Shenzhen) suffix (e.g., 601398.SS, 000001.SZ)
        """
        if region == MarketRegion.USA:
            return symbol.isalpha() and symbol.isupper()
        elif region == MarketRegion.HONG_KONG:
            return symbol.endswith('.HK') and symbol[:-3].isdigit()
        elif region == MarketRegion.CHINA:
            return (symbol.endswith('.SS') or symbol.endswith('.SZ')) and symbol[:-3].isdigit()
        return False
    
    def _format_symbol_for_yfinance(self, symbol: str, region: MarketRegion) -> str:
        """
        Formats symbol for Yahoo Finance API.
        Most regions use the symbol as-is, but this allows for future customization.
        """
        return symbol
    
    def _apply_rate_limit(self):
        """Implements rate limiting to respect Yahoo Finance API limits."""
        if self.last_request_time:
            elapsed = (datetime.now() - self.last_request_time).total_seconds()
            if elapsed < self.rate_limit_delay:
                time.sleep(self.rate_limit_delay - elapsed)
        self.last_request_time = datetime.now()
    
    def _validate_data_completeness(self, data) -> bool:
        """
        Validates that all required fields are present and valid.
        
        Required fields: Open, Close, High, Low, Volume
        """
        required_fields = ['Open', 'Close', 'High', 'Low', 'Volume']
        
        for field in required_fields:
            if field not in data or pd.isna(data[field]):
                return False
            if field == 'Volume' and data[field] <= 0:
                return False
        
        return True
    
    def _get_from_cache(self, symbol: str) -> Optional[MarketData]:
        """Retrieves data from cache if not expired."""
        if symbol in self.cache:
            data, timestamp = self.cache[symbol]
            if datetime.now() - timestamp < self.cache_ttl:
                return data
            else:
                del self.cache[symbol]
        return None
    
    def _add_to_cache(self, symbol: str, data: MarketData):
        """Adds data to cache with current timestamp."""
        self.cache[symbol] = (data, datetime.now())
```

**Dependencies:**
- yfinance library (pip install yfinance)
- Logger (for error and retry logging)
- No API key required

**Symbol Format Examples:**
- US stocks: AAPL, MSFT, GOOGL, TSLA
- Hong Kong stocks: 0700.HK (Tencent), 9988.HK (Alibaba)
- China stocks: 601398.SS (ICBC Shanghai), 000001.SZ (Ping An Shenzhen)

### MockMarketDataAPI

**Responsibilities:**
- Generate simulated market data for testing
- Maintain consistent patterns for reproducible tests
- Support all regions and symbol formats

**Public Interface:**
```python
import random
from decimal import Decimal
from datetime import datetime

class MockMarketDataAPI(MarketDataAPI):
    def __init__(self, seed: Optional[int] = None):
        """
        Initializes the mock API with optional random seed for reproducibility.
        
        Args:
            seed: Random seed for reproducible data generation
        """
        if seed:
            random.seed(seed)
        self.base_prices = {}  # Track base prices for consistency
    
    def fetch_stock_data(self, symbol: str, region: MarketRegion, 
                        start_date: date, end_date: date) -> Optional[MarketData]:
        """
        Generates simulated market data for a stock.
        
        Data characteristics:
        - Consistent base price per symbol
        - Realistic daily variations (±5%)
        - Valid OHLC relationships (High >= Open/Close, Low <= Open/Close)
        - Reasonable volume ranges
        """
        # Get or create base price for symbol
        if symbol not in self.base_prices:
            self.base_prices[symbol] = Decimal(str(random.uniform(10, 500)))
        
        base_price = self.base_prices[symbol]
        
        # Generate realistic daily variation
        variation = random.uniform(-0.05, 0.05)
        close_price = base_price * Decimal(str(1 + variation))
        
        # Generate OHLC with valid relationships
        open_price = base_price * Decimal(str(1 + random.uniform(-0.03, 0.03)))
        high_price = max(open_price, close_price) * Decimal(str(1 + random.uniform(0, 0.02)))
        low_price = min(open_price, close_price) * Decimal(str(1 - random.uniform(0, 0.02)))
        
        # Generate volume
        volume = random.randint(1000000, 100000000)
        
        return MarketData(
            symbol=symbol,
            region=region,
            timestamp=datetime.now(),
            open_price=open_price,
            close_price=close_price,
            high_price=high_price,
            low_price=low_price,
            volume=volume,
            additional_metrics={}
        )
    
    def fetch_multiple_stocks(self, symbols: List[str], region: MarketRegion,
                             start_date: date, end_date: date) -> Dict[str, MarketData]:
        """Generates simulated data for multiple stocks."""
        results = {}
        for symbol in symbols:
            data = self.fetch_stock_data(symbol, region, start_date, end_date)
            if data:
                results[symbol] = data
        return results
    
    def validate_symbol_format(self, symbol: str, region: MarketRegion) -> bool:
        """Mock API accepts any symbol format."""
        return True
```

**Dependencies:**
- None (pure Python implementation)

### Market_Monitor (Updated)

**Responsibilities:**
- Collect stock market data from configured regions
- Use MarketDataAPI interface (mock or real based on configuration)
- Handle data source failures gracefully
- Timestamp all collected data

**Public Interface:**
```python
class MarketMonitor:
    def __init__(self, config_manager: ConfigurationManager):
        """
        Initializes the Market Monitor with configuration.
        
        Selects data source (mock or real) based on use_mock_data config setting.
        """
        self.config_manager = config_manager
        self.data_api = self._create_data_api()
    
    def _create_data_api(self) -> MarketDataAPI:
        """
        Creates the appropriate data API based on configuration.
        
        Returns MockMarketDataAPI if use_mock_data is true,
        otherwise returns YahooFinanceAPI.
        """
        if self.config_manager.get_use_mock_data():
            return MockMarketDataAPI()
        else:
            return YahooFinanceAPI()
    
    def collect_market_data(self, regions: List[MarketRegion]) -> MarketDataCollection:
        """
        Collects market data from specified regions using configured data source.
        
        Args:
            regions: List of market regions to monitor
            
        Returns:
            MarketDataCollection containing data from all available regions
            
        Raises:
            No exceptions - logs errors and continues with available regions
        """
        # Get stock symbols for each region from configuration
        all_data = {}
        failed_regions = []
        
        for region in regions:
            try:
                symbols = self.config_manager.get_symbols_for_region(region)
                end_date = date.today()
                start_date = end_date - timedelta(days=7)  # Get last week of data
                
                region_data = self.data_api.fetch_multiple_stocks(
                    symbols, region, start_date, end_date
                )
                
                if region_data:
                    all_data[region] = list(region_data.values())
                else:
                    logger.warning(f"No data collected for region {region}")
                    failed_regions.append(region)
                    
            except Exception as e:
                logger.error(f"Failed to collect data for {region}: {e}")
                failed_regions.append(region)
        
        return MarketDataCollection(
            collection_time=datetime.now(),
            data_by_region=all_data,
            failed_regions=failed_regions
        )
    
    def get_last_collection_time(self, region: MarketRegion) -> Optional[datetime]:
        """Returns the timestamp of the last successful data collection for a region."""
        pass
```

**Dependencies:**
- Configuration_Manager (for region list and use_mock_data setting)
- Logger (for error logging)
- MarketDataAPI (for data fetching)

### Analysis_Engine

**Responsibilities:**
- Analyze market data
- Generate stock recommendations
- Classify recommendations (buy/sell/hold)
- Include rationale and risk assessment
- Handle insufficient data scenarios

**Public Interface:**
```python
class AnalysisEngine:
    def analyze_and_recommend(self, market_data: MarketDataCollection) -> List[StockRecommendation]:
        """
        Analyzes market data and generates recommendations.
        
        Args:
            market_data: Collection of market data from all regions
            
        Returns:
            List of stock recommendations with rationale and risk assessment
            
        Note:
            Stocks with insufficient data are excluded from results
        """
        pass
    
    def execute_scheduled_analysis(self) -> AnalysisResult:
        """
        Executes the full analysis pipeline with retry logic.
        
        Returns:
            AnalysisResult containing recommendations or error information
            
        Implements 3 retry attempts with 5-minute intervals on failure
        """
        pass
```

**Dependencies:**
- Market_Monitor (for market data)
- Configuration_Manager (for analysis parameters)
- Logger (for execution logging)

### Report_Generator

**Responsibilities:**
- Compile daily reports from recommendations
- Include market summaries
- Add generation timestamps
- Handle zero-recommendation scenarios

**Public Interface:**
```python
class ReportGenerator:
    def generate_daily_report(self, recommendations: List[StockRecommendation], 
                             market_summaries: Dict[MarketRegion, MarketSummary]) -> DailyReport:
        """
        Generates a comprehensive daily report.
        
        Args:
            recommendations: List of stock recommendations for the day
            market_summaries: Summary information for each market region
            
        Returns:
            DailyReport with all recommendations and summaries
            
        Note:
            Creates report even when recommendations list is empty
        """
        pass
```

**Dependencies:**
- Analysis_Engine (for recommendations)
- Market_Monitor (for market summaries)
- Logger (for generation logging)

### Notification_Service

**Responsibilities:**
- Deliver reports through multiple channels
- Format reports for each channel
- Handle channel-specific failures
- Log delivery attempts

**Public Interface:**
```python
class NotificationService:
    def deliver_report(self, report: DailyReport) -> DeliveryResult:
        """
        Delivers report through all configured channels.
        
        Args:
            report: The daily report to deliver
            
        Returns:
            DeliveryResult containing success/failure status for each channel
            
        Note:
            Continues delivery through remaining channels on individual failures
        """
        pass
    
    def deliver_to_telegram(self, report: DailyReport) -> bool:
        """Delivers report via Telegram. Returns success status."""
        pass
    
    def deliver_to_slack(self, report: DailyReport) -> bool:
        """Delivers report via Slack. Returns success status."""
        pass
    
    def deliver_to_email(self, report: DailyReport) -> bool:
        """Delivers report via Email. Returns success status."""
        pass
```

**Dependencies:**
- Configuration_Manager (for channel credentials)
- Logger (for delivery logging)
- External APIs (Telegram Bot API, Slack Webhooks, SMTP server)

### Configuration_Manager

**Responsibilities:**
- Manage market region configuration
- Store notification channel credentials
- Validate configuration changes
- Persist settings
- Apply changes to system

**Public Interface:**
```python
class ConfigurationManager:
    def add_market_region(self, region: MarketRegion) -> Result[None, str]:
        """
        Adds a market region to monitoring list.
        
        Returns:
            Success or error message
        """
        pass
    
    def remove_market_region(self, region: MarketRegion) -> Result[None, str]:
        """
        Removes a market region from monitoring list.
        
        Returns:
            Success or error message if removal would leave zero regions
        """
        pass
    
    def get_configured_regions(self) -> List[MarketRegion]:
        """
        Returns list of configured market regions.
        
        Returns default regions (China, Hong Kong, USA) if none configured.
        """
        pass
    
    def set_telegram_config(self, bot_token: str, chat_ids: List[str]) -> Result[None, str]:
        """Validates and stores Telegram configuration."""
        pass
    
    def set_slack_config(self, webhook_url: str, channel: str) -> Result[None, str]:
        """Validates and stores Slack configuration."""
        pass
    
    def set_email_config(self, smtp_settings: SMTPConfig, recipients: List[str]) -> Result[None, str]:
        """Validates and stores Email configuration."""
        pass
    
    def get_use_mock_data(self) -> bool:
        """
        Returns whether the system should use mock data or real data.
        
        Returns:
            True if mock data should be used, False for real data from Yahoo Finance
        """
        pass
    
    def set_use_mock_data(self, use_mock: bool) -> None:
        """
        Sets whether to use mock data or real data.
        
        Args:
            use_mock: True to use mock data, False to use real Yahoo Finance data
        """
        pass
    
    def get_symbols_for_region(self, region: MarketRegion) -> List[str]:
        """
        Returns the list of stock symbols to monitor for a given region.
        
        Args:
            region: Market region
            
        Returns:
            List of stock symbols in the appropriate format for the region
        """
        pass
    
    def set_symbols_for_region(self, region: MarketRegion, symbols: List[str]) -> Result[None, str]:
        """
        Sets the list of stock symbols to monitor for a region.
        
        Args:
            region: Market region
            symbols: List of stock symbols (must match region format)
            
        Returns:
            Success or error message if symbols have invalid format
        """
        pass
    
    def persist_configuration(self) -> None:
        """Saves configuration to persistent storage."""
        pass
    
    def load_configuration(self) -> None:
        """Loads configuration from persistent storage."""
        pass
```

**Dependencies:**
- Logger (for configuration change logging)
- Persistent storage (file system or database)
- MarketDataAPI (for symbol format validation)

### Scheduler

**Responsibilities:**
- Trigger daily analysis execution
- Respect market close times
- Support custom schedules

**Public Interface:**
```python
class Scheduler:
    def schedule_daily_analysis(self, market_regions: List[MarketRegion]) -> None:
        """
        Schedules analysis to run after market close for each region.
        
        Args:
            market_regions: Regions to consider for scheduling
        """
        pass
    
    def set_custom_schedule(self, cron_expression: str) -> Result[None, str]:
        """
        Sets a custom schedule for analysis execution.
        
        Args:
            cron_expression: Cron-style schedule expression
            
        Returns:
            Success or validation error
        """
        pass
```

**Dependencies:**
- Analysis_Engine (to trigger execution)
- Configuration_Manager (for schedule settings)

## Data Models

### MarketRegion

Represents a geographic stock market area.

```python
class MarketRegion(Enum):
    CHINA = "china"
    HONG_KONG = "hong_kong"
    USA = "usa"
    # Extensible for additional regions
```

### MarketData

Raw market data for a single stock.

```python
@dataclass
class MarketData:
    symbol: str
    region: MarketRegion
    timestamp: datetime
    open_price: Decimal
    close_price: Decimal
    high_price: Decimal
    low_price: Decimal
    volume: int
    additional_metrics: Dict[str, Any]  # Extensible for technical indicators
```

### MarketDataCollection

Collection of market data from multiple regions.

```python
@dataclass
class MarketDataCollection:
    collection_time: datetime
    data_by_region: Dict[MarketRegion, List[MarketData]]
    failed_regions: List[MarketRegion]  # Regions that failed to collect
```

### StockRecommendation

A buy/sell/hold recommendation with supporting analysis.

```python
class RecommendationType(Enum):
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"

@dataclass
class StockRecommendation:
    symbol: str
    region: MarketRegion
    recommendation_type: RecommendationType
    rationale: str  # Human-readable explanation
    risk_assessment: str  # Risk level and factors
    confidence_score: float  # 0.0 to 1.0
    target_price: Optional[Decimal]
    generated_at: datetime
```

### MarketSummary

Summary information for a market region.

```python
@dataclass
class MarketSummary:
    region: MarketRegion
    trading_date: date
    total_stocks_analyzed: int
    market_trend: str  # "bullish", "bearish", "neutral"
    notable_events: List[str]
    index_performance: Dict[str, Decimal]  # Index name -> performance percentage
```

### DailyReport

Comprehensive daily report containing all recommendations and summaries.

```python
@dataclass
class DailyReport:
    report_id: str  # Unique identifier
    generation_time: datetime
    trading_date: date
    recommendations: List[StockRecommendation]
    market_summaries: Dict[MarketRegion, MarketSummary]
    
    def has_recommendations(self) -> bool:
        """Returns True if report contains any recommendations."""
        return len(self.recommendations) > 0
    
    def format_for_telegram(self) -> str:
        """Formats report for Telegram delivery."""
        pass
    
    def format_for_slack(self) -> str:
        """Formats report for Slack delivery."""
        pass
    
    def format_for_email(self) -> str:
        """Formats report for Email delivery (HTML)."""
        pass
```

### Configuration Models

```python
@dataclass
class TelegramConfig:
    bot_token: str
    chat_ids: List[str]

@dataclass
class SlackConfig:
    webhook_url: str
    channel: str

@dataclass
class SMTPConfig:
    host: str
    port: int
    username: str
    password: str
    use_tls: bool

@dataclass
class EmailConfig:
    smtp: SMTPConfig
    recipients: List[str]
    sender_address: str

@dataclass
class SystemConfiguration:
    market_regions: List[MarketRegion]
    telegram: Optional[TelegramConfig]
    slack: Optional[SlackConfig]
    email: Optional[EmailConfig]
    custom_schedule: Optional[str]  # Cron expression
    use_mock_data: bool = False  # False = use real Yahoo Finance data, True = use mock data
    stock_symbols: Dict[MarketRegion, List[str]] = None  # Stock symbols to monitor per region
    
    def get_default_regions() -> List[MarketRegion]:
        """Returns default regions: China, Hong Kong, USA."""
        return [MarketRegion.CHINA, MarketRegion.HONG_KONG, MarketRegion.USA]
    
    def get_default_symbols() -> Dict[MarketRegion, List[str]]:
        """
        Returns default stock symbols for each region.
        
        US: Major tech and blue-chip stocks
        Hong Kong: Major companies listed on HKEX
        China: Major companies on Shanghai and Shenzhen exchanges
        """
        return {
            MarketRegion.USA: ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"],
            MarketRegion.HONG_KONG: ["0700.HK", "9988.HK", "0941.HK", "1299.HK"],
            MarketRegion.CHINA: ["601398.SS", "600519.SS", "000001.SZ", "000858.SZ"]
        }
```

### Result Types

```python
@dataclass
class AnalysisResult:
    success: bool
    recommendations: List[StockRecommendation]
    error_message: Optional[str]
    retry_count: int

@dataclass
class DeliveryResult:
    telegram_success: bool
    slack_success: bool
    email_success: bool
    errors: Dict[str, str]  # Channel name -> error message
    
    def all_succeeded(self) -> bool:
        """Returns True if all channels delivered successfully."""
        return self.telegram_success and self.slack_success and self.email_success
    
    def any_succeeded(self) -> bool:
        """Returns True if at least one channel delivered successfully."""
        return self.telegram_success or self.slack_success or self.email_success
```


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Complete Region Data Collection

*For any* list of configured market regions, when the Market_Monitor collects data, the resulting MarketDataCollection should contain data entries for all regions that are available (not in the failed_regions list).

**Validates: Requirements 1.1**

### Property 2: Graceful Region Failure Handling

*For any* list of market regions where some regions fail during collection, the Market_Monitor should successfully collect data from all non-failing regions and include the failing regions in the failed_regions list.

**Validates: Requirements 1.3**

### Property 3: Market Data Timestamp Presence

*For any* MarketDataCollection returned by the Market_Monitor, all MarketData entries should have non-null timestamps.

**Validates: Requirements 1.5**

### Property 4: Recommendation Completeness

*For any* StockRecommendation generated by the Analysis_Engine, it should have a valid classification (buy/sell/hold), a non-empty rationale, and a non-empty risk assessment.

**Validates: Requirements 2.2, 2.3, 2.4**

### Property 5: Insufficient Data Exclusion

*For any* market data where some stocks have insufficient data for analysis, those stocks should not appear in the generated recommendations list.

**Validates: Requirements 2.5**

### Property 6: Report Includes All Recommendations

*For any* list of StockRecommendations, when a DailyReport is generated, the report should contain all recommendations from the input list.

**Validates: Requirements 3.2**

### Property 7: Report Includes All Region Summaries

*For any* set of configured market regions, when a DailyReport is generated, the report should contain market summaries for each configured region.

**Validates: Requirements 3.3**

### Property 8: Report Timestamp Presence

*For any* DailyReport generated, it should have a non-null generation_time timestamp.

**Validates: Requirements 3.4**

### Property 9: Multi-Channel Delivery Attempts

*For any* DailyReport, when delivered through the Notification_Service, all three delivery methods (Telegram, Slack, Email) should be attempted.

**Validates: Requirements 4.1, 4.2, 4.3**

### Property 10: Channel Failure Isolation

*For any* DailyReport delivery where one or more channels fail, the Notification_Service should still attempt delivery through all remaining channels and return a DeliveryResult indicating which channels succeeded and which failed.

**Validates: Requirements 4.4**

### Property 11: Channel-Specific Formatting

*For any* DailyReport, the formatted output for each channel (Telegram, Slack, Email) should be non-empty and contain key report information (recommendations count, generation time).

**Validates: Requirements 4.5**

### Property 12: Region Addition Persistence

*For any* MarketRegion, when added to the Configuration_Manager, it should appear in the list of configured regions returned by get_configured_regions().

**Validates: Requirements 5.1**

### Property 13: Region Removal Persistence

*For any* MarketRegion that exists in the configured regions list (and is not the last region), when removed from the Configuration_Manager, it should not appear in the list of configured regions returned by get_configured_regions().

**Validates: Requirements 5.2**

### Property 14: Configuration Persistence Round-Trip

*For any* valid SystemConfiguration, when saved via persist_configuration() and then loaded via load_configuration(), the loaded configuration should match the saved configuration.

**Validates: Requirements 5.5, 6.1, 6.2, 6.3**

### Property 15: Invalid Credentials Rejection

*For any* invalid notification channel credentials (malformed tokens, invalid URLs, incorrect SMTP settings), the Configuration_Manager should reject them and return an error result.

**Validates: Requirements 6.4**

### Property 16: Descriptive Error Messages

*For any* invalid configuration input, the Configuration_Manager should return an error message that is non-empty and describes the validation failure.

**Validates: Requirements 6.5**

### Property 17: Analysis Retry Count

*For any* analysis execution that fails, the Analysis_Engine should retry up to 3 times before returning a failure result, and the AnalysisResult should reflect the correct retry_count.

**Validates: Requirements 7.4**

### Property 18: Comprehensive Event Logging

*For any* significant system event (errors, report generation, delivery attempts, configuration changes), the system should create a log entry with a timestamp and relevant context information.

**Validates: Requirements 8.1, 8.2, 8.3, 8.4**

### Property 19: Component Failure Isolation

*For any* critical error in one component (Market_Monitor, Analysis_Engine, or Notification_Service), other unaffected components should continue to operate normally.

**Validates: Requirements 9.5**

### Property 20: Symbol Format Validation

*For any* stock symbol and market region, the YahooFinanceAPI should correctly validate whether the symbol format matches the expected format for that region (US: alphabetic, HK: numeric.HK, China: numeric.SS or numeric.SZ).

**Validates: Requirements 8.2**

### Property 21: Data Completeness Validation

*For any* market data fetched by YahooFinanceAPI, if the data is returned (not None), it should contain all required fields (open, close, high, low, volume) with valid non-null values.

**Validates: Requirements 8.4, 8.5**

### Property 22: Mock vs Real Data Source Selection

*For any* configuration setting of use_mock_data, the Market_Monitor should use MockMarketDataAPI when use_mock_data is true and YahooFinanceAPI when use_mock_data is false.

**Validates: Requirements 8.6, 8.7, 8.8**

### Property 23: Cache Effectiveness

*For any* stock symbol, when YahooFinanceAPI fetches data twice within the cache TTL period, the second fetch should return cached data without making an API call.

**Validates: Requirements 8.9**

### Property 24: Rate Limiting Compliance

*For any* sequence of API calls made by YahooFinanceAPI, the time between consecutive calls should be at least the configured rate_limit_delay.

**Validates: Requirements 8.10**

### Property 25: Retry with Exponential Backoff

*For any* failed API call in YahooFinanceAPI, the system should retry up to 3 times with exponentially increasing delays (1s, 2s, 4s) before returning None.

**Validates: Requirements 8.3**

## Error Handling

The system implements a comprehensive error handling strategy based on graceful degradation and fault isolation:

### Error Categories

**Recoverable Errors:**
- Individual market region data collection failures
- Individual notification channel delivery failures
- Temporary analysis failures (handled by retry logic)
- Yahoo Finance API rate limiting or temporary unavailability

**Non-Recoverable Errors:**
- Invalid configuration that violates system constraints
- Persistent analysis failures after all retries
- Critical system component failures

### Error Handling Patterns

**Graceful Degradation:**
- Market region failures don't prevent collection from other regions
- Notification channel failures don't prevent delivery through other channels
- Component failures don't cascade to unaffected components

**Retry Logic:**
- Analysis failures trigger automatic retry (3 attempts)
- Each retry is logged with attempt number
- After exhausting retries, system logs failure and continues with other operations

**Error Logging:**
- All errors are logged with timestamp and context
- Error logs include component name, operation, and error details
- Critical errors trigger administrator notifications

**Validation:**
- Configuration changes are validated before application
- Invalid inputs return descriptive error messages
- System maintains valid state even when operations fail

### Error Response Patterns

```python
# Pattern 1: Graceful degradation with partial results
def collect_market_data(regions: List[MarketRegion]) -> MarketDataCollection:
    successful_data = []
    failed_regions = []
    
    for region in regions:
        try:
            data = fetch_data_for_region(region)
            successful_data.append(data)
        except Exception as e:
            logger.error(f"Failed to collect data for {region}: {e}")
            failed_regions.append(region)
    
    return MarketDataCollection(
        collection_time=datetime.now(),
        data_by_region=successful_data,
        failed_regions=failed_regions
    )

# Pattern 2: Retry with exponential backoff
def execute_scheduled_analysis() -> AnalysisResult:
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            recommendations = perform_analysis()
            return AnalysisResult(
                success=True,
                recommendations=recommendations,
                error_message=None,
                retry_count=retry_count
            )
        except Exception as e:
            retry_count += 1
            logger.warning(f"Analysis attempt {retry_count} failed: {e}")
            if retry_count < max_retries:
                time.sleep(300)  # 5 minutes
    
    logger.error("All analysis retry attempts failed")
    notify_administrators("Analysis execution failed after all retries")
    return AnalysisResult(
        success=False,
        recommendations=[],
        error_message="Analysis failed after 3 retry attempts",
        retry_count=retry_count
    )

# Pattern 3: Validation with descriptive errors
def set_telegram_config(bot_token: str, chat_ids: List[str]) -> Result[None, str]:
    if not bot_token or len(bot_token) < 10:
        return Err("Invalid bot token: must be at least 10 characters")
    
    if not chat_ids or len(chat_ids) == 0:
        return Err("Invalid chat IDs: at least one chat ID required")
    
    for chat_id in chat_ids:
        if not chat_id.isdigit() and not chat_id.startswith("-"):
            return Err(f"Invalid chat ID format: {chat_id}")
    
    # Validate by attempting to connect
    try:
        validate_telegram_credentials(bot_token, chat_ids)
    except Exception as e:
        return Err(f"Telegram credential validation failed: {str(e)}")
    
    self.telegram_config = TelegramConfig(bot_token, chat_ids)
    return Ok(None)
```

### Error Monitoring

The system maintains error metrics for monitoring:
- Count of failed market region collections per day
- Count of failed notification deliveries per channel
- Analysis failure rate and retry statistics
- Configuration validation failure rate

These metrics help identify systemic issues and guide system improvements.

## Testing Strategy

The testing strategy employs a dual approach combining unit tests for specific scenarios and property-based tests for comprehensive coverage.

### Testing Approach

**Unit Tests:**
- Specific examples demonstrating correct behavior
- Edge cases (empty inputs, boundary conditions)
- Error conditions and validation failures
- Integration points between components

**Property-Based Tests:**
- Universal properties that hold for all inputs
- Comprehensive input coverage through randomization
- Minimum 100 iterations per property test
- Each test references its design document property

### Property-Based Testing Framework

**Language:** Python
**Framework:** Hypothesis (https://hypothesis.readthedocs.io/)

Hypothesis provides:
- Automatic test case generation
- Shrinking of failing examples
- Stateful testing capabilities
- Excellent integration with pytest

**Configuration:**
```python
from hypothesis import given, settings, strategies as st

# Standard configuration for all property tests
@settings(max_examples=100)
```

### Test Organization

```
tests/
├── unit/
│   ├── test_market_monitor.py
│   ├── test_analysis_engine.py
│   ├── test_report_generator.py
│   ├── test_notification_service.py
│   └── test_configuration_manager.py
├── property/
│   ├── test_properties_market_monitor.py
│   ├── test_properties_analysis_engine.py
│   ├── test_properties_report_generator.py
│   ├── test_properties_notification_service.py
│   └── test_properties_configuration_manager.py
└── integration/
    ├── test_end_to_end_pipeline.py
    └── test_scheduler_integration.py
```

### Property Test Examples

**Property 1: Complete Region Data Collection**
```python
from hypothesis import given, settings
from hypothesis import strategies as st

@settings(max_examples=100)
@given(regions=st.lists(st.sampled_from(MarketRegion), min_size=1, max_size=5))
def test_complete_region_data_collection(regions):
    """
    Feature: stock-market-analysis, Property 1: 
    For any list of configured market regions, when the Market_Monitor collects data, 
    the resulting MarketDataCollection should contain data entries for all regions 
    that are available (not in the failed_regions list).
    """
    monitor = MarketMonitor()
    result = monitor.collect_market_data(regions)
    
    # All regions should either have data or be in failed_regions
    collected_regions = set(result.data_by_region.keys())
    failed_regions = set(result.failed_regions)
    all_accounted = collected_regions.union(failed_regions)
    
    assert all_accounted == set(regions)
    # Regions with data should not be in failed list
    assert collected_regions.isdisjoint(failed_regions)
```

**Property 14: Configuration Persistence Round-Trip**
```python
@settings(max_examples=100)
@given(config=st.builds(
    SystemConfiguration,
    market_regions=st.lists(st.sampled_from(MarketRegion), min_size=1, max_size=5),
    custom_schedule=st.one_of(st.none(), st.text(min_size=5, max_size=20))
))
def test_configuration_persistence_round_trip(config, tmp_path):
    """
    Feature: stock-market-analysis, Property 14: 
    For any valid SystemConfiguration, when saved via persist_configuration() 
    and then loaded via load_configuration(), the loaded configuration should 
    match the saved configuration.
    """
    manager = ConfigurationManager(storage_path=tmp_path)
    
    # Save configuration
    manager.set_configuration(config)
    manager.persist_configuration()
    
    # Create new manager instance and load
    new_manager = ConfigurationManager(storage_path=tmp_path)
    new_manager.load_configuration()
    loaded_config = new_manager.get_configuration()
    
    # Configurations should match
    assert loaded_config.market_regions == config.market_regions
    assert loaded_config.custom_schedule == config.custom_schedule
```

### Unit Test Examples

**Edge Case: Empty Recommendations Report**
```python
def test_report_generation_with_no_recommendations():
    """
    Tests that a report is generated even when no recommendations exist.
    Validates: Requirement 3.5
    """
    generator = ReportGenerator()
    market_summaries = {
        MarketRegion.USA: MarketSummary(
            region=MarketRegion.USA,
            trading_date=date.today(),
            total_stocks_analyzed=100,
            market_trend="neutral",
            notable_events=[],
            index_performance={"S&P 500": Decimal("0.5")}
        )
    }
    
    report = generator.generate_daily_report([], market_summaries)
    
    assert report is not None
    assert len(report.recommendations) == 0
    assert not report.has_recommendations()
    assert report.generation_time is not None
```

**Edge Case: Last Region Removal Prevention**
```python
def test_cannot_remove_last_market_region():
    """
    Tests that removing the last market region is prevented.
    Validates: Requirement 5.3
    """
    manager = ConfigurationManager()
    manager.add_market_region(MarketRegion.USA)
    
    result = manager.remove_market_region(MarketRegion.USA)
    
    assert result.is_err()
    assert "at least one" in result.error().lower()
    assert MarketRegion.USA in manager.get_configured_regions()
```

**Edge Case: All Retries Exhausted**
```python
def test_analysis_failure_after_all_retries():
    """
    Tests that analysis logs failure after exhausting all retry attempts.
    Validates: Requirement 7.5
    """
    engine = AnalysisEngine()
    
    # Mock to always fail
    with patch.object(engine, 'perform_analysis', side_effect=Exception("Analysis error")):
        with patch('time.sleep'):  # Skip actual sleep delays
            result = engine.execute_scheduled_analysis()
    
    assert not result.success
    assert result.retry_count == 3
    assert result.error_message is not None
    # Verify administrator notification was sent
    # Verify error was logged
```

### Integration Tests

Integration tests verify the complete pipeline:

```python
def test_end_to_end_daily_pipeline():
    """
    Tests the complete daily analysis pipeline from data collection to notification.
    """
    # Setup
    config_manager = ConfigurationManager()
    config_manager.add_market_region(MarketRegion.USA)
    
    monitor = MarketMonitor(config_manager)
    engine = AnalysisEngine()
    generator = ReportGenerator()
    notifier = NotificationService(config_manager)
    
    # Execute pipeline
    market_data = monitor.collect_market_data(config_manager.get_configured_regions())
    recommendations = engine.analyze_and_recommend(market_data)
    report = generator.generate_daily_report(recommendations, market_data.summaries)
    delivery_result = notifier.deliver_report(report)
    
    # Verify
    assert market_data is not None
    assert len(recommendations) >= 0
    assert report is not None
    assert delivery_result.any_succeeded()
```

### Test Coverage Goals

- Unit test coverage: >90% for all components
- Property test coverage: 100% of correctness properties
- Integration test coverage: All major workflows
- Edge case coverage: All identified edge cases from requirements

### Continuous Testing

- All tests run on every commit
- Property tests run with increased iterations (1000) in CI/CD
- Integration tests run in staging environment
- Performance benchmarks track analysis execution time
