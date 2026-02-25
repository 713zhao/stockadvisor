"""
Property-based tests for core data models.

These tests validate universal properties that should hold for all valid inputs.
"""

import pytest
from datetime import datetime, date
from decimal import Decimal
from hypothesis import given, settings, strategies as st

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


# Hypothesis strategies for generating test data
market_region_strategy = st.sampled_from(list(MarketRegion))

market_data_strategy = st.builds(
    MarketData,
    symbol=st.text(min_size=1, max_size=10, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))),
    region=market_region_strategy,
    timestamp=st.datetimes(min_value=datetime(2020, 1, 1), max_value=datetime(2030, 12, 31)),
    open_price=st.decimals(min_value=Decimal('0.01'), max_value=Decimal('10000.00'), places=2),
    close_price=st.decimals(min_value=Decimal('0.01'), max_value=Decimal('10000.00'), places=2),
    high_price=st.decimals(min_value=Decimal('0.01'), max_value=Decimal('10000.00'), places=2),
    low_price=st.decimals(min_value=Decimal('0.01'), max_value=Decimal('10000.00'), places=2),
    volume=st.integers(min_value=0, max_value=1000000000),
    additional_metrics=st.dictionaries(st.text(min_size=1, max_size=20), st.text(min_size=1, max_size=50))
)

recommendation_strategy = st.builds(
    StockRecommendation,
    symbol=st.text(min_size=1, max_size=10, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))),
    region=market_region_strategy,
    recommendation_type=st.sampled_from(list(RecommendationType)),
    rationale=st.text(min_size=10, max_size=200),
    risk_assessment=st.text(min_size=10, max_size=200),
    confidence_score=st.floats(min_value=0.0, max_value=1.0),
    target_price=st.one_of(st.none(), st.decimals(min_value=Decimal('0.01'), max_value=Decimal('10000.00'), places=2)),
    generated_at=st.datetimes(min_value=datetime(2020, 1, 1), max_value=datetime(2030, 12, 31))
)


class TestMarketDataProperties:
    """Property-based tests for MarketData model."""
    
    @settings(max_examples=100)
    @given(market_data=market_data_strategy)
    def test_market_data_timestamp_is_not_none(self, market_data):
        """
        Property: All MarketData instances should have non-null timestamps.
        This validates that timestamp presence is maintained across all data.
        """
        assert market_data.timestamp is not None
        assert isinstance(market_data.timestamp, datetime)
    
    @settings(max_examples=100)
    @given(market_data=market_data_strategy)
    def test_market_data_prices_are_positive(self, market_data):
        """
        Property: All price fields in MarketData should be positive.
        This validates basic data integrity for financial data.
        """
        assert market_data.open_price > 0
        assert market_data.close_price > 0
        assert market_data.high_price > 0
        assert market_data.low_price > 0
    
    @settings(max_examples=100)
    @given(market_data=market_data_strategy)
    def test_market_data_volume_is_non_negative(self, market_data):
        """
        Property: Volume in MarketData should be non-negative.
        This validates that volume data is realistic.
        """
        assert market_data.volume >= 0


class TestStockRecommendationProperties:
    """Property-based tests for StockRecommendation model."""
    
    @settings(max_examples=100)
    @given(recommendation=recommendation_strategy)
    def test_recommendation_has_required_fields(self, recommendation):
        """
        Property: All StockRecommendations should have non-empty rationale and risk assessment.
        This validates completeness of recommendation data.
        """
        assert recommendation.rationale is not None
        assert len(recommendation.rationale.strip()) > 0
        assert recommendation.risk_assessment is not None
        assert len(recommendation.risk_assessment.strip()) > 0
    
    @settings(max_examples=100)
    @given(recommendation=recommendation_strategy)
    def test_recommendation_confidence_score_in_range(self, recommendation):
        """
        Property: Confidence scores should be between 0.0 and 1.0 inclusive.
        This validates that confidence scores are within valid range.
        """
        assert 0.0 <= recommendation.confidence_score <= 1.0
    
    @settings(max_examples=100)
    @given(recommendation=recommendation_strategy)
    def test_recommendation_has_valid_type(self, recommendation):
        """
        Property: All recommendations should have a valid recommendation type.
        This validates that recommendation classification is present.
        """
        assert recommendation.recommendation_type in [
            RecommendationType.BUY,
            RecommendationType.SELL,
            RecommendationType.HOLD
        ]


class TestDailyReportProperties:
    """Property-based tests for DailyReport model."""
    
    @settings(max_examples=100)
    @given(
        recommendations=st.lists(recommendation_strategy, min_size=0, max_size=10),
        market_summaries=st.dictionaries(
            market_region_strategy,
            st.builds(
                MarketSummary,
                region=market_region_strategy,
                trading_date=st.dates(min_value=date(2020, 1, 1), max_value=date(2030, 12, 31)),
                total_stocks_analyzed=st.integers(min_value=0, max_value=10000),
                market_trend=st.sampled_from(["bullish", "bearish", "neutral"]),
                notable_events=st.lists(st.text(min_size=1, max_size=100), max_size=5),
                index_performance=st.dictionaries(
                    st.text(min_size=1, max_size=20),
                    st.decimals(min_value=Decimal('-50.0'), max_value=Decimal('50.0'), places=2),
                    max_size=5
                )
            ),
            min_size=0,
            max_size=3
        )
    )
    def test_daily_report_timestamp_presence(self, recommendations, market_summaries):
        """
        Property: All DailyReports should have non-null generation timestamps.
        This validates that report generation time is always recorded.
        """
        report = DailyReport(
            report_id="test-report",
            generation_time=datetime.now(),
            trading_date=date.today(),
            recommendations=recommendations,
            market_summaries=market_summaries
        )
        
        assert report.generation_time is not None
        assert isinstance(report.generation_time, datetime)
    
    @settings(max_examples=100)
    @given(
        recommendations=st.lists(recommendation_strategy, min_size=0, max_size=10),
        market_summaries=st.dictionaries(
            market_region_strategy,
            st.builds(
                MarketSummary,
                region=market_region_strategy,
                trading_date=st.dates(min_value=date(2020, 1, 1), max_value=date(2030, 12, 31)),
                total_stocks_analyzed=st.integers(min_value=0, max_value=10000),
                market_trend=st.sampled_from(["bullish", "bearish", "neutral"]),
                notable_events=st.lists(st.text(min_size=1, max_size=100), max_size=5),
                index_performance=st.dictionaries(
                    st.text(min_size=1, max_size=20),
                    st.decimals(min_value=Decimal('-50.0'), max_value=Decimal('50.0'), places=2),
                    max_size=5
                )
            ),
            min_size=0,
            max_size=3
        )
    )
    def test_daily_report_includes_all_recommendations(self, recommendations, market_summaries):
        """
        Property: DailyReports should contain all recommendations provided during creation.
        This validates that no recommendations are lost during report generation.
        """
        report = DailyReport(
            report_id="test-report",
            generation_time=datetime.now(),
            trading_date=date.today(),
            recommendations=recommendations,
            market_summaries=market_summaries
        )
        
        assert len(report.recommendations) == len(recommendations)
        for original_rec in recommendations:
            assert original_rec in report.recommendations
    
    @settings(max_examples=100)
    @given(
        recommendations=st.lists(recommendation_strategy, min_size=0, max_size=10),
        market_summaries=st.dictionaries(
            market_region_strategy,
            st.builds(
                MarketSummary,
                region=market_region_strategy,
                trading_date=st.dates(min_value=date(2020, 1, 1), max_value=date(2030, 12, 31)),
                total_stocks_analyzed=st.integers(min_value=0, max_value=10000),
                market_trend=st.sampled_from(["bullish", "bearish", "neutral"]),
                notable_events=st.lists(st.text(min_size=1, max_size=100), max_size=5),
                index_performance=st.dictionaries(
                    st.text(min_size=1, max_size=20),
                    st.decimals(min_value=Decimal('-50.0'), max_value=Decimal('50.0'), places=2),
                    max_size=5
                )
            ),
            min_size=0,
            max_size=3
        )
    )
    def test_daily_report_formatting_produces_non_empty_output(self, recommendations, market_summaries):
        """
        Property: All report formatting methods should produce non-empty output.
        This validates that formatted reports contain meaningful content.
        """
        report = DailyReport(
            report_id="test-report",
            generation_time=datetime.now(),
            trading_date=date.today(),
            recommendations=recommendations,
            market_summaries=market_summaries
        )
        
        telegram_format = report.format_for_telegram()
        slack_format = report.format_for_slack()
        email_format = report.format_for_email()
        
        assert len(telegram_format.strip()) > 0
        assert len(slack_format.strip()) > 0
        assert len(email_format.strip()) > 0
        
        # All formats should contain key information
        assert "Daily Market Report" in telegram_format
        assert "Daily Market Report" in slack_format
        assert "Daily Market Report" in email_format


class TestSystemConfigurationProperties:
    """Property-based tests for SystemConfiguration model."""
    
    @settings(max_examples=100)
    @given(regions=st.lists(market_region_strategy, min_size=1, max_size=5, unique=True))
    def test_configuration_maintains_region_list(self, regions):
        """
        Property: SystemConfiguration should maintain the exact list of regions provided.
        This validates that configuration preserves region settings.
        """
        config = SystemConfiguration(
            market_regions=regions,
            telegram=None,
            slack=None,
            email=None,
            custom_schedule=None
        )
        
        assert len(config.market_regions) == len(regions)
        for region in regions:
            assert region in config.market_regions
    
    def test_default_regions_are_complete(self):
        """
        Property: Default regions should include China, Hong Kong, and USA.
        This validates that the default configuration covers expected markets.
        """
        default_regions = SystemConfiguration.get_default_regions()
        
        assert len(default_regions) == 3
        assert MarketRegion.CHINA in default_regions
        assert MarketRegion.HONG_KONG in default_regions
        assert MarketRegion.USA in default_regions