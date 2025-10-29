# Zipline-Reloaded Example Notebooks

This directory contains comprehensive examples for using zipline-reloaded with different data sources and approaches.

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

### For Sharadar Subscribers (Professional/Premium)

**👉 Start here: [`06_sharadar_professional_backtesting.ipynb`](./06_sharadar_professional_backtesting.ipynb)**

If you have a [Sharadar subscription](https://data.nasdaq.com/databases/SFA), this is the best way to use zipline-reloaded:

- ✅ Institutional-grade data quality
- ✅ Point-in-time accurate (no look-ahead bias)
- ✅ Built-in bundle system (easiest setup)
- ✅ Optimized for performance
- ✅ Comprehensive US equity coverage

**Quick Setup:**
```bash
# Setup Sharadar bundle
export NASDAQ_DATA_LINK_API_KEY='your_key'
python /scripts/manage_data.py setup --source sharadar --tickers AAPL,MSFT,GOOGL
```

### For Free Data Users

**👉 Start here: [`05_backtesting_with_bundles.ipynb`](./05_backtesting_with_bundles.ipynb)**

Uses Yahoo Finance data (free, no API key required):

- ✅ Free and open access
- ✅ Current market data
- ✅ Easy setup
- ✅ Good for learning and prototyping

**Quick Setup:**
```bash
# Setup Yahoo Finance bundle
python /scripts/manage_data.py setup --source yahoo
```

## 📚 All Notebooks

### Backtesting & Trading

| Notebook | Description | Data Source | Difficulty |
|----------|-------------|-------------|------------|
| **06_sharadar_professional_backtesting.ipynb** | Professional backtesting with Sharadar | Sharadar (Premium) | ⭐⭐ Intermediate |
| **05_backtesting_with_bundles.ipynb** | Complete backtesting tutorial | Yahoo Finance (Free) | ⭐ Beginner |
| **03_market_data_example.ipynb** | Yahoo Finance CustomData integration | Yahoo Finance (Free) | ⭐⭐ Intermediate |

### CustomData (Advanced)

| Notebook | Description | Use Case | Difficulty |
|----------|-------------|----------|------------|
| **01_customdata_quickstart.ipynb** | CustomData basics | Custom indicators in Pipeline | ⭐ Beginner |
| **02_database_storage.ipynb** | Database storage for CustomData | Large datasets, persistence | ⭐⭐ Intermediate |
| **04_nasdaq_datalink_example.ipynb** | NASDAQ Data Link CustomData | Non-Sharadar NASDAQ data | ⭐⭐⭐ Advanced |

**Note on 04_nasdaq_datalink_example.ipynb**: This notebook shows CustomData usage with NASDAQ Data Link API. However, if you have Sharadar, use `06_sharadar_professional_backtesting.ipynb` instead - it's much simpler and more powerful!

## 🎯 Quick Decision Tree

### What Should I Use?

```
Do you have a Sharadar subscription?
├─ YES → Use 06_sharadar_professional_backtesting.ipynb
│         (Best data quality, easiest setup)
│
└─ NO → Do you want to pay for data?
    ├─ NO → Use 05_backtesting_with_bundles.ipynb
    │        (Yahoo Finance, free and good)
    │
    └─ YES → Consider getting Sharadar
             Then use 06_sharadar_professional_backtesting.ipynb
```

### Bundles vs CustomData?

**Use Bundles (Recommended):**
- ✅ For backtesting with `run_algorithm()`
- ✅ For OHLCV pricing data
- ✅ When you want automatic adjustment handling
- ✅ When you need maximum performance

**Use CustomData:**
- ✅ For custom indicators in Pipeline
- ✅ For non-standard data (sentiment, fundamentals, etc.)
- ✅ For research and factor analysis
- ✅ When you need flexible data schemas

## 📖 Learning Path

### Beginner

1. **Start**: `05_backtesting_with_bundles.ipynb`
   - Learn bundle basics
   - Write your first strategy
   - Understand backtest results

2. **Next**: `01_customdata_quickstart.ipynb`
   - Understand CustomData
   - Create custom factors
   - Use Pipeline for screening

### Intermediate

3. **Then**: `06_sharadar_professional_backtesting.ipynb` (if you have Sharadar)
   - Professional-grade data
   - Advanced strategies
   - Pipeline with bundles

4. **Or**: `03_market_data_example.ipynb` (if using free data)
   - Yahoo Finance integration
   - CustomData + bundles together

### Advanced

5. **Finally**: `02_database_storage.ipynb`
   - Persistent CustomData storage
   - Large dataset management
   - Production workflows

6. **Optional**: `04_nasdaq_datalink_example.ipynb`
   - NASDAQ Data Link integration
   - Custom data pipelines

## 🚀 Setup Instructions

### Prerequisites

```bash
# Make sure you're in the Docker container
docker exec -it zipline-reloaded-jupyter bash

# Or access Jupyter Lab at http://localhost:9000
```

### Setup Sharadar (Premium)

```bash
# 1. Set API key in .env file
echo "NASDAQ_DATA_LINK_API_KEY=your_key_here" >> .env

# 2. Restart Docker
docker compose restart

# 3. Setup bundle
docker exec -it zipline-reloaded-jupyter python /scripts/manage_data.py setup \
    --source sharadar \
    --tickers AAPL,MSFT,GOOGL,AMZN,TSLA

# 4. Verify
docker exec -it zipline-reloaded-jupyter zipline bundles
```

### Setup Yahoo Finance (Free)

```bash
# 1. Setup bundle
docker exec -it zipline-reloaded-jupyter python /scripts/manage_data.py setup \
    --source yahoo

# 2. Verify
docker exec -it zipline-reloaded-jupyter zipline bundles
```

## 📚 Additional Resources

### Documentation

- [Sharadar Setup Guide](../docs/SHARADAR_GUIDE.md) - Complete Sharadar documentation
- [Bundle System](../docs/BUNDLES.md) - Understanding bundles
- [CustomData Guide](../docs/CUSTOM_DATA.md) - CustomData documentation
- [Getting Started](../GETTING_STARTED.md) - Repository setup
- [Docker Guide](../docs/DOCKER_BUNDLES.md) - Docker-specific instructions

### External Resources

- [Zipline Documentation](https://zipline.ml4trading.io/)
- [Pipeline Tutorial](https://zipline.ml4trading.io/beginner-tutorial.html)
- [Sharadar Data](https://data.nasdaq.com/databases/SFA)
- [ML4Trading Book](https://www.ml4trading.io/) - Uses Sharadar extensively

## ❓ Common Issues

### "No bundle registered with name 'X'"

**Solution**: Run the extension setup
```bash
docker exec -it zipline-reloaded-jupyter python /scripts/setup_extension.py
```

### "NASDAQData is not defined" (in notebook 04)

**Issue**: Cell 19 must be run before cell 21. The notebook creates `NASDAQData` variable in cell 19 by loading from database.

**Better Solution**: If you have Sharadar, use `06_sharadar_professional_backtesting.ipynb` instead - it's much simpler!

### "WIKI dataset has no data"

**Solution**: WIKI was discontinued in 2018. Use one of these instead:
- Sharadar (premium, recommended)
- Yahoo Finance (free)
- NASDAQ EOD (premium)

See [WIKI Dataset Notice](../docs/WIKI_DATASET_NOTICE.md) for details.

## Tips

- **Save frequently** - Notebooks auto-save but manual saves are recommended
- **Restart kernel** if you encounter issues: Kernel → Restart Kernel
- **Run cells in order** - Especially for notebooks that build on previous cells
- **Clear outputs** before committing: Cell → All Output → Clear
- **Use markdown** cells for documentation

## 🤝 Contributing

Found an issue or want to add an example?
- [Report Issues](https://github.com/stefan-jansen/zipline-reloaded/issues)
- [ML4Trading Community](https://exchange.ml4trading.io)

---

**Happy Backtesting! 🚀**
