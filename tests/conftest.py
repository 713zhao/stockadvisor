"""
Pytest configuration and fixtures for Stock Market Analysis tests.
"""

import pytest
from datetime import datetime, date
from decimal import Decimal
from hypothesis import settings

from stock_market_analysis.models import (
    MarketRegion,
    MarketData,
    MarketDataCollection,
    MarketSummary,
    StockRecommendation,
    RecommendationType,
    DailyReport,
    SystemConfiguration
)

# Configure Hypothesis for property-based tests
settings.register_profile("default", max_examples=100)
settings.load_profile("default")


@pytest.fixture
def sample_market_data():
    """Sample market data for testing."""
    return MarketData(
        symbol="AAPL",
        region=MarketRegion.USA,
        timestamp=datetime.now(),
        open_price=Decimal("150.00"),
        close_price=Decimal("152.50"),
        high_price=Decimal("153.00"),
        low_price=Decimal("149.50"),
        volume=1000000,
        additional_metrics={}
    )


@pytest.fixture
def sample_recommendation():
    """Sample stock recommendation for testing."""
    return StockRecommendation(
        symbol="AAPL",
        region=MarketRegion.USA,
        recommendation_type=RecommendationType.BUY,
        rationale="Strong earnings growth and positive market sentiment",
        risk_assessment="Low to moderate risk due to market volatility",
        confidence_score=0.85,
        target_price=Decimal("160.00"),
        generated_at=datetime.now()
    )


@pytest.fixture
def sample_market_summary():
    """Sample market summary for testing."""
    return MarketSummary(
        region=MarketRegion.USA,
        trading_date=date.today(),
        total_stocks_analyzed=100,
        market_trend="bullish",
        notable_events=["Fed rate decision pending"],
        index_performance={"S&P 500": Decimal("1.2"), "NASDAQ": Decimal("2.1")}
    )


@pytest.fixture
def sample_daily_report(sample_recommendation, sample_market_summary):
    """Sample daily report for testing."""
    return DailyReport(
        report_id="test-report-001",
        generation_time=datetime.now(),
        trading_date=date.today(),
        recommendations=[sample_recommendation],
        market_summaries={MarketRegion.USA: sample_market_summary}
    )