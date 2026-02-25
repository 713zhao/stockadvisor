#!/usr/bin/env python3
"""
Configuration setup helper script.

This script helps users create and validate their configuration files.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from stock_market_analysis.components import ConfigurationManager
from stock_market_analysis.models import MarketRegion, SMTPConfig


def create_production_config():
    """Interactive script to create production configuration."""
    print("=" * 60)
    print("Stock Market Analysis - Configuration Setup")
    print("=" * 60)
    print()
    
    config_manager = ConfigurationManager()
    
    # Market regions
    print("1. Market Regions Configuration")
    print("-" * 40)
    print("Available regions: china, hong_kong, usa")
    regions_input = input("Enter regions (comma-separated) [china,hong_kong,usa]: ").strip()
    
    if regions_input:
        region_names = [r.strip() for r in regions_input.split(',')]
        config_manager._configuration.market_regions = []
        for region_name in region_names:
            try:
                region = MarketRegion(region_name.lower())
                config_manager.add_market_region(region)
                print(f"  ✓ Added region: {region.value}")
            except ValueError:
                print(f"  ✗ Invalid region: {region_name}")
    
    print()
    
    # Telegram configuration
    print("2. Telegram Configuration")
    print("-" * 40)
    enable_telegram = input("Enable Telegram notifications? (y/n) [n]: ").strip().lower()
    
    if enable_telegram == 'y':
        bot_token = input("  Bot token: ").strip()
        chat_ids_input = input("  Chat IDs (comma-separated): ").strip()
        chat_ids = [cid.strip() for cid in chat_ids_input.split(',')]
        
        result = config_manager.set_telegram_config(bot_token, chat_ids)
        if result.is_ok():
            print("  ✓ Telegram configured successfully")
        else:
            print(f"  ✗ Error: {result.error()}")
    
    print()
    
    # Slack configuration
    print("3. Slack Configuration")
    print("-" * 40)
    enable_slack = input("Enable Slack notifications? (y/n) [n]: ").strip().lower()
    
    if enable_slack == 'y':
        webhook_url = input("  Webhook URL: ").strip()
        channel = input("  Channel name: ").strip()
        
        result = config_manager.set_slack_config(webhook_url, channel)
        if result.is_ok():
            print("  ✓ Slack configured successfully")
        else:
            print(f"  ✗ Error: {result.error()}")
    
    print()
    
    # Email configuration
    print("4. Email Configuration")
    print("-" * 40)
    enable_email = input("Enable Email notifications? (y/n) [n]: ").strip().lower()
    
    if enable_email == 'y':
        smtp_host = input("  SMTP host [smtp.gmail.com]: ").strip() or "smtp.gmail.com"
        smtp_port = input("  SMTP port [587]: ").strip() or "587"
        smtp_username = input("  SMTP username: ").strip()
        smtp_password = input("  SMTP password: ").strip()
        use_tls = input("  Use TLS? (y/n) [y]: ").strip().lower() != 'n'
        recipients_input = input("  Recipients (comma-separated): ").strip()
        recipients = [r.strip() for r in recipients_input.split(',')]
        
        smtp_config = SMTPConfig(
            host=smtp_host,
            port=int(smtp_port),
            username=smtp_username,
            password=smtp_password,
            use_tls=use_tls
        )
        
        result = config_manager.set_email_config(smtp_config, recipients)
        if result.is_ok():
            print("  ✓ Email configured successfully")
        else:
            print(f"  ✗ Error: {result.error()}")
    
    print()
    
    # Schedule configuration
    print("5. Schedule Configuration")
    print("-" * 40)
    print("Default schedule: 0 18 * * 1-5 (Weekdays at 6 PM)")
    custom_schedule = input("Enter custom schedule (cron format) or press Enter for default: ").strip()
    
    if custom_schedule:
        config_manager._configuration.custom_schedule = custom_schedule
        print(f"  ✓ Custom schedule set: {custom_schedule}")
    
    print()
    
    # Save configuration
    print("6. Save Configuration")
    print("-" * 40)
    output_file = input("Output file [config/production.yaml]: ").strip() or "config/production.yaml"
    
    config_manager.storage_path = Path(output_file)
    
    try:
        config_manager.persist_configuration()
        print(f"  ✓ Configuration saved to {output_file}")
        print()
        print("Configuration setup complete!")
        print()
        print("IMPORTANT: Keep your configuration file secure!")
        print("Do not commit it to version control if it contains credentials.")
    except Exception as e:
        print(f"  ✗ Error saving configuration: {e}")
        return 1
    
    return 0


def validate_config(config_file: str):
    """Validate a configuration file."""
    print(f"Validating configuration: {config_file}")
    print("-" * 60)
    
    try:
        config_manager = ConfigurationManager(storage_path=Path(config_file))
        
        # Check regions
        regions = config_manager.get_configured_regions()
        print(f"✓ Market regions: {[r.value for r in regions]}")
        
        # Check notification channels
        if config_manager.get_telegram_config():
            print("✓ Telegram: Configured")
        else:
            print("  Telegram: Not configured")
        
        if config_manager.get_slack_config():
            print("✓ Slack: Configured")
        else:
            print("  Slack: Not configured")
        
        if config_manager.get_email_config():
            print("✓ Email: Configured")
        else:
            print("  Email: Not configured")
        
        # Check schedule
        schedule = config_manager._configuration.custom_schedule
        if schedule:
            print(f"✓ Custom schedule: {schedule}")
        else:
            print("  Schedule: Using default")
        
        print()
        print("Configuration is valid!")
        return 0
        
    except Exception as e:
        print(f"✗ Configuration validation failed: {e}")
        return 1


def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        if sys.argv[1] == "validate":
            if len(sys.argv) < 3:
                print("Usage: python setup_config.py validate <config_file>")
                return 1
            return validate_config(sys.argv[2])
        elif sys.argv[1] == "create":
            return create_production_config()
        else:
            print("Unknown command. Use 'create' or 'validate'")
            return 1
    else:
        # Interactive mode
        print("Configuration Setup Helper")
        print()
        print("1. Create new configuration")
        print("2. Validate existing configuration")
        print()
        choice = input("Choose an option (1 or 2): ").strip()
        
        if choice == "1":
            return create_production_config()
        elif choice == "2":
            config_file = input("Configuration file path: ").strip()
            return validate_config(config_file)
        else:
            print("Invalid choice")
            return 1


if __name__ == "__main__":
    sys.exit(main())
