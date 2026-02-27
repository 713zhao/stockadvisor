"""
Example script demonstrating intraday market monitoring.

This script shows how to set up and run hourly market monitoring
during trading hours with automatic trade execution.
"""

import logging
import time
from pathlib import Path

from stock_market_analysis.components.configuration_manager import ConfigurationManager
from stock_market_analysis.components.analysis_engine import AnalysisEngine
from stock_market_analysis.components.market_monitor import MarketMonitor
from stock_market_analysis.components.intraday import (
    IntradayMonitor,
    TimezoneConverter,
    MarketHoursDetector
)
from stock_market_analysis.trading.models.portfolio import Portfolio
from stock_market_analysis.trading.models.trade_history import TradeHistory
from stock_market_analysis.trading.trade_executor import TradeExecutor
from stock_market_analysis.models.market_region import MarketRegion


def setup_logging():
    """Configure logging for the example."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def main():
    """Main example function."""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("=== Intraday Monitoring Example ===")
    
    # 1. Initialize configuration manager
    config_manager = ConfigurationManager()
    
    # 2. Enable intraday monitoring (if not already enabled)
    intraday_config = config_manager.get_intraday_config()
    if not intraday_config.get('enabled', False):
        logger.info("Enabling intraday monitoring...")
        result = config_manager.set_intraday_config(
            enabled=True,
            interval_minutes=60,  # Check every hour
            regions=[MarketRegion.CHINA, MarketRegion.HONG_KONG, MarketRegion.USA]
        )
        if result.is_ok():
            logger.info("Intraday monitoring enabled")
        else:
            logger.error(f"Failed to enable intraday monitoring: {result.error()}")
            return
    else:
        logger.info("Intraday monitoring already enabled")
    
    # 3. Initialize components
    logger.info("Initializing components...")
    
    # Market monitoring
    market_monitor = MarketMonitor(config_manager=config_manager)
    
    # Analysis engine
    analysis_engine = AnalysisEngine(market_monitor=market_monitor)
    
    # Trading components
    portfolio = Portfolio.load_from_file("data/default_portfolio.json")
    trade_history = TradeHistory.load_from_file("data/trade_history.json")
    trade_executor = TradeExecutor(
        portfolio=portfolio,
        trade_history=trade_history,
        config=config_manager.get_trading_config()
    )
    
    # Intraday monitoring components
    timezone_converter = TimezoneConverter()
    market_hours_detector = MarketHoursDetector(
        timezone_converter=timezone_converter,
        config_manager=config_manager
    )
    
    intraday_monitor = IntradayMonitor(
        market_hours_detector=market_hours_detector,
        analysis_engine=analysis_engine,
        trade_executor=trade_executor,
        config_manager=config_manager
    )
    
    logger.info("Components initialized")
    
    # 4. Start intraday monitoring
    logger.info("Starting intraday monitoring...")
    intraday_monitor.start_monitoring()
    
    # 5. Monitor status
    logger.info("\nMonitoring status:")
    for region in [MarketRegion.CHINA, MarketRegion.HONG_KONG, MarketRegion.USA]:
        status = intraday_monitor.get_monitoring_status(region)
        logger.info(f"\n{region.value.upper()}:")
        logger.info(f"  Active: {status.is_active}")
        logger.info(f"  Paused: {status.is_paused}")
        if status.is_paused:
            logger.info(f"  Pause reason: {status.pause_reason}")
            logger.info(f"  Pause until: {status.pause_until}")
        logger.info(f"  Last cycle: {status.last_cycle_time}")
        logger.info(f"  Next cycle: {status.next_cycle_time}")
        logger.info(f"  Cycles today: {status.total_cycles_today}")
        logger.info(f"  Consecutive failures: {status.consecutive_failures}")
    
    # 6. Run for a period (or until interrupted)
    try:
        logger.info("\nMonitoring active. Press Ctrl+C to stop...")
        while True:
            time.sleep(60)  # Check status every minute
            
            # Optionally print status updates
            # for region in [MarketRegion.CHINA, MarketRegion.HONG_KONG, MarketRegion.USA]:
            #     status = intraday_monitor.get_monitoring_status(region)
            #     if status.is_active:
            #         logger.info(f"{region.value}: {status.total_cycles_today} cycles today")
    
    except KeyboardInterrupt:
        logger.info("\nStopping intraday monitoring...")
        intraday_monitor.stop_monitoring()
        logger.info("Monitoring stopped")
    
    # 7. Save portfolio and trade history
    logger.info("Saving portfolio and trade history...")
    portfolio.save_to_file("data/default_portfolio.json")
    trade_history.save_to_file("data/trade_history.json")
    logger.info("Saved")
    
    logger.info("\n=== Example Complete ===")


if __name__ == "__main__":
    main()
