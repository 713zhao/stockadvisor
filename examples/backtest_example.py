"""
Backtest Example

Demonstrates how to run a backtest with historical recommendations.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from decimal import Decimal
from datetime import datetime, timedelta
from stock_market_analysis.trading import BacktestEngine
from stock_market_analysis.components import ConfigurationManager
from stock_market_analysis.models import (
    StockRecommendation,
    RecommendationType,
    MarketRegion
)


def create_sample_recommendations():
    """Creates sample historical recommendations for backtesting."""
    base_date = datetime.now() - timedelta(days=30)
    recommendations = []
    
    # Day 1: Buy AAPL
    recommendations.append(StockRecommendation(
        symbol="AAPL",
        name="Apple Inc.",
        region=MarketRegion.USA,
        recommendation_type=RecommendationType.BUY,
        rationale="Strong iPhone sales and services growth",
        risk_assessment="Low risk: market leader",
        confidence_score=0.85,
        target_price=Decimal("150.00"),
        generated_at=base_date
    ))
    
    # Day 2: Buy NVDA
    recommendations.append(StockRecommendation(
        symbol="NVDA",
        name="NVIDIA Corporation",
        region=MarketRegion.USA,
        recommendation_type=RecommendationType.BUY,
        rationale="AI chip demand surge",
        risk_assessment="Medium risk: high valuation",
        confidence_score=0.90,
        target_price=Decimal("500.00"),
        generated_at=base_date + timedelta(days=1)
    ))
    
    # Day 5: Buy MSFT
    recommendations.append(StockRecommendation(
        symbol="MSFT",
        name="Microsoft Corporation",
        region=MarketRegion.USA,
        recommendation_type=RecommendationType.BUY,
        rationale="Cloud growth and AI integration",
        risk_assessment="Low risk: diversified revenue",
        confidence_score=0.80,
        target_price=Decimal("380.00"),
        generated_at=base_date + timedelta(days=5)
    ))
    
    # Day 10: Sell AAPL (take profit)
    recommendations.append(StockRecommendation(
        symbol="AAPL",
        name="Apple Inc.",
        region=MarketRegion.USA,
        recommendation_type=RecommendationType.SELL,
        rationale="Target price reached, take profit",
        risk_assessment="Low risk",
        confidence_score=0.75,
        target_price=Decimal("160.00"),
        generated_at=base_date + timedelta(days=10)
    ))
    
    # Day 15: Buy GOOGL
    recommendations.append(StockRecommendation(
        symbol="GOOGL",
        name="Alphabet Inc.",
        region=MarketRegion.USA,
        recommendation_type=RecommendationType.BUY,
        rationale="Search dominance and AI advancements",
        risk_assessment="Low risk: strong fundamentals",
        confidence_score=0.82,
        target_price=Decimal("140.00"),
        generated_at=base_date + timedelta(days=15)
    ))
    
    # Day 20: Sell NVDA (take profit)
    recommendations.append(StockRecommendation(
        symbol="NVDA",
        name="NVIDIA Corporation",
        region=MarketRegion.USA,
        recommendation_type=RecommendationType.SELL,
        rationale="Significant gains, reduce exposure",
        risk_assessment="Medium risk",
        confidence_score=0.78,
        target_price=Decimal("550.00"),
        generated_at=base_date + timedelta(days=20)
    ))
    
    # Day 25: Hold recommendations (below threshold)
    recommendations.append(StockRecommendation(
        symbol="TSLA",
        name="Tesla Inc.",
        region=MarketRegion.USA,
        recommendation_type=RecommendationType.HOLD,
        rationale="Neutral outlook, wait for clarity",
        risk_assessment="High risk: volatile",
        confidence_score=0.60,
        target_price=None,
        generated_at=base_date + timedelta(days=25)
    ))
    
    return recommendations


def main():
    print("=" * 60)
    print("Backtest Example")
    print("=" * 60)
    print()
    
    # Create sample recommendations
    print("1. Creating sample historical recommendations...")
    recommendations = create_sample_recommendations()
    print(f"   ✓ Created {len(recommendations)} recommendations")
    print(f"   Date range: {recommendations[0].generated_at.date()} to {recommendations[-1].generated_at.date()}")
    print()
    
    # Initialize backtest engine
    print("2. Initializing backtest engine...")
    config_manager = ConfigurationManager()
    engine = BacktestEngine(config_manager)
    print("   ✓ Engine initialized")
    print()
    
    # Run backtest
    print("3. Running backtest...")
    print("   Initial cash: $100,000.00")
    print("   Confidence threshold: 0.70")
    print("   Position sizing: 10% of portfolio")
    print()
    
    result = engine.run_backtest(
        recommendations=recommendations,
        initial_cash=Decimal("100000.00"),
        confidence_threshold=0.70
    )
    
    print("   ✓ Backtest complete")
    print()
    
    # Display results
    print("4. Backtest Results:")
    print("=" * 60)
    print(f"Backtest ID: {result.backtest_id}")
    print(f"Period: {result.start_date.date()} to {result.end_date.date()}")
    print(f"Recommendations processed: {result.total_recommendations_processed}")
    print()
    print(f"Initial Cash: ${result.initial_cash:,.2f}")
    print(f"Final Portfolio Value: ${result.final_portfolio_value:,.2f}")
    print()
    
    # Display performance report
    print("Performance Metrics:")
    print("-" * 60)
    report = result.performance_report
    print(f"Total Return: {report.total_return_pct:.2f}%")
    print(f"Total P&L: ${report.total_pnl:,.2f}")
    print(f"Realized P&L: ${report.realized_pnl:,.2f}")
    print(f"Unrealized P&L: ${report.unrealized_pnl:,.2f}")
    print()
    print(f"Total Trades: {report.total_trades}")
    print(f"Win Rate: {report.win_rate:.2f}%")
    print(f"Avg Profit/Win: ${report.avg_profit_per_win:,.2f}")
    print(f"Avg Loss/Loss: ${report.avg_loss_per_loss:,.2f}")
    print(f"Max Drawdown: {report.max_drawdown:.2f}%")
    print()
    
    # Display open positions
    if report.open_positions_list:
        print("Open Positions:")
        print("-" * 60)
        for pos in report.open_positions_list:
            print(f"{pos['symbol']:8} | Qty: {pos['quantity']:6} | "
                  f"Value: ${pos['current_value']:>10,.2f} | "
                  f"P&L: ${pos['unrealized_pnl']:>10,.2f}")
        print()
    
    # Display recent trades
    if report.recent_trades:
        print("Trade History:")
        print("-" * 60)
        for trade in report.recent_trades:
            print(f"{trade['timestamp'][:10]} | {trade['action']:4} | "
                  f"{trade['symbol']:8} | Qty: {trade['quantity']:6} | "
                  f"Price: ${trade['price']:>8,.2f}")
        print()
    
    # Save results
    print("5. Saving backtest results...")
    filepath = f"data/backtest_{result.backtest_id}.json"
    with open(filepath, 'w') as f:
        f.write(result.to_json())
    print(f"   ✓ Results saved to {filepath}")
    print()
    
    print("=" * 60)
    print("Backtest complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
