"""
Shared state module for cross-component access.

This module provides a way to share the main system instance
between the analysis system and the web dashboard.
"""

from typing import Optional

# Global reference to the main system instance
_system_instance: Optional['StockMarketAnalysisSystem'] = None


def set_system_instance(system: 'StockMarketAnalysisSystem') -> None:
    """
    Set the global system instance.
    
    Args:
        system: The StockMarketAnalysisSystem instance
    """
    global _system_instance
    _system_instance = system
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"SharedState: set_system_instance() called with system={system}, intraday_monitor={system.intraday_monitor if system else None}")


def get_system_instance() -> Optional['StockMarketAnalysisSystem']:
    """
    Get the global system instance.
    
    Returns:
        The StockMarketAnalysisSystem instance or None if not set
    """
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"SharedState: get_system_instance() called, returning {_system_instance}")
    return _system_instance
