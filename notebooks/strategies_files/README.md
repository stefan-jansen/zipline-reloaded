# Strategy Files

This folder contains **copies** of the strategy files for easy access in Jupyter.

## Files in This Directory

- `sma_crossover.py` - 50/200 day SMA crossover strategy (long-term)
- `ema_crossover.py` - 10/20 day EMA crossover strategy (short-term)

## Accessing These Files

You can now access these files directly in Jupyter:

**In your browser:**
```
http://localhost:9000/tree/strategies_files
```

Or click on the `strategies_files` folder in the Jupyter file browser!

## Editing Strategies

Click on any `.py` file in this folder to open and edit it in Jupyter.

## Important Notes

### These are COPIES
The **original** strategy files are located in: `/home/user/zipline-reloaded/strategies/`

If you edit files in THIS directory (`strategies_files`), you're editing copies.

### To use your edited strategies:

**Option 1: Copy your changes back to the original location**
```bash
# In a Jupyter Terminal
cp strategies_files/my_strategy.py ../strategies/my_strategy.py
```

**Option 2: Import from this directory**
```python
# In a notebook, add to your path:
import sys
sys.path.insert(0, '/home/user/zipline-reloaded/notebooks')

# Then import:
from strategies_files.sma_crossover import initialize, before_trading_start, rebalance
```

**Option 3: Run directly with full path**
```bash
zipline run -f /home/user/zipline-reloaded/notebooks/strategies_files/sma_crossover.py -b sharadar --start 2022-01-01 --end 2023-12-31
```

## Workflow Recommendation

**For browsing and learning:** Edit files here in `strategies_files/`

**For production strategies:**
1. Develop and test in `strategies_files/`
2. When ready, copy to the main `strategies/` directory
3. Commit to git from the main directory

## Syncing Changes

If you want to sync changes from the main strategies directory:
```bash
# In a Jupyter Terminal
cp /home/user/zipline-reloaded/strategies/*.py strategies_files/
```

Or to push your changes to the main directory:
```bash
# In a Jupyter Terminal
cp strategies_files/*.py /home/user/zipline-reloaded/strategies/
```

Then commit with git if you want to save them permanently.
