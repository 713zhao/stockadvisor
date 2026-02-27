"""
Web Dashboard for Stock Market Analysis and Trading Simulation

A Flask-based web interface to view:
- Portfolio performance and positions
- Trade history
- Market recommendations
- Performance metrics and charts
"""

from flask import Flask, render_template, jsonify, request
from decimal import Decimal
from datetime import datetime, timedelta
import json
from pathlib import Path
import yfinance as yf

from stock_market_analysis.trading import TradingSimulator
from stock_market_analysis.components import ConfigurationManager
from stock_market_analysis.trading.models import TradeHistory

app = Flask(__name__)

# Initialize components
config_manager = ConfigurationManager()
simulator = TradingSimulator(config_manager)

# Trade history loads automatically in TradingSimulator
trade_history = simulator.trade_history

# Load or create default portfolio
DEFAULT_PORTFOLIO_FILE = "data/default_portfolio.json"

# Cache for stock names
stock_name_cache = {}

def get_stock_name(symbol: str) -> str:
    """
    Get stock name from Yahoo Finance with caching.
    
    Args:
        symbol: Stock symbol
        
    Returns:
        Stock name or symbol if not found
    """
    if symbol in stock_name_cache:
        return stock_name_cache[symbol]
    
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        name = info.get('longName') or info.get('shortName') or symbol
        stock_name_cache[symbol] = name
        return name
    except:
        stock_name_cache[symbol] = symbol
        return symbol

def get_yahoo_finance_url(symbol: str) -> str:
    """
    Generate Yahoo Finance URL for a stock symbol.
    
    Args:
        symbol: Stock symbol
        
    Returns:
        Yahoo Finance URL
    """
    return f"https://finance.yahoo.com/quote/{symbol}"

def get_default_portfolio_id():
    """Get or create the default portfolio ID."""
    if Path(DEFAULT_PORTFOLIO_FILE).exists():
        try:
            portfolio_id = simulator.load_portfolio(DEFAULT_PORTFOLIO_FILE)
            return portfolio_id
        except:
            pass
    
    # Create new portfolio
    portfolio_id = simulator.create_portfolio(Decimal("100000.00"))
    simulator.save_portfolio(portfolio_id, DEFAULT_PORTFOLIO_FILE)
    return portfolio_id

PORTFOLIO_ID = get_default_portfolio_id()


@app.route('/')
def index():
    """Main dashboard page."""
    return render_template('dashboard.html')


@app.route('/api/portfolio')
def get_portfolio():
    """Get current portfolio status."""
    try:
        portfolio = simulator.get_portfolio(PORTFOLIO_ID)
        report = simulator.get_performance_report(PORTFOLIO_ID)
        
        # Convert to JSON-serializable format
        positions = []
        for symbol, position in portfolio.positions.items():
            stock_name = get_stock_name(symbol)
            yahoo_url = get_yahoo_finance_url(symbol)
            positions.append({
                'symbol': symbol,
                'stock_name': stock_name,
                'yahoo_url': yahoo_url,
                'quantity': position.quantity,
                'average_cost': float(position.average_cost_basis),
                'current_value': float(position.calculate_value(position.average_cost_basis))
            })
        
        return jsonify({
            'portfolio_id': portfolio.portfolio_id,
            'cash_balance': float(portfolio.cash_balance),
            'initial_cash': float(portfolio.initial_cash_balance),
            'portfolio_value': float(report.portfolio_value),
            'total_pnl': float(report.total_pnl),
            'total_return_pct': float(report.total_return_pct),
            'positions': positions,
            'total_positions': len(positions)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/performance')
def get_performance():
    """Get detailed performance metrics."""
    try:
        report = simulator.get_performance_report(PORTFOLIO_ID)
        
        return jsonify({
            'portfolio_value': float(report.portfolio_value),
            'cash_balance': float(report.cash_balance),
            'total_positions': report.total_positions,
            'realized_pnl': float(report.realized_pnl),
            'unrealized_pnl': float(report.unrealized_pnl),
            'total_pnl': float(report.total_pnl),
            'total_return_pct': float(report.total_return_pct),
            'win_rate': float(report.win_rate),
            'avg_profit_per_win': float(report.avg_profit_per_win),
            'avg_loss_per_loss': float(report.avg_loss_per_loss),
            'max_drawdown': float(report.max_drawdown),
            'total_trades': report.total_trades,
            'open_positions': report.open_positions_list
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/trades')
def get_trades():
    """Get trade history."""
    try:
        limit = request.args.get('limit', 50, type=int)
        trades = trade_history.get_trades_by_portfolio(PORTFOLIO_ID)
        
        # Sort by timestamp descending
        trades.sort(key=lambda t: t.timestamp, reverse=True)
        
        # Limit results
        trades = trades[:limit]
        
        # Convert to JSON
        trades_data = []
        for trade in trades:
            # Get stock name (from trade or fetch from Yahoo)
            stock_name = trade.stock_name if trade.stock_name else get_stock_name(trade.symbol)
            yahoo_url = get_yahoo_finance_url(trade.symbol)
            rationale = trade.rationale if trade.rationale else "No rationale available"
            
            trades_data.append({
                'trade_id': trade.trade_id,
                'timestamp': trade.timestamp.isoformat(),
                'action': trade.action.value,
                'symbol': trade.symbol,
                'stock_name': stock_name,
                'yahoo_url': yahoo_url,
                'quantity': trade.quantity,
                'price': float(trade.price),
                'total': float(trade.calculate_total_cost() if trade.action.value == 'BUY' else trade.calculate_proceeds()),
                'rationale': rationale
            })
        
        return jsonify({'trades': trades_data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/reports')
def get_reports():
    """Get list of available reports."""
    try:
        reports_dir = Path('reports')
        if not reports_dir.exists():
            return jsonify({'reports': []})
        
        reports = []
        for date_dir in sorted(reports_dir.iterdir(), reverse=True):
            if date_dir.is_dir():
                for report_file in date_dir.glob('*.json'):
                    try:
                        with open(report_file, 'r') as f:
                            report_data = json.load(f)
                        
                        reports.append({
                            'report_id': report_data['report_id'],
                            'date': report_data['trading_date'],
                            'generation_time': report_data['generation_time'],
                            'recommendations_count': len(report_data['recommendations']),
                            'file_path': str(report_file)
                        })
                    except:
                        continue
        
        return jsonify({'reports': reports[:20]})  # Last 20 reports
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/report/<report_id>')
def get_report_detail(report_id):
    """Get detailed report data."""
    try:
        # Find report file
        reports_dir = Path('reports')
        report_file = None
        
        for date_dir in reports_dir.iterdir():
            if date_dir.is_dir():
                for f in date_dir.glob(f'{report_id}.json'):
                    report_file = f
                    break
            if report_file:
                break
        
        if not report_file:
            return jsonify({'error': 'Report not found'}), 404
        
        with open(report_file, 'r') as f:
            report_data = json.load(f)
        
        return jsonify(report_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/stats')
def get_stats():
    """Get overall statistics."""
    try:
        portfolio = simulator.get_portfolio(PORTFOLIO_ID)
        report = simulator.get_performance_report(PORTFOLIO_ID)
        trades = trade_history.get_trades_by_portfolio(PORTFOLIO_ID)
        
        # Calculate daily P&L
        today_trades = [t for t in trades if t.timestamp.date() == datetime.now().date()]
        
        return jsonify({
            'total_trades': len(trades),
            'trades_today': len(today_trades),
            'open_positions': len(portfolio.positions),
            'portfolio_value': float(report.portfolio_value),
            'total_return': float(report.total_return_pct),
            'win_rate': float(report.win_rate),
            'max_drawdown': float(report.max_drawdown)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print("=" * 60)
    print("Stock Market Analysis & Trading Dashboard")
    print("=" * 60)
    print(f"Portfolio ID: {PORTFOLIO_ID}")
    print(f"Dashboard URL: http://localhost:5000")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5000)
