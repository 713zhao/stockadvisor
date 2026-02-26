# Comprehensive Stock Analysis Algorithm Guide

## Overview

The Stock Market Analysis system uses a **multi-dimensional analysis approach** that combines five distinct types of analysis to generate BUY/SELL/HOLD recommendations. This comprehensive methodology provides more reliable investment signals by considering technical indicators, company fundamentals, trading patterns, market sentiment, and chart patterns.

## Analysis Framework

### Weight Distribution

Each analysis type contributes to the final recommendation with the following weights:

| Analysis Type | Weight | Purpose |
|--------------|--------|---------|
| Technical Analysis | 35% | Price trends and momentum indicators |
| Fundamental Analysis | 25% | Company financial health and valuation |
| Volume Analysis | 15% | Trading activity and conviction |
| Sentiment Analysis | 15% | Market psychology and news |
| Pattern Recognition | 10% | Chart patterns and support/resistance |

---

## 1. Technical Analysis (35% Weight)

Technical analysis examines price movements and momentum indicators to identify trading opportunities.

### RSI (Relative Strength Index)

**What it measures**: Momentum indicator that identifies overbought/oversold conditions

**Formula**: `RSI = 100 - (100 / (1 + RS))` where `RS = Average Gain / Average Loss`

**Signals**:
- **RSI < 30**: Oversold → Strong BUY signal (+3 points)
  - Stock may be undervalued and due for a bounce
- **RSI 30-40**: Weak → Moderate BUY signal (+2 points)
  - Some upside potential remains
- **RSI 40-60**: Neutral → No signal
  - Stock is fairly valued
- **RSI 60-70**: Strong → Moderate SELL signal (+2 points)
  - Stock may be getting expensive
- **RSI > 70**: Overbought → Strong SELL signal (+3 points)
  - Stock may be overvalued and due for correction

**Example**:
```
Stock A: RSI = 28
Signal: Strong BUY (+3 points)
Rationale: "RSI at 28.0 indicates oversold conditions"
```

### MACD (Moving Average Convergence Divergence)

**What it measures**: Trend momentum and direction changes

**Formula**: 
- `MACD = EMA(12) - EMA(26)`
- `Signal Line = EMA(MACD, 9)`

**Signals**:
- **MACD > 1**: Strong bullish momentum → BUY signal (+2.5 points)
- **MACD 0-1**: Positive momentum → Weak BUY signal (+1.5 points)
- **MACD -1-0**: Negative momentum → Weak SELL signal (+1.5 points)
- **MACD < -1**: Strong bearish momentum → SELL signal (+2.5 points)

**Example**:
```
Stock B: MACD = 1.8
Signal: Strong BUY (+2.5 points)
Rationale: "MACD shows bullish momentum"
```

### Price Momentum

**What it measures**: Recent price change percentage

**Formula**: `Price Change % = ((Close - Open) / Open) * 100`

**Signals**:
- **Change > 3%**: Strong upward momentum → BUY signal (+2.5 points)
- **Change 1-3%**: Moderate upward momentum → Weak BUY signal (+1.5 points)
- **Change -1-1%**: Neutral → No signal
- **Change -3--1%**: Moderate downward momentum → Weak SELL signal (+1.5 points)
- **Change < -3%**: Strong downward momentum → SELL signal (+2.5 points)

### Volatility

**What it measures**: Price stability and risk

**Formula**: `Volatility = ((High - Low) / Close) * 100`

**Impact**:
- **Volatility < 3%**: Low volatility → Increases confidence (+0.5 points)
- **Volatility 3-10%**: Normal volatility → No adjustment
- **Volatility > 10%**: High volatility → Decreases confidence (-0.5 points)

---

## 2. Fundamental Analysis (25% Weight)

Fundamental analysis evaluates company financial health and valuation metrics.

### P/E Ratio (Price-to-Earnings)

**What it measures**: Stock valuation relative to earnings

**Signals**:
- **P/E < 15**: Undervalued → BUY signal (+2 points)
  - Stock is cheap relative to earnings
- **P/E 15-25**: Fair valuation → Weak BUY signal (+1 point)
  - Reasonably priced
- **P/E 25-30**: Expensive → Weak SELL signal (-1 point)
  - Getting pricey
- **P/E > 30**: Overvalued → SELL signal (-2 points)
  - Stock may be in a bubble

**Example**:
```
Stock C: P/E = 12.5
Signal: BUY (+2 points)
Rationale: "P/E ratio of 12.5 suggests undervaluation"
```

### Earnings Growth

**What it measures**: Year-over-year earnings growth rate

**Signals**:
- **Growth > 20%**: Strong growth → BUY signal (+2 points)
- **Growth 10-20%**: Moderate growth → Weak BUY signal (+1 point)
- **Growth 0-10%**: Neutral → No signal
- **Growth < -10%**: Declining → SELL signal (-2 points)

### Revenue Growth

**What it measures**: Year-over-year revenue growth rate

**Signals**:
- **Growth > 15%**: Strong growth → BUY signal (+1.5 points)
- **Growth 5-15%**: Moderate growth → Weak BUY signal (+0.5 points)
- **Growth < -5%**: Declining → SELL signal (-1.5 points)

### Debt-to-Equity Ratio

**What it measures**: Financial leverage and risk

**Signals**:
- **Ratio < 0.5**: Low debt → Positive signal (+0.5 points)
- **Ratio 0.5-2.0**: Moderate debt → Neutral
- **Ratio > 2.0**: High debt → Negative signal (-1 point)

---

## 3. Volume Analysis (15% Weight)

Volume analysis examines trading activity to confirm price movements.

### Volume Trends

**What it measures**: Current volume relative to historical average

**Signals**:
- **Volume > 2x average**: Surge → Strong signal (+2 points)
  - High conviction in price movement
- **Volume > 1.5x average**: High → Moderate signal (+1 point)
  - Good participation
- **Volume < 0.5x average**: Low → Weak signal (-1 point)
  - Lack of conviction

**Example**:
```
Stock D: Current Volume = 50M, Average = 20M
Ratio: 2.5x average
Signal: Strong (+2 points)
Rationale: "Volume surge indicates strong interest"
```

### Price-Volume Relationship

**What it measures**: Correlation between price and volume

**Signals**:
- **Price up + High volume**: Accumulation → BUY signal (+0.5 points)
  - Smart money buying
- **Price down + High volume**: Distribution → SELL signal (-0.5 points)
  - Smart money selling
- **Price move + Low volume**: Weak conviction → Reduces confidence

**Example**:
```
Stock E: Price +3%, Volume 2x average
Signal: Accumulation (+0.5 points)
Rationale: "Price-volume pattern shows accumulation"
```

---

## 4. Sentiment Analysis (15% Weight)

Sentiment analysis evaluates market psychology from news and social media.

### News Sentiment

**What it measures**: Sentiment score from news articles (-1.0 to +1.0)

**Signals**:
- **Sentiment > 0.3**: Very positive → BUY signal (+2 points)
- **Sentiment 0.1-0.3**: Positive → Weak BUY signal (+1 point)
- **Sentiment -0.1-0.1**: Neutral → No signal
- **Sentiment < -0.3**: Very negative → SELL signal (-2 points)

### Social Media Sentiment

**What it measures**: Sentiment from social media discussions

**Combined Score**: 60% news + 40% social media

**Example**:
```
Stock F: News Sentiment = +0.4, Social = +0.2
Combined: (0.4 × 0.6) + (0.2 × 0.4) = 0.32
Signal: Very Positive (+2 points)
Rationale: "Strong positive market sentiment"
```

---

## 5. Pattern Recognition (10% Weight)

Pattern recognition identifies technical chart patterns and key price levels.

### Support and Resistance Levels

**What it measures**: Historical price levels where buying/selling pressure changes

**Calculation**: 
- Support = Minimum of last 10 prices
- Resistance = Maximum of last 10 prices

**Signals**:
- **Breakout above resistance**: Strong BUY signal (+2 points)
  - Price breaking through ceiling
- **Near support level**: Potential bounce → BUY signal (+1 point)
  - Price at floor, likely to bounce
- **Near resistance level**: Potential rejection → SELL signal (-1 point)
  - Price at ceiling, likely to fall
- **Breakdown below support**: Strong SELL signal (-2 points)
  - Price breaking through floor

**Example**:
```
Stock G: Price = $105, Resistance = $100
Signal: Breakout (+2 points)
Rationale: "Breakout above resistance level"
```

### Chart Patterns

**Patterns Detected**:

1. **Hammer Pattern**: Potential bullish reversal (+0.5 points)
   - Long lower shadow, small body near top
   - Indicates buying pressure at lows

2. **Shooting Star**: Potential bearish reversal (-0.5 points)
   - Long upper shadow, small body near bottom
   - Indicates selling pressure at highs

---

## Decision-Making Process

### Step 1: Calculate Individual Scores

For each analysis type, calculate the score based on the signals:

```
Technical Score = RSI + MACD + Price Momentum + Volatility
Fundamental Score = P/E + Earnings + Revenue + Debt
Volume Score = Volume Trend + Price-Volume Relationship
Sentiment Score = News + Social Media
Pattern Score = Support/Resistance + Chart Patterns
```

### Step 2: Apply Weights

Apply the weight multipliers to each score:

```
Weighted Technical = Technical Score × 1.0 (35% base weight)
Weighted Fundamental = Fundamental Score × 0.8 (25% weight)
Weighted Volume = Volume Score × 0.6 (15% weight)
Weighted Sentiment = Sentiment Score × 0.6 (15% weight)
Weighted Pattern = Pattern Score × 0.4 (10% weight)
```

### Step 3: Calculate Total Scores

Sum up all positive and negative signals separately:

```
Total BUY Score = Sum of all positive weighted scores
Total SELL Score = Sum of all negative weighted scores
Score Difference = BUY Score - SELL Score
```

### Step 4: Determine Recommendation

Based on the score difference:

| Score Difference | Recommendation | Confidence Range |
|-----------------|----------------|------------------|
| ≥ 4.0 | **STRONG BUY** | 75-95% |
| 2.0-4.0 | **BUY** | 70-85% |
| -2.0 to 2.0 | **HOLD** | 60% |
| -4.0 to -2.0 | **SELL** | 70-85% |
| ≤ -4.0 | **STRONG SELL** | 75-95% |

### Step 5: Calculate Confidence

Base confidence is determined by score strength, then adjusted by:
- Multiple confirming signals → Increase confidence
- High volatility → Decrease confidence
- Low volume → Decrease confidence

---

## Complete Examples

### Example 1: Strong BUY Signal

**Stock: AAPL (Apple Inc.)**

**Technical Analysis (35%)**:
- RSI: 28 (oversold) → +3 points
- MACD: 1.5 (bullish) → +2.5 points
- Price Change: +4.2% → +2.5 points
- Volatility: 2.8% (low) → +0.5 points
- **Subtotal: 8.5 points**

**Fundamental Analysis (25%)**:
- P/E Ratio: 18 (fair) → +1 point
- Earnings Growth: 22% → +2 points
- Revenue Growth: 18% → +1.5 points
- Debt-to-Equity: 0.4 → +0.5 points
- **Subtotal: 5 points × 0.8 = 4.0 points**

**Volume Analysis (15%)**:
- Volume: 2.5x average (surge) → +2 points
- Price-Volume: Accumulation → +0.5 points
- **Subtotal: 2.5 points × 0.6 = 1.5 points**

**Sentiment Analysis (15%)**:
- News Sentiment: +0.4 (positive) → +1 point
- **Subtotal: 1 point × 0.6 = 0.6 points**

**Pattern Recognition (10%)**:
- Breakout above resistance → +2 points
- **Subtotal: 2 points × 0.4 = 0.8 points**

**Final Calculation**:
```
Total BUY Score: 15.4
Total SELL Score: 0
Score Difference: +15.4

Recommendation: STRONG BUY
Confidence: 95%
Target Price: $165.00 (10% above current)
```

**Rationale**:
"RSI at 28.0 indicates oversold conditions; MACD shows bullish momentum; strong upward price movement of 4.2%; P/E ratio of 18.0 suggests fair valuation; earnings growth of 22.0%; volume surge indicates strong interest; price-volume pattern shows accumulation; positive market sentiment; breakout above resistance level; low volatility indicates stability."

---

### Example 2: SELL Signal

**Stock: TSLA (Tesla Inc.)**

**Technical Analysis (35%)**:
- RSI: 72 (overbought) → +3 points (sell)
- MACD: -0.8 (bearish) → +1.5 points (sell)
- Price Change: -2.1% → +1.5 points (sell)
- Volatility: 8.5% (moderate) → 0 points
- **Subtotal: 6 points (sell)**

**Fundamental Analysis (25%)**:
- P/E Ratio: 45 (overvalued) → -2 points
- Earnings Growth: -5% → -1 point
- Revenue Growth: 8% → +0.5 points
- **Subtotal: -2.5 points × 0.8 = -2.0 points**

**Volume Analysis (15%)**:
- Volume: 1.8x average (high) → +1 point
- Price-Volume: Distribution → -0.5 points
- **Subtotal: 0.5 points × 0.6 = 0.3 points**

**Sentiment Analysis (15%)**:
- News Sentiment: -0.2 (negative) → -1 point
- **Subtotal: -1 point × 0.6 = -0.6 points**

**Pattern Recognition (10%)**:
- Near resistance, rejection → -1 point
- **Subtotal: -1 point × 0.4 = -0.4 points**

**Final Calculation**:
```
Total BUY Score: 0.8
Total SELL Score: 9.0
Score Difference: -8.2

Recommendation: STRONG SELL
Confidence: 90%
Target Price: $180.00 (10% below current)
```

**Rationale**:
"RSI at 72.0 indicates overbought conditions; MACD shows bearish momentum; moderate downward trend with 2.1% change; P/E ratio of 45.0 indicates overvaluation; earnings decline of 5.0%; high volume; price-volume pattern shows distribution; negative market sentiment; testing resistance level."

---

### Example 3: HOLD Signal

**Stock: MSFT (Microsoft Corporation)**

**Technical Analysis (35%)**:
- RSI: 52 (neutral) → 0 points
- MACD: 0.2 (slightly positive) → +1.5 points (buy)
- Price Change: +0.5% → 0 points
- Volatility: 4.2% (low) → +0.5 points
- **Subtotal: 2 points (buy)**

**Fundamental Analysis (25%)**:
- P/E Ratio: 28 (fair/expensive) → -1 point
- Earnings Growth: 12% → +1 point
- Revenue Growth: 7% → +0.5 points
- **Subtotal: 0.5 points × 0.8 = 0.4 points**

**Volume Analysis (15%)**:
- Volume: 0.9x average (normal) → 0 points
- **Subtotal: 0 points**

**Sentiment Analysis (15%)**:
- Neutral sentiment → 0 points
- **Subtotal: 0 points**

**Pattern Recognition (10%)**:
- No significant patterns → 0 points
- **Subtotal: 0 points**

**Final Calculation**:
```
Total BUY Score: 2.4
Total SELL Score: 0
Score Difference: +2.4 (below BUY threshold of 4.0)

Recommendation: HOLD
Confidence: 60%
Target Price: None
```

**Rationale**:
"RSI at 52.0 shows potential upside; MACD shows bullish momentum; P/E ratio at 28.0; earnings growth of 12.0%; volume at 5,000,000 shares; low volatility indicates stability."

---

## Advantages of This Approach

1. **Holistic Analysis**: Considers multiple dimensions of stock performance
2. **Reduced False Signals**: Requires multiple factors to align for strong recommendations
3. **Transparent**: Clear scoring system shows why recommendations are made
4. **Adaptable**: Weights can be adjusted based on market conditions
5. **Risk-Aware**: Incorporates volatility and volume to assess conviction
6. **Explainable**: Detailed rationale helps users understand the reasoning

---

## Limitations and Considerations

### Current Limitations

1. **Simulated Sentiment**: Currently uses simulated sentiment data
   - **Solution**: Integrate real news APIs (NewsAPI, Alpha Vantage)

2. **Limited Historical Data**: Uses recent data only
   - **Solution**: Extend to 200+ days for better indicator calculations

3. **Static Weights**: Fixed weight distribution
   - **Solution**: Implement machine learning to optimize weights

4. **No Sector Context**: Doesn't compare to sector averages
   - **Solution**: Add sector and market index comparisons

### Risk Warnings

⚠️ **Important Disclaimers**:
- Past performance does not guarantee future results
- This algorithm is for educational purposes only
- Always do your own research before investing
- Consider consulting a financial advisor
- Markets can be irrational longer than you can stay solvent
- Diversification is key to risk management

---

## Customization Guide

### Adjusting Component Weights

Edit `stock_market_analysis/components/analysis_engine.py`:

```python
# In _determine_recommendation() method

# Fundamental Analysis weight (currently 25%)
if fundamental_score > 0:
    buy_score += fundamental_score * 0.8  # Change 0.8 to adjust

# Volume Analysis weight (currently 15%)
if volume_score > 0:
    buy_score += volume_score * 0.6  # Change 0.6 to adjust

# Sentiment Analysis weight (currently 15%)
if sentiment_score > 0:
    buy_score += sentiment_score * 0.6  # Change 0.6 to adjust

# Pattern Recognition weight (currently 10%)
if pattern_score > 0:
    buy_score += pattern_score * 0.4  # Change 0.4 to adjust
```

### Adjusting Thresholds

```python
# RSI thresholds
if rsi < 30:  # Change from 30 to your preferred oversold level
    buy_score += 3  # Adjust weight

# Decision thresholds
if score_diff >= 4:  # Change from 4 to make more/less aggressive
    return RecommendationType.BUY, confidence
```

### Adjusting Fundamental Thresholds

Edit `stock_market_analysis/components/fundamental_analysis.py`:

```python
# P/E ratio thresholds
if pe_ratio < 15:  # Change undervalued threshold
    signals['fundamental_score'] += 2

# Earnings growth thresholds
if earnings_growth > 20:  # Change strong growth threshold
    signals['fundamental_score'] += 2
```

---

## Future Enhancements

### Planned Improvements

1. **Real Sentiment Integration**
   - Connect to NewsAPI for real-time news sentiment
   - Integrate Twitter/Reddit APIs for social sentiment
   - Use NLP models for sentiment scoring

2. **Machine Learning Optimization**
   - Train models on historical data
   - Optimize weights dynamically
   - Predict optimal entry/exit points

3. **Advanced Pattern Recognition**
   - Head and shoulders patterns
   - Triangle patterns
   - Flag and pennant patterns
   - Fibonacci retracements

4. **Sector Analysis**
   - Compare to sector averages
   - Identify sector rotation opportunities
   - Analyze sector-specific metrics

5. **Risk Management**
   - Position sizing recommendations
   - Stop-loss suggestions
   - Portfolio allocation advice
   - Correlation analysis

6. **Backtesting Framework**
   - Test algorithm on historical data
   - Calculate win rate and returns
   - Optimize parameters
   - Generate performance reports

---

## References and Resources

### Technical Analysis
- [Investopedia: RSI](https://www.investopedia.com/terms/r/rsi.asp)
- [Investopedia: MACD](https://www.investopedia.com/terms/m/macd.asp)
- [Technical Analysis Explained](https://www.investopedia.com/terms/t/technicalanalysis.asp)

### Fundamental Analysis
- [Investopedia: P/E Ratio](https://www.investopedia.com/terms/p/price-earningsratio.asp)
- [Investopedia: Fundamental Analysis](https://www.investopedia.com/terms/f/fundamentalanalysis.asp)

### Volume Analysis
- [Investopedia: Volume Analysis](https://www.investopedia.com/terms/v/volume-analysis.asp)
- [On-Balance Volume](https://www.investopedia.com/terms/o/onbalancevolume.asp)

### Pattern Recognition
- [Chart Patterns](https://www.investopedia.com/articles/technical/112601.asp)
- [Support and Resistance](https://www.investopedia.com/trading/support-and-resistance-basics/)

---

## Contact and Support

For questions, suggestions, or contributions:
- Review the code in `stock_market_analysis/components/`
- Check the main README.md for system overview
- See ALGORITHM_README.md for technical indicator details

---

**Last Updated**: February 26, 2026
**Version**: 2.0 (Comprehensive Analysis)
