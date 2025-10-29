# Zipline Reloaded - Project Context for Claude

## Overview
Zipline is a Pythonic algorithmic trading library for backtesting trading strategies. This is the "reloaded" fork maintained by Stefan Jansen after Quantopian closed in 2020.

## Key Information
- **Python Version**: >= 3.9
- **Main Dependencies**: pandas >= 2.0, SQLAlchemy >= 2.0, numpy >= 2.0
- **Documentation**: https://zipline.ml4trading.io
- **Community**: https://exchange.ml4trading.io

## Project Structure
- `src/zipline/`: Main source code
  - `algorithm.py`: Core algorithm execution
  - `api.py`: Public API functions
  - `data/`: Data ingestion and handling
  - `finance/`: Financial calculations and order execution
  - `pipeline/`: Factor-based screening system
- `tests/`: Test suite
- `docs/`: Documentation source

## Development Commands
```bash
# Run tests
pytest tests/

# Run specific test file
pytest tests/test_algorithm.py

# Build documentation
cd docs && make html

# Install in development mode
pip install -e .
```

## Testing Approach
- Unit tests use pytest
- Test data is stored in `tests/resources/`
- Mock trading environments for testing strategies

## Common Tasks
1. **Implementing new data bundles**: See `src/zipline/data/bundles/`
2. **Adding new pipeline factors**: See `src/zipline/pipeline/factors/`
3. **Modifying order execution**: See `src/zipline/finance/execution.py`
4. **Working with trading calendars**: Uses `exchange_calendars` library

## Current Branch
You're on branch `v3.1.1` with some modifications to the Quandl bundle and CI fixes.

## Important Notes
- The project uses Cython for performance-critical components
- Be careful with numpy/pandas API changes due to major version updates
- Trading calendars are handled by the external `exchange_calendars` package
