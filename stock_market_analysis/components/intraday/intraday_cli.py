"""
CLI interface for intraday market monitoring.

Provides command-line interface for:
- Starting intraday monitoring
- Stopping monitoring
- Querying status for each region
- Viewing and updating configuration
"""

import argparse
import sys
import logging
from pathlib import Path
from typing import List

from stock_market_analysis.components.configuration_manager import ConfigurationManager
from stock_market_analysis.components.analysis_engine import AnalysisEngine
from stock_market_analysis.components.market_monitor import MarketMonitor
from stock_market_analysis.trading.trade_executor import TradeExecutor
from stock_market_analysis.models.market_region import MarketRegion
from .intraday_monitor import IntradayMonitor
from .market_hours_detector import MarketHoursDetector
from .timezone_converter import TimezoneConverter


# Global monitor instance for start/stop commands
_monitor_instance = None


def _create_monitor() -> IntradayMonitor:
    """Create and return an IntradayMonitor instance."""
    config_manager = ConfigurationManager()
    
    # Create timezone converter
    timezone_converter = TimezoneConverter()
    
    # Create market hours detector
    market_hours_detector = MarketHoursDetector(
        timezone_converter=timezone_converter,
        config_manager=config_manager
    )
    
    # Create analysis engine
    market_monitor = MarketMonitor(config_manager)
    analysis_engine = AnalysisEngine(
        market_monitor=market_monitor,
        config_manager=config_manager
    )
    
    # Create trade executor
    trade_executor = TradeExecutor(config_manager)
    
    # Create intraday monitor
    monitor = IntradayMonitor(
        market_hours_detector=market_hours_detector,
        analysis_engine=analysis_engine,
        trade_executor=trade_executor,
        config_manager=config_manager
    )
    
    return monitor


def start_command(args):
    """Start intraday monitoring."""
    global _monitor_instance
    
    print("Starting intraday monitoring...")
    
    try:
        # Create monitor instance
        _monitor_instance = _create_monitor()
        
        # Start monitoring
        _monitor_instance.start_monitoring()
        
        print("✓ Intraday monitoring started")
        print()
        print("Monitoring is now running in background threads.")
        print("Use 'intraday-cli status' to check monitoring status.")
        print("Use 'intraday-cli stop' to stop monitoring.")
        print()
        print("Note: This process must remain running for monitoring to continue.")
        print("Press Ctrl+C to stop monitoring and exit.")
        
        # Keep the process running
        try:
            import time
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopping monitoring...")
            _monitor_instance.stop_monitoring()
            print("✓ Monitoring stopped")
            
    except Exception as e:
        print(f"Error starting monitoring: {e}", file=sys.stderr)
        sys.exit(1)


def stop_command(args):
    """Stop intraday monitoring."""
    global _monitor_instance
    
    print("Stopping intraday monitoring...")
    
    if _monitor_instance is None:
        print("Warning: No active monitoring instance found", file=sys.stderr)
        print("If monitoring is running in another process, you'll need to stop it there.")
        sys.exit(1)
    
    try:
        _monitor_instance.stop_monitoring()
        print("✓ Intraday monitoring stopped")
        _monitor_instance = None
    except Exception as e:
        print(f"Error stopping monitoring: {e}", file=sys.stderr)
        sys.exit(1)


def status_command(args):
    """Query monitoring status for each region."""
    print("Querying intraday monitoring status...")
    print()
    
    try:
        # Create monitor instance to query status
        monitor = _create_monitor()
        
        # Get configuration to see which regions are configured
        config_manager = ConfigurationManager()
        config = config_manager.get_intraday_config()
        
        print("=" * 70)
        print("INTRADAY MONITORING STATUS")
        print("=" * 70)
        print()
        
        # Display global configuration
        print("Configuration:")
        print(f"  Enabled: {config.get('enabled', False)}")
        print(f"  Monitoring Interval: {config.get('monitoring_interval_minutes', 60)} minutes")
        print(f"  Monitored Regions: {', '.join(config.get('monitored_regions', []))}")
        print()
        
        if not config.get('enabled', False):
            print("⚠ Intraday monitoring is DISABLED in configuration")
            print()
            return
        
        # Get status for each configured region
        region_names = config.get('monitored_regions', [])
        
        if not region_names:
            print("⚠ No regions configured for monitoring")
            print()
            return
        
        print("Region Status:")
        print("-" * 70)
        
        for region_name in region_names:
            try:
                region = MarketRegion(region_name)
                status = monitor.get_monitoring_status(region)
                
                print(f"\n{region.value.upper()}:")
                print(f"  Active: {'Yes' if status.is_active else 'No'}")
                print(f"  Paused: {'Yes' if status.is_paused else 'No'}")
                
                if status.is_paused:
                    print(f"  Pause Reason: {status.pause_reason}")
                    print(f"  Pause Until: {status.pause_until.strftime('%Y-%m-%d %H:%M:%S UTC') if status.pause_until else 'N/A'}")
                
                print(f"  Last Cycle: {status.last_cycle_time.strftime('%Y-%m-%d %H:%M:%S UTC') if status.last_cycle_time else 'Never'}")
                print(f"  Next Cycle: {status.next_cycle_time.strftime('%Y-%m-%d %H:%M:%S UTC') if status.next_cycle_time else 'Not scheduled'}")
                print(f"  Consecutive Failures: {status.consecutive_failures}")
                print(f"  Total Cycles Today: {status.total_cycles_today}")
                
            except ValueError:
                print(f"\n{region_name.upper()}: Invalid region name")
        
        print()
        print("=" * 70)
        
    except Exception as e:
        print(f"Error querying status: {e}", file=sys.stderr)
        sys.exit(1)


def config_view_command(args):
    """View current configuration."""
    print("Current intraday monitoring configuration:")
    print()
    
    try:
        config_manager = ConfigurationManager()
        config = config_manager.get_intraday_config()
        
        print("=" * 70)
        print("INTRADAY MONITORING CONFIGURATION")
        print("=" * 70)
        print()
        print(f"Enabled: {config.get('enabled', False)}")
        print(f"Monitoring Interval: {config.get('monitoring_interval_minutes', 60)} minutes")
        print(f"Monitored Regions: {', '.join(config.get('monitored_regions', [])) or 'None'}")
        print()
        
        # Display market holidays if configured
        holidays = config.get('market_holidays', {})
        if holidays:
            print("Market Holidays:")
            for region, dates in holidays.items():
                print(f"  {region}: {len(dates)} holidays configured")
        else:
            print("Market Holidays: None configured")
        
        print()
        print("=" * 70)
        
    except Exception as e:
        print(f"Error viewing configuration: {e}", file=sys.stderr)
        sys.exit(1)


def config_set_command(args):
    """Update configuration."""
    print("Updating intraday monitoring configuration...")
    
    try:
        config_manager = ConfigurationManager()
        
        # Parse regions
        regions = []
        if args.regions:
            for region_name in args.regions:
                try:
                    region = MarketRegion(region_name.lower())
                    regions.append(region)
                except ValueError:
                    print(f"Error: Invalid region '{region_name}'", file=sys.stderr)
                    print(f"Valid regions: {', '.join([r.value for r in MarketRegion])}")
                    sys.exit(1)
        
        # Set configuration
        result = config_manager.set_intraday_config(
            enabled=args.enabled,
            interval_minutes=args.interval,
            regions=regions
        )
        
        if result.is_ok():
            print("✓ Configuration updated successfully")
            print()
            print(f"  Enabled: {args.enabled}")
            print(f"  Monitoring Interval: {args.interval} minutes")
            print(f"  Monitored Regions: {', '.join([r.value for r in regions])}")
            print()
            print("Note: Restart monitoring for changes to take effect.")
        else:
            print(f"Error: {result.error()}", file=sys.stderr)
            sys.exit(1)
            
    except Exception as e:
        print(f"Error updating configuration: {e}", file=sys.stderr)
        sys.exit(1)


def config_enable_command(args):
    """Enable intraday monitoring."""
    print("Enabling intraday monitoring...")
    
    try:
        config_manager = ConfigurationManager()
        
        # Get current configuration
        current_config = config_manager.get_intraday_config()
        
        # Parse regions from current config
        region_names = current_config.get('monitored_regions', [])
        if not region_names:
            print("Error: No regions configured. Use 'config set' to configure regions first.", file=sys.stderr)
            sys.exit(1)
        
        regions = [MarketRegion(name) for name in region_names]
        
        # Enable monitoring
        result = config_manager.set_intraday_config(
            enabled=True,
            interval_minutes=current_config.get('monitoring_interval_minutes', 60),
            regions=regions
        )
        
        if result.is_ok():
            print("✓ Intraday monitoring enabled")
        else:
            print(f"Error: {result.error()}", file=sys.stderr)
            sys.exit(1)
            
    except Exception as e:
        print(f"Error enabling monitoring: {e}", file=sys.stderr)
        sys.exit(1)


def config_disable_command(args):
    """Disable intraday monitoring."""
    print("Disabling intraday monitoring...")
    
    try:
        config_manager = ConfigurationManager()
        
        # Get current configuration
        current_config = config_manager.get_intraday_config()
        
        # Parse regions from current config (keep them, just disable)
        region_names = current_config.get('monitored_regions', [])
        regions = [MarketRegion(name) for name in region_names] if region_names else [MarketRegion.USA]
        
        # Disable monitoring
        result = config_manager.set_intraday_config(
            enabled=False,
            interval_minutes=current_config.get('monitoring_interval_minutes', 60),
            regions=regions
        )
        
        if result.is_ok():
            print("✓ Intraday monitoring disabled")
        else:
            print(f"Error: {result.error()}", file=sys.stderr)
            sys.exit(1)
            
    except Exception as e:
        print(f"Error disabling monitoring: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Intraday Market Monitoring CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start monitoring
  intraday-cli start
  
  # Check status
  intraday-cli status
  
  # View configuration
  intraday-cli config view
  
  # Enable monitoring
  intraday-cli config enable
  
  # Disable monitoring
  intraday-cli config disable
  
  # Configure monitoring
  intraday-cli config set --enabled --interval 60 --regions china usa
  
  # Stop monitoring
  intraday-cli stop
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Start command
    start_parser = subparsers.add_parser('start', help='Start intraday monitoring')
    start_parser.set_defaults(func=start_command)
    
    # Stop command
    stop_parser = subparsers.add_parser('stop', help='Stop intraday monitoring')
    stop_parser.set_defaults(func=stop_command)
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Query monitoring status')
    status_parser.set_defaults(func=status_command)
    
    # Config command with subcommands
    config_parser = subparsers.add_parser('config', help='View/update configuration')
    config_subparsers = config_parser.add_subparsers(dest='config_command', help='Configuration commands')
    
    # Config view
    config_view_parser = config_subparsers.add_parser('view', help='View current configuration')
    config_view_parser.set_defaults(func=config_view_command)
    
    # Config set
    config_set_parser = config_subparsers.add_parser('set', help='Update configuration')
    config_set_parser.add_argument(
        '--enabled',
        action='store_true',
        help='Enable intraday monitoring'
    )
    config_set_parser.add_argument(
        '--disabled',
        action='store_true',
        help='Disable intraday monitoring'
    )
    config_set_parser.add_argument(
        '--interval',
        type=int,
        default=60,
        help='Monitoring interval in minutes (15-240, default: 60)'
    )
    config_set_parser.add_argument(
        '--regions',
        nargs='+',
        choices=['china', 'hong_kong', 'usa'],
        help='Market regions to monitor'
    )
    config_set_parser.set_defaults(func=config_set_command)
    
    # Config enable
    config_enable_parser = config_subparsers.add_parser('enable', help='Enable intraday monitoring')
    config_enable_parser.set_defaults(func=config_enable_command)
    
    # Config disable
    config_disable_parser = config_subparsers.add_parser('disable', help='Disable intraday monitoring')
    config_disable_parser.set_defaults(func=config_disable_command)
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Handle config command without subcommand
    if args.command == 'config' and not hasattr(args, 'func'):
        config_parser.print_help()
        sys.exit(1)
    
    # Handle --enabled/--disabled flags for config set
    if hasattr(args, 'enabled') and hasattr(args, 'disabled'):
        if args.disabled:
            args.enabled = False
        # If neither flag is set, default to enabled
        elif not args.enabled and not args.disabled:
            args.enabled = True
    
    # Execute command
    try:
        args.func(args)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
