# Stock Analysis Algorithm

## Overview

The system uses a **multi-indicator technical analysis algorithm** to generate BUY/SELL/HOLD recommendations with confidence scores.

## Technical Indicators Used

### 1. RSI (Relative Strength Index) - Weight: 30%

**Formula**: `RSI = 100 - (100 / (1 + RS))` where `RS = Average Gain / Average Loss`

**Interpretation**:
- **RSI < 30**: Oversold condition → Strong BUY signal (+3 points)
- **RSI 30-40**: Weak → Moderate BUY signal (+2 points)
- **RSI 40-60**: Neutral → No signal
- **RSI 60-70**: Strong → Moderate SELL signal (+2 points)
- **RSI > 70**: Overbought condition → Strong SELL signal (+3 points)

**Why it matters**: RSI identifies when a stock is potentially oversold (good buying opportunity) or overbought (good selling opportunity).

### 2. MACD (Moving Average Convergence Divergence) - Weight: 25%

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

### 3. Price Momentum - Weight: 25%

**Formula**: `Price Change % = ((Close - Open) / Open) * 100`

**Interpretation**:
- **Change > 3%**: Strong upward momentum → BUY signal (+2.5 points)
- **Change 1-3%**: Moderate upward momentum → Weak BUY signal (+1.5 points)
- **Change -1-1%**: Neutral → No signal
- **Change -3--1%**: Moderate downward momentum → Weak SELL signal (+1.5 points)
- **Change < -3%**: Strong downward momentum → SELL signal (+2.5 points)

**Why it matters**: Recent price movement indicates current market sentiment and trend direction.

### 4. Volatility - Weight: 10%

**Formula**: `Volatility = ((High - Low) / Close) * 100`

**Interpretation**:
- **Volatility < 3%**: Low volatility → Increases confidence (+0.5 points)
- **Volatility 3-10%**: Normal volatility → No adjustment
- **Volatility > 10%**: High volatility → Decreases confidence (-0.5 points)

**Why it matters**: Lower volatility means more predictable price movements and higher confidence in recommendations.

### 5. Volume Confirmation - Weight: 10%

**Interpretation**:
- **Volume > 10M**: Strong volume → High confidence (+1 point)
- **Volume 1M-10M**: Good volume → Moderate confidence (+0.5 points)
- **Volume < 1M**: Low volume → Lower confidence

**Why it matters**: High volume confirms that price movements are supported by actual trading activity.

## Scoring System

The algorithm uses a **point-based scoring system**:

1. Calculate BUY score (sum of all positive indicators)
2. Calculate SELL score (sum of all negative indicators)
3. Calculate score difference: `score_diff = buy_score - sell_score`

### Decision Rules:

| Score Difference | Recommendation | Base Confidence |
|-----------------|----------------|-----------------|
| ≥ 3.0 | **STRONG BUY** | 70-90% |
| 1.5-3.0 | **BUY** | 65-80% |
| -1.5 to 1.5 | **HOLD** | 60% |
| -3.0 to -1.5 | **SELL** | 65-80% |
| ≤ -3.0 | **STRONG SELL** | 70-90% |

### Confidence Calculation:

- Base confidence starts at 65-70%
- Additional confidence added based on score strength
- Maximum confidence capped at 90%
- Volatility and volume can adjust final confidence

## Example Analysis

### Example 1: Strong BUY Signal

```
Stock: AAPL
RSI: 28 (oversold) → +3 points
MACD: 1.5 (bullish) → +2.5 points  
Price Change: +4.2% → +2.5 points
Volatility: 2.8% (low) → +0.5 points
Volume: 15M (strong) → +1 point

Buy Score: 9.5
Sell Score: 0
Score Diff: +9.5

Recommendation: STRONG BUY
Confidence: 90%
Rationale: "RSI at 28.0 indicates oversold conditions; MACD shows bullish momentum; 
Strong upward price movement of 4.2%; low volatility indicates stability; strong volume confirms trend."
```

### Example 2: SELL Signal

```
Stock: TSLA
RSI: 72 (overbought) → +3 points (sell)
MACD: -0.8 (bearish) → +1.5 points (sell)
Price Change: -2.1% → +1.5 points (sell)
Volatility: 8.5% (moderate) → 0 points
Volume: 8M (good) → +0.5 points

Buy Score: 0.5
Sell Score: 6.5
Score Diff: -6.0

Recommendation: STRONG SELL
Confidence: 85%
Rationale: "RSI at 72.0 indicates overbought conditions; MACD shows bearish momentum;
Moderate downward trend with 2.1% change; moderate volatility; adequate volume."
```

### Example 3: HOLD Signal

```
Stock: MSFT
RSI: 52 (neutral) → 0 points
MACD: 0.2 (slightly positive) → +1.5 points (buy)
Price Change: +0.5% → 0 points
Volatility: 4.2% (low) → +0.5 points
Volume: 5M (good) → +0.5 points

Buy Score: 2.5
Sell Score: 0
Score Diff: +2.5 (but < 3.0)

Recommendation: HOLD
Confidence: 60%
Rationale: "RSI at 52.0 shows potential upside; MACD shows bullish momentum;
Stable price action with 0.5% change; low volatility indicates stability; adequate volume."
```

## Advantages of This Algorithm

1. **Multi-Factor Analysis**: Combines multiple indicators for more reliable signals
2. **Weighted Scoring**: More important indicators (RSI, MACD) have higher weights
3. **Confidence Levels**: Provides transparency about recommendation strength
4. **Adaptable**: Easy to adjust weights and thresholds based on backtesting results
5. **Explainable**: Clear rationale shows which factors influenced the decision

## Limitations

1. **Historical Data**: Currently uses single-day data; real system should use historical price series
2. **No Fundamental Analysis**: Doesn't consider P/E ratios, earnings, revenue, etc.
3. **No Market Context**: Doesn't account for overall market conditions or sector trends
4. **No News Sentiment**: Doesn't incorporate news or social media sentiment
5. **Simplified Indicators**: Real RSI/MACD need 14+ days of historical data

## Future Enhancements

1. **Historical Data Integration**: Connect to APIs for multi-day price history
2. **Machine Learning**: Train models on historical data to optimize weights
3. **Fundamental Analysis**: Add P/E ratio, EPS growth, debt ratios
4. **Sentiment Analysis**: Incorporate news and social media sentiment
5. **Sector Analysis**: Compare stock performance to sector averages
6. **Backtesting**: Test algorithm performance on historical data
7. **Risk Management**: Add position sizing and stop-loss recommendations

## How to Customize

Edit `stock_market_analysis/components/analysis_engine.py`:

```python
# Adjust RSI thresholds
if rsi < 30:  # Change from 30 to your preferred oversold level
    buy_score += 3  # Adjust weight

# Adjust MACD thresholds
if macd > 1:  # Change threshold
    buy_score += 2.5  # Adjust weight

# Adjust decision thresholds
if score_diff >= 3:  # Change from 3 to make more/less aggressive
    return RecommendationType.BUY, confidence
```

## References

- [RSI Indicator](https://www.investopedia.com/terms/r/rsi.asp)
- [MACD Indicator](https://www.investopedia.com/terms/m/macd.asp)
- [Technical Analysis](https://www.investopedia.com/terms/t/technicalanalysis.asp)
