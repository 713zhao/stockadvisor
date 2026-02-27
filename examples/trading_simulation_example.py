"""
Trading Simulation Example

Demonstrates basic usage of the trading simulation system.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from decimal import Decimal
from datetime import datetime
from stock_market_analysis.trading import TradingSimulator
from stock_market_analysis.components import ConfigurationManager
from stock_market_analysis.models import (
    StockRecommendation,
    RecommendationType,
    MarketRegion
)


def main():
    print("=" * 60)
    print("Trading Simulation Example")
    print("=" * 60)
    print()
    
    # Initialize components
    config_manager = ConfigurationManager()
    simulator = TradingSimulator(config_manager)
    
    # Create portfolio
    print("1. Creating portfolio...")
    initial_cash = Decimal("100000.00")
    portfolio_id = simulator.create_portfolio(initial_cash)
    print(f"   ✓ Portfolio created: {portfolio_id}")
    print(f"   Initial cash: ${initial_cash:,.2f}")
    print()
    
    # Execute manual buy order
    print("2. Executing manual BUY order...")
    trade1 = simulator.execute_trade(
        portfolio_id=portfolio_id,
        symbol="AAPL",
        action="BUY",
        quantity=100,
        price=Decimal("150.00")
    )
    print(f"   ✓ Bought {trade1.quantity} {trade1.symbol} @ ${trade1.price}")
    portfolio = simulator.get_portfolio(portfolio_id)
    print(f"   Cash remaining: ${portfolio.cash_balance:,.2f}")
    print()
    
    # Execute another buy
    print("3. Executing another BUY order...")
    trade2 = simulator.execute_trade(
        portfolio_id=portfolio_id,
        symbol="NVDA",
        action="BUY",
        quantity=50,
        price=Decimal("500.00")
    )
    print(f"   ✓ Bought {trade2.quantity} {trade2.symbol} @ ${trade2.price}")
    portfolio = simulator.get_portfolio(portfolio_id)
    print(f"   Cash remaining: ${portfolio.cash_balance:,.2f}")
    print()
    
    # View portfolio
    print("4. Current portfolio:")
    print(f"   Cash: ${portfolio.cash_balance:,.2f}")
    print(f"   Positions:")
    for symbol, position in portfolio.positions.items():
        value = position.calculate_value(position.average_cost_basis)
        print(f"     {symbol}: {position.quantity} shares @ ${position.average_cost_basis:.2f} = ${value:,.2f}")
    print()
    
    # Process a recommendation
    print("5. Processing a BUY recommendation...")
    recommendation = StockRecommendation(
        symbol="MSFT",
        name="Microsoft Corporation",
        region=MarketRegion.USA,
        recommendation_type=RecommendationType.BUY,
        rationale="Strong AI growth and cloud revenue",
        risk_assessment="Low risk: stable tech leader",
        confidence_score=0.85,
        target_price=Decimal("400.00"),
        generated_at=datetime.now()
    )
    
    trade3 = simulator.process_recommendation(portfolio_id, recommendation)
    if trade3:
        print(f"   ✓ Executed: {trade3.action.value} {trade3.quantity} {trade3.symbol} @ ${trade3.price}")
    else:
        print("   No trade executed (below threshold or insufficient funds)")
    print()
    
    # Execute a sell order
    print("6. Executing SELL order...")
    trade4 = simulator.execute_trade(
        portfolio_id=portfolio_id,
        symbol="AAPL",
        action="SELL",
        quantity=50,
        price=Decimal("155.00")
    )
    print(f"   ✓ Sold {trade4.quantity} {trade4.symbol} @ ${trade4.price}")
    portfolio = simulator.get_portfolio(portfolio_id)
    print(f"   Cash balance: ${portfolio.cash_balance:,.2f}")
    print()
    
    # Get performance report
    print("7. Performance Report:")
    print("-" * 60)
    report = simulator.get_performance_report(portfolio_id)
    print(report.to_text())
    
    # Save portfolio
    print("\n8. Saving portfolio...")
    filepath = "data/example_portfolio.json"
    simulator.save_portfolio(portfolio_id, filepath)
    print(f"   ✓ Portfolio saved to {filepath}")
    print()
    
    # Demonstrate loading
    print("9. Loading portfolio...")
    loaded_id = simulator.load_portfolio(filepath)
    print(f"   ✓ Portfolio loaded: {loaded_id}")
    loaded_portfolio = simulator.get_portfolio(loaded_id)
    print(f"   Cash balance: ${loaded_portfolio.cash_balance:,.2f}")
    print(f"   Positions: {len(loaded_portfolio.positions)}")
    print()
    
    print("=" * 60)
    print("Example complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
