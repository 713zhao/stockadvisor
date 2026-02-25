"""
Integration tests for the complete Stock Market Analysis system.

Tests the full system integration including all components wired together.
"""

import pytest
from pathlib import Path
from stock_market_analysis.main import StockMarketAnalysisSystem


def test_system_initialization():
    """Test that the system can initialize all components successfully."""
    system = StockMarketAnalysisSystem(config_path=Path("config/default.yaml"))
    
    # Initialize the system
    success = system.initialize()
    
    assert success is True
    assert system._initialized is True
    assert system.config_manager is not None
    assert system.market_monitor is not None
    assert system.analysis_engine is not None
    assert system.report_generator is not None
    assert system.notification_service is not None
    assert system.scheduler is not None


def test_system_run_once():
    """Test that the system can run the analysis pipeline once."""
    system = StockMarketAnalysisSystem(config_path=Path("config/default.yaml"))
    
    # Initialize and run
    system.initialize()
    success = system.run_once()
    
    # Should succeed even without notification channels configured
    # (graceful degradation)
    assert success is True


def test_system_pipeline_execution():
    """Test the complete analysis pipeline execution."""
    system = StockMarketAnalysisSystem(config_path=Path("config/default.yaml"))
    system.initialize()
    
    # Execute the pipeline
    result = system.run_analysis_pipeline()
    
    # Verify result
    assert result.success is True
    assert result.recommendations is not None
    assert isinstance(result.recommendations, list)
    assert result.error_message is None
    assert result.retry_count == 0


def test_system_with_custom_regions():
    """Test system with custom market regions."""
    system = StockMarketAnalysisSystem(config_path=Path("config/default.yaml"))
    system.initialize()
    
    # Get configured regions
    regions = system.config_manager.get_configured_regions()
    
    # Should have default regions
    assert len(regions) == 3
    region_values = [r.value for r in regions]
    assert 'china' in region_values
    assert 'hong_kong' in region_values
    assert 'usa' in region_values


def test_system_graceful_shutdown():
    """Test that the system can shutdown gracefully."""
    system = StockMarketAnalysisSystem(config_path=Path("config/default.yaml"))
    system.initialize()
    system._running = True
    
    # Shutdown should not raise exceptions
    system.shutdown()
    
    assert system._running is False
