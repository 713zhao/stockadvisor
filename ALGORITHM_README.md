# Stock Analysis Algorithm

## Overview

The system uses a **comprehensive multi-factor analysis algorithm** that combines five types of analysis to generate BUY/SELL/HOLD recommendations with confidence scores:

1. **Technical Analysis** (35% weight) - RSI, MACD, price momentum, volatility
2. **Fundamental Analysis** (25% weight) - P/E ratio, earnings growth, revenue growth, debt levels
3. **Volume Analysis** (15% weight) - Trading volume trends and price-volume relationships
4. **Sentiment Analysis** (15% weight) - Market sentiment from news and social media
5. **Pattern Recognition** (10% weight) - Support/resistance levels, breakouts, chart patterns

This multi-dimensional approach provides more reliable and well-rounded investment recommendations.

## Analysis Components

### 1. Technical Analysis (Weight: 35%)

Uses traditional technical indicators to identify trading opportunities.

#### RSI (Relative Strength Index)

**Formula**: `RSI = 100 - (100 / (1 + RS))` where `RS = Average Gain / Average Loss`

**Interpretation**:
- **RSI < 30**: Oversold condition → Strong BUY signal (+3 points)
- **RSI 30-40**: Weak → Moderate BUY signal (+2 points)
- **RSI 40-60**: Neutral → No signal
- **RSI 60-70**: Strong → Moderate SELL signal (+2 points)
- **RSI > 70**: Overbought condition → Strong SELL signal (+3 points)

**Why it matters**: RSI identifies when a stock is potentially oversold (good buying opportunity) or overbought (good selling opportunity).

#### MACD (Moving Average Convergence Divergence)

**Formula**: 
- `MACD = EMA(12) - EMA(26)`
- `Signal Line = EMA(MACD, 9)`
- `Histogram = MACD - Signal`

**Interpretation**:
- **MACD > 1**: Strong bullish momentum → BUY signal (+2.5 points)
- **MACD 0-1**: Positive momentum → Weak BUY signal (+1.5 points)
- **MACD -1-0**: Negative momentum → Weak SELL signal (+1.5 points)
- **MACD < -1**: Strong bearish momentum → SELL signal (+2.5 points)

**Why it matters**: MACD shows the relationship between two moving averages and helps identify trend changes.

#### Price Momentum

**Formula**: `Price Change % = ((Close - Open) / Open) * 100`

**Interpretation**:
- **Change > 3%**: Strong upward momentum → BUY signal (+2.5 points)
- **Change 1-3%**: Moderate upward momentum → Weak BUY signal (+1.5 points)
- **Change -1-1%**: Neutral → No signal
- **Change -3--1%**: Moderate downward momentum → Weak SELL signal (+1.5 points)
- **Change < -3%**: Strong downward momentum → SELL signal (+2.5 points)

**Why it matters**: Recent price movement indicates current market sentiment and trend direction.

#### Volatility

**Formula**: `Volatility = ((High - Low) / Close) * 100`

**Interpretation**:
- **Volatility < 3%**: Low volatility → Increases confidence (+0.5 points)
- **Volatility 3-10%**: Normal volatility → No adjustment
- **Volatility > 10%**: High volatility → Decreases confidence (-0.5 points)

**Why it matters**: Lower volatility means more predictable price movements and higher confidence in recommendations.

### 2. Fundamental Analysis (Weight: 25%)

Evaluates company financial health and valuation metrics.

#### P/E Ratio (Price-to-Earnings)

**Interpretation**:
- **P/E < 15**: Undervalued → BUY signal (+2 points)
- **P/E 15-25**: Fair valuation → Weak BUY signal (+1 point)
- **P/E 25-30**: Expensive → Weak SELL signal (-1 point)
- **P/E > 30**: Overvalued → SELL signal (-2 points)

**Why it matters**: P/E ratio indicates whether a stock is trading at a reasonable price relative to its earnings.

#### Earnings Growth

**Interpretation**:
- **Growth > 20%**: Strong growth → BUY signal (+2 points)
- **Growth 10-20%**: Moderate growth → Weak BUY signal (+1 point)
- **Growth 0-10%**: Neutral → No signal
- **Growth < -10%**: Declining → SELL signal (-2 points)

**Why it matters**: Growing earnings indicate a healthy, expanding business.

#### Revenue Growth

**Interpretation**:
- **Growth > 15%**: Strong growth → BUY signal (+1.5 points)
- **Growth 5-15%**: Moderate growth → Weak BUY signal (+0.5 points)
- **Growth < -5%**: Declining → SELL signal (-1.5 points)

**Why it matters**: Revenue growth shows the company is expanding its market share and customer base.

#### Debt-to-Equity Ratio

**Interpretation**:
- **Ratio < 0.5**: Low debt → Positive signal (+0.5 points)
- **Ratio 0.5-2.0**: Moderate debt → Neutral
- **Ratio > 2.0**: High debt → Negative signal (-1 point)

**Why it matters**: Lower debt means less financial risk and more stability.

### 3. Volume Analysis (Weight: 15%)

Analyzes trading volume patterns to confirm price movements.

#### Volume Trends

**Interpretation**:
- **Volume > 2x average**: Surge → Strong signal (+2 points)
- **Volume > 1.5x average**: High → Moderate signal (+1 point)
- **Volume < 0.5x average**: Low → Weak signal (-1 point)

**Why it matters**: High volume confirms that price movements are backed by real trading activity.

#### Price-Volume Relationship

**Interpretation**:
- **Price up + High volume**: Accumulation → BUY signal (+0.5 points)
- **Price down + High volume**: Distribution → SELL signal (-0.5 points)
- **Price move + Low volume**: Weak conviction → Reduces confidence

**Why it matters**: Volume should confirm price direction for reliable signals.

### 4. Sentiment Analysis (Weight: 15%)

Evaluates market sentiment from news and social media.

#### News Sentiment

**Interpretation**:
- **Sentiment > 0.3**: Very positive → BUY signal (+2 points)
- **Sentiment 0.1-0.3**: Positive → Weak BUY signal (+1 point)
- **Sentiment -0.1-0.1**: Neutral → No signal
- **Sentiment < -0.3**: Very negative → SELL signal (-2 points)

**Why it matters**: Positive news coverage can drive investor interest and price appreciation.

#### Social Media Sentiment

**Interpretation**:
- Combined with news sentiment (60% news, 40% social)
- Provides real-time market mood indicator

**Why it matters**: Social media can predict short-term price movements and identify trending stocks.

### 5. Pattern Recognition (Weight: 10%)

Identifies technical chart patterns and support/resistance levels.

#### Support and Resistance Levels

**Interpretation**:
- **Breakout above resistance**: Strong BUY signal (+2 points)
- **Near support level**: Potential bounce → BUY signal (+1 point)
- **Near resistance level**: Potential rejection → SELL signal (-1 point)
- **Breakdown below support**: Strong SELL signal (-2 points)

**Why it matters**: These levels represent psychological price points where buying/selling pressure changes.

#### Chart Patterns

**Patterns Detected**:
- **Hammer**: Potential bullish reversal (+0.5 points)
- **Shooting Star**: Potential bearish reversal (-0.5 points)
- **Breakout patterns**: Continuation signals

**Why it matters**: Chart patterns have historically predicted future price movements.

### Volume Confirmation (Legacy)

**Interpretation**:
- **Volume > 10M**: Strong volume → High confidence (+1 point)
- **Volume 1M-10M**: Good volume → Moderate confidence (+0.5 points)
- **Volume < 1M**: Low volume → Lower confidence

**Why it matters**: High volume confirms that price movements are supported by actual trading activity.

## Comprehensive Scoring System

The algorithm uses a **weighted point-based scoring system** that combines all five analysis types:

1. Calculate scores from each analysis component
2. Apply weights to each component (Technical 35%, Fundamental 25%, Volume 15%, Sentiment 15%, Pattern 10%)
3. Sum up BUY score and SELL score separately
4. Calculate score difference: `score_diff = buy_score - sell_score`

### Decision Rules:

| Score Difference | Recommendation | Base Confidence |
|-----------------|----------------|-----------------|
| ≥ 4.0 | **STRONG BUY** | 75-95% |
| 2.0-4.0 | **BUY** | 70-85% |
| -2.0 to 2.0 | **HOLD** | 60% |
| -4.0 to -2.0 | **SELL** | 70-85% |
| ≤ -4.0 | **STRONG SELL** | 75-95% |

### Confidence Calculation:

- Base confidence starts at 70-75%
- Additional confidence added based on score strength
- Maximum confidence capped at 95%
- Volatility and volume can adjust final confidence
- Multiple confirming signals increase confidence

## Example Comprehensive Analysis

### Example 1: Strong BUY Signal (All Factors Aligned)

```
Stock: AAPL

TECHNICAL ANALYSIS (35%):
  RSI: 28 (oversold) → +3 points
  MACD: 1.5 (bullish) → +2.5 points  
  Price Change: +4.2% → +2.5 points
  Volatility: 2.8% (low) → +0.5 points
  Subtotal: 8.5 points

FUNDAMENTAL ANALYSIS (25%):
  P/E Ratio: 18 (fair) → +1 point
  Earnings Growth: 22% → +2 points
  Revenue Growth: 18% → +1.5 points
  Debt-to-Equity: 0.4 → +0.5 points
  Subtotal: 5 points × 0.8 weight = 4 points

VOLUME ANALYSIS (15%):
  Volume: 2.5x average (surge) → +2 points
  Price-Volume: Accumulation → +0.5 points
  Subtotal: 2.5 points × 0.6 weight = 1.5 points

SENTIMENT ANALYSIS (15%):
  News Sentiment: +0.4 (positive) → +1 point
  Social Sentiment: +0.2 → Combined score
  Subtotal: 1 point × 0.6 weight = 0.6 points

PATTERN RECOGNITION (10%):
  Breakout above resistance → +2 points
  Subtotal: 2 points × 0.4 weight = 0.8 points

Total Buy Score: 15.4
Total Sell Score: 0
Score Diff: +15.4

Recommendation: STRONG BUY
Confidence: 95%
Rationale: "RSI at 28.0 indicates oversold conditions; MACD shows bullish momentum; 
strong upward price movement of 4.2%; P/E ratio of 18.0 suggests undervaluation; 
earnings growth of 22.0%; volume surge indicates strong interest; price-volume pattern 
shows accumulation; positive market sentiment; breakout above resistance level; 
low volatility indicates stability."
```

### Example 2: SELL Signal (Mixed Factors)

```
Stock: TSLA

TECHNICAL ANALYSIS (35%):
  RSI: 72 (overbought) → +3 points (sell)
  MACD: -0.8 (bearish) → +1.5 points (sell)
  Price Change: -2.1% → +1.5 points (sell)
  Volatility: 8.5% (moderate) → 0 points
  Subtotal: 6 points (sell)

FUNDAMENTAL ANALYSIS (25%):
  P/E Ratio: 45 (overvalued) → -2 points
  Earnings Growth: -5% → -1 point
  Revenue Growth: 8% → +0.5 points
  Debt-to-Equity: 0.6 → 0 points
  Subtotal: -2.5 points × 0.8 weight = -2 points

VOLUME ANALYSIS (15%):
  Volume: 1.8x average (high) → +1 point
  Price-Volume: Distribution → -0.5 points
  Subtotal: 0.5 points × 0.6 weight = 0.3 points

SENTIMENT ANALYSIS (15%):
  News Sentiment: -0.2 (negative) → -1 point
  Subtotal: -1 point × 0.6 weight = -0.6 points

PATTERN RECOGNITION (10%):
  Near resistance, rejection → -1 point
  Subtotal: -1 point × 0.4 weight = -0.4 points

Total Buy Score: 0.8
Total Sell Score: 9.0
Score Diff: -8.2

Recommendation: STRONG SELL
Confidence: 90%
Rationale: "RSI at 72.0 indicates overbought conditions; MACD shows bearish momentum;
moderate downward trend with 2.1% change; P/E ratio of 45.0 indicates overvaluation;
earnings decline of 5.0%; high volume; price-volume pattern shows distribution;
negative market sentiment; testing resistance level."
```

### Example 3: HOLD Signal (Conflicting Signals)

```
Stock: MSFT

TECHNICAL ANALYSIS (35%):
  RSI: 52 (neutral) → 0 points
  MACD: 0.2 (slightly positive) → +1.5 points (buy)
  Price Change: +0.5% → 0 points
  Volatility: 4.2% (low) → +0.5 points
  Subtotal: 2 points (buy)

FUNDAMENTAL ANALYSIS (25%):
  P/E Ratio: 28 (fair/expensive) → -1 point
  Earnings Growth: 12% → +1 point
  Revenue Growth: 7% → +0.5 points
  Subtotal: 0.5 points × 0.8 weight = 0.4 points

VOLUME ANALYSIS (15%):
  Volume: 0.9x average (normal) → 0 points
  Subtotal: 0 points

SENTIMENT ANALYSIS (15%):
  Neutral sentiment → 0 points
  Subtotal: 0 points

PATTERN RECOGNITION (10%):
  No significant patterns → 0 points
  Subtotal: 0 points

Total Buy Score: 2.4
Total Sell Score: 0
Score Diff: +2.4 (but < 4.0)

Recommendation: HOLD
Confidence: 60%
Rationale: "RSI at 52.0 shows potential upside; MACD shows bullish momentum;
P/E ratio at 28.0; earnings growth of 12.0%; volume at 5,000,000 shares;
low volatility indicates stability."
```

## Advantages of This Comprehensive Algorithm

1. **Multi-Dimensional Analysis**: Combines technical, fundamental, volume, sentiment, and pattern analysis
2. **Weighted Scoring**: More important factors (technical, fundamental) have higher weights
3. **Holistic View**: Considers both quantitative metrics and market psychology
4. **Confidence Levels**: Provides transparency about recommendation strength
5. **Adaptable**: Easy to adjust weights and thresholds based on backtesting results
6. **Explainable**: Clear rationale shows which factors influenced the decision
7. **Robust**: Less likely to give false signals when multiple factors must align

## Current Limitations

1. **Simulated Sentiment**: Currently uses simulated sentiment data; needs real API integration
2. **Historical Data**: Uses limited historical data; real system should use longer time series
3. **No Sector Context**: Doesn't account for overall market conditions or sector trends
4. **Simplified Patterns**: Pattern recognition could be enhanced with more sophisticated algorithms
5. **Static Weights**: Weights are fixed; could be optimized through machine learning

## Future Enhancements

1. **Real Sentiment APIs**: Integrate with news APIs (NewsAPI, Alpha Vantage) and social media (Twitter, Reddit)
2. **Extended Historical Data**: Use 200+ days of price history for better indicator calculations
3. **Machine Learning**: Train models on historical data to optimize weights and thresholds
4. **Sector Analysis**: Compare stock performance to sector averages and market indices
5. **Advanced Patterns**: Add more chart patterns (head & shoulders, triangles, flags)
6. **Backtesting Framework**: Test algorithm performance on historical data
7. **Risk Management**: Add position sizing, stop-loss, and portfolio allocation recommendations
8. **Real-time Updates**: Stream live market data for intraday analysis
9. **Options Analysis**: Include options flow and implied volatility
10. **Insider Trading**: Track insider buying/selling activity

## How to Customize

Edit `stock_market_analysis/components/analysis_engine.py` to adjust the algorithm:

### Adjust Component Weights

```python
# In _determine_recommendation() method

# Technical Analysis weight (currently 35%)
if fundamental_score > 0:
    buy_score += fundamental_score * 0.8  # Change 0.8 to adjust weight

# Volume Analysis weight (currently 15%)
if volume_score > 0:
    buy_score += volume_score * 0.6  # Change 0.6 to adjust weight

# Sentiment Analysis weight (currently 15%)
if sentiment_score > 0:
    buy_score += sentiment_score * 0.6  # Change 0.6 to adjust weight

# Pattern Recognition weight (currently 10%)
if pattern_score > 0:
    buy_score += pattern_score * 0.4  # Change 0.4 to adjust weight
```

### Adjust Technical Indicator Thresholds

```python
# RSI thresholds
if rsi < 30:  # Change from 30 to your preferred oversold level
    buy_score += 3  # Adjust weight

# MACD thresholds
if macd > 1:  # Change threshold
    buy_score += 2.5  # Adjust weight

# Decision thresholds
if score_diff >= 4:  # Change from 4 to make more/less aggressive
    return RecommendationType.BUY, confidence
```

### Adjust Fundamental Thresholds

Edit `stock_market_analysis/components/fundamental_analysis.py`:

```python
# P/E ratio thresholds
if pe_ratio < 15:  # Change undervalued threshold
    signals['fundamental_score'] += 2

# Earnings growth thresholds
if earnings_growth > 20:  # Change strong growth threshold
    signals['fundamental_score'] += 2
```

## References

- [RSI Indicator](https://www.investopedia.com/terms/r/rsi.asp)
- [MACD Indicator](https://www.investopedia.com/terms/m/macd.asp)
- [Technical Analysis](https://www.investopedia.com/terms/t/technicalanalysis.asp)
