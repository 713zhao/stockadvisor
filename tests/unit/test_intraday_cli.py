"""
Unit tests for intraday CLI interface.

Tests all CLI commands including start, stop, status, and configuration management.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock, call
from io import StringIO
import sys
from datetime import datetime

from stock_market_analysis.components.intraday.intraday_cli import (
    start_command,
    stop_command,
    status_command,
    config_view_command,
    config_set_command,
    config_enable_command,
    config_disable_command,
    main
)
from stock_market_analysis.models.market_region import MarketRegion
from stock_market_analysis.components.intraday.models import MonitoringStatus
from stock_market_analysis.components.configuration_manager import Result


class TestIntradayCLI(unittest.TestCase):
    """Test cases for intraday CLI commands."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.maxDiff = None
    
    @patch('stock_market_analysis.components.intraday.intraday_cli._create_monitor')
    @patch('time.sleep')
    def test_start_command_success(self, mock_sleep, mock_create_monitor):
        """Test start command successfully starts monitoring."""
        # Setup
        mock_monitor = Mock()
        mock_create_monitor.return_value = mock_monitor
        
        # Simulate KeyboardInterrupt after a short time
        mock_sleep.side_effect = [None, KeyboardInterrupt()]
        
        args = Mock()
        
        # Capture output
        captured_output = StringIO()
        sys.stdout = captured_output
        
        try:
            # Execute
            start_command(args)
        except SystemExit:
            pass
        finally:
            sys.stdout = sys.__stdout__
        
        # Verify
        mock_monitor.start_monitoring.assert_called_once()
        mock_monitor.stop_monitoring.assert_called_once()
        
        output = captured_output.getvalue()
        self.assertIn("Starting intraday monitoring", output)
        self.assertIn("Intraday monitoring started", output)
    
    @patch('stock_market_analysis.components.intraday.intraday_cli._create_monitor')
    def test_start_command_error(self, mock_create_monitor):
        """Test start command handles errors gracefully."""
        # Setup
        mock_create_monitor.side_effect = Exception("Test error")
        
        args = Mock()
        
        # Capture output
        captured_output = StringIO()
        sys.stderr = captured_output
        
        # Execute and verify
        with self.assertRaises(SystemExit) as cm:
            start_command(args)
        
        sys.stderr = sys.__stderr__
        
        self.assertEqual(cm.exception.code, 1)
        output = captured_output.getvalue()
        self.assertIn("Error starting monitoring", output)
        self.assertIn("Test error", output)
    
    @patch('stock_market_analysis.components.intraday.intraday_cli._monitor_instance')
    def test_stop_command_success(self, mock_instance):
        """Test stop command successfully stops monitoring."""
        # Setup
        mock_monitor = Mock()
        
        # Patch the module-level variable
        with patch('stock_market_analysis.components.intraday.intraday_cli._monitor_instance', mock_monitor):
            args = Mock()
            
            # Capture output
            captured_output = StringIO()
            sys.stdout = captured_output
            
            try:
                # Execute
                stop_command(args)
            finally:
                sys.stdout = sys.__stdout__
            
            # Verify
            mock_monitor.stop_monitoring.assert_called_once()
            
            output = captured_output.getvalue()
            self.assertIn("Stopping intraday monitoring", output)
            self.assertIn("Intraday monitoring stopped", output)
    
    def test_stop_command_no_instance(self):
        """Test stop command when no monitoring instance exists."""
        # Setup
        with patch('stock_market_analysis.components.intraday.intraday_cli._monitor_instance', None):
            args = Mock()
            
            # Capture output
            captured_output = StringIO()
            sys.stderr = captured_output
            
            # Execute and verify
            with self.assertRaises(SystemExit) as cm:
                stop_command(args)
            
            sys.stderr = sys.__stderr__
            
            self.assertEqual(cm.exception.code, 1)
            output = captured_output.getvalue()
            self.assertIn("No active monitoring instance", output)
    
    @patch('stock_market_analysis.components.intraday.intraday_cli._create_monitor')
    @patch('stock_market_analysis.components.intraday.intraday_cli.ConfigurationManager')
    def test_status_command_enabled_with_regions(self, mock_config_class, mock_create_monitor):
        """Test status command displays status for all configured regions."""
        # Setup
        mock_monitor = Mock()
        mock_create_monitor.return_value = mock_monitor
        
        mock_config_manager = Mock()
        mock_config_class.return_value = mock_config_manager
        
        # Mock configuration
        mock_config_manager.get_intraday_config.return_value = {
            'enabled': True,
            'monitoring_interval_minutes': 60,
            'monitored_regions': ['china', 'usa']
        }
        
        # Mock status for each region
        china_status = MonitoringStatus(
            region=MarketRegion.CHINA,
            is_active=True,
            is_paused=False,
            pause_reason=None,
            pause_until=None,
            last_cycle_time=datetime(2024, 1, 15, 10, 30),
            next_cycle_time=datetime(2024, 1, 15, 11, 30),
            consecutive_failures=0,
            total_cycles_today=5
        )
        
        usa_status = MonitoringStatus(
            region=MarketRegion.USA,
            is_active=True,
            is_paused=True,
            pause_reason="3 consecutive failures",
            pause_until=datetime(2024, 1, 15, 12, 0),
            last_cycle_time=datetime(2024, 1, 15, 11, 0),
            next_cycle_time=None,
            consecutive_failures=3,
            total_cycles_today=2
        )
        
        mock_monitor.get_monitoring_status.side_effect = [china_status, usa_status]
        
        args = Mock()
        
        # Capture output
        captured_output = StringIO()
        sys.stdout = captured_output
        
        try:
            # Execute
            status_command(args)
        finally:
            sys.stdout = sys.__stdout__
        
        # Verify
        output = captured_output.getvalue()
        self.assertIn("INTRADAY MONITORING STATUS", output)
        self.assertIn("Enabled: True", output)
        self.assertIn("Monitoring Interval: 60 minutes", output)
        self.assertIn("Monitored Regions: china, usa", output)
        self.assertIn("CHINA:", output)
        self.assertIn("Active: Yes", output)
        self.assertIn("Paused: No", output)
        self.assertIn("Total Cycles Today: 5", output)
        self.assertIn("USA:", output)
        self.assertIn("Paused: Yes", output)
        self.assertIn("Pause Reason: 3 consecutive failures", output)
    
    @patch('stock_market_analysis.components.intraday.intraday_cli._create_monitor')
    @patch('stock_market_analysis.components.intraday.intraday_cli.ConfigurationManager')
    def test_status_command_disabled(self, mock_config_class, mock_create_monitor):
        """Test status command when monitoring is disabled."""
        # Setup
        mock_config_manager = Mock()
        mock_config_class.return_value = mock_config_manager
        
        mock_config_manager.get_intraday_config.return_value = {
            'enabled': False,
            'monitoring_interval_minutes': 60,
            'monitored_regions': []
        }
        
        args = Mock()
        
        # Capture output
        captured_output = StringIO()
        sys.stdout = captured_output
        
        try:
            # Execute
            status_command(args)
        finally:
            sys.stdout = sys.__stdout__
        
        # Verify
        output = captured_output.getvalue()
        self.assertIn("Enabled: False", output)
        self.assertIn("monitoring is DISABLED", output)
    
    @patch('stock_market_analysis.components.intraday.intraday_cli.ConfigurationManager')
    def test_config_view_command(self, mock_config_class):
        """Test config view command displays current configuration."""
        # Setup
        mock_config_manager = Mock()
        mock_config_class.return_value = mock_config_manager
        
        mock_config_manager.get_intraday_config.return_value = {
            'enabled': True,
            'monitoring_interval_minutes': 30,
            'monitored_regions': ['china', 'hong_kong', 'usa'],
            'market_holidays': {
                'china': ['2024-01-01', '2024-02-10'],
                'usa': ['2024-01-01', '2024-07-04']
            }
        }
        
        args = Mock()
        
        # Capture output
        captured_output = StringIO()
        sys.stdout = captured_output
        
        try:
            # Execute
            config_view_command(args)
        finally:
            sys.stdout = sys.__stdout__
        
        # Verify
        output = captured_output.getvalue()
        self.assertIn("INTRADAY MONITORING CONFIGURATION", output)
        self.assertIn("Enabled: True", output)
        self.assertIn("Monitoring Interval: 30 minutes", output)
        self.assertIn("Monitored Regions: china, hong_kong, usa", output)
        self.assertIn("Market Holidays:", output)
        self.assertIn("china: 2 holidays configured", output)
        self.assertIn("usa: 2 holidays configured", output)
    
    @patch('stock_market_analysis.components.intraday.intraday_cli.ConfigurationManager')
    def test_config_set_command_success(self, mock_config_class):
        """Test config set command successfully updates configuration."""
        # Setup
        mock_config_manager = Mock()
        mock_config_class.return_value = mock_config_manager
        
        mock_config_manager.set_intraday_config.return_value = Result.ok()
        
        args = Mock()
        args.enabled = True
        args.interval = 45
        args.regions = ['china', 'usa']
        
        # Capture output
        captured_output = StringIO()
        sys.stdout = captured_output
        
        try:
            # Execute
            config_set_command(args)
        finally:
            sys.stdout = sys.__stdout__
        
        # Verify
        mock_config_manager.set_intraday_config.assert_called_once_with(
            enabled=True,
            interval_minutes=45,
            regions=[MarketRegion.CHINA, MarketRegion.USA]
        )
        
        output = captured_output.getvalue()
        self.assertIn("Configuration updated successfully", output)
        self.assertIn("Enabled: True", output)
        self.assertIn("Monitoring Interval: 45 minutes", output)
        self.assertIn("Monitored Regions: china, usa", output)
    
    @patch('stock_market_analysis.components.intraday.intraday_cli.ConfigurationManager')
    def test_config_set_command_invalid_region(self, mock_config_class):
        """Test config set command rejects invalid region."""
        # Setup
        args = Mock()
        args.enabled = True
        args.interval = 60
        args.regions = ['invalid_region']
        
        # Capture output
        captured_output = StringIO()
        sys.stderr = captured_output
        
        # Execute and verify
        with self.assertRaises(SystemExit) as cm:
            config_set_command(args)
        
        sys.stderr = sys.__stderr__
        
        self.assertEqual(cm.exception.code, 1)
        output = captured_output.getvalue()
        self.assertIn("Invalid region", output)
        self.assertIn("invalid_region", output)
    
    @patch('stock_market_analysis.components.intraday.intraday_cli.ConfigurationManager')
    def test_config_set_command_validation_error(self, mock_config_class):
        """Test config set command handles validation errors."""
        # Setup
        mock_config_manager = Mock()
        mock_config_class.return_value = mock_config_manager
        
        mock_config_manager.set_intraday_config.return_value = Result.err(
            "Monitoring interval must be between 15 and 240 minutes"
        )
        
        args = Mock()
        args.enabled = True
        args.interval = 300  # Invalid
        args.regions = ['china']
        
        # Capture output
        captured_output = StringIO()
        sys.stderr = captured_output
        
        # Execute and verify
        with self.assertRaises(SystemExit) as cm:
            config_set_command(args)
        
        sys.stderr = sys.__stderr__
        
        self.assertEqual(cm.exception.code, 1)
        output = captured_output.getvalue()
        self.assertIn("Monitoring interval must be between 15 and 240 minutes", output)
    
    @patch('stock_market_analysis.components.intraday.intraday_cli.ConfigurationManager')
    def test_config_enable_command(self, mock_config_class):
        """Test config enable command enables monitoring."""
        # Setup
        mock_config_manager = Mock()
        mock_config_class.return_value = mock_config_manager
        
        mock_config_manager.get_intraday_config.return_value = {
            'enabled': False,
            'monitoring_interval_minutes': 60,
            'monitored_regions': ['china', 'usa']
        }
        
        mock_config_manager.set_intraday_config.return_value = Result.ok()
        
        args = Mock()
        
        # Capture output
        captured_output = StringIO()
        sys.stdout = captured_output
        
        try:
            # Execute
            config_enable_command(args)
        finally:
            sys.stdout = sys.__stdout__
        
        # Verify
        mock_config_manager.set_intraday_config.assert_called_once_with(
            enabled=True,
            interval_minutes=60,
            regions=[MarketRegion.CHINA, MarketRegion.USA]
        )
        
        output = captured_output.getvalue()
        self.assertIn("Intraday monitoring enabled", output)
    
    @patch('stock_market_analysis.components.intraday.intraday_cli.ConfigurationManager')
    def test_config_enable_command_no_regions(self, mock_config_class):
        """Test config enable command fails when no regions configured."""
        # Setup
        mock_config_manager = Mock()
        mock_config_class.return_value = mock_config_manager
        
        mock_config_manager.get_intraday_config.return_value = {
            'enabled': False,
            'monitoring_interval_minutes': 60,
            'monitored_regions': []
        }
        
        args = Mock()
        
        # Capture output
        captured_output = StringIO()
        sys.stderr = captured_output
        
        # Execute and verify
        with self.assertRaises(SystemExit) as cm:
            config_enable_command(args)
        
        sys.stderr = sys.__stderr__
        
        self.assertEqual(cm.exception.code, 1)
        output = captured_output.getvalue()
        self.assertIn("No regions configured", output)
    
    @patch('stock_market_analysis.components.intraday.intraday_cli.ConfigurationManager')
    def test_config_disable_command(self, mock_config_class):
        """Test config disable command disables monitoring."""
        # Setup
        mock_config_manager = Mock()
        mock_config_class.return_value = mock_config_manager
        
        mock_config_manager.get_intraday_config.return_value = {
            'enabled': True,
            'monitoring_interval_minutes': 60,
            'monitored_regions': ['china', 'usa']
        }
        
        mock_config_manager.set_intraday_config.return_value = Result.ok()
        
        args = Mock()
        
        # Capture output
        captured_output = StringIO()
        sys.stdout = captured_output
        
        try:
            # Execute
            config_disable_command(args)
        finally:
            sys.stdout = sys.__stdout__
        
        # Verify
        mock_config_manager.set_intraday_config.assert_called_once_with(
            enabled=False,
            interval_minutes=60,
            regions=[MarketRegion.CHINA, MarketRegion.USA]
        )
        
        output = captured_output.getvalue()
        self.assertIn("Intraday monitoring disabled", output)
    
    @patch('sys.argv', ['intraday-cli'])
    def test_main_no_command(self):
        """Test main function with no command shows help."""
        # Capture output
        captured_output = StringIO()
        sys.stdout = captured_output
        
        # Execute and verify
        with self.assertRaises(SystemExit) as cm:
            main()
        
        sys.stdout = sys.__stdout__
        
        self.assertEqual(cm.exception.code, 1)
    
    @patch('sys.argv', ['intraday-cli', 'config'])
    def test_main_config_no_subcommand(self):
        """Test main function with config but no subcommand shows help."""
        # Capture output
        captured_output = StringIO()
        sys.stdout = captured_output
        
        # Execute and verify
        with self.assertRaises(SystemExit) as cm:
            main()
        
        sys.stdout = sys.__stdout__
        
        self.assertEqual(cm.exception.code, 1)
    
    @patch('sys.argv', ['intraday-cli', 'config', 'view'])
    @patch('stock_market_analysis.components.intraday.intraday_cli.ConfigurationManager')
    def test_main_config_view(self, mock_config_class):
        """Test main function executes config view command."""
        # Setup
        mock_config_manager = Mock()
        mock_config_class.return_value = mock_config_manager
        
        mock_config_manager.get_intraday_config.return_value = {
            'enabled': True,
            'monitoring_interval_minutes': 60,
            'monitored_regions': ['china']
        }
        
        # Capture output
        captured_output = StringIO()
        sys.stdout = captured_output
        
        try:
            # Execute
            main()
        finally:
            sys.stdout = sys.__stdout__
        
        # Verify
        output = captured_output.getvalue()
        self.assertIn("INTRADAY MONITORING CONFIGURATION", output)


if __name__ == '__main__':
    unittest.main()
