# Implementation Plan: Trading Simulation System

## Overview

This implementation plan creates a trading simulation system that integrates with the existing stock market analysis system. The system will execute virtual trades based on AnalysisEngine recommendations, track portfolio performance, and provide backtesting capabilities. Implementation follows a bottom-up approach: data models → core components → integration → testing.

## Tasks

- [x] 1. Set up project structure and data models
  - [x] 1.1 Create trading simulation module structure
    - Create `stock_market_analysis/trading/` directory
    - Create `__init__.py` with module exports
    - Create `stock_market_analysis/trading/models/` directory for data models
    - _Requirements: All requirements depend on proper structure_
  
  - [x] 1.2 Implement Portfolio data model
    - Create `stock_market_analysis/trading/models/portfolio.py`
    - Implement Portfolio class with portfolio_id, cash_balance, positions dict, creation_timestamp, initial_cash_balance
    - Implement methods: get_cash_balance(), get_positions(), add_position(), remove_position(), update_cash()
    - Use Decimal for all monetary values to preserve precision
    - Implement JSON serialization and deserialization methods
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 7.4, 7.5, 12.1, 12.2, 12.3, 12.4, 12.5, 12.6_
  
  - [ ]* 1.3 Write property tests for Portfolio model
    - **Property 1: Cash balance non-negativity** - Cash balance never becomes negative after valid operations
    - **Property 2: Portfolio value consistency** - Total portfolio value equals cash plus sum of position values
    - **Property 3: Serialization round-trip** - Portfolio serialized then deserialized equals original
    - **Property 4: Decimal precision preservation** - Monetary values maintain precision through operations
    - **Validates: Requirements 1.1, 1.4, 12.6**
  
  - [x] 1.4 Implement Position data model
    - Create `stock_market_analysis/trading/models/position.py`
    - Implement Position class with symbol, quantity, average_cost_basis
    - Implement methods: update_average_cost(), calculate_value(), calculate_unrealized_pnl()
    - Use Decimal for cost basis and calculations
    - _Requirements: 3.4, 3.5, 3.6, 4.4, 4.5, 7.2, 8.2_
  
  - [ ]* 1.5 Write property tests for Position model
    - **Property 5: Average cost basis calculation** - Adding shares updates average cost correctly
    - **Property 6: Position value calculation** - Position value equals quantity times current price
    - **Property 7: Unrealized P&L calculation** - Unrealized P&L equals (current_price - avg_cost) × quantity
    - **Validates: Requirements 3.6, 7.2, 8.2**

- [x] 2. Implement Trade and TradeHistory models
  - [x] 2.1 Implement Trade data model
    - Create `stock_market_analysis/trading/models/trade.py`
    - Implement Trade class with trade_id, portfolio_id, symbol, action (BUY/SELL), quantity, price, timestamp, recommendation_id
    - Implement calculate_total_cost() and calculate_proceeds() methods
    - Use Decimal for price and monetary calculations
    - Implement JSON serialization
    - _Requirements: 3.7, 4.6, 5.6, 10.1, 10.2_
  
  - [x] 2.2 Implement TradeHistory persistence
    - Create `stock_market_analysis/trading/models/trade_history.py`
    - Implement TradeHistory class with methods: add_trade(), get_trades_by_portfolio(), get_trades_by_symbol(), get_trades_by_date_range(), get_trades_by_action()
    - Store trades in JSON format in `data/trade_history.json`
    - Implement file-based persistence with atomic writes
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.7_
  
  - [ ]* 2.3 Write property tests for Trade and TradeHistory
    - **Property 8: Trade cost calculation** - Buy trade cost equals quantity × price
    - **Property 9: Trade proceeds calculation** - Sell trade proceeds equals quantity × price
    - **Property 10: Trade history persistence** - Trades saved and loaded maintain all data
    - **Property 11: Trade query correctness** - Filtered queries return only matching trades
    - **Validates: Requirements 10.1, 10.3, 10.4, 10.5, 10.6**

- [x] 3. Implement PerformanceReport and BacktestResult models
  - [x] 3.1 Implement PerformanceReport data model
    - Create `stock_market_analysis/trading/models/performance_report.py`
    - Implement PerformanceReport class with portfolio_value, cash_balance, total_positions, realized_pnl, unrealized_pnl, total_pnl, total_return_pct, win_rate, avg_profit_per_win, avg_loss_per_loss, max_drawdown, total_trades, open_positions_list, recent_trades
    - Implement to_json() and to_text() export methods
    - _Requirements: 7.1, 7.2, 8.1, 8.2, 8.3, 8.4, 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7, 15.1, 15.2, 15.3, 15.4, 15.5, 15.6, 15.7_
  
  - [x] 3.2 Implement BacktestResult data model
    - Create `stock_market_analysis/trading/models/backtest_result.py`
    - Implement BacktestResult class with backtest_id, start_date, end_date, initial_cash, final_portfolio_value, performance_report, total_recommendations_processed
    - Implement JSON serialization
    - _Requirements: 11.5_
  
  - [ ]* 3.3 Write unit tests for report models
    - Test PerformanceReport JSON and text export formats
    - Test BacktestResult serialization
    - Verify all required fields are present in exports
    - _Requirements: 15.7_

- [x] 4. Implement Trade_Executor component
  - [x] 4.1 Create Trade_Executor class with validation
    - Create `stock_market_analysis/trading/trade_executor.py`
    - Implement Trade_Executor class with __init__(portfolio, trade_history, config)
    - Implement validation methods: _validate_symbol(), _validate_price(), _validate_quantity()
    - Implement error handling with descriptive error messages
    - _Requirements: 13.1, 13.2, 13.3_
  
  - [x] 4.2 Implement buy order execution
    - Implement execute_buy_order(symbol, quantity, price, recommendation_id=None) method
    - Validate sufficient cash balance before execution
    - Calculate total cost and deduct from portfolio cash
    - Create or update position with new shares
    - Update average cost basis for existing positions
    - Record trade in trade history
    - Return Trade object or raise descriptive error
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 13.4_
  
  - [ ]* 4.3 Write property tests for buy order execution
    - **Property 12: Buy order cash deduction** - Cash decreases by exactly quantity × price
    - **Property 13: Buy order position update** - Position quantity increases by buy quantity
    - **Property 14: Average cost basis correctness** - Average cost calculated correctly for multiple buys
    - **Property 15: Buy order atomicity** - Failed buy doesn't modify portfolio state
    - **Validates: Requirements 3.3, 3.4, 3.6**
  
  - [x] 4.4 Implement sell order execution
    - Implement execute_sell_order(symbol, quantity, price, recommendation_id=None) method
    - Validate position exists and has sufficient quantity
    - Calculate proceeds and add to portfolio cash
    - Reduce position quantity or remove if quantity reaches zero
    - Record trade in trade history
    - Return Trade object or raise descriptive error
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 13.5, 13.6_
  
  - [ ]* 4.5 Write property tests for sell order execution
    - **Property 16: Sell order cash addition** - Cash increases by exactly quantity × price
    - **Property 17: Sell order position update** - Position quantity decreases by sell quantity
    - **Property 18: Position removal** - Position removed when quantity reaches zero
    - **Property 19: Sell order atomicity** - Failed sell doesn't modify portfolio state
    - **Validates: Requirements 4.3, 4.4, 4.5**
  
  - [x] 4.6 Implement position sizing strategies
    - Implement _calculate_buy_quantity(price, strategy, strategy_value, portfolio_value) method
    - Support "fixed_amount" strategy: quantity = fixed_amount ÷ price
    - Support "percentage" strategy: quantity = (portfolio_value × percentage) ÷ price
    - Round down to nearest whole share
    - Return 0 if calculated quantity is less than 1
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6_
  
  - [ ]* 4.7 Write property tests for position sizing
    - **Property 20: Fixed amount sizing** - Quantity equals fixed_amount ÷ price (rounded down)
    - **Property 21: Percentage sizing** - Quantity equals (portfolio_value × pct) ÷ price (rounded down)
    - **Property 22: Quantity non-negative** - Calculated quantity is always >= 0
    - **Property 23: Whole shares only** - Quantity is always an integer
    - **Validates: Requirements 6.3, 6.4, 6.5, 6.6**

- [x] 5. Implement recommendation-based trading
  - [x] 5.1 Implement recommendation processing in Trade_Executor
    - Implement execute_recommendation(recommendation, confidence_threshold, sizing_strategy, sizing_value) method
    - Check if recommendation confidence exceeds threshold
    - For BUY recommendations: calculate quantity using position sizing, execute buy order
    - For SELL recommendations: check if position exists, sell entire position if it does
    - For HOLD recommendations: do nothing
    - Use recommendation.current_price as execution price
    - Record recommendation_id in trade
    - Return Trade object or None if no trade executed
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7_
  
  - [ ]* 5.2 Write property tests for recommendation execution
    - **Property 24: Confidence threshold enforcement** - Trades only execute when confidence >= threshold
    - **Property 25: BUY recommendation execution** - BUY with sufficient confidence creates buy trade
    - **Property 26: SELL recommendation execution** - SELL with position and sufficient confidence creates sell trade
    - **Property 27: HOLD recommendation no-op** - HOLD recommendations never create trades
    - **Property 28: Recommendation price usage** - Trade price equals recommendation current_price
    - **Validates: Requirements 5.1, 5.2, 5.3, 5.4, 5.7**
  
  - [ ]* 5.3 Write unit tests for edge cases
    - Test BUY recommendation with insufficient cash
    - Test SELL recommendation without existing position
    - Test recommendation with confidence below threshold
    - Test recommendation with invalid data
    - _Requirements: 5.1, 5.2, 13.4, 13.5, 13.6_

- [x] 6. Implement Performance_Calculator component
  - [x] 6.1 Create Performance_Calculator class
    - Create `stock_market_analysis/trading/performance_calculator.py`
    - Implement Performance_Calculator class with __init__(portfolio, trade_history)
    - Implement _get_current_price(symbol) helper to get latest price from trade history
    - _Requirements: 7.3_
  
  - [x] 6.2 Implement portfolio valuation
    - Implement calculate_portfolio_value(current_prices=None) method
    - Calculate total value as cash balance plus sum of all position values
    - Use provided current_prices dict or fall back to last trade prices
    - Return total portfolio value as Decimal
    - _Requirements: 7.1, 7.2, 7.3_
  
  - [ ]* 6.3 Write property tests for portfolio valuation
    - **Property 29: Portfolio value composition** - Total value equals cash plus sum of position values
    - **Property 30: Price fallback correctness** - Uses last trade price when current price unavailable
    - **Validates: Requirements 7.1, 7.2, 7.3**
  
  - [x] 6.4 Implement profit and loss calculations
    - Implement calculate_realized_pnl() method - sum P&L from all closed trades
    - Implement calculate_unrealized_pnl(current_prices=None) method - sum unrealized P&L for all open positions
    - Implement calculate_total_pnl(current_prices=None) method - realized + unrealized
    - Implement calculate_pnl_percentage() method - (total_pnl ÷ initial_cash) × 100
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_
  
  - [ ]* 6.5 Write property tests for P&L calculations
    - **Property 31: Realized P&L from closed trades** - Realized P&L equals sum of completed trade profits
    - **Property 32: Unrealized P&L calculation** - Unrealized P&L equals sum of position unrealized P&Ls
    - **Property 33: Total P&L composition** - Total P&L equals realized plus unrealized
    - **Property 34: P&L percentage calculation** - P&L % equals (total_pnl ÷ initial_cash) × 100
    - **Validates: Requirements 8.1, 8.2, 8.3, 8.4**
  
  - [x] 6.6 Implement performance metrics calculations
    - Implement calculate_total_return_percentage(current_prices=None) method
    - Implement calculate_win_rate() method - count profitable vs total closed trades
    - Implement calculate_average_profit_per_win() method
    - Implement calculate_average_loss_per_loss() method
    - Implement calculate_maximum_drawdown() method - track peak-to-trough decline
    - Implement get_trade_statistics() method - total trades, open positions count
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7_
  
  - [ ]* 6.7 Write property tests for performance metrics
    - **Property 35: Total return calculation** - Return % equals ((current_value - initial) ÷ initial) × 100
    - **Property 36: Win rate calculation** - Win rate equals (winning_trades ÷ total_trades) × 100
    - **Property 37: Average profit correctness** - Avg profit equals sum of wins ÷ count of wins
    - **Property 38: Average loss correctness** - Avg loss equals sum of losses ÷ count of losses
    - **Property 39: Max drawdown non-positive** - Maximum drawdown is always <= 0
    - **Validates: Requirements 9.1, 9.2, 9.3, 9.4, 9.5**
  
  - [x] 6.8 Implement performance report generation
    - Implement generate_performance_report(current_prices=None) method
    - Collect all performance metrics into PerformanceReport object
    - Include list of open positions with current values
    - Include list of last 10 trades
    - Return PerformanceReport object
    - _Requirements: 15.1, 15.2, 15.3, 15.4, 15.5, 15.6_

- [x] 7. Implement Trading_Simulator component
  - [x] 7.1 Create Trading_Simulator class
    - Create `stock_market_analysis/trading/trading_simulator.py`
    - Implement Trading_Simulator class with __init__(config_manager)
    - Load configuration from YAML file
    - Initialize trade_history, portfolios dict
    - _Requirements: 14.1, 14.6_
  
  - [x] 7.2 Implement portfolio management
    - Implement create_portfolio(initial_cash_balance) method
    - Validate initial_cash_balance > 0 and <= 999999999.99
    - Generate unique portfolio_id using UUID
    - Create Portfolio object and store in portfolios dict
    - Return portfolio_id
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 2.4_
  
  - [ ]* 7.3 Write property tests for portfolio management
    - **Property 40: Portfolio initialization** - New portfolio has correct initial cash and zero positions
    - **Property 41: Portfolio ID uniqueness** - Each portfolio gets unique ID
    - **Property 42: Initial cash validation** - Negative or excessive initial cash rejected
    - **Validates: Requirements 1.1, 1.2, 1.4, 1.5**
  
  - [x] 7.4 Implement cash deposit functionality
    - Implement deposit_cash(portfolio_id, amount) method
    - Validate amount > 0
    - Validate portfolio exists
    - Validate new balance won't exceed maximum
    - Update portfolio cash balance
    - Record deposit transaction with timestamp
    - _Requirements: 2.1, 2.2, 2.3, 2.4_
  
  - [ ]* 7.5 Write property tests for cash deposits
    - **Property 43: Deposit increases cash** - Cash balance increases by deposit amount
    - **Property 44: Deposit validation** - Non-positive deposits rejected
    - **Validates: Requirements 2.1, 2.2_
  
  - [x] 7.6 Implement portfolio state serialization
    - Implement save_portfolio(portfolio_id, filepath) method
    - Serialize portfolio to JSON with all fields
    - Preserve Decimal precision in JSON
    - Implement load_portfolio(filepath) method
    - Validate all required fields present during deserialization
    - Raise descriptive errors for invalid data
    - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5, 12.6_
  
  - [ ]* 7.7 Write property tests for serialization
    - **Property 45: Serialization round-trip** - Portfolio saved and loaded equals original
    - **Property 46: Decimal precision preservation** - Monetary values maintain precision through save/load
    - **Validates: Requirements 12.1, 12.2, 12.3, 12.6**
  
  - [x] 7.8 Implement trading interface methods
    - Implement execute_trade(portfolio_id, symbol, action, quantity, price) method
    - Get portfolio and create Trade_Executor
    - Delegate to Trade_Executor.execute_buy_order() or execute_sell_order()
    - Return Trade object
    - Implement process_recommendation(portfolio_id, recommendation) method
    - Get portfolio and create Trade_Executor
    - Get configuration for confidence_threshold and position sizing
    - Delegate to Trade_Executor.execute_recommendation()
    - Return Trade object or None
    - _Requirements: 3.1, 3.2, 4.1, 4.2, 5.1, 5.2, 5.3_
  
  - [x] 7.9 Implement performance reporting interface
    - Implement get_performance_report(portfolio_id, current_prices=None) method
    - Get portfolio and create Performance_Calculator
    - Delegate to Performance_Calculator.generate_performance_report()
    - Return PerformanceReport object
    - _Requirements: 15.1_

- [x] 8. Implement Backtest_Engine component
  - [x] 8.1 Create Backtest_Engine class
    - Create `stock_market_analysis/trading/backtest_engine.py`
    - Implement Backtest_Engine class with __init__(config_manager)
    - Load backtest configuration (initial_cash, confidence_threshold, position sizing)
    - _Requirements: 11.6, 11.7_
  
  - [x] 8.2 Implement backtest execution
    - Implement run_backtest(recommendations, initial_cash=None, confidence_threshold=None) method
    - Sort recommendations by timestamp chronologically
    - Create separate Portfolio for backtest
    - Create Trade_Executor for backtest portfolio
    - Iterate through recommendations and execute trades
    - Track all trades and portfolio state changes
    - Generate performance report at end
    - Create and return BacktestResult object
    - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5, 11.6, 11.7_
  
  - [ ]* 8.3 Write property tests for backtesting
    - **Property 47: Backtest chronological order** - Recommendations processed in timestamp order
    - **Property 48: Backtest isolation** - Backtest doesn't affect live portfolios
    - **Validates: Requirements 11.2, 11.4**
  
  - [ ]* 8.4 Write unit tests for backtest scenarios
    - Test backtest with empty recommendations list
    - Test backtest with only BUY recommendations
    - Test backtest with mixed BUY/SELL/HOLD recommendations
    - Test backtest with custom initial cash and threshold
    - Verify BacktestResult contains all required data
    - _Requirements: 11.1, 11.5, 11.6, 11.7_

- [x] 9. Implement configuration management
  - [x] 9.1 Create trading configuration schema
    - Add trading configuration section to `config/default.yaml`
    - Define initial_cash_balance (default: 100000.00)
    - Define confidence_threshold (default: 0.70)
    - Define position_sizing_strategy (default: "percentage")
    - Define position_size_value (default: 0.10 for 10%)
    - _Requirements: 14.2, 14.3, 14.4, 14.5_
  
  - [x] 9.2 Extend ConfigurationManager for trading
    - Add methods to ConfigurationManager: get_trading_config(), get_initial_cash_balance(), get_confidence_threshold(), get_position_sizing_config()
    - Implement validation for trading configuration values
    - Validate confidence_threshold between 0.0 and 1.0
    - Validate position_sizing_strategy in ["fixed_amount", "percentage"]
    - Validate percentage between 0.01 and 1.0
    - Raise descriptive errors for invalid configuration
    - _Requirements: 14.1, 14.6, 14.7, 6.7_
  
  - [ ]* 9.3 Write unit tests for configuration
    - Test loading valid trading configuration
    - Test default values when configuration missing
    - Test validation errors for invalid values
    - Test confidence_threshold bounds
    - Test position sizing strategy validation
    - _Requirements: 14.6, 14.7_

- [x] 10. Integration with AnalysisEngine
  - [x] 10.1 Create integration module
    - Create `stock_market_analysis/trading/integration.py`
    - Implement TradingIntegration class with __init__(trading_simulator, analysis_engine)
    - Implement method to subscribe to AnalysisEngine recommendations
    - _Requirements: 5.1, 5.2, 5.3_
  
  - [x] 10.2 Implement automatic recommendation processing
    - Implement process_analysis_results(portfolio_id, recommendations) method
    - Iterate through recommendations from AnalysisEngine
    - Call trading_simulator.process_recommendation() for each
    - Collect and return list of executed trades
    - Log each trade execution with symbol, action, and quantity
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6_
  
  - [ ]* 10.3 Write integration tests
    - Test processing multiple recommendations
    - Test filtering by confidence threshold
    - Test handling recommendations with insufficient cash/positions
    - Verify trades recorded in trade history
    - _Requirements: 5.1, 5.2, 5.7_

- [x] 11. Create CLI interface for trading simulation
  - [x] 11.1 Implement trading CLI commands
    - Create `stock_market_analysis/trading/cli.py`
    - Implement create_portfolio command
    - Implement deposit_cash command
    - Implement execute_trade command (manual buy/sell)
    - Implement view_portfolio command
    - Implement view_performance command
    - Implement run_backtest command
    - Use argparse for command-line argument parsing
    - _Requirements: 1.1, 2.1, 3.1, 4.1, 7.1, 15.1, 11.1_
  
  - [ ]* 11.2 Write CLI integration tests
    - Test each CLI command with valid inputs
    - Test error handling for invalid inputs
    - Verify output formatting
    - _Requirements: 13.1, 13.2, 13.3, 13.4, 13.5, 13.6_

- [x] 12. Update main application to include trading
  - [x] 12.1 Integrate trading simulator into main.py
    - Import TradingSimulator and TradingIntegration
    - Initialize trading_simulator in StockMarketAnalysisSystem.__init__()
    - Create default portfolio on system startup
    - Wire TradingIntegration to connect AnalysisEngine and TradingSimulator
    - _Requirements: 5.1_
  
  - [x] 12.2 Add trading to analysis pipeline
    - In run_analysis_pipeline(), after generating recommendations, process them through trading integration
    - Log trading results (number of trades executed, portfolio value)
    - Include trading performance summary in daily report
    - _Requirements: 5.1, 5.2, 5.3, 15.1_
  
  - [ ]* 12.3 Write end-to-end integration tests
    - Test complete pipeline: market data → analysis → recommendations → trades → performance report
    - Verify portfolio state updates correctly
    - Verify trade history persistence
    - Test with multiple analysis cycles
    - _Requirements: 5.1, 5.6, 10.1, 15.1_

- [x] 13. Checkpoint - Ensure all tests pass
  - Run all unit tests: `python -m pytest tests/unit/test_trading_*.py -v`
  - Run all property tests: `python -m pytest tests/property/test_properties_trading.py -v`
  - Run integration tests: `python -m pytest tests/integration/test_trading_integration.py -v`
  - Verify no errors or failures
  - Ask the user if questions arise

- [x] 14. Documentation and examples
  - [x] 14.1 Create trading simulation README
    - Create `stock_market_analysis/trading/README.md`
    - Document system architecture and components
    - Provide usage examples for each major feature
    - Document configuration options
    - Include example backtest workflow
    - _Requirements: All requirements_
  
  - [x] 14.2 Create example scripts
    - Create `examples/trading_simulation_example.py`
    - Demonstrate creating portfolio, executing trades, viewing performance
    - Create `examples/backtest_example.py`
    - Demonstrate running backtest with historical data
    - _Requirements: 1.1, 3.1, 4.1, 7.1, 11.1, 15.1_

- [x] 15. Final checkpoint - Complete system validation
  - Run complete test suite: `python -m pytest tests/ -v`
  - Run example scripts to verify end-to-end functionality
  - Verify all configuration options work correctly
  - Verify portfolio serialization and persistence
  - Verify backtest produces expected results
  - Ensure all tests pass, ask the user if questions arise

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Property tests validate universal correctness properties from the design
- Unit tests validate specific examples and edge cases
- Implementation uses Python with Decimal for financial precision
- Integration with existing AnalysisEngine maintains backward compatibility
- All monetary values use Decimal to avoid floating-point precision issues
- Trade history uses JSON file storage for simplicity (can be upgraded to database later)
- Configuration extends existing YAML-based ConfigurationManager
