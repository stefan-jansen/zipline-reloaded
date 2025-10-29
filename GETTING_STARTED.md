# Getting Started with Zipline-Reloaded

Complete guide to clone this repository and start backtesting in minutes.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Clone the Repository](#clone-the-repository)
3. [Quick Start with Docker](#quick-start-with-docker)
4. [Setup Data Bundles](#setup-data-bundles)
5. [Run Your First Backtest](#run-your-first-backtest)
6. [Daily Workflow](#daily-workflow)
7. [Next Steps](#next-steps)

---

## Prerequisites

### Required

- **Git** - To clone the repository
- **Docker** and **Docker Compose** - For running the environment

### Check Prerequisites

```bash
# Check Git
git --version
# Should show: git version 2.x.x

# Check Docker
docker --version
# Should show: Docker version 20.x.x or higher

# Check Docker Compose
docker compose version
# Should show: Docker Compose version v2.x.x or higher

# Note: Modern Docker uses 'docker compose' (not 'docker-compose')
# The file is still named docker-compose.yml but the command is 'docker compose'
```

### Install Prerequisites

**Ubuntu/Debian:**
```bash
# Install Git
sudo apt update
sudo apt install -y git

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
newgrp docker

# Install Docker Compose
sudo apt install -y docker compose
```

**macOS:**
```bash
# Install Git (if not already installed)
brew install git

# Install Docker Desktop (includes Docker Compose)
# Download from: https://www.docker.com/products/docker-desktop
```

**Windows:**
```bash
# Install Git for Windows
# Download from: https://git-scm.com/download/win

# Install Docker Desktop (includes Docker Compose)
# Download from: https://www.docker.com/products/docker-desktop
```

---

## Clone the Repository

### Step 1: Choose Your Directory

```bash
# Navigate to where you want the project
cd ~  # Home directory
# Or
cd ~/projects  # Projects directory
# Or any location you prefer
```

### Step 2: Clone the Repo

```bash
# Clone from your fork (replace with your GitHub username)
git clone https://github.com/YOUR_USERNAME/zipline-reloaded.git

# Or clone from the main repository
git clone https://github.com/stefan-jansen/zipline-reloaded.git

# Navigate into the directory
cd zipline-reloaded
```

### Step 3: Verify Clone

```bash
# Check you're in the right directory
pwd
# Should show: /path/to/zipline-reloaded

# List files
ls -la
# Should see: Dockerfile, docker-compose.yml, notebooks/, scripts/, etc.
```

### Step 4: Checkout the CustomData Branch (If Using This Implementation)

```bash
# If you want the version with CustomData and Bundle features
git checkout claude/implement-custom-data-011CUXBP4M1HT2VGQGmKJkVf

# Verify you're on the right branch
git branch
# Should show: * claude/implement-custom-data-011CUXBP4M1HT2VGQGmKJkVf
```

---

## Quick Start with Docker

### Step 1: Configure Environment (Required)

```bash
# Copy the example environment file
cp .env.example .env

# Edit if you want to add API keys or change ports (optional)
nano .env
# Or use your preferred editor: vim, code, etc.
```

**Note:** The `.env` file is required by Docker Compose. Even if you don't add any API keys, you must create it from the example.

**Important settings in .env:**
```bash
# Jupyter port (default: 9000)
JUPYTER_PORT=9000

# API keys (optional, for premium data)
NASDAQ_DATA_LINK_API_KEY=your_key_here
```

### Step 2: Build and Start Docker

```bash
# Build the Docker image (first time only, takes 5-10 minutes)
docker compose build

# Start the container
docker compose up -d

# Verify it's running
docker compose ps
# Should show: zipline-reloaded-jupyter   Up
```

### Step 3: Access Jupyter Lab

```bash
# Open in your browser
open http://localhost:9000

# Or manually navigate to:
# http://localhost:9000
```

**No password required** - configured for local development.

### Step 4: Verify Installation

In Jupyter Lab, create a new notebook and run:

```python
import zipline
print(f"Zipline version: {zipline.__version__}")

from zipline.pipeline.data import CustomData
print("✓ CustomData available")

from zipline.data.bundles import bundles
print(f"✓ Bundle system available")

import yfinance as yf
import nasdaqdatalink
print("✓ Data sources available")
```

If all imports work, you're ready to go! 🎉

---

## Setup Data Bundles

### Option 1: Yahoo Finance (Free, No API Key)

```bash
# Setup Yahoo Finance bundle with default stocks
docker exec -it zipline-reloaded-jupyter python /scripts/manage_data.py setup --source yahoo

# Or with custom tickers
docker exec -it zipline-reloaded-jupyter python /scripts/manage_data.py setup --source yahoo --tickers AAPL,MSFT,GOOGL,AMZN,TSLA

# Verify bundle was created
docker exec -it zipline-reloaded-jupyter zipline bundles
# Should show: yahoo
```

**This will take 2-5 minutes** depending on the number of stocks and your internet speed.

### Option 2: NASDAQ Data Link (Requires API Key)

**IMPORTANT NOTE ABOUT FREE WIKI DATASET:**
The free WIKI dataset was discontinued on March 27, 2018 and contains NO data after that date. It's only useful for historical backtests before 2018. For current data, you need:
- **Yahoo Finance bundle (free)** - Recommended for most users
- **NASDAQ EOD dataset (premium)** - Requires paid subscription

**First, get your API key:**
1. Sign up at [NASDAQ Data Link](https://data.nasdaq.com/)
2. Go to Account Settings → API Key
3. Copy your key

**Then setup with premium EOD dataset:**

```bash
# Add API key to .env file
echo "NASDAQ_DATA_LINK_API_KEY=your_actual_key_here" >> .env

# Restart container to load the key
docker compose restart

# Setup NASDAQ bundle with EOD (premium, current data)
docker exec -it zipline-reloaded-jupyter python /scripts/manage_data.py setup --source nasdaq --dataset EOD

# Verify
docker exec -it zipline-reloaded-jupyter zipline bundles
# Should show: nasdaq
```

**For historical backtests only (pre-2018), you can use WIKI:**

```bash
# Setup NASDAQ bundle with WIKI (free, but discontinued March 2018)
docker exec -it zipline-reloaded-jupyter python /scripts/manage_data.py setup --source nasdaq --dataset WIKI

# Note: Data will be automatically capped at 2018-03-27
```

### Verify Bundle Data

```bash
# List all bundles
docker exec -it zipline-reloaded-jupyter python /scripts/manage_data.py list

# Check bundle size
docker exec -it zipline-reloaded-jupyter du -sh /root/.zipline/data/*
```

---

## Run Your First Backtest

### Method 1: Using Example Notebook (Recommended)

1. **Open Jupyter Lab** at http://localhost:9000
2. **Navigate to** `notebooks/05_backtesting_with_bundles.ipynb`
3. **Run all cells** (Cell → Run All)

This notebook contains a complete working example with explanations.

### Method 2: Quick Python Script

Create a new notebook or Python file:

```python
import pandas as pd
from zipline import run_algorithm
from zipline.api import order_target_percent, symbol, record
from zipline.finance import commission, slippage

def initialize(context):
    """Called once at the start"""
    # Our stocks
    context.stocks = [
        symbol('AAPL'),
        symbol('MSFT'),
        symbol('GOOGL'),
    ]

    # Set realistic costs
    context.set_commission(commission.PerShare(cost=0.001, min_trade_cost=1.0))
    context.set_slippage(slippage.VolumeShareSlippage())

    print(f"✓ Strategy initialized with {len(context.stocks)} stocks")

def handle_data(context, data):
    """Called every trading day"""
    # Equal weight portfolio
    weight = 1.0 / len(context.stocks)

    # Rebalance
    for stock in context.stocks:
        if data.can_trade(stock):
            order_target_percent(stock, weight)

    # Record metrics
    record(
        portfolio_value=context.portfolio.portfolio_value,
        cash=context.portfolio.cash,
    )

# Run the backtest
print("Starting backtest...")
results = run_algorithm(
    start=pd.Timestamp('2022-01-01', tz='UTC'),
    end=pd.Timestamp('2023-12-31', tz='UTC'),
    initialize=initialize,
    handle_data=handle_data,
    capital_base=100000,  # $100,000 starting capital
    bundle='yahoo',       # Use Yahoo bundle data
)

# Display results
print("\n" + "="*60)
print("BACKTEST RESULTS")
print("="*60)

initial_value = 100000
final_value = results['portfolio_value'].iloc[-1]
total_return = (final_value - initial_value) / initial_value

print(f"Initial Capital:  ${initial_value:,.2f}")
print(f"Final Value:      ${final_value:,.2f}")
print(f"Total Return:     {total_return*100:+.2f}%")
print(f"Sharpe Ratio:     {results['sharpe'].iloc[-1]:.2f}")
print(f"Max Drawdown:     {results['max_drawdown'].min()*100:.2f}%")
print("="*60)
```

**Expected output:**
```
✓ Strategy initialized with 3 stocks
Starting backtest...
[2022-01-03 00:00:00+00:00] INFO: Performance: Simulated 503 trading days...

============================================================
BACKTEST RESULTS
============================================================
Initial Capital:  $100,000.00
Final Value:      $115,234.56
Total Return:     +15.23%
Sharpe Ratio:     1.23
Max Drawdown:     -8.45%
============================================================
```

### Method 3: From Terminal

Create a file `my_strategy.py` in the notebooks directory, then:

```bash
docker exec -it zipline-reloaded-jupyter python /notebooks/my_strategy.py
```

---

## Daily Workflow

### Morning: Update Data (Optional Manual Update)

```bash
# Update all bundles with latest data
docker exec -it zipline-reloaded-jupyter python /scripts/manage_data.py update --all
```

### During the Day: Develop & Test

1. **Open Jupyter** at http://localhost:9000
2. **Work on your strategy** in notebooks
3. **Run backtests** using bundle data
4. **Analyze results** with pandas and matplotlib

### Evening: Automated Updates

Set up automatic daily updates (runs at 5 PM ET):

```bash
# Add to your crontab (on host machine)
(crontab -l 2>/dev/null; echo "0 17 * * 1-5 docker exec zipline-reloaded-jupyter python /scripts/manage_data.py update --all >> /var/log/zipline_update.log 2>&1") | crontab -

# Verify cron was added
crontab -l
```

---

## Next Steps

### Explore Example Notebooks

All notebooks are in the `notebooks/` directory:

1. **`01_customdata_quickstart.ipynb`** - Learn CustomData basics
2. **`02_database_storage.ipynb`** - Persistent data storage
3. **`03_market_data_example.ipynb`** - Yahoo Finance integration
4. **`04_nasdaq_datalink_example.ipynb`** - Premium NASDAQ data
5. **`05_backtesting_with_bundles.ipynb`** - Complete backtesting guide

### Read the Documentation

- [Bundle System Guide](docs/BUNDLES.md) - Complete bundle documentation
- [CustomData Guide](docs/CUSTOM_DATA.md) - Custom data integration
- [Docker Guide](README_DOCKER.md) - Docker-specific setup
- [Docker Bundles Guide](docs/DOCKER_BUNDLES.md) - Bundles in Docker

### Build Your Strategy

1. **Start simple** - Buy and hold, moving average crossover
2. **Add complexity** - Multiple indicators, filters, risk management
3. **Backtest thoroughly** - Different time periods, market conditions
4. **Optimize carefully** - Avoid overfitting
5. **Paper trade** - Test with simulated money before going live

### Join the Community

- [ML4Trading Community](https://exchange.ml4trading.io)
- [GitHub Issues](https://github.com/stefan-jansen/zipline-reloaded/issues)
- [Documentation](https://zipline.ml4trading.io)

---

## Common Commands Reference

### Docker Management

```bash
# Start containers
docker compose up -d

# Stop containers
docker compose down

# Restart containers
docker compose restart

# View logs
docker compose logs -f

# Access container shell
docker exec -it zipline-reloaded-jupyter bash

# Rebuild after code changes
docker compose build
```

### Bundle Management

```bash
# Setup new bundle
docker exec -it zipline-reloaded-jupyter python /scripts/manage_data.py setup --source yahoo

# Update bundles
docker exec -it zipline-reloaded-jupyter python /scripts/manage_data.py update --all

# List bundles
docker exec -it zipline-reloaded-jupyter zipline bundles

# Clean old data
docker exec -it zipline-reloaded-jupyter python /scripts/manage_data.py clean --bundle yahoo --keep-last 3
```

### Jupyter Access

```bash
# Open Jupyter Lab
open http://localhost:9000

# Or find the URL with token
docker logs zipline-reloaded-jupyter 2>&1 | grep "http://127.0.0.1"
```

---

## Troubleshooting

### Container Won't Start

```bash
# Check Docker is running
docker ps

# Check logs for errors
docker compose logs

# Rebuild and try again
docker compose down
docker compose build --no-cache
docker compose up -d
```

### Can't Access Jupyter

```bash
# Verify container is running
docker compose ps

# Check port mapping
docker port zipline-reloaded-jupyter

# Try alternate URL
open http://127.0.0.1:9000
```

### Bundle Ingestion Fails

```bash
# Check internet connection
ping data.nasdaq.com

# Verify API key (for NASDAQ)
docker exec -it zipline-reloaded-jupyter env | grep NASDAQ

# Check disk space
df -h

# Try with verbose output
docker exec -it zipline-reloaded-jupyter zipline --verbose ingest -b yahoo
```

### Port Already in Use

If port 9000 is already in use:

```bash
# Edit .env file
echo "JUPYTER_PORT=9001" >> .env

# Restart
docker compose restart

# Access at new port
open http://localhost:9001
```

---

## Getting Help

### Before Asking for Help

1. **Check the logs**: `docker compose logs`
2. **Search existing issues**: [GitHub Issues](https://github.com/stefan-jansen/zipline-reloaded/issues)
3. **Read the docs**: [Documentation](https://zipline.ml4trading.io)

### How to Ask for Help

Include:
1. **What you're trying to do**
2. **What happened** (error messages, logs)
3. **Your environment** (OS, Docker version)
4. **Steps to reproduce**

### Resources

- [GitHub Issues](https://github.com/stefan-jansen/zipline-reloaded/issues)
- [Community Forum](https://exchange.ml4trading.io)
- [Documentation](https://zipline.ml4trading.io)

---

## Summary

You should now have:

✅ Cloned the repository
✅ Docker environment running
✅ Jupyter Lab accessible at http://localhost:9000
✅ At least one data bundle set up (Yahoo or NASDAQ)
✅ Run your first backtest successfully
✅ Understand the daily workflow

**Next**: Explore the example notebooks and start building your trading strategies!

Happy backtesting! 🚀
