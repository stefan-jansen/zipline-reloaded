# Zipline Data Bundles Guide

## Table of Contents

1. [Overview](#overview)
2. [Why Use Bundles](#why-use-bundles)
3. [Quick Start](#quick-start)
4. [Available Bundles](#available-bundles)
5. [Bundle vs CustomData](#bundle-vs-customdata)
6. [Daily Updates](#daily-updates)
7. [Advanced Usage](#advanced-usage)
8. [Troubleshooting](#troubleshooting)

## Overview

Zipline data bundles provide persistent, optimized storage for market data used in backtesting. Bundles store data in zipline's native format (bcolz), which is optimized for fast access during backtests.

### Key Features

- **Persistent Storage**: Data survives between sessions
- **Optimized Format**: Fast access using bcolz compression
- **Corporate Actions**: Automatic handling of splits and dividends
- **Backtesting Ready**: Direct integration with `run_algorithm()`
- **Easy Updates**: Simple commands to fetch latest data

## Why Use Bundles?

### Bundles vs CustomData

| Feature | Bundles | CustomData |
|---------|---------|------------|
| **Primary Use** | Backtesting with `run_algorithm()` | Pipeline analysis |
| **Storage Format** | bcolz (highly optimized) | SQLite |
| **Performance** | Excellent (optimized for speed) | Good |
| **API** | TradingAlgorithm API | Pipeline API |
| **Adjustments** | Automatic (splits, dividends) | Manual |
| **Updates** | Via `zipline ingest` | Via custom scripts |
| **Size Efficiency** | Very efficient | Moderate |

**Recommendation**: Use bundles for backtesting, CustomData for custom indicators and research.

## Quick Start

### 1. Setup a Bundle

**Option A: Using Management Script (Recommended)**

```bash
# Yahoo Finance (free)
python scripts/manage_data.py setup --source yahoo

# NASDAQ Data Link (requires API key)
export NASDAQ_DATA_LINK_API_KEY=your_key
python scripts/manage_data.py setup --source nasdaq --dataset EOD

# Custom tickers
python scripts/manage_data.py setup --source yahoo --tickers AAPL,MSFT,GOOGL
```

**Option B: Manual Setup**

```python
from zipline.data.bundles import register
from zipline.data.bundles.yahoo_bundle import yahoo_bundle

# Register bundle
register('my-yahoo', yahoo_bundle(
    tickers=['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA'],
))
```

```bash
# Ingest data
zipline ingest -b my-yahoo
```

### 2. Use in Backtest

```python
from zipline import run_algorithm
from zipline.api import order_target_percent, symbol

def initialize(context):
    context.stock = symbol('AAPL')

def handle_data(context, data):
    order_target_percent(context.stock, 1.0)

results = run_algorithm(
    start=pd.Timestamp('2022-01-01', tz='UTC'),
    end=pd.Timestamp('2023-12-31', tz='UTC'),
    initialize=initialize,
    handle_data=handle_data,
    capital_base=100000,
    bundle='my-yahoo',  # Use your bundle here
)
```

### 3. Update Data

```bash
# Update specific bundle
zipline ingest -b my-yahoo

# Or using management script
python scripts/manage_data.py update --bundle my-yahoo
```

## Available Bundles

### Yahoo Finance Bundle

**Source**: `zipline.data.bundles.yahoo_bundle`

**Advantages**:
- ✅ Free
- ✅ No API key required
- ✅ Good data quality
- ✅ Includes splits and dividends

**Limitations**:
- ⚠️ Rate limits may apply
- ⚠️ Occasional data gaps
- ⚠️ No real-time data

**Setup**:
```python
from zipline.data.bundles import register
from zipline.data.bundles.yahoo_bundle import yahoo_bundle

register('yahoo', yahoo_bundle())
```

**Pre-configured Variants**:
```python
from zipline.data.bundles.yahoo_bundle import (
    yahoo_tech_bundle,     # Tech stocks
    yahoo_dow_bundle,      # Dow Jones
    yahoo_sp500_bundle,    # S&P 500 subset
)

register('yahoo-tech', yahoo_tech_bundle())
```

### NASDAQ Data Link Bundle

**Source**: `zipline.data.bundles.nasdaq_bundle`

**⚠️ IMPORTANT: WIKI Dataset Discontinued**
The free WIKI dataset was discontinued on **March 27, 2018** and contains NO data after that date.
- For **historical backtests** (pre-2018): You can use WIKI (free)
- For **current data**: Use Yahoo Finance bundle (free) or NASDAQ EOD (premium)

**Advantages**:
- ✅ Professional quality (EOD dataset)
- ✅ Clean, adjusted data
- ✅ Extensive history
- ✅ Reliable API

**Limitations**:
- ⚠️ Requires API key
- ⚠️ Premium datasets cost money (EOD)
- ⚠️ Free WIKI dataset discontinued March 2018
- ⚠️ Rate limits on free tier

**Setup (Premium EOD)**:
```python
from zipline.data.bundles import register
from zipline.data.bundles.nasdaq_bundle import nasdaq_bundle

# Premium EOD dataset (current data)
register('nasdaq', nasdaq_bundle(
    api_key='your_key',  # or set NASDAQ_DATA_LINK_API_KEY env var
    dataset='EOD',       # Premium, current data
))
```

**Setup (Free WIKI - Historical Only)**:
```python
# WIKI dataset (free, but discontinued March 2018)
register('nasdaq-wiki', nasdaq_bundle(
    api_key='your_key',
    dataset='WIKI',      # Free, but only data up to 2018-03-27
))
# Note: Dates will be automatically capped at 2018-03-27
```

**Pre-configured Variants**:
```python
from zipline.data.bundles.nasdaq_bundle import (
    nasdaq_premium_bundle,  # EOD dataset, 20 stocks (premium)
    nasdaq_free_bundle,     # WIKI dataset, 5 stocks (discontinued 2018)
    nasdaq_sp500_bundle,    # S&P 500 subset (premium)
)

register('nasdaq-premium', nasdaq_premium_bundle())
```

### Sharadar Equity Prices Bundle

**Source**: `zipline.data.bundles.sharadar_bundle`

**⚠️ PREMIUM SUBSCRIPTION REQUIRED**
Sharadar is a professional-grade dataset that requires a paid subscription.
- Subscribe at: [https://data.nasdaq.com/databases/SFA](https://data.nasdaq.com/databases/SFA)
- Pricing: Contact NASDAQ for current pricing
- Free trial: Usually available for new subscribers

**Advantages**:
- ✅ **Institutional-grade quality** - Best-in-class data accuracy
- ✅ **Comprehensive coverage** - All US equities (~8,000+ tickers)
- ✅ **Point-in-time** - Historical values as they were known at the time
- ✅ **Corporate actions included** - Splits, dividends, etc.
- ✅ **Fundamental data available** - Via SF1 table (separate from bundle)
- ✅ **Professional support** - Support from NASDAQ

**Limitations**:
- 💰 **Paid subscription required** - Not free
- ⚠️ **Large downloads** - Full dataset is 10-20 GB
- ⚠️ **Long ingestion time** - 10-30 minutes for full dataset

**Setup (Specific tickers - recommended for testing)**:
```python
from zipline.data.bundles import register
from zipline.data.bundles.sharadar_bundle import sharadar_bundle

# Specific tickers
register('sharadar', sharadar_bundle(
    tickers=['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA'],
))
```

**Setup (All tickers - production use)**:
```python
# ALL US equities (~8,000+ tickers)
# WARNING: 10-20 GB download, 10-30 minutes ingestion time
register('sharadar-all', sharadar_bundle())  # tickers=None means all
```

**Pre-configured Variants**:
```python
from zipline.data.bundles.sharadar_bundle import (
    sharadar_tech_bundle,         # Tech stocks (15 tickers)
    sharadar_sp500_sample_bundle, # S&P 500 sample (30 tickers)
    sharadar_all_bundle,          # All US equities
)

register('sharadar-tech', sharadar_tech_bundle())
```

**Data tables used**:
- **SEP (Sharadar Equity Prices)**: Daily OHLCV pricing data
- **ACTIONS**: Corporate actions (splits, dividends, etc.)

## Bundle vs CustomData

### When to Use Bundles

Use bundles when:
- Running backtests with `run_algorithm()`
- Need maximum performance
- Want automatic adjustment handling
- Working with standard OHLCV data

### When to Use CustomData

Use CustomData when:
- Building custom Pipeline factors
- Need flexible data schemas
- Integrating non-standard data sources
- Doing research and analysis (not backtesting)

### Using Both Together

You can combine bundles and CustomData:

```python
# Bundle for pricing data in backtest
def initialize(context):
    # Pipeline uses bundle data automatically
    pipe = Pipeline()
    pipe.add(SimpleMovingAverage(...), 'sma')
    attach_pipeline(pipe, 'my_pipe')

def handle_data(context, data):
    # Get pipeline signals
    pipeline_data = pipeline_output('my_pipe')

    # Trade using bundle pricing data
    for stock in pipeline_data.index:
        order_target_percent(stock, ...)

results = run_algorithm(
    ...,
    bundle='my-yahoo',  # Bundle provides pricing
)
```

## Daily Updates

### Manual Updates

```bash
# Update specific bundle
zipline ingest -b my-bundle

# Using management script
python scripts/manage_data.py update --bundle my-bundle

# Update all bundles
python scripts/manage_data.py update --all
```

### Automated Updates

**Setup cron job** (Linux/Mac):

```bash
# Edit crontab
crontab -e

# Add line to run at 5 PM ET, Monday-Friday
0 17 * * 1-5 cd /path/to/zipline-reloaded && python scripts/manage_data.py update --all >> /var/log/zipline_update.log 2>&1
```

**Windows Task Scheduler**:

1. Open Task Scheduler
2. Create Basic Task
3. Trigger: Daily, 5:00 PM
4. Action: Start a program
   - Program: `python`
   - Arguments: `C:\path\to\zipline-reloaded\scripts\manage_data.py update --all`
   - Start in: `C:\path\to\zipline-reloaded`

**Docker**:

Add to `docker-compose.yml`:

```yaml
services:
  zipline-updater:
    build: .
    command: python scripts/manage_data.py update --all
    environment:
      - NASDAQ_DATA_LINK_API_KEY=${NASDAQ_DATA_LINK_API_KEY}
    volumes:
      - ./data:/root/.zipline
    deploy:
      restart_policy:
        condition: none
```

Schedule with host cron:
```bash
0 17 * * 1-5 docker compose run zipline-updater
```

### Update Script

Create `scripts/daily_update.py`:

```python
#!/usr/bin/env python
"""Daily bundle update script with error handling"""

import subprocess
import logging
from datetime import datetime

logging.basicConfig(
    filename='/var/log/zipline_update.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

BUNDLES = ['yahoo', 'nasdaq']

def update_bundles():
    logging.info("Starting daily update")

    for bundle in BUNDLES:
        try:
            logging.info(f"Updating {bundle}...")

            result = subprocess.run(
                ['zipline', 'ingest', '-b', bundle],
                capture_output=True,
                text=True,
                timeout=600,
            )

            if result.returncode == 0:
                logging.info(f"✓ {bundle} updated successfully")
            else:
                logging.error(f"✗ {bundle} failed: {result.stderr}")

        except subprocess.TimeoutExpired:
            logging.error(f"✗ {bundle} timed out")
        except Exception as e:
            logging.error(f"✗ {bundle} error: {e}")

    logging.info("Update complete")

if __name__ == '__main__':
    update_bundles()
```

## Advanced Usage

### Custom Bundle Configuration

Create your own bundle with specific settings:

```python
from zipline.data.bundles import register
from zipline.data.bundles.yahoo_bundle import yahoo_bundle

# Custom tech portfolio
register('my-tech-portfolio', yahoo_bundle(
    tickers=[
        'AAPL', 'MSFT', 'GOOGL', 'AMZN',
        'META', 'NVDA', 'TSLA', 'NFLX',
    ],
    start_date='2015-01-01',
))

# Small-cap focus
register('small-caps', yahoo_bundle(
    tickers=['ROKU', 'SQ', 'SHOP', 'PINS'],
    start_date='2020-01-01',
))
```

### Multiple Bundles

Use different bundles for different strategies:

```python
# Long-term value strategy
results_value = run_algorithm(
    ...,
    bundle='sp500-value',
)

# Short-term momentum strategy
results_momentum = run_algorithm(
    ...,
    bundle='tech-momentum',
)
```

### Bundle Inspection

Check what's in a bundle:

```python
from zipline.data.bundles import load

bundle_data = load('my-bundle')

# Get asset finder
asset_finder = bundle_data.asset_finder

# List all assets
assets = asset_finder.retrieve_all(asset_finder.sids)
for asset in assets:
    print(f"{asset.symbol}: {asset.start_date} to {asset.end_date}")

# Get specific asset
asset = asset_finder.lookup_symbol('AAPL', as_of_date=None)
print(f"AAPL SID: {asset.sid}")
```

### Custom Data Frequency

Bundles support different frequencies:

```python
# Daily data (default)
results = run_algorithm(
    ...,
    data_frequency='daily',
    bundle='my-bundle',
)

# Minute data (if bundle supports it)
results = run_algorithm(
    ...,
    data_frequency='minute',
    bundle='my-minute-bundle',
)
```

## Troubleshooting

### Bundle Not Found

```
Error: No bundle registered with name 'my-bundle'
```

**Solution**:
```python
# Make sure to register before use
from zipline.data.bundles import register, bundles

# Check what's registered
print(list(bundles.keys()))

# Register your bundle
register('my-bundle', ...)
```

### Ingestion Fails

```
Error: Failed to ingest bundle
```

**Checklist**:
1. Check API key (for NASDAQ):
   ```bash
   echo $NASDAQ_DATA_LINK_API_KEY
   ```

2. Check internet connection:
   ```bash
   ping data.nasdaq.com
   ```

3. Check disk space:
   ```bash
   df -h ~/.zipline
   ```

4. Check permissions:
   ```bash
   ls -la ~/.zipline/data
   ```

5. Try with verbose output:
   ```bash
   zipline --verbose ingest -b my-bundle
   ```

### Asset Not Found in Bundle

```
Error: Symbol 'AAPL' not found in bundle
```

**Solution**:
1. Check if ticker is in bundle configuration
2. Verify ingestion completed successfully
3. Check date range:
   ```python
   # Asset might not exist at requested date
   # Use as_of_date parameter
   asset = asset_finder.lookup_symbol('AAPL', as_of_date=pd.Timestamp('2020-01-01'))
   ```

### Old Data

```
Data seems outdated
```

**Solution**:
```bash
# Re-ingest to get latest data
zipline ingest -b my-bundle

# Or clean and re-ingest
zipline clean -b my-bundle
zipline ingest -b my-bundle
```

### Memory Issues

```
Error: Out of memory during ingestion
```

**Solution**:
1. Reduce ticker list
2. Shorten date range
3. Increase swap space (Linux)
4. Close other applications

### Performance Issues

**Slow backtests**:

1. **Check bundle format**: Ensure using bcolz (not SQLite)
2. **Reduce universe**: Fewer assets = faster backtests
3. **Optimize strategy**: Reduce computation in handle_data
4. **Use before_trading_start**: Move heavy calculations out of handle_data

## Bundle Storage

### Location

Bundles are stored in:
```
~/.zipline/data/
└── [bundle-name]/
    ├── [timestamp]/
    │   ├── daily_equities.bcolz/
    │   ├── adjustments.sqlite
    │   └── assets-7.sqlite
    └── [timestamp]/
        └── ...
```

### Size Management

```bash
# Check bundle sizes
du -sh ~/.zipline/data/*

# Clean old ingestions (keep last 3)
zipline clean -b my-bundle --keep-last 3

# Remove specific bundle
rm -rf ~/.zipline/data/my-bundle

# Clean all bundles
zipline clean --all
```

### Backup

```bash
# Backup all bundles
tar -czf zipline-bundles-backup.tar.gz ~/.zipline/data/

# Restore
tar -xzf zipline-bundles-backup.tar.gz -C ~/
```

## Best Practices

1. **Update After Market Close**: Run updates at 5 PM ET or later
2. **Keep Multiple Ingestions**: Store 3-5 recent versions as backup
3. **Monitor Updates**: Check logs for failures
4. **Test Before Production**: Verify bundle data before trading
5. **Document Configuration**: Keep bundle configs in version control
6. **Separate Bundles**: Use different bundles for different strategies
7. **Regular Cleaning**: Clean old ingestions monthly
8. **Backup Important Bundles**: Backup before major changes

## Next Steps

- Build [trading strategies](../notebooks/05_backtesting_with_bundles.ipynb)
- Learn [Pipeline API](./CUSTOM_DATA.md)
- Set up [automated updates](#automated-updates)
- Explore [advanced strategies](../examples/)

## Resources

- [Zipline Documentation](https://zipline.ml4trading.io/)
- [Bundle System](https://zipline.ml4trading.io/bundles.html)
- [TradingAlgorithm API](https://zipline.ml4trading.io/api-reference.html)
- [NASDAQ Data Link](https://data.nasdaq.com/)
- [Yahoo Finance](https://finance.yahoo.com/)
