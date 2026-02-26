"""Volume analysis for trading activity patterns."""
import logging
from typing import Dict, Any, List


class VolumeAnalysis:
    """Analyze trading volume trends and patterns."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def analyze_volume(self, current_volume: int, volume_history: List[int] = None,
                      price_change: float = 0) -> Dict[str, Any]:
        """
        Analyze volume trends and generate signals.
        
        Args:
            current_volume: Current trading volume
            volume_history: Historical volume data (optional)
            price_change: Price change percentage
            
        Returns:
            Dict with volume analysis results
        """
        signals = {
            'volume_signal': 'neutral',
            'volume_trend': 'stable',
            'volume_score': 0,
            'accumulation': False
        }
        
        # Calculate average volume if history available
        if volume_history and len(volume_history) > 0:
            avg_volume = sum(volume_history) / len(volume_history)
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
            
            # Volume Surge Analysis
            if volume_ratio > 2.0:
                signals['volume_signal'] = 'surge'
                signals['volume_score'] += 2
                signals['volume_trend'] = 'increasing'
            elif volume_ratio > 1.5:
                signals['volume_signal'] = 'high'
                signals['volume_score'] += 1
                signals['volume_trend'] = 'increasing'
            elif volume_ratio < 0.5:
                signals['volume_signal'] = 'low'
                signals['volume_score'] -= 1
                signals['volume_trend'] = 'decreasing'
        else:
            # Absolute volume analysis
            if current_volume > 50000000:
                signals['volume_signal'] = 'very_high'
                signals['volume_score'] += 2
            elif current_volume > 10000000:
                signals['volume_signal'] = 'high'
                signals['volume_score'] += 1
            elif current_volume < 1000000:
                signals['volume_signal'] = 'low'
                signals['volume_score'] -= 1
        
        # Price-Volume Relationship
        if price_change > 2 and signals['volume_score'] > 0:
            signals['accumulation'] = True
            signals['volume_score'] += 0.5
        elif price_change < -2 and signals['volume_score'] > 0:
            signals['distribution'] = True
            signals['volume_score'] -= 0.5
        
        return signals
    
    def generate_volume_rationale(self, signals: Dict[str, Any], 
                                 current_volume: int) -> str:
        """Generate human-readable volume analysis rationale."""
        parts = []
        
        if signals['volume_signal'] == 'surge':
            parts.append("volume surge indicates strong interest")
        elif signals['volume_signal'] == 'very_high' or signals['volume_signal'] == 'high':
            parts.append("high volume confirms trend strength")
        elif signals['volume_signal'] == 'low':
            parts.append("low volume suggests weak conviction")
        
        if signals.get('accumulation'):
            parts.append("price-volume pattern shows accumulation")
        elif signals.get('distribution'):
            parts.append("price-volume pattern shows distribution")
        
        if signals['volume_trend'] == 'increasing':
            parts.append("volume trending higher")
        elif signals['volume_trend'] == 'decreasing':
            parts.append("volume declining")
        
        return "; ".join(parts) if parts else f"volume at {current_volume:,} shares"
