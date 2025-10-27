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

3. **`03_advanced_pipelines.ipynb`** (Coming soon)
   - Custom factors and filters
   - Complex pipeline expressions
   - Multi-dataset pipelines

4. **`04_real_data_example.ipynb`** (Coming soon)
   - Working with real market data
   - Data preprocessing
   - Production workflows

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
