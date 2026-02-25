"""
Analysis Engine component for the stock market analysis system.

Analyzes market data and generates stock recommendations with rationale and risk assessment.
"""

import logging
import time
from datetime import datetime
from decimal import Decimal
from typing import List, Optional, Callable

from ..models import (
    MarketData,
    MarketDataCollection,
    StockRecommendation,
    RecommendationType,
    MarketRegion,
    AnalysisResult
)


class AnalysisEngine:
    """
    Analyzes market data and generates stock recommendations.
    
    Responsibilities:
    - Analyze market data
    - Generate stock recommendations
    - Classify recommendations (buy/sell/hold)
    - Include rationale and risk assessment
    - Handle insufficient data scenarios
    """
    
    def __init__(self, market_monitor=None, admin_notifier: Optional[Callable[[str], None]] = None):
        """
        Initialize the Analysis Engine.
        
        Args:
            market_monitor: Optional MarketMonitor instance for data collection
            admin_notifier: Optional callback function for administrator notifications
        """
        self.logger = logging.getLogger(__name__)
        self.market_monitor = market_monitor
        self.admin_notifier = admin_notifier
        
        # Retry configuration
        self.max_retries = 3
        self.retry_interval_seconds = 300  # 5 minutes
        
        # Minimum data requirements for analysis
        self.min_volume = 1000  # Minimum trading volume
        self.min_price = Decimal("0.01")  # Minimum price to consider
    
    def analyze_and_recommend(self, market_data: MarketDataCollection) -> List[StockRecommendation]:
        """
        Analyzes market data and generates recommendations.
        
        Args:
            market_data: Collection of market data from all regions
            
        Returns:
            List of stock recommendations with rationale and risk assessment
            
        Note:
            Stocks with insufficient data are excluded from results
        """
        self.logger.info("Starting market data analysis")
        recommendations = []
        
        for region, stocks in market_data.data_by_region.items():
            self.logger.debug(f"Analyzing {len(stocks)} stocks from {region.value}")
            
            for stock in stocks:
                # Filter out stocks with insufficient data
                if not self._has_sufficient_data(stock):
                    self.logger.debug(
                        f"Skipping {stock.symbol} due to insufficient data"
                    )
                    continue
                
                # Analyze the stock and generate recommendation
                recommendation = self._analyze_stock(stock)
                
                if recommendation:
                    recommendations.append(recommendation)
        
        self.logger.info(f"Analysis complete: generated {len(recommendations)} recommendations")
        return recommendations
    
    def _has_sufficient_data(self, stock: MarketData) -> bool:
        """
        Checks if stock has sufficient data for analysis.
        
        Args:
            stock: Market data for a stock
            
        Returns:
            True if stock has sufficient data, False otherwise
        """
        # Check for required fields
        if not stock.symbol or not stock.timestamp:
            return False
        
        # Check for valid prices
        if (stock.close_price < self.min_price or 
            stock.open_price < self.min_price or
            stock.high_price < self.min_price or
            stock.low_price < self.min_price):
            return False
        
        # Check for minimum volume
        if stock.volume < self.min_volume:
            return False
        
        # Check for price consistency
        if stock.high_price < stock.low_price:
            return False
        
        if (stock.close_price > stock.high_price or 
            stock.close_price < stock.low_price):
            return False
        
        if (stock.open_price > stock.high_price or 
            stock.open_price < stock.low_price):
            return False
        
        return True
    
    def _analyze_stock(self, stock: MarketData) -> Optional[StockRecommendation]:
        """
        Analyzes a single stock and generates a recommendation.
        
        Args:
            stock: Market data for the stock
            
        Returns:
            StockRecommendation if analysis produces a recommendation, None otherwise
        """
        # Calculate price change
        price_change = stock.close_price - stock.open_price
        price_change_pct = (price_change / stock.open_price) * 100
        
        # Calculate volatility (high-low range as percentage of close)
        volatility = ((stock.high_price - stock.low_price) / stock.close_price) * 100
        
        # Determine recommendation type based on analysis
        recommendation_type, confidence = self._determine_recommendation(
            price_change_pct, volatility, stock
        )
        
        # Generate rationale
        rationale = self._generate_rationale(
            stock, price_change_pct, volatility, recommendation_type
        )
        
        # Generate risk assessment
        risk_assessment = self._generate_risk_assessment(volatility, stock)
        
        # Calculate target price (simple projection based on trend)
        target_price = self._calculate_target_price(stock, recommendation_type)
        
        return StockRecommendation(
            symbol=stock.symbol,
            region=stock.region,
            recommendation_type=recommendation_type,
            rationale=rationale,
            risk_assessment=risk_assessment,
            confidence_score=confidence,
            target_price=target_price,
            generated_at=datetime.now()
        )
    
    def _determine_recommendation(
        self, 
        price_change_pct: Decimal, 
        volatility: Decimal,
        stock: MarketData
    ) -> tuple[RecommendationType, float]:
        """
        Determines recommendation type and confidence based on analysis.
        
        Args:
            price_change_pct: Percentage price change
            volatility: Volatility measure
            stock: Market data
            
        Returns:
            Tuple of (recommendation_type, confidence_score)
        """
        # Simple momentum-based strategy
        # In a real system, this would use sophisticated technical and fundamental analysis
        
        # Strong upward momentum
        if price_change_pct > 3:
            if volatility < 5:
                return RecommendationType.BUY, 0.85
            else:
                return RecommendationType.BUY, 0.70
        
        # Moderate upward momentum
        elif price_change_pct > 1:
            if volatility < 5:
                return RecommendationType.BUY, 0.70
            else:
                return RecommendationType.HOLD, 0.65
        
        # Strong downward momentum
        elif price_change_pct < -3:
            if volatility < 5:
                return RecommendationType.SELL, 0.80
            else:
                return RecommendationType.SELL, 0.75
        
        # Moderate downward momentum
        elif price_change_pct < -1:
            if volatility < 5:
                return RecommendationType.SELL, 0.65
            else:
                return RecommendationType.HOLD, 0.60
        
        # Neutral - hold position
        else:
            return RecommendationType.HOLD, 0.60
    
    def _generate_rationale(
        self,
        stock: MarketData,
        price_change_pct: Decimal,
        volatility: Decimal,
        recommendation_type: RecommendationType
    ) -> str:
        """
        Generates human-readable rationale for the recommendation.
        
        Args:
            stock: Market data
            price_change_pct: Percentage price change
            volatility: Volatility measure
            recommendation_type: Type of recommendation
            
        Returns:
            Rationale string
        """
        direction = "up" if price_change_pct > 0 else "down"
        abs_change = abs(float(price_change_pct))
        
        rationale_parts = []
        
        # Price movement analysis
        if abs_change > 3:
            rationale_parts.append(
                f"Strong {direction}ward momentum with {abs_change:.2f}% price movement"
            )
        elif abs_change > 1:
            rationale_parts.append(
                f"Moderate {direction}ward trend with {abs_change:.2f}% price change"
            )
        else:
            rationale_parts.append(
                f"Stable price action with minimal {abs_change:.2f}% change"
            )
        
        # Volatility analysis
        vol_float = float(volatility)
        if vol_float > 10:
            rationale_parts.append("high intraday volatility indicates uncertainty")
        elif vol_float > 5:
            rationale_parts.append("moderate volatility suggests active trading")
        else:
            rationale_parts.append("low volatility indicates stable trading")
        
        # Volume analysis
        if stock.volume > 1000000:
            rationale_parts.append("strong volume confirms trend")
        elif stock.volume > 100000:
            rationale_parts.append("adequate volume supports movement")
        else:
            rationale_parts.append("limited volume suggests caution")
        
        return "; ".join(rationale_parts) + "."
    
    def _generate_risk_assessment(self, volatility: Decimal, stock: MarketData) -> str:
        """
        Generates risk assessment for the recommendation.
        
        Args:
            volatility: Volatility measure
            stock: Market data
            
        Returns:
            Risk assessment string
        """
        vol_float = float(volatility)
        
        # Determine risk level
        if vol_float > 10:
            risk_level = "High"
            risk_factors = [
                "significant price volatility",
                "potential for rapid price swings"
            ]
        elif vol_float > 5:
            risk_level = "Medium"
            risk_factors = [
                "moderate price volatility",
                "normal market fluctuations expected"
            ]
        else:
            risk_level = "Low"
            risk_factors = [
                "stable price action",
                "limited downside risk in current conditions"
            ]
        
        # Add volume-based risk factors
        if stock.volume < 10000:
            risk_factors.append("low liquidity may impact execution")
        
        return f"{risk_level} risk: {', '.join(risk_factors)}."
    
    def _calculate_target_price(
        self, 
        stock: MarketData, 
        recommendation_type: RecommendationType
    ) -> Optional[Decimal]:
        """
        Calculates target price based on recommendation.
        
        Args:
            stock: Market data
            recommendation_type: Type of recommendation
            
        Returns:
            Target price or None for HOLD recommendations
        """
        if recommendation_type == RecommendationType.HOLD:
            return None
        
        # Simple target price calculation
        # In a real system, this would use sophisticated valuation models
        
        if recommendation_type == RecommendationType.BUY:
            # Target 10% above current price for buy recommendations
            return stock.close_price * Decimal("1.10")
        else:  # SELL
            # Target 10% below current price for sell recommendations
            return stock.close_price * Decimal("0.90")

    def execute_scheduled_analysis(self, regions: Optional[List[MarketRegion]] = None) -> AnalysisResult:
        """
        Executes the full analysis pipeline with retry logic.
        
        Args:
            regions: Optional list of market regions to analyze. If None and market_monitor
                    is configured, uses regions from configuration.
        
        Returns:
            AnalysisResult containing recommendations or error information
            
        Implements 3 retry attempts with 5-minute intervals on failure.
        Notifies administrators when all retry attempts fail.
        """
        retry_count = 0
        last_error = None
        
        while retry_count < self.max_retries:
            try:
                self.logger.info(f"Starting scheduled analysis (attempt {retry_count + 1}/{self.max_retries})")
                
                # Collect market data
                if self.market_monitor is None:
                    raise ValueError("Market monitor not configured for scheduled analysis")
                
                if regions is None:
                    # Get regions from configuration if available
                    if hasattr(self.market_monitor, 'config_manager'):
                        regions = self.market_monitor.config_manager.get_configured_regions()
                    else:
                        raise ValueError("No regions specified and no configuration available")
                
                market_data = self.market_monitor.collect_market_data(regions)
                
                # Perform analysis
                recommendations = self.analyze_and_recommend(market_data)
                
                self.logger.info(
                    f"Scheduled analysis completed successfully: "
                    f"{len(recommendations)} recommendations generated"
                )
                
                return AnalysisResult(
                    success=True,
                    recommendations=recommendations,
                    error_message=None,
                    retry_count=retry_count
                )
                
            except Exception as e:
                retry_count += 1
                last_error = str(e)
                
                self.logger.warning(
                    f"Analysis attempt {retry_count} failed: {last_error}",
                    exc_info=True
                )
                
                # If not the last attempt, wait before retrying
                if retry_count < self.max_retries:
                    self.logger.info(
                        f"Waiting {self.retry_interval_seconds} seconds before retry..."
                    )
                    time.sleep(self.retry_interval_seconds)
        
        # All retries exhausted
        error_message = f"Analysis failed after {self.max_retries} retry attempts. Last error: {last_error}"
        
        self.logger.error(error_message)
        
        # Notify administrators of persistent failure
        self._notify_administrators(error_message)
        
        return AnalysisResult(
            success=False,
            recommendations=[],
            error_message=error_message,
            retry_count=retry_count
        )
    
    def _notify_administrators(self, message: str) -> None:
        """
        Notifies administrators of critical failures.
        
        Args:
            message: Error message to send to administrators
        """
        try:
            if self.admin_notifier:
                self.logger.info("Sending administrator notification")
                self.admin_notifier(message)
            else:
                self.logger.warning(
                    "Administrator notification requested but no notifier configured. "
                    f"Message: {message}"
                )
        except Exception as e:
            self.logger.error(
                f"Failed to send administrator notification: {e}",
                exc_info=True
            )
