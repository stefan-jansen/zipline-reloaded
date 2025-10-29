# How to Access Strategy Files

## Location
Strategy files are located in: `/home/user/zipline-reloaded/strategies/`

## Available Strategies

### 1. SMA Crossover Strategy
**File:** `sma_crossover.py`
- Long-term trend following (50/200 day SMA)
- Golden Cross (buy) / Death Cross (sell)
- Best for: Fewer, high-conviction signals

### 2. EMA Crossover Strategy
**File:** `ema_crossover.py`
- Short-term responsive (10/20 day EMA)
- More frequent trading signals
- Best for: Active trading

## How to Edit Strategies

### Option 1: Via Jupyter Terminal
1. In Jupyter, go to **New** → **Terminal**
2. Navigate to strategies: `cd /home/user/zipline-reloaded/strategies`
3. Edit files: `nano sma_crossover.py` or `vim sma_crossover.py`

### Option 2: Via Jupyter Text Editor
1. In Jupyter, go to **New** → **Text File**
2. In the URL bar, change the path to: `/tree/home/user/zipline-reloaded/strategies`
3. Click on any `.py` file to edit

### Option 3: Via File Browser (direct path)
Manually enter this in your browser's address bar:
```
http://localhost:8888/tree/home/user/zipline-reloaded/strategies
```
(Replace `localhost:8888` with your Jupyter server address)

### Option 4: From Your Host Machine
If you have the repository mounted to your host:
- Use your favorite code editor (VS Code, PyCharm, etc.)
- Edit files in: `./strategies/`
- Changes are immediately reflected in the container

## Importing Strategies in Notebooks

Strategies can be imported directly in notebooks:

```python
# Import SMA strategy
from strategies.sma_crossover import initialize, before_trading_start, rebalance, analyze

# Import EMA strategy
from strategies.ema_crossover import initialize, before_trading_start, rebalance, analyze
```

See `08_run_external_strategy.ipynb` for a complete example.

## Running Strategies via CLI

From a terminal in Jupyter:

```bash
# Run SMA strategy
zipline run -f /home/user/zipline-reloaded/strategies/sma_crossover.py \
    -b sharadar --start 2022-01-01 --end 2023-12-31

# Run EMA strategy
zipline run -f /home/user/zipline-reloaded/strategies/ema_crossover.py \
    -b sharadar --start 2022-01-01 --end 2023-12-31
```

## Creating New Strategies

1. Copy an existing strategy as a template:
   ```bash
   cd /home/user/zipline-reloaded/strategies
   cp sma_crossover.py my_new_strategy.py
   ```

2. Edit your new strategy file

3. Import and test in a notebook:
   ```python
   from strategies.my_new_strategy import initialize, before_trading_start, rebalance
   ```

## Troubleshooting

**Q: Why can't I see the strategies folder in the notebooks directory?**
A: Jupyter doesn't follow symbolic links for security reasons. Use one of the methods above to access the files directly.

**Q: Import error "ModuleNotFoundError: No module named 'strategies'"?**
A: Make sure you've added the project root to your path (see `08_run_external_strategy.ipynb` cell 2).

**Q: Can I edit strategies directly from VS Code or other editors?**
A: Yes! If you have the repository mounted from your host machine, you can edit the files with any editor and they'll be immediately available in the container.
