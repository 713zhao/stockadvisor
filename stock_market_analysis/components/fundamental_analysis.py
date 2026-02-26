"""Fundamental analysis for stock evaluation."""
import logging
from typing import Dict, Any, Optional
from decimal import Decimal


class FundamentalAnalysis:
    """Analyze fundamental metrics like P/E ratio, earnings, revenue growth."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def analyze_fundamentals(self, stock_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze fundamental metrics and generate signals.
        
        Args:
            stock_data: Dict containing fundamental metrics
            
        Returns:
            Dict with fundamental analysis results
        """
        signals = {
            'pe_signal': 'neutral',
            'earnings_signal': 'neutral',
            'revenue_signal': 'neutral',
            'fundamental_score': 0,
            'valuation': 'fair'
        }
        
        # P/E Ratio Analysis
        pe_ratio = stock_data.get('pe_ratio', 0)
        if pe_ratio > 0:
            if pe_ratio < 15:
                signals['pe_signal'] = 'undervalued'
                signals['fundamental_score'] += 2
                signals['valuation'] = 'undervalued'
            elif pe_ratio < 25:
                signals['pe_signal'] = 'fair'
                signals['fundamental_score'] += 1
            elif pe_ratio > 40:
                signals['pe_signal'] = 'overvalued'
                signals['fundamental_score'] -= 2
                signals['valuation'] = 'overvalued'
            elif pe_ratio > 30:
                signals['pe_signal'] = 'expensive'
                signals['fundamental_score'] -= 1
        
        # Earnings Growth Analysis
        earnings_growth = stock_data.get('earnings_growth', 0)
        if earnings_growth > 20:
            signals['earnings_signal'] = 'strong_growth'
            signals['fundamental_score'] += 2
        elif earnings_growth > 10:
            signals['earnings_signal'] = 'moderate_growth'
            signals['fundamental_score'] += 1
        elif earnings_growth < -10:
            signals['earnings_signal'] = 'declining'
            signals['fundamental_score'] -= 2
        elif earnings_growth < 0:
            signals['earnings_signal'] = 'weak'
            signals['fundamental_score'] -= 1
        
        # Revenue Growth Analysis
        revenue_growth = stock_data.get('revenue_growth', 0)
        if revenue_growth > 15:
            signals['revenue_signal'] = 'strong_growth'
            signals['fundamental_score'] += 1.5
        elif revenue_growth > 5:
            signals['revenue_signal'] = 'moderate_growth'
            signals['fundamental_score'] += 0.5
        elif revenue_growth < -5:
            signals['revenue_signal'] = 'declining'
            signals['fundamental_score'] -= 1.5
        
        # Debt-to-Equity Analysis
        debt_to_equity = stock_data.get('debt_to_equity', 0)
        if debt_to_equity < 0.5:
            signals['debt_signal'] = 'low_debt'
            signals['fundamental_score'] += 0.5
        elif debt_to_equity > 2.0:
            signals['debt_signal'] = 'high_debt'
            signals['fundamental_score'] -= 1
        
        return signals
    
    def generate_fundamental_rationale(self, signals: Dict[str, Any], 
                                      stock_data: Dict[str, Any]) -> str:
        """Generate human-readable fundamental analysis rationale."""
        parts = []
        
        # P/E Ratio
        pe_ratio = stock_data.get('pe_ratio', 0)
        if pe_ratio > 0:
            if signals['pe_signal'] == 'undervalued':
                parts.append(f"P/E ratio of {pe_ratio:.1f} suggests undervaluation")
            elif signals['pe_signal'] == 'overvalued':
                parts.append(f"P/E ratio of {pe_ratio:.1f} indicates overvaluation")
            elif pe_ratio > 0:
                parts.append(f"P/E ratio at {pe_ratio:.1f}")
        
        # Earnings Growth
        earnings_growth = stock_data.get('earnings_growth', 0)
        if abs(earnings_growth) > 5:
            direction = "growth" if earnings_growth > 0 else "decline"
            parts.append(f"earnings {direction} of {abs(earnings_growth):.1f}%")
        
        # Revenue Growth
        revenue_growth = stock_data.get('revenue_growth', 0)
        if abs(revenue_growth) > 5:
            direction = "growth" if revenue_growth > 0 else "decline"
            parts.append(f"revenue {direction} of {abs(revenue_growth):.1f}%")
        
        return "; ".join(parts) if parts else "limited fundamental data available"
