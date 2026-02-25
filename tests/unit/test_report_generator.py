"""
Unit tests for the Report Generator component.
"""

import pytest
from datetime import datetime, date
from decimal import Decimal

from stock_market_analysis.components import ReportGenerator
from stock_market_analysis.models import (
    StockRecommendation,
    RecommendationType,
    MarketRegion,
    MarketSummary,
    DailyReport
)


class TestReportGenerator:
    """Test suite for ReportGenerator component."""
    
    def test_generate_report_with_recommendations(self):
        """
        Tests that a report is generated with recommendations.
        Validates: Requirements 3.1, 3.2, 3.3, 3.4
        """
        generator = ReportGenerator()
        
        # Create sample recommendations
        recommendations = [
            StockRecommendation(
                symbol="AAPL",
                region=MarketRegion.USA,
                recommendation_type=RecommendationType.BUY,
                rationale="Strong upward momentum",
                risk_assessment="Low risk",
                confidence_score=0.85,
                target_price=Decimal("150.00"),
                generated_at=datetime.now()
            ),
            StockRecommendation(
                symbol="GOOGL",
                region=MarketRegion.USA,
                recommendation_type=RecommendationType.HOLD,
                rationale="Stable performance",
                risk_assessment="Medium risk",
                confidence_score=0.70,
                target_price=None,
                generated_at=datetime.now()
            )
        ]
        
        # Create market summaries
        market_summaries = {
            MarketRegion.USA: MarketSummary(
                region=MarketRegion.USA,
                trading_date=date.today(),
                total_stocks_analyzed=100,
                market_trend="bullish",
                notable_events=["Fed rate decision"],
                index_performance={"S&P 500": Decimal("1.5")}
            )
        }
        
        # Generate report
        report = generator.generate_daily_report(recommendations, market_summaries)
        
        # Verify report structure
        assert report is not None
        assert isinstance(report, DailyReport)
        assert report.report_id is not None
        assert report.report_id.startswith("REPORT-")
        
        # Verify timestamp
        assert report.generation_time is not None
        assert isinstance(report.generation_time, datetime)
        
        # Verify trading date
        assert report.trading_date == date.today()
        
        # Verify recommendations are included
        assert len(report.recommendations) == 2
        assert report.recommendations == recommendations
        assert report.has_recommendations()
        
        # Verify market summaries are included
        assert len(report.market_summaries) == 1
        assert MarketRegion.USA in report.market_summaries
        assert report.market_summaries[MarketRegion.USA] == market_summaries[MarketRegion.USA]
    
    def test_generate_report_with_no_recommendations(self):
        """
        Tests that a report is generated even when no recommendations exist.
        Validates: Requirement 3.5
        """
        generator = ReportGenerator()
        
        # Create market summaries but no recommendations
        market_summaries = {
            MarketRegion.USA: MarketSummary(
                region=MarketRegion.USA,
                trading_date=date.today(),
                total_stocks_analyzed=100,
                market_trend="neutral",
                notable_events=[],
                index_performance={"S&P 500": Decimal("0.1")}
            )
        }
        
        # Generate report with empty recommendations list
        report = generator.generate_daily_report([], market_summaries)
        
        # Verify report is created
        assert report is not None
        assert isinstance(report, DailyReport)
        
        # Verify no recommendations
        assert len(report.recommendations) == 0
        assert not report.has_recommendations()
        
        # Verify report still has timestamp and summaries
        assert report.generation_time is not None
        assert report.trading_date == date.today()
        assert len(report.market_summaries) == 1
    
    def test_generate_report_with_multiple_regions(self):
        """
        Tests report generation with multiple market regions.
        Validates: Requirements 3.3
        """
        generator = ReportGenerator()
        
        # Create recommendations from multiple regions
        recommendations = [
            StockRecommendation(
                symbol="AAPL",
                region=MarketRegion.USA,
                recommendation_type=RecommendationType.BUY,
                rationale="Strong momentum",
                risk_assessment="Low risk",
                confidence_score=0.85,
                target_price=Decimal("150.00"),
                generated_at=datetime.now()
            ),
            StockRecommendation(
                symbol="0700.HK",
                region=MarketRegion.HONG_KONG,
                recommendation_type=RecommendationType.SELL,
                rationale="Downward trend",
                risk_assessment="Medium risk",
                confidence_score=0.75,
                target_price=Decimal("300.00"),
                generated_at=datetime.now()
            )
        ]
        
        # Create market summaries for multiple regions
        market_summaries = {
            MarketRegion.USA: MarketSummary(
                region=MarketRegion.USA,
                trading_date=date.today(),
                total_stocks_analyzed=100,
                market_trend="bullish",
                notable_events=[],
                index_performance={"S&P 500": Decimal("1.5")}
            ),
            MarketRegion.HONG_KONG: MarketSummary(
                region=MarketRegion.HONG_KONG,
                trading_date=date.today(),
                total_stocks_analyzed=50,
                market_trend="bearish",
                notable_events=["Market volatility"],
                index_performance={"Hang Seng": Decimal("-0.8")}
            ),
            MarketRegion.CHINA: MarketSummary(
                region=MarketRegion.CHINA,
                trading_date=date.today(),
                total_stocks_analyzed=75,
                market_trend="neutral",
                notable_events=[],
                index_performance={"Shanghai Composite": Decimal("0.2")}
            )
        }
        
        # Generate report
        report = generator.generate_daily_report(recommendations, market_summaries)
        
        # Verify all regions are included in summaries
        assert len(report.market_summaries) == 3
        assert MarketRegion.USA in report.market_summaries
        assert MarketRegion.HONG_KONG in report.market_summaries
        assert MarketRegion.CHINA in report.market_summaries
        
        # Verify recommendations from multiple regions
        assert len(report.recommendations) == 2
        regions_in_recommendations = {rec.region for rec in report.recommendations}
        assert MarketRegion.USA in regions_in_recommendations
        assert MarketRegion.HONG_KONG in regions_in_recommendations
    
    def test_report_id_uniqueness(self):
        """
        Tests that each generated report has a unique ID.
        """
        generator = ReportGenerator()
        
        market_summaries = {
            MarketRegion.USA: MarketSummary(
                region=MarketRegion.USA,
                trading_date=date.today(),
                total_stocks_analyzed=100,
                market_trend="neutral",
                notable_events=[],
                index_performance={"S&P 500": Decimal("0.0")}
            )
        }
        
        # Generate multiple reports
        report1 = generator.generate_daily_report([], market_summaries)
        report2 = generator.generate_daily_report([], market_summaries)
        report3 = generator.generate_daily_report([], market_summaries)
        
        # Verify all IDs are unique
        assert report1.report_id != report2.report_id
        assert report2.report_id != report3.report_id
        assert report1.report_id != report3.report_id
        
        # Verify ID format
        assert report1.report_id.startswith("REPORT-")
        assert report2.report_id.startswith("REPORT-")
        assert report3.report_id.startswith("REPORT-")
    
    def test_report_formatting_telegram(self):
        """
        Tests that report can be formatted for Telegram.
        Validates: Requirement 4.5
        """
        generator = ReportGenerator()
        
        recommendations = [
            StockRecommendation(
                symbol="AAPL",
                region=MarketRegion.USA,
                recommendation_type=RecommendationType.BUY,
                rationale="Strong momentum",
                risk_assessment="Low risk",
                confidence_score=0.85,
                target_price=Decimal("150.00"),
                generated_at=datetime.now()
            )
        ]
        
        market_summaries = {
            MarketRegion.USA: MarketSummary(
                region=MarketRegion.USA,
                trading_date=date.today(),
                total_stocks_analyzed=100,
                market_trend="bullish",
                notable_events=[],
                index_performance={"S&P 500": Decimal("1.5")}
            )
        }
        
        report = generator.generate_daily_report(recommendations, market_summaries)
        
        # Format for Telegram
        telegram_text = report.format_for_telegram()
        
        # Verify formatting
        assert telegram_text is not None
        assert len(telegram_text) > 0
        assert "Daily Market Report" in telegram_text
        assert str(report.trading_date) in telegram_text
        assert "AAPL" in telegram_text
        assert "BUY" in telegram_text
    
    def test_report_formatting_slack(self):
        """
        Tests that report can be formatted for Slack.
        Validates: Requirement 4.5
        """
        generator = ReportGenerator()
        
        recommendations = [
            StockRecommendation(
                symbol="GOOGL",
                region=MarketRegion.USA,
                recommendation_type=RecommendationType.HOLD,
                rationale="Stable",
                risk_assessment="Medium risk",
                confidence_score=0.70,
                target_price=None,
                generated_at=datetime.now()
            )
        ]
        
        market_summaries = {
            MarketRegion.USA: MarketSummary(
                region=MarketRegion.USA,
                trading_date=date.today(),
                total_stocks_analyzed=100,
                market_trend="neutral",
                notable_events=[],
                index_performance={"S&P 500": Decimal("0.1")}
            )
        }
        
        report = generator.generate_daily_report(recommendations, market_summaries)
        
        # Format for Slack
        slack_text = report.format_for_slack()
        
        # Verify formatting
        assert slack_text is not None
        assert len(slack_text) > 0
        assert "Daily Market Report" in slack_text
        assert "GOOGL" in slack_text
        assert "HOLD" in slack_text
    
    def test_report_formatting_email(self):
        """
        Tests that report can be formatted for Email (HTML).
        Validates: Requirement 4.5
        """
        generator = ReportGenerator()
        
        recommendations = [
            StockRecommendation(
                symbol="TSLA",
                region=MarketRegion.USA,
                recommendation_type=RecommendationType.SELL,
                rationale="Downward trend",
                risk_assessment="High risk",
                confidence_score=0.80,
                target_price=Decimal("200.00"),
                generated_at=datetime.now()
            )
        ]
        
        market_summaries = {
            MarketRegion.USA: MarketSummary(
                region=MarketRegion.USA,
                trading_date=date.today(),
                total_stocks_analyzed=100,
                market_trend="bearish",
                notable_events=[],
                index_performance={"S&P 500": Decimal("-1.2")}
            )
        }
        
        report = generator.generate_daily_report(recommendations, market_summaries)
        
        # Format for Email
        email_html = report.format_for_email()
        
        # Verify HTML formatting
        assert email_html is not None
        assert len(email_html) > 0
        assert "<html>" in email_html
        assert "</html>" in email_html
        assert "Daily Market Report" in email_html
        assert "TSLA" in email_html
        assert "SELL" in email_html
    
    def test_report_formatting_with_no_recommendations(self):
        """
        Tests that report formatting works with no recommendations.
        Validates: Requirement 3.5, 4.5
        """
        generator = ReportGenerator()
        
        market_summaries = {
            MarketRegion.USA: MarketSummary(
                region=MarketRegion.USA,
                trading_date=date.today(),
                total_stocks_analyzed=100,
                market_trend="neutral",
                notable_events=[],
                index_performance={"S&P 500": Decimal("0.0")}
            )
        }
        
        report = generator.generate_daily_report([], market_summaries)
        
        # Format for all channels
        telegram_text = report.format_for_telegram()
        slack_text = report.format_for_slack()
        email_html = report.format_for_email()
        
        # Verify all formats handle empty recommendations
        assert "No recommendations" in telegram_text or "no recommendations" in telegram_text.lower()
        assert "No recommendations" in slack_text or "no recommendations" in slack_text.lower()
        assert "No recommendations" in email_html or "no recommendations" in email_html.lower()
        
        # Verify all formats are non-empty
        assert len(telegram_text) > 0
        assert len(slack_text) > 0
        assert len(email_html) > 0
