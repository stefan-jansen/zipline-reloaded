# Sharadar Bundle - Complete Guide

## Overview

Sharadar is a **premium, institutional-grade dataset** from NASDAQ Data Link that provides the highest quality US equity data available. This guide will help you set up and use Sharadar data with zipline-reloaded.

## What is Sharadar?

Sharadar provides comprehensive financial data for US equities:

- **SEP (Sharadar Equity Prices)**: Daily OHLCV pricing data
- **SF1 (Sharadar Fundamentals)**: Fundamental data (revenue, earnings, ratios, etc.)
- **SF3 (Sharadar Institutional Holdings)**: 13-F institutional ownership data
- **ACTIONS**: Corporate actions (splits, dividends, etc.)
- **TICKERS**: Ticker metadata and classification

For zipline bundles, we primarily use the **SEP** (pricing) and **ACTIONS** (corporate actions) tables.

## Why Choose Sharadar?

### Advantages Over Free Data Sources

| Feature | Sharadar | Yahoo Finance | NASDAQ WIKI |
|---------|----------|---------------|-------------|
| **Data Quality** | Institutional-grade | Good | Good (discontinued) |
| **Coverage** | All US equities | Most US equities | ~3,000 tickers |
| **Point-in-Time** | ✅ Yes | ❌ No | ✅ Yes |
| **Corporate Actions** | Comprehensive | Basic | Basic |
| **Historical Depth** | Complete history | ~20 years | Up to 2018 only |
| **Support** | Professional | Community | None (discontinued) |
| **Cost** | $$$$ | Free | Free |
| **Update Frequency** | Daily | Daily | Discontinued 2018 |

### When to Use Sharadar

**Use Sharadar if:**
- ✅ You're building professional trading strategies
- ✅ You need point-in-time accuracy for backtesting
- ✅ You require comprehensive fundamental data
- ✅ You need institutional-quality data
- ✅ You're doing academic research requiring high-quality data
- ✅ You can afford the subscription

**Use free alternatives if:**
- ✅ You're learning zipline (use Yahoo Finance)
- ✅ You're prototyping strategies (use Yahoo Finance)
- ✅ Budget is limited (use Yahoo Finance)
- ✅ You only need basic OHLCV data (use Yahoo Finance)

## Subscription

### Get a Subscription

1. **Visit**: [https://data.nasdaq.com/databases/SFA](https://data.nasdaq.com/databases/SFA)
2. **Click**: "Subscribe Now" or "Start Free Trial"
3. **Choose**: Sharadar Core US Equities (or Sharadar Core + Insiders)
4. **Complete**: Registration and payment

### Pricing (as of 2024)

Pricing varies based on user type and data access level. Contact NASDAQ for current pricing:
- **Individual traders**: Typically $200-500/month
- **Professional/Commercial**: Contact for pricing
- **Academic**: Discounted rates available
- **Free trial**: Usually 7-14 days available

### Get Your API Key

After subscribing:
1. Log in to NASDAQ Data Link
2. Go to **Account Settings**
3. Find **API Key** section
4. Copy your key (format: `abc123xyz...`)

## Installation

### Step 1: Add API Key

**Option A: Via .env file (Recommended)**

```bash
# Edit .env file
echo "NASDAQ_DATA_LINK_API_KEY=your_actual_key_here" >> .env

# Restart container
docker compose restart
```

**Option B: Via environment variable**

```bash
# Export in shell
export NASDAQ_DATA_LINK_API_KEY='your_actual_key_here'

# Or add to ~/.bashrc or ~/.zshrc for persistence
echo "export NASDAQ_DATA_LINK_API_KEY='your_actual_key_here'" >> ~/.bashrc
source ~/.bashrc
```

### Step 2: Verify API Key

```bash
# Test API connection (inside container)
docker exec -it zipline-reloaded-jupyter python3 -c "
import os
import requests
api_key = os.environ.get('NASDAQ_DATA_LINK_API_KEY')
print(f'API Key: {api_key[:10]}...' if api_key else 'API Key not set!')

# Test API access
url = f'https://data.nasdaq.com/api/v3/datatables/SHARADAR/TICKERS.json?qopts.export=false&api_key={api_key}'
r = requests.get(url)
if r.status_code == 200:
    print('✓ API key is valid!')
else:
    print(f'✗ API error: {r.status_code}')
"
```

## Usage

### Option 1: Specific Tickers (Recommended for Testing)

**Best for**: Learning, development, testing strategies

```bash
# Setup with specific tickers
docker exec -it zipline-reloaded-jupyter python /scripts/manage_data.py setup \
    --source sharadar \
    --tickers AAPL,MSFT,GOOGL,AMZN,TSLA,META,NVDA,NFLX \
    --name sharadar-test

# This will:
# - Download only specified tickers
# - Take 2-5 minutes
# - Use ~100-500 MB storage
```

### Option 2: Pre-configured Bundles

**Tech Stocks (15 tickers)**:
```bash
docker exec -it zipline-reloaded-jupyter python /scripts/manage_data.py setup \
    --source sharadar \
    --name sharadar-tech \
    --tickers AAPL,MSFT,GOOGL,AMZN,META,NVDA,TSLA,NFLX,ADBE,CRM,INTC,AMD,ORCL,CSCO,AVGO
```

**S&P 500 Sample (30 tickers)**:
```bash
docker exec -it zipline-reloaded-jupyter python /scripts/manage_data.py setup \
    --source sharadar \
    --name sharadar-sp500 \
    --tickers AAPL,MSFT,GOOGL,AMZN,NVDA,META,TSLA,BRK.B,V,UNH,JPM,JNJ,WMT,MA,PG,XOM,CVX,HD,MRK,ABBV,PFE,KO,PEP,COST,AVGO,TMO,DIS,CSCO,ABT,ACN
```

### Option 3: ALL US Equities (Production Use)

**Best for**: Production systems, comprehensive strategies

```bash
# WARNING: This downloads ~8,000+ tickers
# - Download time: 10-30 minutes
# - Storage: 10-20 GB
# - First run will take longer

docker exec -it zipline-reloaded-jupyter python /scripts/manage_data.py setup \
    --source sharadar \
    --name sharadar-all

# You will be prompted to confirm
```

### Verify Bundle

```bash
# List bundles
docker exec -it zipline-reloaded-jupyter zipline bundles

# Check bundle size
docker exec -it zipline-reloaded-jupyter du -sh /root/.zipline/data/sharadar*

# Inspect bundle contents
docker exec -it zipline-reloaded-jupyter python3 -c "
from zipline.data.bundles import load
bundle_data = load('sharadar-test')
assets = bundle_data.asset_finder.retrieve_all(bundle_data.asset_finder.sids)
print(f'Bundle contains {len(assets)} assets')
for asset in assets[:10]:
    print(f'  {asset.symbol}: {asset.start_date} to {asset.end_date}')
"
```

## Using Sharadar in Backtests

### Basic Example

```python
import pandas as pd
from zipline import run_algorithm
from zipline.api import order_target_percent, symbol, record

def initialize(context):
    """Setup strategy"""
    context.stocks = [
        symbol('AAPL'),
        symbol('MSFT'),
        symbol('GOOGL'),
    ]

def handle_data(context, data):
    """Execute strategy"""
    # Equal weight portfolio
    weight = 1.0 / len(context.stocks)

    for stock in context.stocks:
        order_target_percent(stock, weight)

# Run backtest with Sharadar data
results = run_algorithm(
    start=pd.Timestamp('2020-01-01', tz='UTC'),
    end=pd.Timestamp('2023-12-31', tz='UTC'),
    initialize=initialize,
    handle_data=handle_data,
    capital_base=100000,
    bundle='sharadar-test',  # Use your bundle name
)

print(results.head())
```

### Advanced: Using Pipeline with Sharadar

```python
from zipline.pipeline import Pipeline
from zipline.pipeline.factors import SimpleMovingAverage, Returns
from zipline.api import attach_pipeline, pipeline_output

def initialize(context):
    # Create pipeline
    pipe = Pipeline()

    # Add factors
    sma_20 = SimpleMovingAverage(inputs=[USEquityPricing.close], window_length=20)
    sma_50 = SimpleMovingAverage(inputs=[USEquityPricing.close], window_length=50)
    returns = Returns(window_length=5)

    pipe.add(sma_20, 'sma_20')
    pipe.add(sma_50, 'sma_50')
    pipe.add(returns, 'returns')

    # Attach pipeline
    attach_pipeline(pipe, 'my_pipeline')

def before_trading_start(context, data):
    # Get pipeline output
    context.pipeline_data = pipeline_output('my_pipeline')

    # Filter: SMA crossover
    context.longs = context.pipeline_data[
        context.pipeline_data.sma_20 > context.pipeline_data.sma_50
    ].index

def handle_data(context, data):
    # Trade based on pipeline signals
    weight = 1.0 / len(context.longs) if context.longs else 0

    for stock in context.longs:
        order_target_percent(stock, weight)
```

## Daily Updates

### Manual Update

```bash
# Update specific bundle
docker exec -it zipline-reloaded-jupyter zipline ingest -b sharadar-test

# Or using management script
docker exec -it zipline-reloaded-jupyter python /scripts/manage_data.py update --bundle sharadar-test
```

### Automated Updates

**Using host cron** (recommended):

```bash
# Edit crontab
crontab -e

# Add line to run at 6 PM ET, Monday-Friday (after market close + data availability)
0 18 * * 1-5 docker exec zipline-reloaded-jupyter python /scripts/manage_data.py update --bundle sharadar-test >> /var/log/zipline-sharadar-update.log 2>&1
```

**Inside Docker container**:

```bash
# Enter container
docker exec -it zipline-reloaded-jupyter bash

# Install cron
apt-get update && apt-get install -y cron

# Add cron job
echo "0 18 * * 1-5 python /scripts/manage_data.py update --bundle sharadar-test" | crontab -

# Start cron
service cron start
```

## Best Practices

### 1. Start Small, Scale Up

```bash
# Step 1: Test with few tickers
docker exec -it zipline-reloaded-jupyter python /scripts/manage_data.py setup \
    --source sharadar --tickers AAPL,MSFT --name sharadar-test

# Step 2: Verify backtest works
# (Run your strategy)

# Step 3: Expand to production tickers
docker exec -it zipline-reloaded-jupyter python /scripts/manage_data.py setup \
    --source sharadar --tickers [your full list] --name sharadar-prod
```

### 2. Use Multiple Bundles

```bash
# Development bundle (fast ingestion, quick testing)
sharadar-dev: 10-20 tickers

# Staging bundle (medium size, realistic testing)
sharadar-stage: 50-100 tickers

# Production bundle (full universe or sector)
sharadar-prod: 500+ tickers or all
```

### 3. Monitor API Usage

Sharadar has API rate limits. Monitor your usage:

```python
import requests
api_key = 'your_key'
url = f'https://data.nasdaq.com/api/v3/datatables/SHARADAR/SEP.json?api_key={api_key}'
r = requests.get(url)
print(f"Rate limit: {r.headers.get('X-RateLimit-Limit')}")
print(f"Remaining: {r.headers.get('X-RateLimit-Remaining')}")
```

### 4. Backup Your Bundles

```bash
# Backup bundle data
docker exec zipline-reloaded-jupyter tar -czf /data/sharadar-backup.tar.gz /root/.zipline/data/sharadar*

# Copy to host
docker cp zipline-reloaded-jupyter:/data/sharadar-backup.tar.gz ./backups/

# Restore if needed
docker cp ./backups/sharadar-backup.tar.gz zipline-reloaded-jupyter:/data/
docker exec zipline-reloaded-jupyter tar -xzf /data/sharadar-backup.tar.gz -C /
```

### 5. Keep Multiple Ingestions

```bash
# Clean old ingestions but keep last 5
docker exec zipline-reloaded-jupyter zipline clean -b sharadar-prod --keep-last 5

# This allows rollback if latest ingestion has issues
```

## Troubleshooting

### API Key Not Working

```bash
# Check if key is set
docker exec zipline-reloaded-jupyter env | grep NASDAQ

# Verify key is valid
docker exec zipline-reloaded-jupyter python3 -c "
import os
import requests
api_key = os.environ.get('NASDAQ_DATA_LINK_API_KEY')
url = f'https://data.nasdaq.com/api/v3/datatables/SHARADAR/TICKERS.json?qopts.export=false&api_key={api_key}'
r = requests.get(url)
print(f'Status: {r.status_code}')
print(r.json() if r.status_code == 200 else r.text)
"
```

### Subscription Not Active

**Error**: "You do not have permission to access this dataset"

**Solution**: Verify your subscription at [NASDAQ Data Link Account](https://data.nasdaq.com/account/profile)

### Ingestion Timeout

**Error**: Download times out or fails

**Solution**:
```bash
# For large downloads, increase timeout in sharadar_bundle.py
# Or download in smaller batches by specifying ticker lists
```

### Memory Issues

**Error**: Out of memory during ingestion

**Solution**:
```bash
# Increase Docker memory limit
# Docker Desktop → Settings → Resources → Memory → Increase to 8+ GB

# Or ingest in batches
docker exec -it zipline-reloaded-jupyter python /scripts/manage_data.py setup \
    --source sharadar --tickers AAPL,MSFT,GOOGL --name sharadar-batch1

docker exec -it zipline-reloaded-jupyter python /scripts/manage_data.py setup \
    --source sharadar --tickers AMZN,META,NVDA --name sharadar-batch2
```

## FAQ

### Q: Can I use Sharadar fundamental data (SF1)?

**A:** The current bundle implementation focuses on pricing data (SEP). For fundamentals, you can:
1. Use CustomData to load SF1 into Pipeline (recommended)
2. Extend the bundle to include fundamental factors
3. Access SF1 directly via API during backtests

### Q: How does point-in-time data work?

**A:** Sharadar provides data "as it was known" on each date. For example, if a company's revenue was later restated, the historical backtest will use the original value, not the restated value. This prevents look-ahead bias.

### Q: Can I share bundles with my team?

**A:** Yes, you can export bundles and share them:
```bash
# Export
tar -czf sharadar-bundle.tar.gz ~/.zipline/data/sharadar*

# Import on another machine
tar -xzf sharadar-bundle.tar.gz -C ~/.zipline/
```

**Note**: All team members need valid Sharadar subscriptions for API updates.

### Q: What's the difference between Sharadar and NASDAQ EOD?

**A:**
- **Sharadar**: Premium dataset with point-in-time data, fundamentals, and institutional ownership
- **NASDAQ EOD**: Basic end-of-day pricing data
- **Use Sharadar** for serious backtesting and research
- **Use EOD** for basic pricing if you don't need fundamentals

## Next Steps

- Read [BUNDLES.md](./BUNDLES.md) for general bundle documentation
- See [notebooks/05_backtesting_with_bundles.ipynb](../notebooks/05_backtesting_with_bundles.ipynb) for examples
- Explore [Sharadar documentation](https://data.nasdaq.com/databases/SFA/documentation) for data dictionary
- Join [ML4Trading community](https://exchange.ml4trading.io) for discussions

## Resources

- [Sharadar Product Page](https://data.nasdaq.com/databases/SFA)
- [Sharadar Documentation](https://data.nasdaq.com/databases/SFA/documentation)
- [NASDAQ Data Link API Docs](https://docs.data.nasdaq.com/)
- [Zipline Bundle System](https://zipline.ml4trading.io/bundles.html)
- [ML4Trading Book](https://www.ml4trading.io/) - Excellent resource using Sharadar data
