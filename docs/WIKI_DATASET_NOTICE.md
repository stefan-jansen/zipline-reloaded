# NASDAQ WIKI Dataset - Important Notice

## Summary

The **NASDAQ WIKI dataset was discontinued on March 27, 2018** and contains **NO DATA after that date**.

If you're trying to use WIKI for current backtesting or live trading, you'll encounter errors or missing data.

## What Happened?

NASDAQ Data Link (formerly Quandl) discontinued their free WIKI dataset in March 2018. According to their documentation:

> "The free Wiki Prices data feed was deprecated in 2018 and therefore only provides data going up to March 2018."

Source: https://data.nasdaq.com/data/WIKI-wiki-eod-stock-prices/documentation

## Your Options

### Option 1: Yahoo Finance Bundle (Recommended for Free Users)

**Best for**: Most users who need free, current market data

```bash
# Setup Yahoo Finance bundle
docker exec -it zipline-reloaded-jupyter python /scripts/manage_data.py setup --source yahoo

# Or with custom tickers
docker exec -it zipline-reloaded-jupyter python /scripts/manage_data.py setup --source yahoo --tickers AAPL,MSFT,GOOGL,AMZN,TSLA
```

**Advantages**:
- ✅ **FREE** - No API key required
- ✅ **Current data** - Updated daily
- ✅ **Good quality** - Includes splits and dividends
- ✅ **Easy setup** - No registration needed

**Limitations**:
- ⚠️ Rate limits may apply for large ticker lists
- ⚠️ Occasional data gaps
- ⚠️ No real-time data (15-20 minute delay)

### Option 2: NASDAQ EOD Dataset (Premium)

**Best for**: Professional traders who need high-quality data

**Requirements**: Paid subscription to NASDAQ Data Link

**Setup**:
```bash
# Add API key to .env
echo "NASDAQ_DATA_LINK_API_KEY=your_premium_key" >> .env

# Restart container
docker compose restart

# Setup NASDAQ EOD bundle
docker exec -it zipline-reloaded-jupyter python /scripts/manage_data.py setup --source nasdaq --dataset EOD
```

**Advantages**:
- ✅ Professional-grade quality
- ✅ Clean, fully adjusted data
- ✅ Reliable updates
- ✅ Comprehensive coverage

**Limitations**:
- 💰 Requires paid subscription

### Option 3: WIKI for Historical Backtests Only

**Best for**: Research on historical market behavior (pre-2018)

**Important**: This option is ONLY useful if you're studying market behavior before 2018. It will NOT give you current data.

```bash
# Setup WIKI bundle (data capped at 2018-03-27)
docker exec -it zipline-reloaded-jupyter python /scripts/manage_data.py setup --source nasdaq --dataset WIKI
```

**Use Cases**:
- ✅ Historical research (studying pre-2018 strategies)
- ✅ Learning zipline (testing with old data)
- ✅ Academic research on historical periods

**NOT Suitable For**:
- ❌ Current backtesting
- ❌ Recent strategy testing (2018+)
- ❌ Live trading
- ❌ Production systems

## What We Fixed

To prevent confusion and errors, we've implemented automatic safeguards:

### 1. Automatic Date Capping
When you use WIKI dataset, dates are automatically capped:

```python
# Your request
nasdaq_bundle(dataset='WIKI', end_date='2024-01-01')

# Automatically adjusted to:
# end_date='2018-03-27'

# You'll see this warning:
⚠️  WARNING: WIKI dataset was discontinued on March 27, 2018
   Automatically capping end_date from 2024-01-01 to 2018-03-27
   For current data, use dataset='EOD' (requires premium subscription)
   Or use the Yahoo Finance bundle (free)
```

### 2. Clear Documentation
All documentation now clearly states WIKI limitations:
- `nasdaq_bundle.py` - Function docstrings updated
- `GETTING_STARTED.md` - Setup instructions clarified
- `docs/BUNDLES.md` - Bundle comparison updated
- This notice document

### 3. Alternative Recommendations
We always point you to better options:
- Yahoo Finance for free current data
- NASDAQ EOD for premium current data

## Migration Guide

### If You're Currently Using WIKI

**Step 1: Check Your Date Range**
```python
# If your backtests use dates after 2018-03-27, WIKI won't work
results = run_algorithm(
    start=pd.Timestamp('2022-01-01', tz='UTC'),  # ❌ WIKI has no data
    end=pd.Timestamp('2023-12-31', tz='UTC'),
    bundle='nasdaq-wiki',  # Won't have this data
)
```

**Step 2: Switch to Yahoo Finance**
```bash
# Setup Yahoo bundle
docker exec -it zipline-reloaded-jupyter python /scripts/manage_data.py setup --source yahoo

# Verify
docker exec -it zipline-reloaded-jupyter zipline bundles
# Should show: yahoo
```

**Step 3: Update Your Code**
```python
# Change from:
results = run_algorithm(
    ...,
    bundle='nasdaq-wiki',  # Old
)

# To:
results = run_algorithm(
    ...,
    bundle='yahoo',  # New
)
```

**Step 4: Test**
```python
# Run a test backtest to verify data
results = run_algorithm(
    start=pd.Timestamp('2022-01-01', tz='UTC'),
    end=pd.Timestamp('2023-12-31', tz='UTC'),
    initialize=initialize,
    handle_data=handle_data,
    capital_base=100000,
    bundle='yahoo',  # Should work now
)
```

### If You Need Historical Data (Pre-2018)

WIKI is still useful for historical research:

```python
# This works - all dates before 2018-03-27
results = run_algorithm(
    start=pd.Timestamp('2015-01-01', tz='UTC'),  # ✅ WIKI has this
    end=pd.Timestamp('2017-12-31', tz='UTC'),    # ✅ WIKI has this
    bundle='nasdaq-wiki',
)
```

## FAQ

### Q: Can I get current WIKI data if I pay?
**A:** No. WIKI dataset is discontinued. Even with a paid NASDAQ subscription, WIKI only has data up to March 27, 2018. You need the EOD dataset for current data.

### Q: Why not just fix the WIKI bundle?
**A:** We can't "fix" it because the data source itself is discontinued. NASDAQ stopped updating WIKI in 2018. No new data exists.

### Q: Is Yahoo Finance data as good as WIKI?
**A:** Yes, for most use cases. Yahoo Finance provides similar OHLCV data with splits and dividends. The main difference is WIKI had professional-grade data quality, but Yahoo Finance is reliable for backtesting.

### Q: What about other free data sources?
**A:** Options include:
- **Alpha Vantage** (free tier with rate limits)
- **IEX Cloud** (free tier with limited history)
- **Polygon.io** (free tier for delayed data)
- **Yahoo Finance via yfinance** (what we use, most reliable free option)

### Q: Can I combine multiple data sources?
**A:** Yes! You can create multiple bundles:
```python
# Different bundles for different purposes
register('yahoo-daily', yahoo_bundle())
register('historical', nasdaq_bundle(dataset='WIKI'))  # Pre-2018 only

# Use the right one for your date range
```

### Q: The old code examples show WIKI, should I follow them?
**A:** No. Any examples or tutorials using WIKI for current data are outdated (pre-2018). Replace with Yahoo Finance or NASDAQ EOD.

## Summary Table

| Data Source | Cost | Current Data | Data Quality | Setup Difficulty |
|-------------|------|--------------|--------------|------------------|
| **Yahoo Finance** | Free | ✅ Yes | Good | Easy |
| **NASDAQ EOD** | Paid | ✅ Yes | Excellent | Easy |
| **NASDAQ WIKI** | Free | ❌ No (ends 2018-03-27) | Excellent | Easy |

## Recommended Action

**For 99% of users**: Use Yahoo Finance bundle

```bash
# One command to get started
docker exec -it zipline-reloaded-jupyter python /scripts/manage_data.py setup --source yahoo
```

Then use in your backtests:
```python
results = run_algorithm(
    start=pd.Timestamp('2022-01-01', tz='UTC'),
    end=pd.Timestamp('2023-12-31', tz='UTC'),
    initialize=initialize,
    handle_data=handle_data,
    capital_base=100000,
    bundle='yahoo',  # Free and current
)
```

## Need Help?

- Check [GETTING_STARTED.md](../GETTING_STARTED.md) for setup instructions
- Read [BUNDLES.md](./BUNDLES.md) for complete bundle documentation
- See example backtest in [notebooks/05_backtesting_with_bundles.ipynb](../notebooks/05_backtesting_with_bundles.ipynb)
- Join the community at [ML4Trading Forum](https://exchange.ml4trading.io)

## References

- [NASDAQ WIKI Documentation](https://data.nasdaq.com/data/WIKI-wiki-eod-stock-prices/documentation)
- [Yahoo Finance via yfinance](https://github.com/ranaroussi/yfinance)
- [NASDAQ Data Link Pricing](https://data.nasdaq.com/databases/EOD/pricing)
