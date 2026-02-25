"""
Integration tests for report generation with other components.
"""

import pytest
from datetime import datetime, date
from decimal import Decimal

from stock_market_analysis.components import (
    ReportGenerator,
    AnalysisEngine,
    MarketMonitor,
    MockMarketDataAPI
)
from stock_market_analysis.models import (
    MarketRegion,
    MarketSummary
)


class TestReportGenerationIntegration:
    """Integration tests for report generation with analysis engine."""
    
    def test_generate_report_from_analysis_results(self):
        """
        Tests generating a report from actual analysis engine output.
        """
        # Setup components
        api = MockMarketDataAPI()
        monitor = MarketMonitor(api)
        engine = AnalysisEngine(monitor)
        generator = ReportGenerator()
        
        # Collect market data
        regions = [MarketRegion.USA]
        market_data = monitor.collect_market_data(regions)
        
        # Generate recommendations
        recommendations = engine.analyze_and_recommend(market_data)
        
        # Create market summaries
        market_summaries = {
            MarketRegion.USA: MarketSummary(
                region=MarketRegion.USA,
                trading_date=date.today(),
                total_stocks_analyzed=len(market_data.data_by_region.get(MarketRegion.USA, [])),
                market_trend="bullish",
                notable_events=[],
                index_performance={"S&P 500": Decimal("1.5")}
            )
        }
        
        # Generate report
        report = generator.generate_daily_report(recommendations, market_summaries)
        
        # Verify report structure
        assert report is not None
        assert report.report_id is not None
        assert report.generation_time is not None
        assert report.trading_date == date.today()
        assert isinstance(report.recommendations, list)
        assert len(report.market_summaries) > 0
        
        # Verify report can be formatted
        telegram_text = report.format_for_telegram()
        slack_text = report.format_for_slack()
        email_html = report.format_for_email()
        
        assert len(telegram_text) > 0
        assert len(slack_text) > 0
        assert len(email_html) > 0
    
    def test_generate_report_with_empty_analysis(self):
        """
        Tests generating a report when analysis produces no recommendations.
        """
        generator = ReportGenerator()
        
        # Empty recommendations
        recommendations = []
        
        # Market summaries
        market_summaries = {
            MarketRegion.USA: MarketSummary(
                region=MarketRegion.USA,
                trading_date=date.today(),
                total_stocks_analyzed=0,
                market_trend="neutral",
                notable_events=[],
                index_performance={"S&P 500": Decimal("0.0")}
            )
        }
        
        # Generate report
        report = generator.generate_daily_report(recommendations, market_summaries)
        
        # Verify report is created even with no recommendations
        assert report is not None
        assert not report.has_recommendations()
        assert len(report.recommendations) == 0
        
        # Verify formatting works
        telegram_text = report.format_for_telegram()
        assert "no recommendations" in telegram_text.lower()
