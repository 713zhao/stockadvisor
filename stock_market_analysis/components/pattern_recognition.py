"""Pattern recognition for support/resistance and chart patterns."""
import logging
from typing import Dict, Any, List, Optional
from decimal import Decimal


class PatternRecognition:
    """Identify support/resistance levels and chart patterns."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def analyze_patterns(self, current_price: Decimal, high: Decimal, low: Decimal,
                        price_history: List[Decimal] = None) -> Dict[str, Any]:
        """
        Analyze price patterns and support/resistance levels.
        
        Args:
            current_price: Current stock price
            high: Day's high price
            low: Day's low price
            price_history: Historical prices (optional)
            
        Returns:
            Dict with pattern analysis results
        """
        signals = {
            'pattern_signal': 'neutral',
            'pattern_score': 0,
            'support_level': None,
            'resistance_level': None,
            'pattern_type': None,
            'breakout': False
        }
        
        # Calculate support and resistance levels
        if price_history and len(price_history) >= 5:
            prices = [float(p) for p in price_history]
            support = min(prices[-10:]) if len(prices) >= 10 else min(prices)
            resistance = max(prices[-10:]) if len(prices) >= 10 else max(prices)
            
            signals['support_level'] = Decimal(str(support))
            signals['resistance_level'] = Decimal(str(resistance))
            
            current = float(current_price)
            
            # Breakout Detection
            if current > resistance * 1.02:
                signals['breakout'] = True
                signals['pattern_signal'] = 'breakout_up'
                signals['pattern_score'] += 2
                signals['pattern_type'] = 'resistance_breakout'
            elif current < support * 0.98:
                signals['breakout'] = True
                signals['pattern_signal'] = 'breakdown'
                signals['pattern_score'] -= 2
                signals['pattern_type'] = 'support_breakdown'
            
            # Near Support/Resistance
            elif abs(current - support) / support < 0.02:
                signals['pattern_signal'] = 'near_support'
                signals['pattern_score'] += 1
                signals['pattern_type'] = 'bouncing_support'
            elif abs(current - resistance) / resistance < 0.02:
                signals['pattern_signal'] = 'near_resistance'
                signals['pattern_score'] -= 1
                signals['pattern_type'] = 'testing_resistance'
        
        # Simple pattern detection based on price action
        price_range = float(high - low)
        body_size = abs(float(current_price - low))
        
        if price_range > 0:
            body_ratio = body_size / price_range
            
            # Hammer pattern (potential reversal)
            if body_ratio > 0.7 and float(current_price) > float(low) * 1.02:
                signals['pattern_type'] = 'hammer'
                signals['pattern_score'] += 0.5
            
            # Shooting star (potential reversal)
            elif body_ratio < 0.3 and float(current_price) < float(high) * 0.98:
                signals['pattern_type'] = 'shooting_star'
                signals['pattern_score'] -= 0.5
        
        return signals
    
    def generate_pattern_rationale(self, signals: Dict[str, Any]) -> str:
        """Generate human-readable pattern analysis rationale."""
        parts = []
        
        if signals.get('breakout'):
            if signals['pattern_signal'] == 'breakout_up':
                parts.append("breakout above resistance level")
            elif signals['pattern_signal'] == 'breakdown':
                parts.append("breakdown below support level")
        
        if signals['pattern_type'] == 'bouncing_support':
            parts.append("price bouncing off support")
        elif signals['pattern_type'] == 'testing_resistance':
            parts.append("testing resistance level")
        elif signals['pattern_type'] == 'hammer':
            parts.append("hammer pattern suggests potential reversal")
        elif signals['pattern_type'] == 'shooting_star':
            parts.append("shooting star pattern indicates weakness")
        
        if signals.get('support_level') and signals.get('resistance_level'):
            support = signals['support_level']
            resistance = signals['resistance_level']
            parts.append(f"trading range ${support:.2f}-${resistance:.2f}")
        
        return "; ".join(parts) if parts else "no significant patterns detected"
