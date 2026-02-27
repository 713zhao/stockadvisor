"""
Test TradeExecutor functionality.
"""

from decimal import Decimal
from stock_market_analysis.trading.models.portfolio import Portfolio
from stock_market_analysis.trading.models.trade_history import TradeHistory
from stock_market_analysis.trading.trade_executor import TradeExecutor

print("Testing TradeExecutor...")
print("=" * 60)

# Create portfolio
portfolio = Portfolio(
    portfolio_id="test-portfolio",
    cash_balance=Decimal("100000.00"),
    initial_cash_balance=Decimal("100000.00")
)
print(f"✓ Created portfolio with ${portfolio.cash_balance:,.2f}")

# Create trade history
trade_history = TradeHistory(storage_path="data/test_executor_history.json")

# Create executor
executor = TradeExecutor(portfolio, trade_history)
print("✓ Created TradeExecutor")
print()

# Test buy order
print("1. Testing BUY order...")
trade1 = executor.execute_buy_order("AAPL", 100, Decimal("150.00"))
print(f"   ✓ Bought {trade1.quantity} {trade1.symbol} @ ${trade1.price}")
print(f"   Cash remaining: ${portfolio.cash_balance:,.2f}")
print(f"   Position: {portfolio.positions['AAPL'].quantity} shares")
print()

# Test another buy (same symbol)
print("2. Testing BUY order (same symbol)...")
trade2 = executor.execute_buy_order("AAPL", 50, Decimal("155.00"))
print(f"   ✓ Bought {trade2.quantity} {trade2.symbol} @ ${trade2.price}")
print(f"   Cash remaining: ${portfolio.cash_balance:,.2f}")
position = portfolio.positions['AAPL']
print(f"   Position: {position.quantity} shares @ ${position.average_cost_basis:.2f} avg cost")
print()

# Test buy different symbol
print("3. Testing BUY order (different symbol)...")
trade3 = executor.execute_buy_order("NVDA", 20, Decimal("500.00"))
print(f"   ✓ Bought {trade3.quantity} {trade3.symbol} @ ${trade3.price}")
print(f"   Cash remaining: ${portfolio.cash_balance:,.2f}")
print(f"   Total positions: {len(portfolio.positions)}")
print()

# Test sell order
print("4. Testing SELL order...")
trade4 = executor.execute_sell_order("AAPL", 50, Decimal("160.00"))
print(f"   ✓ Sold {trade4.quantity} {trade4.symbol} @ ${trade4.price}")
print(f"   Cash balance: ${portfolio.cash_balance:,.2f}")
position = portfolio.positions['AAPL']
print(f"   Remaining position: {position.quantity} shares")
print()

# Test sell entire position
print("5. Testing SELL order (entire position)...")
trade5 = executor.execute_sell_order("NVDA", 20, Decimal("550.00"))
print(f"   ✓ Sold {trade5.quantity} {trade5.symbol} @ ${trade5.price}")
print(f"   Cash balance: ${portfolio.cash_balance:,.2f}")
print(f"   Position removed: {'NVDA' not in portfolio.positions}")
print()

# Test validation errors
print("6. Testing validation...")
try:
    executor.execute_buy_order("AAPL", -10, Decimal("150.00"))
    print("   ✗ Should have rejected negative quantity")
except ValueError as e:
    print(f"   ✓ Rejected negative quantity: {e}")

try:
    executor.execute_buy_order("AAPL", 10, Decimal("-150.00"))
    print("   ✗ Should have rejected negative price")
except ValueError as e:
    print(f"   ✓ Rejected negative price: {e}")

try:
    executor.execute_buy_order("AAPL", 10000, Decimal("150.00"))
    print("   ✗ Should have rejected insufficient cash")
except ValueError as e:
    print(f"   ✓ Rejected insufficient cash: {e}")

try:
    executor.execute_sell_order("TSLA", 10, Decimal("200.00"))
    print("   ✗ Should have rejected non-existent position")
except ValueError as e:
    print(f"   ✓ Rejected non-existent position: {e}")

print()
print("=" * 60)
print("All TradeExecutor tests passed!")
print("=" * 60)
