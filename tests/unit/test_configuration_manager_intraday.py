"""
Unit tests for ConfigurationManager intraday monitoring extensions.
"""

import pytest
import tempfile
import yaml
from pathlib import Path

from stock_market_analysis.components.configuration_manager import ConfigurationManager
from stock_market_analysis.models.market_region import MarketRegion


class TestConfigurationManagerIntraday:
    """Test suite for ConfigurationManager intraday extensions."""
    
    @pytest.fixture
    def temp_config_file(self):
        """Create a temporary configuration file for testing."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            temp_path = Path(f.name)
        yield temp_path
        # Cleanup
        if temp_path.exists():
            temp_path.unlink()
    
    @pytest.fixture
    def config_manager(self, temp_config_file):
        """Create a ConfigurationManager instance with temporary storage."""
        return ConfigurationManager(storage_path=temp_config_file)
    
    def test_get_intraday_config_default(self, config_manager):
        """Test getting default intraday configuration when no config exists."""
        config = config_manager.get_intraday_config()
        
        assert config['enabled'] is False
        assert config['monitoring_interval_minutes'] == 60
        assert config['monitored_regions'] == []
    
    def test_set_intraday_config_valid(self, config_manager):
        """Test setting valid intraday configuration."""
        result = config_manager.set_intraday_config(
            enabled=True,
            interval_minutes=60,
            regions=[MarketRegion.CHINA, MarketRegion.USA]
        )
        
        assert result.is_ok()
        
        # Verify configuration was saved
        config = config_manager.get_intraday_config()
        assert config['enabled'] is True
        assert config['monitoring_interval_minutes'] == 60
        assert set(config['monitored_regions']) == {'china', 'usa'}
    
    def test_set_intraday_config_interval_too_low(self, config_manager):
        """Test setting intraday config with interval below minimum (14 minutes)."""
        result = config_manager.set_intraday_config(
            enabled=True,
            interval_minutes=14,
            regions=[MarketRegion.CHINA]
        )
        
        assert result.is_err()
        assert "between 15 and 240" in result.error()
    
    def test_set_intraday_config_interval_minimum_valid(self, config_manager):
        """Test setting intraday config with minimum valid interval (15 minutes)."""
        result = config_manager.set_intraday_config(
            enabled=True,
            interval_minutes=15,
            regions=[MarketRegion.CHINA]
        )
        
        assert result.is_ok()
    
    def test_set_intraday_config_interval_maximum_valid(self, config_manager):
        """Test setting intraday config with maximum valid interval (240 minutes)."""
        result = config_manager.set_intraday_config(
            enabled=True,
            interval_minutes=240,
            regions=[MarketRegion.CHINA]
        )
        
        assert result.is_ok()
    
    def test_set_intraday_config_interval_too_high(self, config_manager):
        """Test setting intraday config with interval above maximum (241 minutes)."""
        result = config_manager.set_intraday_config(
            enabled=True,
            interval_minutes=241,
            regions=[MarketRegion.CHINA]
        )
        
        assert result.is_err()
        assert "between 15 and 240" in result.error()
    
    def test_set_intraday_config_no_regions(self, config_manager):
        """Test setting intraday config with no regions."""
        result = config_manager.set_intraday_config(
            enabled=True,
            interval_minutes=60,
            regions=[]
        )
        
        assert result.is_err()
        assert "at least one region" in result.error().lower()
    
    def test_set_intraday_config_multiple_regions(self, config_manager):
        """Test setting intraday config with multiple regions."""
        result = config_manager.set_intraday_config(
            enabled=True,
            interval_minutes=60,
            regions=[MarketRegion.CHINA, MarketRegion.HONG_KONG, MarketRegion.USA]
        )
        
        assert result.is_ok()
        
        config = config_manager.get_intraday_config()
        assert set(config['monitored_regions']) == {'china', 'hong_kong', 'usa'}
    
    def test_set_intraday_config_disabled(self, config_manager):
        """Test setting intraday config to disabled."""
        result = config_manager.set_intraday_config(
            enabled=False,
            interval_minutes=60,
            regions=[MarketRegion.CHINA]
        )
        
        assert result.is_ok()
        
        config = config_manager.get_intraday_config()
        assert config['enabled'] is False
    
    def test_get_market_holidays_no_config(self, config_manager):
        """Test getting market holidays when no configuration exists."""
        holidays = config_manager.get_market_holidays(MarketRegion.CHINA)
        assert holidays == []
    
    def test_get_market_holidays_with_config(self, config_manager, temp_config_file):
        """Test getting market holidays from configuration."""
        # Create config with holidays
        config_data = {
            'intraday_monitoring': {
                'enabled': True,
                'monitoring_interval_minutes': 60,
                'monitored_regions': ['china'],
                'market_holidays': {
                    'china': ['2024-01-01', '2024-02-10', '2024-10-01'],
                    'usa': ['2024-01-01', '2024-07-04', '2024-12-25']
                }
            }
        }
        
        with open(temp_config_file, 'w') as f:
            yaml.dump(config_data, f)
        
        # Get holidays for China
        holidays = config_manager.get_market_holidays(MarketRegion.CHINA)
        assert holidays == ['2024-01-01', '2024-02-10', '2024-10-01']
        
        # Get holidays for USA
        holidays = config_manager.get_market_holidays(MarketRegion.USA)
        assert holidays == ['2024-01-01', '2024-07-04', '2024-12-25']
        
        # Get holidays for Hong Kong (not configured)
        holidays = config_manager.get_market_holidays(MarketRegion.HONG_KONG)
        assert holidays == []
    
    def test_validate_intraday_config_invalid_interval(self, config_manager):
        """Test validation of invalid monitoring interval."""
        with pytest.raises(ValueError, match="between 15 and 240"):
            config_manager._validate_intraday_config({
                'monitoring_interval_minutes': 10
            })
    
    def test_validate_intraday_config_invalid_enabled_type(self, config_manager):
        """Test validation of invalid enabled flag type."""
        with pytest.raises(ValueError, match="must be a boolean"):
            config_manager._validate_intraday_config({
                'enabled': 'yes'
            })
    
    def test_validate_intraday_config_invalid_regions_type(self, config_manager):
        """Test validation of invalid monitored_regions type."""
        with pytest.raises(ValueError, match="must be a list"):
            config_manager._validate_intraday_config({
                'monitored_regions': 'china'
            })
    
    def test_validate_intraday_config_invalid_region_value(self, config_manager):
        """Test validation of invalid region value."""
        with pytest.raises(ValueError, match="Invalid region"):
            config_manager._validate_intraday_config({
                'monitored_regions': ['invalid_region']
            })
    
    def test_validate_intraday_config_valid(self, config_manager):
        """Test validation of valid intraday configuration."""
        # Should not raise any exception
        config_manager._validate_intraday_config({
            'enabled': True,
            'monitoring_interval_minutes': 60,
            'monitored_regions': ['china', 'usa']
        })
    
    def test_config_persistence(self, config_manager, temp_config_file):
        """Test that configuration persists across manager instances."""
        # Set configuration
        config_manager.set_intraday_config(
            enabled=True,
            interval_minutes=120,
            regions=[MarketRegion.HONG_KONG]
        )
        
        # Create new manager instance with same storage path
        new_manager = ConfigurationManager(storage_path=temp_config_file)
        
        # Verify configuration persisted
        config = new_manager.get_intraday_config()
        assert config['enabled'] is True
        assert config['monitoring_interval_minutes'] == 120
        assert config['monitored_regions'] == ['hong_kong']
    
    def test_config_preserves_holidays_on_update(self, config_manager, temp_config_file):
        """Test that updating config preserves existing holiday configuration."""
        # Create initial config with holidays
        config_data = {
            'intraday_monitoring': {
                'enabled': False,
                'monitoring_interval_minutes': 60,
                'monitored_regions': [],
                'market_holidays': {
                    'china': ['2024-01-01', '2024-02-10']
                }
            }
        }
        
        with open(temp_config_file, 'w') as f:
            yaml.dump(config_data, f)
        
        # Update configuration
        config_manager.set_intraday_config(
            enabled=True,
            interval_minutes=30,
            regions=[MarketRegion.CHINA]
        )
        
        # Verify holidays are preserved
        holidays = config_manager.get_market_holidays(MarketRegion.CHINA)
        assert holidays == ['2024-01-01', '2024-02-10']
