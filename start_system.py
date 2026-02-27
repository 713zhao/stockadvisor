"""
Unified startup script for Stock Market Analysis System.

This script starts both:
1. The main analysis system with intraday monitoring
2. The web dashboard for portfolio monitoring

Press Ctrl+C to stop both services.
"""

import logging
import sys
import signal
import threading
import time
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('logs/system.log', mode='a')
    ]
)

logger = logging.getLogger(__name__)


def run_analysis_system():
    """Run the main analysis system with intraday monitoring."""
    try:
        from stock_market_analysis.main import StockMarketAnalysisSystem, setup_logging
        
        logger.info("Starting Stock Market Analysis System...")
        
        # Initialize system
        system = StockMarketAnalysisSystem()
        system.system_logger = setup_logging()
        
        # Initialize components
        if not system.initialize():
            logger.error("Failed to initialize analysis system")
            return
        
        # Start system (includes intraday monitoring)
        system.start()
        
        # Keep running
        logger.info("Analysis system running...")
        while True:
            time.sleep(60)
            
    except KeyboardInterrupt:
        logger.info("Analysis system received shutdown signal")
        if 'system' in locals():
            system.shutdown()
    except Exception as e:
        logger.error(f"Analysis system error: {e}", exc_info=True)


def run_web_dashboard():
    """Run the web dashboard server."""
    try:
        import web_dashboard
        
        logger.info("Starting Web Dashboard on http://localhost:5000")
        
        # Run Flask app (this blocks)
        web_dashboard.app.run(
            host='0.0.0.0',
            port=5000,
            debug=False,
            use_reloader=False  # Disable reloader to avoid duplicate processes
        )
        
    except KeyboardInterrupt:
        logger.info("Web dashboard received shutdown signal")
    except Exception as e:
        logger.error(f"Web dashboard error: {e}", exc_info=True)


def main():
    """Main entry point - starts both services."""
    logger.info("=" * 70)
    logger.info("Stock Market Analysis System - Unified Startup")
    logger.info("=" * 70)
    logger.info("")
    logger.info("Starting services:")
    logger.info("  1. Analysis System (with intraday monitoring)")
    logger.info("  2. Web Dashboard (http://localhost:5000)")
    logger.info("")
    logger.info("Press Ctrl+C to stop all services")
    logger.info("=" * 70)
    
    # Ensure logs directory exists
    Path("logs").mkdir(exist_ok=True)
    
    # Create threads for each service
    analysis_thread = threading.Thread(
        target=run_analysis_system,
        name="AnalysisSystem",
        daemon=True
    )
    
    dashboard_thread = threading.Thread(
        target=run_web_dashboard,
        name="WebDashboard",
        daemon=True
    )
    
    # Setup signal handler for graceful shutdown
    def signal_handler(signum, frame):
        logger.info("")
        logger.info("=" * 70)
        logger.info("Shutdown signal received - stopping all services...")
        logger.info("=" * 70)
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Start both services
    try:
        logger.info("Starting Analysis System thread...")
        analysis_thread.start()
        time.sleep(2)  # Give analysis system time to initialize
        
        logger.info("Starting Web Dashboard thread...")
        dashboard_thread.start()
        time.sleep(1)
        
        logger.info("")
        logger.info("=" * 70)
        logger.info("✓ All services started successfully!")
        logger.info("=" * 70)
        logger.info("")
        logger.info("Access the dashboard at: http://localhost:5000")
        logger.info("")
        logger.info("Services running:")
        logger.info("  • Analysis System: Running with intraday monitoring")
        logger.info("  • Web Dashboard: http://localhost:5000")
        logger.info("")
        logger.info("Press Ctrl+C to stop all services")
        logger.info("=" * 70)
        
        # Keep main thread alive
        while True:
            time.sleep(1)
            
            # Check if threads are still alive
            if not analysis_thread.is_alive():
                logger.error("Analysis system thread died unexpectedly")
                break
            if not dashboard_thread.is_alive():
                logger.error("Web dashboard thread died unexpectedly")
                break
                
    except KeyboardInterrupt:
        logger.info("")
        logger.info("Shutting down gracefully...")
    except Exception as e:
        logger.error(f"System error: {e}", exc_info=True)
    finally:
        logger.info("System shutdown complete")


if __name__ == "__main__":
    main()
