"""
Daily report model for stock market analysis.
"""

from dataclasses import dataclass
from datetime import datetime, date
from typing import List, Dict
from pathlib import Path
import json

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
    
    def format_for_telegram(self, full_rationale_count: int = 0, truncated_length: int = 80, max_recommendations: int = 0) -> str:
        """
        Formats report for Telegram delivery.
        
        Args:
            full_rationale_count: Number of top recommendations to show full rationale (0 = all)
            truncated_length: Maximum length for truncated rationale
            max_recommendations: Maximum total recommendations to include (0 = all)
                                Split evenly between BUY and SELL
        """
        lines = [
            f"📊 Market Report {self.trading_date.strftime('%m/%d')}",
            ""
        ]
        
        if self.has_recommendations():
            # Group by recommendation type and sort by confidence
            buys = sorted(
                [r for r in self.recommendations if r.recommendation_type.value == "buy"],
                key=lambda x: x.confidence_score,
                reverse=True
            )
            sells = sorted(
                [r for r in self.recommendations if r.recommendation_type.value == "sell"],
                key=lambda x: x.confidence_score,
                reverse=True
            )
            holds = [r for r in self.recommendations if r.recommendation_type.value == "hold"]
            
            # Limit recommendations if max_recommendations is set
            if max_recommendations > 0:
                # Split evenly between BUY and SELL
                max_per_type = max_recommendations // 2
                original_buy_count = len(buys)
                original_sell_count = len(sells)
                buys = buys[:max_per_type]
                sells = sells[:max_per_type]
                
                # Add note if recommendations were limited
                if original_buy_count > len(buys) or original_sell_count > len(sells):
                    lines.append(f"📋 Showing top {len(buys)} BUY and top {len(sells)} SELL recommendations")
                    lines.append(f"   (Full report with all {original_buy_count + original_sell_count + len(holds)} recommendations saved to disk)")
                    lines.append("")
            
            if buys:
                lines.append(f"🟢 BUY ({len(buys)}):")
                for idx, rec in enumerate(buys):
                    # Show full rationale for top N or if full_rationale_count is 0
                    show_full = (full_rationale_count == 0) or (idx < full_rationale_count)
                    rationale = rec.rationale if show_full else self._truncate_text(rec.rationale, truncated_length)
                    
                    lines.append(f"• {rec.name}")
                    lines.append(f"  {rec.symbol} | ${rec.target_price} | {rec.confidence_score:.0%}")
                    lines.append(f"  📊 {rationale}")
                    lines.append(f"  ⚠️ {rec.risk_assessment}")
                    if show_full:
                        lines.append(f"  {rec.get_stock_url()}")
                lines.append("")
            
            if sells:
                lines.append(f"🔴 SELL ({len(sells)}):")
                for idx, rec in enumerate(sells):
                    # Show full rationale for top N or if full_rationale_count is 0
                    show_full = (full_rationale_count == 0) or (idx < full_rationale_count)
                    rationale = rec.rationale if show_full else self._truncate_text(rec.rationale, truncated_length)
                    
                    lines.append(f"• {rec.name}")
                    lines.append(f"  {rec.symbol} | ${rec.target_price} | {rec.confidence_score:.0%}")
                    lines.append(f"  📊 {rationale}")
                    lines.append(f"  ⚠️ {rec.risk_assessment}")
                    if show_full:
                        lines.append(f"  {rec.get_stock_url()}")
                lines.append("")
            
            # Only show HOLD if not limiting recommendations, or if there's room
            if max_recommendations == 0 and holds:
                lines.append(f"🟡 HOLD ({len(holds)}):")
                for rec in holds:
                    # Always truncate HOLD recommendations
                    rationale = self._truncate_text(rec.rationale, truncated_length)
                    lines.append(f"• {rec.name}")
                    lines.append(f"  {rec.symbol} | ${rec.target_price} | {rec.confidence_score:.0%}")
                    lines.append(f"  📊 {rationale}")
                    lines.append(f"  ⚠️ {rec.risk_assessment}")
                lines.append("")
        else:
            lines.append("ℹ️ No recommendations today")
        
        return "\n".join(lines)
    
    def _truncate_text(self, text: str, max_length: int) -> str:
        """Truncates text to max_length and adds ellipsis."""
        if len(text) <= max_length:
            return text
        return text[:max_length].rsplit(' ', 1)[0] + "..."
    
    def format_for_slack(self) -> str:
        """Formats report for Slack delivery."""
        blocks = [
            f"*Daily Market Report - {self.trading_date}*",
            f"Generated: {self.generation_time.strftime('%Y-%m-%d %H:%M:%S')}",
            ""
        ]
        
        if self.has_recommendations():
            blocks.append(f"*{len(self.recommendations)} Recommendations:*")
            blocks.append("")
            for rec in self.recommendations:
                symbol = ":large_green_circle:" if rec.recommendation_type.value == "buy" else ":red_circle:" if rec.recommendation_type.value == "sell" else ":yellow_circle:"
                blocks.append(f"{symbol} *{rec.symbol}* ({rec.region.value.upper()}): *{rec.recommendation_type.value.upper()}*")
                blocks.append(f"   :moneybag: Target: ${rec.target_price}")
                blocks.append(f"   :chart_with_upwards_trend: Confidence: {rec.confidence_score:.1%}")
                blocks.append(f"   :bulb: Rationale: {rec.rationale}")
                blocks.append(f"   :warning: Risk: {rec.risk_assessment}")
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
    
    def save_to_disk(self, reports_dir: str = "reports") -> str:
        """
        Saves the full report to disk in multiple formats.
        
        Args:
            reports_dir: Directory to save reports (default: "reports")
            
        Returns:
            Path to the saved report directory
        """
        # Create reports directory if it doesn't exist
        report_path = Path(reports_dir) / self.trading_date.strftime('%Y-%m-%d')
        report_path.mkdir(parents=True, exist_ok=True)
        
        # Save as JSON
        json_file = report_path / f"{self.report_id}.json"
        report_data = {
            "report_id": self.report_id,
            "generation_time": self.generation_time.isoformat(),
            "trading_date": self.trading_date.isoformat(),
            "recommendations": [
                {
                    "symbol": rec.symbol,
                    "name": rec.name,
                    "region": rec.region.value,
                    "type": rec.recommendation_type.value,
                    "rationale": rec.rationale,
                    "risk_assessment": rec.risk_assessment,
                    "confidence_score": rec.confidence_score,
                    "target_price": str(rec.target_price) if rec.target_price else None,
                    "url": rec.get_stock_url(),
                    "generated_at": rec.generated_at.isoformat()
                }
                for rec in self.recommendations
            ],
            "market_summaries": {
                region.value: {
                    "trading_date": summary.trading_date.isoformat(),
                    "total_stocks_analyzed": summary.total_stocks_analyzed,
                    "market_trend": summary.market_trend,
                    "notable_events": summary.notable_events,
                    "index_performance": {k: str(v) for k, v in summary.index_performance.items()}
                }
                for region, summary in self.market_summaries.items()
            }
        }
        
        with open(json_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        # Save as HTML
        html_file = report_path / f"{self.report_id}.html"
        with open(html_file, 'w') as f:
            f.write(self.format_for_email())
        
        # Save as plain text
        txt_file = report_path / f"{self.report_id}.txt"
        with open(txt_file, 'w', encoding='utf-8') as f:
            f.write(self.format_for_telegram())
        
        return str(report_path)