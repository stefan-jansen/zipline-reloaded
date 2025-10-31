# Zipline-Reloaded Example Notebooks

This directory contains comprehensive examples for using zipline-reloaded with Sharadar professional data.

## 🗺️ Navigation

**NEW!** You now have full access to the entire project from Jupyter:

- 📁 **`project_root/`** - Full project directory (README, setup.py, etc.)
- 📜 **`scripts/`** - Data ingestion and utility scripts
- 💻 **`src/`** - Zipline source code
- 🧪 **`tests/`** - Test suite
- 📚 **`docs/`** - Documentation
- 📓 **`strategies_files/`** - Your trading strategies

👉 **See [NAVIGATION.md](./NAVIGATION.md) for a complete guide to navigating the project from Jupyter**

## 🌟 Recommended Starting Point

**👉 Start here: [`05_backtesting_with_bundles.ipynb`](./05_backtesting_with_bundles.ipynb)**

This notebook introduces backtesting with Sharadar data:

- ✅ Institutional-grade data quality
- ✅ Point-in-time accurate (no look-ahead bias)
- ✅ Built-in bundle system (easiest setup)
- ✅ Optimized for performance
- ✅ Comprehensive US equity coverage (~13,000 tickers)

**Quick Setup:**
```bash
# Set API key
export NASDAQ_DATA_LINK_API_KEY='your_key'

# Ingest specific tickers for testing
python scripts/manage_sharadar.py ingest --tickers AAPL,MSFT,GOOGL,AMZN,TSLA

# Check status
python scripts/manage_sharadar.py status
```

## 📚 All Notebooks

### Backtesting & Trading

| Notebook | Description | Difficulty |
|----------|-------------|------------|
| **05_backtesting_with_bundles.ipynb** | Introduction to backtesting | ⭐ Beginner |
| **06_sharadar_professional_backtesting.ipynb** | Advanced strategies with Pipeline | ⭐⭐ Intermediate |
| **07_pipeline_research.ipynb** | Stock screening and research | ⭐⭐ Intermediate |
| **08_run_external_strategy.ipynb** | Using external strategy files | ⭐ Beginner |

### Analysis

| Notebook | Description | Difficulty |
|----------|-------------|------------|
| **analyze_backtest_results.ipynb** | Performance analysis with pyfolio | ⭐⭐ Intermediate |

### Navigation

| Notebook | Description |
|----------|-------------|
| **00_quick_links.ipynb** | Quick navigation and helper tools |

## 📖 Learning Path

### 1. Beginner - Start Here

**First**: [`05_backtesting_with_bundles.ipynb`](./05_backtesting_with_bundles.ipynb)
- Learn bundle basics
- Write your first strategy
- Understand backtest results

**Then**: [`08_run_external_strategy.ipynb`](./08_run_external_strategy.ipynb)
- Use external strategy files
- Organize your code better
- Learn CLI usage

### 2. Intermediate

**Next**: [`06_sharadar_professional_backtesting.ipynb`](./06_sharadar_professional_backtesting.ipynb)
- Advanced trading strategies
- Pipeline for stock selection
- Moving averages and momentum

**Also**: [`07_pipeline_research.ipynb`](./07_pipeline_research.ipynb)
- Stock screening
- Custom factors
- Technical indicators

### 3. Advanced

**Finally**: [`analyze_backtest_results.ipynb`](./analyze_backtest_results.ipynb)
- Detailed performance metrics
- Risk analysis with pyfolio
- Tear sheets and reports

## 🚀 Setup Instructions

### Prerequisites

You need:
1. [Sharadar subscription](https://data.nasdaq.com/databases/SFA) from NASDAQ Data Link
2. Docker installed and running
3. API key from your NASDAQ Data Link account

### Quick Start

```bash
# 1. Set API key in .env file
echo "NASDAQ_DATA_LINK_API_KEY=your_key_here" >> .env

# 2. Start Docker
docker compose up -d

# 3. Access Jupyter at http://localhost:9000

# 4. In Jupyter terminal, ingest data
python scripts/manage_sharadar.py ingest --tickers AAPL,MSFT,GOOGL,AMZN,TSLA

# 5. Verify bundle
python scripts/manage_sharadar.py status
```

### Full Database (Production)

```bash
# Download all ~13,000 US equities (takes 10-30 minutes, ~15 GB)
python scripts/manage_sharadar.py ingest --all

# Inspect data
python scripts/inspect_bundle.py

# Check specific ticker
python scripts/inspect_bundle.py --ticker AAPL
```

## 🔧 Data Management

### Daily Updates

Sharadar data is updated daily. To update your bundle:

```bash
# Simple update
python scripts/manage_sharadar.py ingest --all
```

### Clean Old Data

```bash
# Keep last 3 ingestions, remove older ones
python scripts/manage_sharadar.py clean --keep-last 3
```

### Inspect Bundle

```bash
# Overview
python scripts/inspect_bundle.py

# Specific ticker with recent prices
python scripts/inspect_bundle.py --ticker AAPL
```

## 📚 Additional Resources

### Documentation

- [Sharadar Documentation](https://data.nasdaq.com/databases/SFA/documentation)
- [NASDAQ Data Link API](https://docs.data.nasdaq.com/)
- [Zipline Documentation](https://zipline.ml4trading.io/)
- [Pipeline Tutorial](https://zipline.ml4trading.io/beginner-tutorial.html)

### Books & Communities

- [ML4Trading Book](https://www.ml4trading.io/) - Uses Sharadar extensively
- [ML4Trading Community](https://exchange.ml4trading.io)

## ❓ Common Issues

### "Missing sessions" error during ingestion

This usually means:
1. **Missing data in source** - Some tickers may have gaps in Sharadar data
2. **Solution**: The bundle now forward-fills missing days automatically

Check your data quality:
```bash
python scripts/inspect_bundle.py --ticker SYMBOL
```

### "No bundle registered with name 'sharadar'"

**Solution**: The bundle is auto-registered. Try:
```bash
# Re-ingest
python scripts/manage_sharadar.py ingest --tickers AAPL

# Verify
zipline bundles
```

### Import errors in notebooks

**Solution**: Restart the kernel
- In Jupyter: Kernel → Restart Kernel
- Then re-run all cells from the top

### Out of date prices

**Solution**: Re-ingest to get latest data
```bash
python scripts/manage_sharadar.py ingest --all
```

## 💡 Tips

- **Start small**: Ingest a few tickers first to test (`--tickers` option)
- **Use inspect_bundle.py**: Check what data you have before backtesting
- **Save frequently**: Notebooks auto-save but manual saves are recommended
- **Run cells in order**: Especially important for Pipeline notebooks
- **Check dates**: Use `inspect_bundle.py` to see your data range before backtesting

## 🎯 Quick Reference

### Common Commands

```bash
# Ingest specific tickers
python scripts/manage_sharadar.py ingest --tickers AAPL,MSFT,GOOGL

# Ingest all US equities
python scripts/manage_sharadar.py ingest --all

# Check status
python scripts/manage_sharadar.py status

# Inspect data
python scripts/inspect_bundle.py

# Clean old data
python scripts/manage_sharadar.py clean --keep-last 3

# Run strategy from CLI
zipline run -f strategies_files/sma_crossover.py -b sharadar --start 2022-01-01 --end 2023-12-31
```

## 🤝 Contributing

Found an issue or want to add an example?
- [Report Issues](https://github.com/stefan-jansen/zipline-reloaded/issues)
- [ML4Trading Community](https://exchange.ml4trading.io)

---

**Happy Backtesting with Sharadar! 🚀**
