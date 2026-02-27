"""
Basic test of trading simulation components.
"""

from decimal import Decimal
from datetime import datetime

# Test imports
print("Testing imports...")
from stock_market_analysis.trading.models.portfolio import Portfolio
from stock_market_analysis.trading.models.position import Position
from stock_market_analysis.trading.models.trade import Trade, TradeAction
from stock_market_analysis.trading.models.trade_history import TradeHistory
print("✓ All models imported successfully")

# Test Portfolio
print("\nTesting Portfolio...")
portfolio = Portfolio(
    portfolio_id="test-123",
    cash_balance=Decimal("100000.00"),
    initial_cash_balance=Decimal("100000.00")
)
print(f"✓ Created portfolio with ${portfolio.cash_balance}")

# Test Position
print("\nTesting Position...")
position = Position(
    symbol="AAPL",
    quantity=100,
    average_cost_basis=Decimal("150.00")
)
value = position.calculate_value(Decimal("155.00"))
pnl = position.calculate_unrealized_pnl(Decimal("155.00"))
print(f"✓ Position: {position.quantity} {position.symbol} @ ${position.average_cost_basis}")
print(f"  Value at $155: ${value}")
print(f"  Unrealized P&L: ${pnl}")

# Test adding position to portfolio
portfolio.add_position("AAPL", position)
print(f"✓ Added position to portfolio")

# Test Trade
print("\nTesting Trade...")
trade = Trade(
    trade_id="trade-001",
    portfolio_id="test-123",
    symbol="AAPL",
    action=TradeAction.BUY,
    quantity=100,
    price=Decimal("150.00"),
    timestamp=datetime.now()
)
cost = trade.calculate_total_cost()
print(f"✓ Created trade: {trade.action.value} {trade.quantity} {trade.symbol} @ ${trade.price}")
print(f"  Total cost: ${cost}")

# Test serialization
print("\nTesting serialization...")
portfolio_json = portfolio.to_json()
print(f"✓ Portfolio serialized to JSON ({len(portfolio_json)} bytes)")

portfolio_restored = Portfolio.from_json(portfolio_json)
print(f"✓ Portfolio restored from JSON")
print(f"  Cash balance: ${portfolio_restored.cash_balance}")
print(f"  Positions: {len(portfolio_restored.positions)}")

# Test TradeHistory
print("\nTesting TradeHistory...")
trade_history = TradeHistory(storage_path="data/test_trade_history.json")
trade_history.add_trade(trade)
print(f"✓ Trade added to history")

trades = trade_history.get_trades_by_portfolio("test-123")
print(f"✓ Retrieved {len(trades)} trades for portfolio")

print("\n" + "=" * 60)
print("All basic tests passed!")
print("=" * 60)
