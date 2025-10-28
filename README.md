<p align="center">
<a href="https://zipline.ml4trading.io">
<img src="https://i.imgur.com/DDetr8I.png" width="25%">
</a>
</p>

# Backtest your Trading Strategies

| Version Info        | [![Python](https://img.shields.io/pypi/pyversions/zipline-reloaded.svg?cacheSeconds=2592000)](https://pypi.python.org/pypi/zipline-reloaded) [![Anaconda-Server Badge](https://anaconda.org/ml4t/zipline-reloaded/badges/platforms.svg)](https://anaconda.org/ml4t/zipline-reloaded) ![PyPI](https://img.shields.io/pypi/v/zipline-reloaded) [![Anaconda-Server Badge](https://anaconda.org/conda-forge/zipline-reloaded/badges/version.svg)](https://anaconda.org/conda-forge/zipline-reloaded)                                                                                                                                                                                                 |
| ------------------- | ---------- |
| **Test** **Status** | [![CI Tests](https://github.com/stefan-jansen/zipline-reloaded/actions/workflows/ci_tests_full.yml/badge.svg)](https://github.com/stefan-jansen/zipline-reloaded/actions/workflows/unit_tests.yml) [![PyPI](https://github.com/stefan-jansen/zipline-reloaded/actions/workflows/build_wheels.yml/badge.svg)](https://github.com/stefan-jansen/zipline-reloaded/actions/workflows/build_wheels.yml)  [![codecov](https://codecov.io/gh/stefan-jansen/zipline-reloaded/branch/main/graph/badge.svg)](https://codecov.io/gh/stefan-jansen/zipline-reloaded) |
| **Community**       | [![Discourse](https://img.shields.io/discourse/topics?server=https%3A%2F%2Fexchange.ml4trading.io%2F)](https://exchange.ml4trading.io) [![ML4T](https://img.shields.io/badge/Powered%20by-ML4Trading-blue)](https://ml4trading.io) [![Twitter](https://img.shields.io/twitter/follow/ml4trading.svg?style=social)](https://twitter.com/ml4trading)                                                                                                                                                                                                                                                                                                                                                                                                          |

Zipline is a Pythonic event-driven system for backtesting, developed and used as the backtesting and live-trading engine by [crowd-sourced investment fund Quantopian](https://www.bizjournals.com/boston/news/2020/11/10/quantopian-shuts-down-cofounders-head-elsewhere.html). Since it closed late 2020, the domain that had hosted these docs expired. The library is used extensively in the book [Machine Larning for Algorithmic Trading](https://ml4trading.io)
by [Stefan Jansen](https://www.linkedin.com/in/applied-ai/) who is trying to keep the library up to date and available to his readers and the wider Python algotrading community.
- [Join our Community!](https://exchange.ml4trading.io)
- [Documentation](https://zipline.ml4trading.io)

## Features

- **Ease of Use:** Zipline tries to get out of your way so that you can focus on algorithm development. See below for a code example.
- **Batteries Included:** many common statistics like moving average and linear regression can be readily accessed from within a user-written algorithm.
- **PyData Integration:** Input of historical data and output of performance statistics are based on Pandas DataFrames to integrate nicely into the existing PyData ecosystem.
- **Statistics and Machine Learning Libraries:** You can use libraries like matplotlib, scipy, statsmodels, and scikit-klearn to support development, analysis, and visualization of state-of-the-art trading systems.
- **📊 NEW: CustomData Support:** Easily integrate your own datasets into Zipline pipelines with persistent database storage. [Learn more](#customdata-integration)
- **📦 NEW: Data Bundles:** Persistent, optimized storage for market data with Yahoo Finance and NASDAQ Data Link integrations. [Learn more](#data-bundles-for-backtesting)

> **Note:** Release 3.05 makes Zipline compatible with Numpy 2.0, which requires Pandas 2.2.2 or higher. If you are using an older version of Pandas, you will need to upgrade it. Other packages may also still take more time to catch up with the latest Numpy release.

> **Note:** Release 3.0 updates Zipline to use [pandas](https://pandas.pydata.org/pandas-docs/stable/whatsnew/v2.0.0.html) >= 2.0 and [SQLAlchemy](https://docs.sqlalchemy.org/en/20/) > 2.0. These are major version updates that may break existing code; please review the linked docs.

> **Note:** Release 2.4 updates Zipline to use [exchange_calendars](https://github.com/gerrymanoim/exchange_calendars) >= 4.2. This is a major version update and may break existing code (which we have tried to avoid but cannot guarantee). Please review the changes [here](https://github.com/gerrymanoim/exchange_calendars/issues/61).

## Installation

Zipline supports Python >= 3.9 and is compatible with current versions of the relevant [NumFOCUS](https://numfocus.org/sponsored-projects?_sft_project_category=python-interface) libraries, including [pandas](https://pandas.pydata.org/) and [scikit-learn](https://scikit-learn.org/stable/index.html).

### 🐳 Using Docker (Recommended for Quick Start)

The fastest way to get started with Zipline-Reloaded and Jupyter notebooks:

```bash
# Clone the repository
git clone https://github.com/stefan-jansen/zipline-reloaded.git
cd zipline-reloaded

# Start with Docker Compose
docker-compose up -d

# Access Jupyter Lab at http://localhost:9000
# Notebooks with examples are pre-loaded!
```

**What's included:**
- ✅ Pre-configured Jupyter Lab environment
- ✅ All dependencies installed
- ✅ Example notebooks ready to run
- ✅ Persistent storage for data and notebooks

[📖 See complete Docker setup guide](README_DOCKER.md)

### Using `pip`

If your system meets the pre-requisites described in the [installation instructions](https://zipline.ml4trading.io/install.html), you can install Zipline using `pip` by running:

```bash
# Install build dependencies first
pip install -r requirements-build.txt

# Install zipline-reloaded
pip install zipline-reloaded

# Or install from source
git clone https://github.com/stefan-jansen/zipline-reloaded.git
cd zipline-reloaded
pip install -e .
```

[📖 Detailed installation instructions](INSTALLATION.md)

### Using `conda`

If you are using the [Anaconda](https://www.anaconda.com/products/individual) or [miniconda](https://docs.conda.io/en/latest/miniconda.html) distributions, you install `zipline-reloaded` from the channel `conda-forge` like so:

```bash
conda install -c conda-forge zipline-reloaded
```

You can also [enable](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-channels.html) `conda-forge` by listing it in your `.condarc`.

In case you are installing `zipline-reloaded` alongside other packages and encounter [conflict errors](https://github.com/conda/conda/issues/9707), consider using [mamba](https://github.com/mamba-org/mamba) instead.

See the [installation](https://zipline.ml4trading.io/install.html) section of the docs for more detailed instructions and the corresponding [conda-forge site](https://github.com/conda-forge/zipline-reloaded-feedstock).

## Quickstart

See our [getting started tutorial](https://zipline.ml4trading.io/beginner-tutorial).

The following code implements a simple dual moving average algorithm.

```python
from zipline.api import order_target, record, symbol


def initialize(context):
    context.i = 0
    context.asset = symbol('AAPL')


def handle_data(context, data):
    # Skip first 300 days to get full windows
    context.i += 1
    if context.i < 300:
        return

    # Compute averages
    # data.history() has to be called with the same params
    # from above and returns a pandas dataframe.
    short_mavg = data.history(context.asset, 'price', bar_count=100, frequency="1d").mean()
    long_mavg = data.history(context.asset, 'price', bar_count=300, frequency="1d").mean()

    # Trading logic
    if short_mavg > long_mavg:
        # order_target orders as many shares as needed to
        # achieve the desired number of shares.
        order_target(context.asset, 100)
    elif short_mavg < long_mavg:
        order_target(context.asset, 0)

    # Save values for later inspection
    record(AAPL=data.current(context.asset, 'price'),
           short_mavg=short_mavg,
           long_mavg=long_mavg)
```

You can then run this algorithm using the Zipline CLI. But first, you need to download some market data with historical prices and trading volumes.

This will download asset pricing data from [NASDAQ](https://data.nasdaq.com/databases/WIKIP) (formerly [Quandl](https://www.nasdaq.com/about/press-center/nasdaq-acquires-quandl-advance-use-alternative-data)).

> This requires an API key, which you can get for free by signing up at [NASDAQ Data Link](https://data.nasdaq.com).

```bash
$ export QUANDL_API_KEY="your_key_here"
$ zipline ingest -b quandl
````

The following will 
- stream the through the algorithm over the specified time range. 
- save the resulting performance DataFrame as `dma.pickle`, which you can load and analyze from Python using, e.g., [pyfolio-reloaded](https://github.com/stefan-jansen/pyfolio-reloaded).

```bash
$ zipline run -f dual_moving_average.py --start 2014-1-1 --end 2018-1-1 -o dma.pickle --no-benchmark
```

You can find other examples in the [zipline/examples](https://github.com/stefan-jansen/zipline-reloaded/tree/main/src/zipline/examples) directory.

## CustomData Integration

**New in this fork:** Zipline-Reloaded now supports easy integration of custom datasets with persistent database storage!

### Quick Example

```python
from zipline.pipeline.data import CustomData, create_custom_db, insert_custom_data, from_db
from zipline.pipeline import Pipeline
import pandas as pd
import numpy as np

# 1. Create a custom dataset (in-memory)
MyData = CustomData(
    'MyData',
    columns={
        'sentiment': float,
        'revenue_growth': float,
        'analyst_rating': int,
    },
    missing_values={'analyst_rating': -1}
)

# Use in a pipeline
pipe = Pipeline(
    columns={
        'sentiment': MyData.sentiment.latest,
        'high_growth': MyData.revenue_growth.latest > 0.1,
    }
)

# 2. Or use persistent database storage
create_custom_db(
    'my-fundamentals',
    columns={'pe_ratio': float, 'market_cap': float}
)

# Insert your data
insert_custom_data('my-fundamentals', your_dataframe)

# Load and use
Fundamentals = from_db('my-fundamentals')
pipe = Pipeline(
    columns={'pe': Fundamentals.pe_ratio.latest}
)
```

### Features

- ✅ **Easy dataset creation** - Define custom datasets with simple Python syntax
- ✅ **Persistent storage** - SQLite-backed database storage for large datasets
- ✅ **Efficient querying** - Automatic date/asset filtering for optimal performance
- ✅ **Type safety** - Full numpy dtype support with validation
- ✅ **Seamless integration** - Works exactly like built-in Pipeline datasets

### Documentation

- [📘 CustomData User Guide](docs/CUSTOM_DATA.md) - Complete guide with examples
- [📗 Database Storage Guide](docs/CUSTOM_DATA_DATABASE.md) - Persistent storage documentation
- [📓 Jupyter Notebooks](notebooks/) - Interactive tutorials
- [💻 Example Scripts](examples/) - Ready-to-run examples

### Quick Start with Docker + Jupyter

Try CustomData interactively:

```bash
# Start Jupyter environment
docker-compose up -d

# Open http://localhost:9000
# Try the notebooks:
# - 01_customdata_quickstart.ipynb
# - 02_database_storage.ipynb
```

## 📦 Data Bundles for Backtesting

Zipline bundles provide persistent, optimized storage for market data. Perfect for backtesting with `run_algorithm()`.

### Quick Start with Bundles

```bash
# Setup Yahoo Finance bundle (free)
python scripts/manage_data.py setup --source yahoo

# Or NASDAQ Data Link (requires API key)
export NASDAQ_DATA_LINK_API_KEY=your_key
python scripts/manage_data.py setup --source nasdaq --dataset EOD

# Run backtest
python -c "
from zipline import run_algorithm
# ... your strategy ...
results = run_algorithm(..., bundle='yahoo')
"
```

### Bundle vs CustomData

| Feature | Bundles | CustomData |
|---------|---------|------------|
| **Best For** | Backtesting with `run_algorithm()` | Pipeline analysis & custom indicators |
| **Storage** | bcolz (highly optimized) | SQLite |
| **Performance** | Excellent | Good |
| **Updates** | `zipline ingest` command | Custom scripts |
| **Use Together?** | ✅ Yes! Complementary features | ✅ Yes! Complementary features |

### Available Bundles

**Yahoo Finance** (Free):
```python
from zipline.data.bundles import register
from zipline.data.bundles.yahoo_bundle import yahoo_bundle

register('my-yahoo', yahoo_bundle(tickers=['AAPL', 'MSFT', 'GOOGL']))
```

**NASDAQ Data Link** (Premium):
```python
from zipline.data.bundles.nasdaq_bundle import nasdaq_bundle

register('my-nasdaq', nasdaq_bundle(dataset='EOD'))
```

### Daily Updates

```bash
# Update specific bundle
zipline ingest -b my-bundle

# Update all bundles
python scripts/manage_data.py update --all

# Automate with cron (runs at 5 PM ET, Mon-Fri)
0 17 * * 1-5 cd /path/to/zipline && python scripts/manage_data.py update --all
```

### Documentation

- [📦 Bundle System Guide](docs/BUNDLES.md) - Complete bundle documentation
- [📓 Backtesting Notebook](notebooks/05_backtesting_with_bundles.ipynb) - Interactive tutorial
- [🔧 Management Script](scripts/manage_data.py) - Automated bundle management

## 🐳 Docker + Jupyter Setup

Get started in minutes with a pre-configured environment:

### Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/stefan-jansen/zipline-reloaded.git
cd zipline-reloaded

# 2. Start with Docker Compose
docker-compose up -d

# 3. Open Jupyter Lab
# Navigate to http://localhost:9000 in your browser
```

### What You Get

- 🐍 **Python 3.11** with zipline-reloaded
- 📓 **Jupyter Lab** for interactive development
- 📊 **Pre-loaded notebooks** with CustomData examples
- 💾 **Persistent storage** for databases and notebooks
- 📦 **All dependencies** pre-installed

### Common Commands

```bash
# Start the container
docker-compose up -d

# Stop the container
docker-compose down

# View logs
docker-compose logs -f

# Access container shell
docker exec -it zipline-reloaded-jupyter bash

# Rebuild after changes
docker-compose build
```

### Directory Structure

```
notebooks/          # Your Jupyter notebooks (persisted)
├── 01_customdata_quickstart.ipynb
├── 02_database_storage.ipynb
└── your_notebooks.ipynb

data/              # Your data files (persisted)
└── custom_databases/  # SQLite databases
```

**📖 Complete Docker guide:** [README_DOCKER.md](README_DOCKER.md)

## Questions, suggestions, bugs?

If you find a bug or have other questions about the library, feel free to [open an issue](https://github.com/stefan-jansen/zipline/issues/new) and fill out the template.
