# Stock Market Analysis & Trading Dashboard

A web-based dashboard for monitoring your trading simulation portfolio, viewing trade history, and analyzing performance metrics.

## Features

### 📊 Real-Time Portfolio Monitoring
- Current portfolio value
- Cash balance
- Total P&L (realized + unrealized)
- Total return percentage
- Auto-refreshes every 30 seconds

### 💼 Position Management
- View all open positions
- See quantity, average cost, and current value
- Real-time position tracking

### 📈 Trade History
- Complete trade history with timestamps
- Filter by action (BUY/SELL)
- View quantity, price, and total value
- Last 50 trades displayed

### 📉 Performance Metrics
- Realized and unrealized P&L
- Win rate percentage
- Average profit per winning trade
- Average loss per losing trade
- Maximum drawdown
- Total trades executed

### 📄 Analysis Reports
- View all generated market analysis reports
- See recommendation counts
- Access historical reports

## Quick Start

### 1. Install Dependencies

```bash
pip install flask
```

Or install from requirements.txt:

```bash
pip install -r requirements.txt
```

### 2. Start the Dashboard

```bash
python web_dashboard.py
```

### 3. Access the Dashboard

Open your browser and navigate to:

```
http://localhost:5000
```

Or access from other devices on your network:

```
http://YOUR_IP_ADDRESS:5000
```

## Dashboard Sections

### Overview (Top Stats)
- **Portfolio Value**: Total value of cash + positions
- **Cash Balance**: Available cash for trading
- **Total P&L**: Combined realized and unrealized profit/loss
- **Total Return**: Return percentage since inception

### Positions Tab
View all currently held stock positions with:
- Symbol
- Quantity of shares
- Average cost basis
- Current market value

### Trade History Tab
Complete chronological list of all trades:
- Date and time of execution
- Action (BUY or SELL)
- Stock symbol
- Quantity traded
- Execution price
- Total transaction value

### Performance Tab
Detailed performance metrics:
- Realized P&L (from closed positions)
- Unrealized P&L (from open positions)
- Win rate (% of profitable trades)
- Average profit per winning trade
- Average loss per losing trade
- Maximum drawdown
- Total number of trades
- Number of open positions

### Reports Tab
List of all generated analysis reports:
- Report date
- Report ID
- Number of recommendations
- Generation timestamp

## API Endpoints

The dashboard provides REST API endpoints for programmatic access:

### GET /api/portfolio
Returns current portfolio status including cash, positions, and P&L.

```json
{
  "portfolio_id": "uuid",
  "cash_balance": 10000.00,
  "portfolio_value": 100000.00,
  "total_pnl": 5000.00,
  "total_return_pct": 5.00,
  "positions": [...]
}
```

### GET /api/performance
Returns detailed performance metrics.

```json
{
  "realized_pnl": 2500.00,
  "unrealized_pnl": 2500.00,
  "win_rate": 75.00,
  "avg_profit_per_win": 500.00,
  "max_drawdown": -5.00,
  ...
}
```

### GET /api/trades?limit=50
Returns trade history (default: last 50 trades).

```json
{
  "trades": [
    {
      "trade_id": "uuid",
      "timestamp": "2026-02-27T10:30:00",
      "action": "BUY",
      "symbol": "AAPL",
      "quantity": 100,
      "price": 150.00,
      "total": 15000.00
    },
    ...
  ]
}
```

### GET /api/reports
Returns list of available analysis reports.

```json
{
  "reports": [
    {
      "report_id": "REPORT-20260227-abc123",
      "date": "2026-02-27",
      "recommendations_count": 30,
      "generation_time": "2026-02-27T14:30:00"
    },
    ...
  ]
}
```

### GET /api/stats
Returns overall statistics summary.

```json
{
  "total_trades": 25,
  "trades_today": 7,
  "open_positions": 7,
  "portfolio_value": 100000.00,
  "total_return": 5.00,
  "win_rate": 75.00
}
```

## Configuration

The dashboard automatically:
- Loads the default portfolio from `data/default_portfolio.json`
- Creates a new portfolio with $100,000 if none exists
- Reads trade history from `data/trade_history.json`
- Accesses reports from `reports/` directory

## Auto-Refresh

The dashboard automatically refreshes data every 30 seconds to show the latest:
- Portfolio values
- Position updates
- New trades
- Performance metrics

You can also manually refresh by clicking the "🔄 Refresh Data" button.

## Responsive Design

The dashboard is fully responsive and works on:
- Desktop browsers
- Tablets
- Mobile devices

## Color Coding

- **Green**: Positive values (profits, gains)
- **Red**: Negative values (losses, drawdowns)
- **Purple**: Headers and accents
- **Gray**: Neutral information

## Security Notes

⚠️ **Development Server**: The dashboard runs on Flask's development server, which is suitable for local use and testing.

For production deployment:
1. Use a production WSGI server (gunicorn, uWSGI)
2. Add authentication/authorization
3. Enable HTTPS
4. Configure firewall rules
5. Set up proper logging

## Troubleshooting

### Dashboard won't start
- Ensure Flask is installed: `pip install flask`
- Check if port 5000 is available
- Verify Python virtual environment is activated

### No data showing
- Ensure the trading simulation has been run at least once
- Check that `data/trade_history.json` exists
- Verify portfolio file exists in `data/`

### Can't access from other devices
- Ensure firewall allows connections on port 5000
- Use your machine's IP address instead of localhost
- Check that the server is running on `0.0.0.0` (all interfaces)

## Integration with Main System

The dashboard works alongside the main stock market analysis system:

1. Run the main system to generate recommendations and execute trades:
   ```bash
   python -m stock_market_analysis.main
   ```

2. Start the dashboard to monitor results:
   ```bash
   python web_dashboard.py
   ```

3. Access the dashboard at http://localhost:5000

The dashboard will show all trades executed by the main system and update automatically.

## Future Enhancements

Potential improvements:
- Real-time charts and graphs
- Trade execution from dashboard
- Portfolio comparison
- Backtesting interface
- Export data to CSV/Excel
- Email/SMS alerts
- Multi-portfolio support
- Dark mode theme

## Support

For issues or questions:
1. Check the logs in the terminal where the dashboard is running
2. Verify all dependencies are installed
3. Ensure the trading simulation system is properly configured
4. Review the main README.md for system requirements

## License

This dashboard is part of the Stock Market Analysis and Trading Simulation system.
