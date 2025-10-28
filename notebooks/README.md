# Zipline-Reloaded Jupyter Notebooks

This directory contains interactive Jupyter notebooks demonstrating the CustomData functionality.

## Notebooks

### Beginner

1. **`01_customdata_quickstart.ipynb`**
   - Introduction to CustomData
   - Creating custom datasets
   - Building basic pipelines
   - Visualizing data

### Intermediate

2. **`02_database_storage.ipynb`**
   - Persistent database storage
   - Inserting and querying data
   - Database management
   - Performance optimization

### Advanced

3. **`03_market_data_example.ipynb`**
   - Fetching real market data from Yahoo Finance
   - Creating databases for market prices
   - Building pipelines with real data
   - Technical analysis and indicators
   - Risk-return analysis
   - Trading signal generation
   - Production data workflows

### Professional

4. **`04_nasdaq_datalink_example.ipynb`**
   - Professional-grade data from NASDAQ Data Link
   - API key setup and configuration
   - Premium EOD and WIKI datasets
   - Adjusted prices (splits/dividends)
   - Advanced technical indicators
   - Golden cross and momentum signals
   - Data quality verification
   - Production deployment workflows

5. **`05_advanced_pipelines.ipynb`** (Coming soon)
   - Custom factors and filters
   - Complex pipeline expressions
   - Multi-dataset pipelines

## Getting Started

### Using Docker

If running in Docker container:
```bash
# Notebooks are already loaded
# Access at http://localhost:8888
```

### Local Installation

```bash
# Install Jupyter
pip install jupyter jupyterlab

# Start Jupyter Lab
jupyter lab
```

## API Key Setup (for NASDAQ Data Link)

To use the professional NASDAQ Data Link notebook (`04_nasdaq_datalink_example.ipynb`):

### 1. Get Your API Key
- Sign up at [NASDAQ Data Link](https://data.nasdaq.com/)
- Navigate to Account Settings → API Key
- Copy your API key

### 2. Configure the API Key

**Option A: Environment Variable (Recommended)**
```bash
# Add to your .env file
echo "NASDAQ_DATA_LINK_API_KEY=your_api_key_here" >> .env
```

**Option B: Docker Compose**
```bash
# Copy example file
cp .env.example .env

# Edit .env and add your key
# NASDAQ_DATA_LINK_API_KEY=your_api_key_here

# Restart container
docker-compose down && docker-compose up
```

**Option C: Direct Export**
```bash
export NASDAQ_DATA_LINK_API_KEY='your_api_key_here'
```

### 3. Verify Setup
Open `04_nasdaq_datalink_example.ipynb` and run the first few cells to verify your API connection.

## Tips

- **Save frequently** - Notebooks auto-save but manual saves are recommended
- **Restart kernel** if you encounter issues: Kernel → Restart Kernel
- **Clear outputs** before committing: Cell → All Output → Clear
- **Use markdown** cells for documentation
- **Split long cells** into smaller, logical units

## Creating Your Own Notebooks

Feel free to create new notebooks based on the examples!

```python
# Standard imports for zipline-reloaded
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from zipline.pipeline.data import CustomData, create_custom_db
from zipline.pipeline import Pipeline
from zipline.pipeline.factors import SimpleMovingAverage

# Your custom analysis here...
```

## Need Help?

- Check the [CustomData Documentation](../docs/CUSTOM_DATA.md)
- See [Database Guide](../docs/CUSTOM_DATA_DATABASE.md)
- Review [Docker Setup](../README_DOCKER.md)
- Run example notebooks for reference

Happy analyzing! 📊
