"""
Unit tests for core data models.
"""

import pytest
from datetime import datetime, date
from decimal import Decimal

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


class TestMarketRegion:
    """Tests for MarketRegion enum."""
    
    def test_market_region_values(self):
        """Test that market regions have expected values."""
        assert MarketRegion.CHINA.value == "china"
        assert MarketRegion.HONG_KONG.value == "hong_kong"
        assert MarketRegion.USA.value == "usa"


class TestMarketData:
    """Tests for MarketData model."""
    
    def test_market_data_creation(self, sample_market_data):
        """Test that MarketData can be created with valid data."""
        assert sample_market_data.symbol == "AAPL"
        assert sample_market_data.region == MarketRegion.USA
        assert isinstance(sample_market_data.timestamp, datetime)
        assert isinstance(sample_market_data.open_price, Decimal)


class TestStockRecommendation:
    """Tests for StockRecommendation model."""
    
    def test_recommendation_creation(self, sample_recommendation):
        """Test that StockRecommendation can be created with valid data."""
        assert sample_recommendation.symbol == "AAPL"
        assert sample_recommendation.recommendation_type == RecommendationType.BUY
        assert sample_recommendation.rationale != ""
        assert sample_recommendation.risk_assessment != ""
        assert 0.0 <= sample_recommendation.confidence_score <= 1.0


class TestDailyReport:
    """Tests for DailyReport model."""
    
    def test_daily_report_creation(self, sample_daily_report):
        """Test that DailyReport can be created with valid data."""
        assert sample_daily_report.report_id == "test-report-001"
        assert isinstance(sample_daily_report.generation_time, datetime)
        assert isinstance(sample_daily_report.trading_date, date)
        assert len(sample_daily_report.recommendations) > 0
    
    def test_has_recommendations_true(self, sample_daily_report):
        """Test has_recommendations returns True when recommendations exist."""
        assert sample_daily_report.has_recommendations() is True
    
    def test_has_recommendations_false(self, sample_market_summary):
        """Test has_recommendations returns False when no recommendations exist."""
        report = DailyReport(
            report_id="empty-report",
            generation_time=datetime.now(),
            trading_date=date.today(),
            recommendations=[],
            market_summaries={MarketRegion.USA: sample_market_summary}
        )
        assert report.has_recommendations() is False
    
    def test_format_for_telegram(self, sample_daily_report):
        """Test Telegram formatting produces non-empty output."""
        formatted = sample_daily_report.format_for_telegram()
        assert formatted != ""
        assert "Daily Market Report" in formatted
        assert str(sample_daily_report.trading_date) in formatted
    
    def test_format_for_slack(self, sample_daily_report):
        """Test Slack formatting produces non-empty output."""
        formatted = sample_daily_report.format_for_slack()
        assert formatted != ""
        assert "Daily Market Report" in formatted
        assert str(sample_daily_report.trading_date) in formatted
    
    def test_format_for_email(self, sample_daily_report):
        """Test Email formatting produces non-empty HTML output."""
        formatted = sample_daily_report.format_for_email()
        assert formatted != ""
        assert "<html>" in formatted
        assert "Daily Market Report" in formatted


class TestSystemConfiguration:
    """Tests for SystemConfiguration model."""
    
    def test_get_default_regions(self):
        """Test that default regions are returned correctly."""
        default_regions = SystemConfiguration.get_default_regions()
        assert len(default_regions) == 3
        assert MarketRegion.CHINA in default_regions
        assert MarketRegion.HONG_KONG in default_regions
        assert MarketRegion.USA in default_regions