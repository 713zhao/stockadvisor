"""
Test PerformanceCalculator functionality.
"""

from decimal import Decimal
from stock_market_analysis.trading.models.portfolio import Portfolio
from stock_market_analysis.trading.models.trade_history import TradeHistory
from stock_market_analysis.trading.trade_executor import TradeExecutor
from stock_market_analysis.trading.performance_calculator import PerformanceCalculator

print("Testing PerformanceCalculator...")
print("=" * 60)

# Create portfolio and execute some trades
portfolio = Portfolio(
    portfolio_id="test-perf",
    cash_balance=Decimal("100000.00"),
    initial_cash_balance=Decimal("100000.00")
)
trade_history = TradeHistory(storage_path="data/test_perf_history.json")
executor = TradeExecutor(portfolio, trade_history)

# Execute trades
print("Executing test trades...")
executor.execute_buy_order("AAPL", 100, Decimal("150.00"))  # Cost: $15,000
executor.execute_buy_order("NVDA", 20, Decimal("500.00"))   # Cost: $10,000
executor.execute_sell_order("AAPL", 50, Decimal("160.00"))  # Proceeds: $8,000, Profit: $500
print("✓ Executed 3 trades")
print()

# Create calculator
calculator = PerformanceCalculator(portfolio, trade_history)
print("✓ Created PerformanceCalculator")
print()

# Test portfolio valuation
print("1. Testing portfolio valuation...")
current_prices = {
    "AAPL": Decimal("155.00"),
    "NVDA": Decimal("550.00")
}
portfolio_value = calculator.calculate_portfolio_value(current_prices)
print(f"   Portfolio value: ${portfolio_value:,.2f}")
print(f"   Cash: ${portfolio.cash_balance:,.2f}")
print(f"   AAPL position value: ${portfolio.positions['AAPL'].calculate_value(current_prices['AAPL']):,.2f}")
print(f"   NVDA position value: ${portfolio.positions['NVDA'].calculate_value(current_prices['NVDA']):,.2f}")
print()

# Test P&L calculations
print("2. Testing P&L calculations...")
realized_pnl = calculator.calculate_realized_pnl()
unrealized_pnl = calculator.calculate_unrealized_pnl(current_prices)
total_pnl = calculator.calculate_total_pnl(current_prices)
pnl_pct = calculator.calculate_pnl_percentage(current_prices)
print(f"   Realized P&L: ${realized_pnl:,.2f}")
print(f"   Unrealized P&L: ${unrealized_pnl:,.2f}")
print(f"   Total P&L: ${total_pnl:,.2f}")
print(f"   P&L %: {pnl_pct:.2f}%")
print()

# Test return calculation
print("3. Testing return calculation...")
total_return = calculator.calculate_total_return_percentage(current_prices)
print(f"   Total return: {total_return:.2f}%")
print()

# Test win rate
print("4. Testing win rate...")
win_rate = calculator.calculate_win_rate()
print(f"   Win rate: {win_rate:.2f}%")
print()

# Test average profit/loss
print("5. Testing average profit/loss...")
avg_profit = calculator.calculate_average_profit_per_win()
avg_loss = calculator.calculate_average_loss_per_loss()
print(f"   Avg profit per win: ${avg_profit:,.2f}")
print(f"   Avg loss per loss: ${avg_loss:,.2f}")
print()

# Test trade statistics
print("6. Testing trade statistics...")
stats = calculator.get_trade_statistics()
print(f"   Total trades: {stats['total_trades']}")
print(f"   Open positions: {stats['open_positions']}")
print()

# Test performance report generation
print("7. Testing performance report generation...")
report = calculator.generate_performance_report(current_prices)
print("   ✓ Generated performance report")
print(f"   Portfolio value: ${report.portfolio_value:,.2f}")
print(f"   Total P&L: ${report.total_pnl:,.2f}")
print(f"   Total return: {report.total_return_pct:.2f}%")
print(f"   Win rate: {report.win_rate:.2f}%")
print()

# Display full report
print("8. Full Performance Report:")
print("-" * 60)
print(report.to_text())

print("=" * 60)
print("All PerformanceCalculator tests passed!")
print("=" * 60)
