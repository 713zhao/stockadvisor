"""
Analysis Engine component for the stock market analysis system.

Analyzes market data and generates stock recommendations with rationale and risk assessment.
Uses technical indicators, fundamental analysis, volume analysis, sentiment analysis, and pattern recognition.
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
from .technical_indicators import TechnicalIndicators
from .fundamental_analysis import FundamentalAnalysis
from .volume_analysis import VolumeAnalysis
from .sentiment_analysis import SentimentAnalysis
from .pattern_recognition import PatternRecognition


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
        
        # Initialize analysis modules
        self.technical_indicators = TechnicalIndicators()
        self.fundamental_analysis = FundamentalAnalysis()
        self.volume_analysis = VolumeAnalysis()
        self.sentiment_analysis = SentimentAnalysis()
        self.pattern_recognition = PatternRecognition()
        
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
            name=stock.name,
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
        Determines recommendation type and confidence based on comprehensive analysis.
        
        Uses multiple analysis types:
        - Technical Analysis: RSI, MACD, momentum, volatility
        - Fundamental Analysis: P/E ratio, earnings growth, revenue growth
        - Volume Analysis: Trading volume trends and patterns
        - Sentiment Analysis: Market sentiment from news and social media
        - Pattern Recognition: Support/resistance levels, chart patterns
        
        Args:
            price_change_pct: Percentage price change
            volatility: Volatility measure
            stock: Market data
            
        Returns:
            Tuple of (recommendation_type, confidence_score)
        """
        # Get technical indicators from stock data
        rsi = stock.additional_metrics.get('rsi', 50)
        macd = stock.additional_metrics.get('macd', 0)
        
        # Initialize scoring system
        buy_score = 0
        sell_score = 0
        confidence_factors = []
        
        # 1. TECHNICAL ANALYSIS (Weight: 35%)
        # RSI Analysis
        if rsi < 30:
            buy_score += 3
            confidence_factors.append("RSI oversold")
        elif rsi < 40:
            buy_score += 2
            confidence_factors.append("RSI weak")
        elif rsi > 70:
            sell_score += 3
            confidence_factors.append("RSI overbought")
        elif rsi > 60:
            sell_score += 2
            confidence_factors.append("RSI strong")
        
        # MACD Analysis
        if macd > 1:
            buy_score += 2.5
            confidence_factors.append("MACD bullish")
        elif macd > 0:
            buy_score += 1.5
        elif macd < -1:
            sell_score += 2.5
            confidence_factors.append("MACD bearish")
        elif macd < 0:
            sell_score += 1.5
        
        # Price Momentum
        price_change_float = float(price_change_pct)
        if price_change_float > 3:
            buy_score += 2.5
        elif price_change_float > 1:
            buy_score += 1.5
        elif price_change_float < -3:
            sell_score += 2.5
        elif price_change_float < -1:
            sell_score += 1.5
        
        # 2. FUNDAMENTAL ANALYSIS (Weight: 25%)
        fundamental_signals = self.fundamental_analysis.analyze_fundamentals(stock.additional_metrics)
        fundamental_score = fundamental_signals['fundamental_score']
        if fundamental_score > 0:
            buy_score += fundamental_score * 0.8
            if fundamental_signals['valuation'] == 'undervalued':
                confidence_factors.append("undervalued")
        elif fundamental_score < 0:
            sell_score += abs(fundamental_score) * 0.8
            if fundamental_signals['valuation'] == 'overvalued':
                confidence_factors.append("overvalued")
        
        # 3. VOLUME ANALYSIS (Weight: 15%)
        volume_signals = self.volume_analysis.analyze_volume(
            stock.volume,
            stock.additional_metrics.get('volume_history', []),
            price_change_float
        )
        volume_score = volume_signals['volume_score']
        if volume_score > 0:
            buy_score += volume_score * 0.6
            sell_score += volume_score * 0.6
            if volume_signals.get('accumulation'):
                confidence_factors.append("accumulation")
        elif volume_score < 0:
            buy_score += volume_score * 0.3
            sell_score += volume_score * 0.3
        
        # 4. SENTIMENT ANALYSIS (Weight: 15%)
        sentiment_signals = self.sentiment_analysis.analyze_sentiment(stock.symbol)
        sentiment_score = sentiment_signals['sentiment_score']
        if sentiment_score > 0:
            buy_score += sentiment_score * 0.6
            if sentiment_signals['sentiment_signal'] in ['positive', 'very_positive']:
                confidence_factors.append("positive sentiment")
        elif sentiment_score < 0:
            sell_score += abs(sentiment_score) * 0.6
            if sentiment_signals['sentiment_signal'] in ['negative', 'very_negative']:
                confidence_factors.append("negative sentiment")
        
        # 5. PATTERN RECOGNITION (Weight: 10%)
        pattern_signals = self.pattern_recognition.analyze_patterns(
            stock.close_price,
            stock.high_price,
            stock.low_price,
            stock.additional_metrics.get('price_history', [])
        )
        pattern_score = pattern_signals['pattern_score']
        if pattern_score > 0:
            buy_score += pattern_score * 0.4
            if pattern_signals.get('breakout'):
                confidence_factors.append("breakout")
        elif pattern_score < 0:
            sell_score += abs(pattern_score) * 0.4
        
        # Volatility Adjustment
        vol_float = float(volatility)
        if vol_float < 3:
            buy_score += 0.5
            sell_score += 0.5
        elif vol_float > 10:
            buy_score -= 0.5
            sell_score -= 0.5
        
        # Determine recommendation based on scores
        score_diff = buy_score - sell_score
        
        if score_diff >= 4:
            confidence = min(0.95, 0.75 + (score_diff - 4) * 0.04)
            return RecommendationType.BUY, confidence
        elif score_diff >= 2:
            confidence = min(0.85, 0.70 + (score_diff - 2) * 0.05)
            return RecommendationType.BUY, confidence
        elif score_diff <= -4:
            confidence = min(0.95, 0.75 + (abs(score_diff) - 4) * 0.04)
            return RecommendationType.SELL, confidence
        elif score_diff <= -2:
            confidence = min(0.85, 0.70 + (abs(score_diff) - 2) * 0.05)
            return RecommendationType.SELL, confidence
        else:
            confidence = 0.60
            return RecommendationType.HOLD, confidence
    
    def _generate_rationale(
        self,
        stock: MarketData,
        price_change_pct: Decimal,
        volatility: Decimal,
        recommendation_type: RecommendationType
    ) -> str:
        """
        Generates comprehensive human-readable rationale for the recommendation.
        
        Combines insights from:
        - Technical Analysis (RSI, MACD, price momentum)
        - Fundamental Analysis (P/E, earnings, revenue)
        - Volume Analysis (trading patterns)
        - Sentiment Analysis (market sentiment)
        - Pattern Recognition (support/resistance, chart patterns)
        
        Args:
            stock: Market data
            price_change_pct: Percentage price change
            volatility: Volatility measure
            recommendation_type: Type of recommendation
            
        Returns:
            Comprehensive rationale string
        """
        rationale_parts = []
        
        # 1. TECHNICAL ANALYSIS
        rsi = stock.additional_metrics.get('rsi', 50)
        macd = stock.additional_metrics.get('macd', 0)
        
        # RSI Analysis
        if rsi < 30:
            rationale_parts.append(f"RSI at {rsi:.1f} indicates oversold conditions")
        elif rsi > 70:
            rationale_parts.append(f"RSI at {rsi:.1f} indicates overbought conditions")
        elif rsi < 45:
            rationale_parts.append(f"RSI at {rsi:.1f} shows potential upside")
        elif rsi > 55:
            rationale_parts.append(f"RSI at {rsi:.1f} suggests caution")
        
        # MACD Analysis
        if abs(macd) > 0.5:
            macd_trend = "bullish" if macd > 0 else "bearish"
            rationale_parts.append(f"MACD shows {macd_trend} momentum")
        
        # Price movement
        direction = "up" if price_change_pct > 0 else "down"
        abs_change = abs(float(price_change_pct))
        if abs_change > 3:
            rationale_parts.append(f"strong {direction}ward price movement of {abs_change:.2f}%")
        elif abs_change > 1:
            rationale_parts.append(f"moderate {direction}ward trend with {abs_change:.2f}% change")
        
        # 2. FUNDAMENTAL ANALYSIS
        fundamental_signals = self.fundamental_analysis.analyze_fundamentals(stock.additional_metrics)
        fundamental_rationale = self.fundamental_analysis.generate_fundamental_rationale(
            fundamental_signals, stock.additional_metrics
        )
        if fundamental_rationale and "limited fundamental data" not in fundamental_rationale:
            rationale_parts.append(fundamental_rationale)
        
        # 3. VOLUME ANALYSIS
        volume_signals = self.volume_analysis.analyze_volume(
            stock.volume,
            stock.additional_metrics.get('volume_history', []),
            float(price_change_pct)
        )
        volume_rationale = self.volume_analysis.generate_volume_rationale(
            volume_signals, stock.volume
        )
        if volume_rationale:
            rationale_parts.append(volume_rationale)
        
        # 4. SENTIMENT ANALYSIS
        sentiment_signals = self.sentiment_analysis.analyze_sentiment(stock.symbol)
        sentiment_rationale = self.sentiment_analysis.generate_sentiment_rationale(sentiment_signals)
        if sentiment_rationale and "neutral market sentiment" not in sentiment_rationale:
            rationale_parts.append(sentiment_rationale)
        
        # 5. PATTERN RECOGNITION
        pattern_signals = self.pattern_recognition.analyze_patterns(
            stock.close_price,
            stock.high_price,
            stock.low_price,
            stock.additional_metrics.get('price_history', [])
        )
        pattern_rationale = self.pattern_recognition.generate_pattern_rationale(pattern_signals)
        if pattern_rationale and "no significant patterns" not in pattern_rationale:
            rationale_parts.append(pattern_rationale)
        
        # Volatility context
        vol_float = float(volatility)
        if vol_float > 10:
            rationale_parts.append("high volatility suggests uncertainty")
        elif vol_float < 3:
            rationale_parts.append("low volatility indicates stability")
        
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
