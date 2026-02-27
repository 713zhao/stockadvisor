# Stock Market Analysis System - Startup Guide

## Quick Start

### Option 1: One-Click Startup (Windows)

Simply double-click:
```
start.bat
```

This will start both the analysis system and web dashboard automatically.

### Option 2: Python Script

Run the unified startup script:
```bash
python start_system.py
```

### Option 3: Manual Startup (Advanced)

If you prefer to run services separately:

**Terminal 1 - Analysis System:**
```bash
python -m stock_market_analysis.main
```

**Terminal 2 - Web Dashboard:**
```bash
python web_dashboard.py
```

## What Gets Started

When you run `start_system.py` or `start.bat`, the following services start:

### 1. Analysis System
- **Daily Analysis**: Runs once immediately, then scheduled for 21:00 daily
- **Intraday Monitoring**: Monitors markets every hour during trading hours
- **Automatic Trading**: Executes trades based on analysis results
- **Telegram Notifications**: Sends reports to your configured Telegram

### 2. Web Dashboard
- **URL**: http://localhost:5000
- **Features**:
  - Real-time portfolio monitoring
  - Trade history with rationale tooltips
  - Performance metrics
  - Analysis reports

## System Status

After starting, you'll see:

```
======================================================================
Stock Market Analysis System - Unified Startup
======================================================================

Starting services:
  1. Analysis System (with intraday monitoring)
  2. Web Dashboard (http://localhost:5000)

Press Ctrl+C to stop all services
======================================================================

✓ All services started successfully!
======================================================================

Access the dashboard at: http://localhost:5000

Services running:
  • Analysis System: Running with intraday monitoring
  • Web Dashboard: http://localhost:5000

Press Ctrl+C to stop all services
======================================================================
```

## Accessing the Dashboard

Open your web browser and go to:
```
http://localhost:5000
```

The dashboard shows:
- **Portfolio Value**: Current total value
- **Cash Balance**: Available cash
- **Total P&L**: Profit/Loss
- **Total Return**: Return percentage
- **Positions**: All open positions with stock names
- **Trade History**: Recent trades with rationale (hover to see)
- **Performance**: Detailed metrics
- **Reports**: Generated analysis reports

## Monitoring Logs

Logs are written to:
- `logs/system.log` - Combined system log
- `logs/stock_analysis.log` - Analysis system log
- `logs/events.jsonl` - Event log

View logs in real-time:
```bash
# Windows PowerShell
Get-Content logs/system.log -Wait -Tail 50

# Or use a text editor to open logs/system.log
```

## Stopping the System

Press `Ctrl+C` in the terminal where the system is running.

Both services will shut down gracefully:
- Intraday monitoring stops
- In-progress analysis cycles complete
- Portfolio and trade history are saved
- Web dashboard stops

## Configuration

Edit `config/default.yaml` to configure:

### Intraday Monitoring
```yaml
intraday_monitoring:
  enabled: true                    # Enable/disable
  monitoring_interval_minutes: 60  # Check every hour
  monitored_regions:               # Markets to monitor
    - china
    - hong_kong
    - usa
```

### Trading Settings
```yaml
trading:
  initial_cash_balance: 100000.00
  confidence_threshold: 0.70       # Minimum confidence to trade
  position_sizing_strategy: "percentage"
  position_size_value: 0.10        # 10% of portfolio per trade
```

### Notifications
```yaml
notifications:
  telegram:
    enabled: true
    bot_token: "your-bot-token"
    chat_ids: [your-chat-id]
```

## Troubleshooting

### Port 5000 Already in Use

If you see "Address already in use" error:

**Option 1**: Stop the existing process
```bash
# Find process using port 5000
netstat -ano | findstr :5000

# Kill the process (replace PID with actual process ID)
taskkill /PID <PID> /F
```

**Option 2**: Change the port in `start_system.py`:
```python
web_dashboard.app.run(
    host='0.0.0.0',
    port=5001,  # Change to different port
    debug=False,
    use_reloader=False
)
```

### System Not Starting

1. **Check virtual environment is activated**:
   ```bash
   venv\Scripts\activate
   ```

2. **Check Python version** (requires Python 3.8+):
   ```bash
   python --version
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Check configuration file exists**:
   ```bash
   # Should exist: config/default.yaml
   ```

### No Trades Executing

1. **Check confidence threshold**: Recommendations must exceed the threshold
2. **Check cash balance**: Must have sufficient cash
3. **Check market hours**: Intraday monitoring only runs during market hours
4. **Check logs**: Look for errors in `logs/stock_analysis.log`

### Dashboard Not Updating

1. **Refresh the browser**: Dashboard auto-refreshes every 30 seconds
2. **Check if system is running**: Look for log messages
3. **Check portfolio file**: `data/default_portfolio.json` should exist

## Market Hours

Intraday monitoring only runs during these hours:

| Market | Trading Hours (Local) | UTC Time |
|--------|----------------------|----------|
| China | 09:30 - 15:00 CST | 01:30 - 07:00 UTC |
| Hong Kong | 09:30 - 16:00 HKT | 01:30 - 08:00 UTC |
| USA | 09:30 - 16:00 ET | 14:30 - 21:00 UTC (summer)<br>15:30 - 22:00 UTC (winter) |

Outside these hours, the system waits until markets open.

## File Locations

- **Configuration**: `config/default.yaml`
- **Portfolio**: `data/default_portfolio.json`
- **Trade History**: `data/trade_history.json`
- **Reports**: `reports/YYYY-MM-DD/`
- **Logs**: `logs/`

## Support

For issues or questions:
1. Check logs in `logs/` directory
2. Review configuration in `config/default.yaml`
3. Check README files in component directories

## Advanced Usage

### Running in Background (Windows)

Create a scheduled task to run `start.bat` at system startup.

### Running as a Service (Linux)

Create a systemd service file:
```ini
[Unit]
Description=Stock Market Analysis System
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/stockmarket
ExecStart=/path/to/venv/bin/python start_system.py
Restart=always

[Install]
WantedBy=multi-user.target
```

### Custom Startup

Modify `start_system.py` to customize:
- Port numbers
- Log levels
- Service configurations

## Next Steps

1. **Monitor the dashboard**: http://localhost:5000
2. **Check Telegram**: You should receive daily reports
3. **Review trades**: Check the Trade History tab
4. **Adjust settings**: Edit `config/default.yaml` as needed
5. **Monitor logs**: Watch `logs/system.log` for activity

Enjoy automated stock market analysis and trading! 📈
