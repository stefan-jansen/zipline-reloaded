"""
Zipline Trading Strategies
===========================

Collection of ready-to-use trading strategies for backtesting with Zipline.

Available Strategies:
---------------------
- sma_crossover: Simple Moving Average crossover (50/200 days) - long-term trend following
- ema_crossover: Exponential Moving Average crossover (10/20 days) - short-term responsive

Usage:
------
Import strategy functions:
    from strategies.sma_crossover import initialize, before_trading_start, rebalance

Or run directly via CLI:
    zipline run -f strategies/sma_crossover.py -b sharadar --start 2022-01-01 --end 2023-12-31
"""

__version__ = '1.0.0'

__all__ = [
    'sma_crossover',
    'ema_crossover',
]
