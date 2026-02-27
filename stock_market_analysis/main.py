"""
Main entry point for the Stock Market Analysis system.

This module wires all components together and provides the main application entry point.
"""

import logging
import sys
import signal
from pathlib import Path
from typing import Optional

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from stock_market_analysis.components import (
    ConfigurationManager,
    MarketMonitor,
    MockMarketDataAPI,
    AnalysisEngine,
    ReportGenerator,
    NotificationService,
    Scheduler,
    initialize_logger,
    EventType,
    EventStatus
)
from stock_market_analysis.components.yahoo_finance_api import YahooFinanceAPI
from stock_market_analysis.trading import TradingSimulator, TradingIntegration
from decimal import Decimal


class StockMarketAnalysisSystem:
    """
    Main system class that wires all components together.
    
    This class implements dependency injection and manages the lifecycle
    of all system components.
    """
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize the Stock Market Analysis system.
        
        Args:
            config_path: Path to configuration file. Defaults to config/default.yaml
        """
        self.config_path = config_path or Path("config/default.yaml")
        self.logger = logging.getLogger(__name__)
        self.system_logger = None
        
        # Component instances
        self.config_manager: Optional[ConfigurationManager] = None
        self.market_monitor: Optional[MarketMonitor] = None
        self.analysis_engine: Optional[AnalysisEngine] = None
        self.report_generator: Optional[ReportGenerator] = None
        self.notification_service: Optional[NotificationService] = None
        self.scheduler: Optional[Scheduler] = None
        self.trading_simulator: Optional[TradingSimulator] = None
        self.trading_integration: Optional[TradingIntegration] = None
        self.default_portfolio_id: Optional[str] = None
        
        # System state
        self._running = False
        self._initialized = False
    
    def initialize(self) -> bool:
        """
        Initialize all system components with dependency injection.
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            self.logger.info("Initializing Stock Market Analysis system...")
            
            # Initialize configuration manager
            self.config_manager = ConfigurationManager(storage_path=self.config_path)
            self.logger.info(f"Configuration loaded from {self.config_path}")
            
            # Initialize market monitor with Yahoo Finance API
            market_api = YahooFinanceAPI(config_manager=self.config_manager)
            self.market_monitor = MarketMonitor(api=market_api)
            self.logger.info("Market monitor initialized with Yahoo Finance API")
            
            # Initialize analysis engine
            self.analysis_engine = AnalysisEngine(
                market_monitor=self.market_monitor
            )
            self.logger.info("Analysis engine initialized")
            
            # Initialize trading simulator
            self.trading_simulator = TradingSimulator(config_manager=self.config_manager)
            self.logger.info("Trading simulator initialized")
            
            # Create default portfolio
            initial_cash = Decimal(str(self.config_manager.get_initial_cash_balance()))
            self.default_portfolio_id = self.trading_simulator.create_portfolio(initial_cash)
            self.logger.info(f"Created default portfolio {self.default_portfolio_id} with ${initial_cash:,.2f}")
            
            # Initialize trading integration
            self.trading_integration = TradingIntegration(
                trading_simulator=self.trading_simulator,
                analysis_engine=self.analysis_engine
            )
            self.logger.info("Trading integration initialized")
            
            # Initialize report generator
            self.report_generator = ReportGenerator()
            self.logger.info("Report generator initialized")
            
            # Initialize notification service
            self.notification_service = NotificationService(
                config_manager=self.config_manager
            )
            self.logger.info("Notification service initialized")
            
            # Initialize scheduler with analysis executor
            def analysis_executor(regions=None):
                """Execute the complete analysis pipeline."""
                return self.run_analysis_pipeline(regions)
            
            self.scheduler = Scheduler(analysis_executor=analysis_executor)
            
            # Schedule daily analysis for configured regions
            configured_regions = self.config_manager.get_configured_regions()
            self.scheduler.schedule_daily_analysis(configured_regions)
            self.logger.info(f"Scheduler configured for regions: {[r.value for r in configured_regions]}")
            
            # Log system initialization event
            if self.system_logger:
                self.system_logger.log_event(
                    event_type=EventType.SYSTEM_STARTUP,
                    status=EventStatus.SUCCESS,
                    component="Main",
                    message="All components initialized successfully"
                )
            
            self._initialized = True
            self.logger.info("System initialization complete")
            return True
            
        except Exception as e:
            self.logger.error(f"System initialization failed: {e}", exc_info=True)
            if self.system_logger:
                self.system_logger.log_event(
                    event_type=EventType.SYSTEM_STARTUP,
                    status=EventStatus.FAILURE,
                    component="Main",
                    message=f"Initialization failed: {str(e)}"
                )
            return False
    
    def run_analysis_pipeline(self, regions=None):
        """
        Execute the complete analysis pipeline.
        
        Args:
            regions: Optional list of regions to analyze. If None, uses configured regions.
            
        Returns:
            AnalysisResult from the pipeline execution
        """
        from stock_market_analysis.models.results import AnalysisResult
        
        try:
            self.logger.info("Starting analysis pipeline...")
            
            # Get regions to analyze
            regions_to_analyze = regions or self.config_manager.get_configured_regions()
            
            # Step 1: Collect market data
            self.logger.info(f"Collecting market data for regions: {[r.value for r in regions_to_analyze]}")
            market_data = self.market_monitor.collect_market_data(regions_to_analyze)
            
            if market_data.failed_regions:
                self.logger.warning(f"Failed to collect data from regions: {[r.value for r in market_data.failed_regions]}")
            
            # Step 2: Analyze and generate recommendations
            self.logger.info("Analyzing market data and generating recommendations...")
            recommendations = self.analysis_engine.analyze_and_recommend(market_data)
            self.logger.info(f"Generated {len(recommendations)} recommendations")
            
            # Step 2.5: Process recommendations through trading simulator
            if self.trading_integration and self.default_portfolio_id:
                self.logger.info("Processing recommendations through trading simulator...")
                executed_trades = self.trading_integration.process_analysis_results(
                    self.default_portfolio_id,
                    recommendations
                )
                self.logger.info(f"Executed {len(executed_trades)} trades")
                
                # Get performance report
                performance_report = self.trading_simulator.get_performance_report(
                    self.default_portfolio_id
                )
                portfolio = self.trading_simulator.get_portfolio(self.default_portfolio_id)
                
                self.logger.info(
                    f"Portfolio value: ${performance_report.portfolio_value:,.2f}, "
                    f"Cash: ${portfolio.cash_balance:,.2f}, "
                    f"Total P&L: ${performance_report.total_pnl:,.2f} "
                    f"({performance_report.total_return_pct:.2f}%)"
                )
            
            # Step 3: Generate daily report
            self.logger.info("Generating daily report...")
            market_summaries = self._create_market_summaries(market_data)
            report = self.report_generator.generate_daily_report(recommendations, market_summaries)
            
            # Step 4: Deliver report through notification channels
            self.logger.info("Delivering report through notification channels...")
            delivery_result = self.notification_service.deliver_report(report)
            
            if delivery_result.all_succeeded():
                self.logger.info("Report delivered successfully through all channels")
            elif delivery_result.any_succeeded():
                self.logger.warning(f"Report delivered through some channels. Errors: {delivery_result.errors}")
            else:
                self.logger.error(f"Failed to deliver report through any channel. Errors: {delivery_result.errors}")
            
            # Log pipeline completion
            if self.system_logger:
                self.system_logger.log_event(
                    event_type=EventType.REPORT_GENERATION,
                    status=EventStatus.SUCCESS,
                    component="Pipeline",
                    message=f"Analysis pipeline completed: {len(recommendations)} recommendations, report delivered"
                )
            
            return AnalysisResult(
                success=True,
                recommendations=recommendations,
                error_message=None,
                retry_count=0
            )
            
        except Exception as e:
            error_msg = f"Analysis pipeline failed: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            
            if self.system_logger:
                self.system_logger.log_event(
                    event_type=EventType.REPORT_GENERATION,
                    status=EventStatus.FAILURE,
                    component="Pipeline",
                    message=error_msg
                )
            
            return AnalysisResult(
                success=False,
                recommendations=[],
                error_message=error_msg,
                retry_count=0
            )
    
    def _create_market_summaries(self, market_data):
        """
        Create market summaries from collected market data.
        
        Args:
            market_data: MarketDataCollection from market monitor
            
        Returns:
            Dictionary mapping MarketRegion to MarketSummary
        """
        from stock_market_analysis.models import MarketSummary
        from datetime import date
        
        summaries = {}
        
        for region, data_list in market_data.data_by_region.items():
            # Calculate basic statistics
            total_stocks = len(data_list)
            
            # Simple trend analysis based on price movements
            bullish_count = sum(1 for d in data_list if d.close_price > d.open_price)
            bearish_count = sum(1 for d in data_list if d.close_price < d.open_price)
            
            if bullish_count > bearish_count * 1.2:
                trend = "bullish"
            elif bearish_count > bullish_count * 1.2:
                trend = "bearish"
            else:
                trend = "neutral"
            
            summaries[region] = MarketSummary(
                region=region,
                trading_date=date.today(),
                total_stocks_analyzed=total_stocks,
                market_trend=trend,
                notable_events=[],
                index_performance={}
            )
        
        return summaries
    
    def run_once(self) -> bool:
        """
        Run the analysis pipeline once immediately.
        
        Returns:
            True if analysis completed successfully, False otherwise
        """
        if not self._initialized:
            self.logger.error("System not initialized. Call initialize() first.")
            return False
        
        self.logger.info("Running analysis pipeline once...")
        result = self.scheduler.execute_now()
        return result.success
    
    def start(self):
        """
        Start the system in scheduled mode.
        
        Note: In a production system, this would start a background scheduler
        (e.g., APScheduler) that runs the analysis at scheduled times.
        For this implementation, it runs the analysis once.
        """
        if not self._initialized:
            self.logger.error("System not initialized. Call initialize() first.")
            return
        
        self._running = True
        self.logger.info("Stock Market Analysis system started")
        
        # Get next execution time
        next_execution = self.scheduler.get_next_execution_time()
        if next_execution:
            self.logger.info(f"Next scheduled analysis: {next_execution}")
        
        # For this implementation, run once immediately
        # In production, this would be handled by a scheduler daemon
        self.run_once()
    
    def shutdown(self):
        """Shutdown the system gracefully."""
        if not self._running:
            return
        
        self.logger.info("Shutting down Stock Market Analysis system...")
        self._running = False
        
        if self.system_logger:
            self.system_logger.log_event(
                event_type=EventType.SYSTEM_SHUTDOWN,
                status=EventStatus.SUCCESS,
                component="Main",
                message="System shutdown complete"
            )
        
        self.logger.info("System shutdown complete")


def setup_logging():
    """Set up logging configuration."""
    # Ensure logs directory exists
    Path("logs").mkdir(exist_ok=True)
    
    # Set up standard Python logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('logs/stock_analysis.log', mode='a')
        ]
    )
    
    # Initialize centralized system logger
    system_logger = initialize_logger(log_dir=Path("logs"))
    
    return system_logger


def main():
    """Main application entry point."""
    # Set up logging
    system_logger = setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("=" * 60)
    logger.info("Stock Market Analysis and Recommendation System")
    logger.info("=" * 60)
    
    # Create system instance
    system = StockMarketAnalysisSystem()
    system.system_logger = system_logger
    
    # Set up signal handlers for graceful shutdown
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, shutting down...")
        system.shutdown()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Initialize system
    if not system.initialize():
        logger.error("Failed to initialize system. Exiting.")
        sys.exit(1)
    
    # Start system
    try:
        system.start()
    except Exception as e:
        logger.error(f"System error: {e}", exc_info=True)
        system.shutdown()
        sys.exit(1)
    
    logger.info("System execution complete")


if __name__ == "__main__":
    main()