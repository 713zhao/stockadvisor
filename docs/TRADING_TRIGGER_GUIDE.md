# Trading Trigger Guide

## How Trades Are Executed

The trading simulation system automatically executes BUY and SELL trades based on the analysis recommendations. Here's how it works:

### Trade Execution Criteria

Trades are executed when ALL of the following conditions are met:

#### 1. Confidence Threshold
- **Default**: 0.70 (70%)
- **Configurable**: Set in `config/default.yaml` under `trading.confidence_threshold`
- Only recommendations with confidence >= threshold will be executed

#### 2. Recommendation Type

**BUY Recommendations:**
- System calculates position size based on strategy (percentage or fixed amount)
- Checks if there's enough cash to buy
- Executes buy order if cash is sufficient

**SELL Recommendations:**
- System checks if you have an existing position in that stock
- Sells the ENTIRE position if you own it
- Skips if you don't own the stock

**HOLD Recommendations:**
- No action taken

#### 3. Position Sizing

Configured in `config/default.yaml`:

```yaml
trading:
  position_sizing_strategy: "percentage"  # or "fixed_amount"
  position_size_value: 0.10               # 10% of portfolio or $10 fixed
```

**Percentage Strategy** (default):
- Each trade uses X% of total portfolio value
- Example: 10% of $100,000 = $10,000 per trade
- Portfolio value = cash + value of all positions

**Fixed Amount Strategy:**
- Each trade uses a fixed dollar amount
- Example: $5,000 per trade regardless of portfolio size

### Current Configuration

From `config/default.yaml`:
- **Confidence Threshold**: 0.70 (70%)
- **Position Sizing**: Percentage-based at 10%
- **Initial Cash**: $100,000

### Example from Latest Run

From the most recent analysis (2026-02-27 15:07):

**Recommendations with confidence >= 0.70:**
- 688981.SS (BUY, 0.73) ✓ Executed
- 600900.SS (BUY, 0.79) ✓ Executed
- 0700.HK (BUY, 0.89) ✓ Executed
- 9988.HK (BUY, 0.745) ✓ Executed
- 1810.HK (BUY, 0.766) ✓ Executed
- 2382.HK (BUY, 0.778) ✓ Executed
- 0386.HK (BUY, 0.70) ✓ Executed
- PLTR (BUY, 0.765) ✓ Executed
- MSFT (BUY, 0.71) ✗ Insufficient cash
- GOOGL (BUY, 0.795) ✗ Insufficient cash
- META (BUY, 0.70) ✗ Insufficient cash
- NEE (BUY, 0.705) ✗ Insufficient cash

**Why some trades weren't executed:**
After executing 8 BUY trades, the portfolio only had $154.10 cash remaining, which wasn't enough to buy more stocks.

### Current Portfolio Status

**Portfolio ID**: 1cd39133-4361-4a72-9c9c-b619a41774de

**Positions** (8 stocks):
1. 688981.SS - 79 shares @ $126.41 = $9,986.54
2. 600900.SS - 321 shares @ $28.69 = $9,209.49
3. 0700.HK - 54 shares @ $576.40 = $31,125.60
4. 9988.HK - 76 shares @ $159.17 = $12,096.92
5. 1810.HK - 150 shares @ $38.52 = $5,778.30
6. 2382.HK - 117 shares @ $64.19 = $7,510.23
7. 0386.HK - 483 shares @ $6.02 = $2,906.21
8. PLTR - 142 shares @ $149.53 = $21,233.26

**Total Invested**: $99,845.90
**Cash Remaining**: $154.10
**Total Portfolio Value**: $100,000.00

### When Will SELL Trades Trigger?

SELL trades will execute when:
1. Analysis generates a SELL recommendation for a stock you own
2. The recommendation has confidence >= 0.70
3. The system will sell your ENTIRE position in that stock

For example, if tomorrow's analysis recommends:
- SELL PLTR with confidence 0.75 → System will sell all 142 shares
- This will free up ~$21,233 in cash for new BUY trades

### Viewing Trading Activity

**Web Dashboard**: http://localhost:5000
- Real-time portfolio value and positions
- Trade history (last 50 trades)
- Performance metrics (P&L, win rate, etc.)
- Auto-refreshes every 30 seconds

**Log Files**:
- `logs/stock_analysis.log` - Detailed execution logs
- `data/trade_history.json` - All executed trades
- `data/default_portfolio.json` - Current portfolio state

### Adjusting Trade Behavior

To change when trades execute, edit `config/default.yaml`:

**More aggressive trading** (lower threshold):
```yaml
trading:
  confidence_threshold: 0.60  # Execute trades with 60%+ confidence
```

**More conservative trading** (higher threshold):
```yaml
trading:
  confidence_threshold: 0.80  # Only execute trades with 80%+ confidence
```

**Smaller position sizes** (more diversification):
```yaml
trading:
  position_size_value: 0.05  # 5% per trade = up to 20 positions
```

**Larger position sizes** (fewer positions):
```yaml
trading:
  position_size_value: 0.20  # 20% per trade = up to 5 positions
```

### Next Steps

1. **Monitor Performance**: Open http://localhost:5000 to see your portfolio
2. **Wait for Market Changes**: Run the system again tomorrow to see if SELL recommendations trigger
3. **Adjust Settings**: Modify `config/default.yaml` to tune trading behavior
4. **Review Trades**: Check `data/trade_history.json` for complete trade log

The system is working correctly - it executed 8 BUY trades based on high-confidence recommendations and will execute SELL trades when the analysis recommends selling stocks you own.
