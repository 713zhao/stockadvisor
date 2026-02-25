"""
Daily report model for stock market analysis.
"""

from dataclasses import dataclass
from datetime import datetime, date
from typing import List, Dict

from .market_region import MarketRegion
from .market_data import MarketSummary
from .recommendation import StockRecommendation


@dataclass
class DailyReport:
    """Comprehensive daily report containing all recommendations and summaries."""
    
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
        lines = [
            f"📊 Daily Market Report - {self.trading_date}",
            f"Generated: {self.generation_time.strftime('%Y-%m-%d %H:%M:%S')}",
            ""
        ]
        
        if self.has_recommendations():
            lines.append(f"🎯 {len(self.recommendations)} Recommendations:")
            for rec in self.recommendations:
                emoji = "🟢" if rec.recommendation_type.value == "buy" else "🔴" if rec.recommendation_type.value == "sell" else "🟡"
                lines.append(f"{emoji} {rec.symbol} ({rec.region.value.upper()}): {rec.recommendation_type.value.upper()}")
                lines.append(f"   Confidence: {rec.confidence_score:.1%}")
                lines.append("")
        else:
            lines.append("ℹ️ No recommendations for today")
        
        return "\n".join(lines)
    
    def format_for_slack(self) -> str:
        """Formats report for Slack delivery."""
        blocks = [
            f"*Daily Market Report - {self.trading_date}*",
            f"Generated: {self.generation_time.strftime('%Y-%m-%d %H:%M:%S')}",
            ""
        ]
        
        if self.has_recommendations():
            blocks.append(f"*{len(self.recommendations)} Recommendations:*")
            for rec in self.recommendations:
                symbol = ":large_green_circle:" if rec.recommendation_type.value == "buy" else ":red_circle:" if rec.recommendation_type.value == "sell" else ":yellow_circle:"
                blocks.append(f"{symbol} *{rec.symbol}* ({rec.region.value.upper()}): *{rec.recommendation_type.value.upper()}*")
                blocks.append(f"   Confidence: {rec.confidence_score:.1%}")
                blocks.append("")
        else:
            blocks.append(":information_source: No recommendations for today")
        
        return "\n".join(blocks)
    
    def format_for_email(self) -> str:
        """Formats report for Email delivery (HTML)."""
        html = f"""
        <html>
        <body>
            <h2>Daily Market Report - {self.trading_date}</h2>
            <p><strong>Generated:</strong> {self.generation_time.strftime('%Y-%m-%d %H:%M:%S')}</p>
        """
        
        if self.has_recommendations():
            html += f"<h3>{len(self.recommendations)} Recommendations</h3><ul>"
            for rec in self.recommendations:
                color = "green" if rec.recommendation_type.value == "buy" else "red" if rec.recommendation_type.value == "sell" else "orange"
                html += f"""
                <li>
                    <strong style="color: {color};">{rec.symbol} ({rec.region.value.upper()}): {rec.recommendation_type.value.upper()}</strong><br>
                    Confidence: {rec.confidence_score:.1%}<br>
                    Rationale: {rec.rationale}<br>
                    Risk: {rec.risk_assessment}
                </li>
                """
            html += "</ul>"
        else:
            html += "<p><em>No recommendations for today</em></p>"
        
        html += """
        </body>
        </html>
        """
        return html