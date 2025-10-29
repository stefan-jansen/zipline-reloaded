"""
Simple Moving Average Crossover Strategy
=========================================

This strategy trades based on SMA crossovers:
- BUY when fast SMA crosses above slow SMA (golden cross)
- SELL when fast SMA crosses below slow SMA (death cross)

Parameters:
-----------
- fast_period: Short-term moving average period (default: 50 days)
- slow_period: Long-term moving average period (default: 200 days)
- universe: List of stock symbols to trade

Usage:
------
Run with zipline CLI:
    zipline run -f strategies/sma_crossover.py -b sharadar --start 2022-01-01 --end 2023-12-31

Or from Python/notebook:
    from strategies.sma_crossover import initialize, handle_data, before_trading_start
    results = run_algorithm(initialize=initialize, ...)
"""

import pandas as pd
from zipline.api import (
    order_target_percent,
    record,
    symbol,
    symbols,
    set_commission,
    set_slippage,
    schedule_function,
    date_rules,
    time_rules,
    attach_pipeline,
    pipeline_output,
    get_datetime,
)
from zipline.finance import commission, slippage
from zipline.pipeline import Pipeline
from zipline.pipeline.data import USEquityPricing
from zipline.pipeline.factors import SimpleMovingAverage


# Strategy Parameters
FAST_MA_PERIOD = 50
SLOW_MA_PERIOD = 200
MAX_POSITIONS = 10  # Maximum number of stocks to hold

# Stock universe (customize this list)
STOCK_UNIVERSE = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA',
    'META', 'NVDA', 'NFLX', 'AMD', 'INTC',
]


def make_pipeline():
    """
    Create a pipeline that calculates moving averages and identifies crossovers.
    """
    # Calculate moving averages
    fast_ma = SimpleMovingAverage(
        inputs=[USEquityPricing.close],
        window_length=FAST_MA_PERIOD,
    )
    slow_ma = SimpleMovingAverage(
        inputs=[USEquityPricing.close],
        window_length=SLOW_MA_PERIOD,
    )

    # Current price
    close = USEquityPricing.close.latest

    # Trading signals
    # Golden cross: fast MA > slow MA (bullish)
    golden_cross = fast_ma > slow_ma

    # Death cross: fast MA < slow MA (bearish)
    death_cross = fast_ma < slow_ma

    return Pipeline(
        columns={
            'close': close,
            'fast_ma': fast_ma,
            'slow_ma': slow_ma,
            'golden_cross': golden_cross,
            'death_cross': death_cross,
        },
    )


def initialize(context):
    """
    Called once at the start of the backtest.

    Parameters:
    -----------
    context : zipline.TradingAlgorithm
        Context object to store strategy state
    """
    # Set our stock universe
    context.universe = symbols(*STOCK_UNIVERSE)

    # Attach the pipeline
    attach_pipeline(make_pipeline(), 'sma_crossover')

    # Set commission model (realistic trading costs)
    # $0.001 per share, minimum $1 per trade
    set_commission(commission.PerShare(cost=0.001, min_trade_cost=1.0))

    # Set slippage model (realistic market impact)
    set_slippage(slippage.VolumeShareSlippage(
        volume_limit=0.025,  # Trade up to 2.5% of daily volume
        price_impact=0.1,    # 10% price impact
    ))

    # Schedule rebalance function
    # Run once per day at market open
    schedule_function(
        rebalance,
        date_rules.every_day(),
        time_rules.market_open(hours=1),  # 1 hour after market open
    )

    # Initialize tracking variables
    context.long_positions = set()  # Stocks we're currently long
    context.trades_made = 0

    print(f"SMA Crossover Strategy Initialized")
    print(f"  Universe: {len(STOCK_UNIVERSE)} stocks")
    print(f"  Fast MA: {FAST_MA_PERIOD} days")
    print(f"  Slow MA: {SLOW_MA_PERIOD} days")
    print(f"  Max Positions: {MAX_POSITIONS}")


def before_trading_start(context, data):
    """
    Called every day before market opens.

    Parameters:
    -----------
    context : zipline.TradingAlgorithm
        Context object
    data : zipline.DataPortal
        Data portal for accessing market data
    """
    # Get pipeline output
    context.pipeline_data = pipeline_output('sma_crossover')

    # Filter to our universe
    context.pipeline_data = context.pipeline_data[
        context.pipeline_data.index.isin(context.universe)
    ]


def rebalance(context, data):
    """
    Execute trading logic based on SMA crossover signals.

    Parameters:
    -----------
    context : zipline.TradingAlgorithm
        Context object
    data : zipline.DataPortal
        Data portal for accessing market data
    """
    pipeline_data = context.pipeline_data

    if pipeline_data is None or len(pipeline_data) == 0:
        return

    # Get current date
    current_date = get_datetime()

    # Find stocks with golden cross (buy signal)
    golden_cross_stocks = pipeline_data[pipeline_data['golden_cross'] == True]
    buy_list = set(golden_cross_stocks.index)

    # Find stocks with death cross (sell signal)
    death_cross_stocks = pipeline_data[pipeline_data['death_cross'] == True]
    sell_list = set(death_cross_stocks.index) & context.long_positions

    # First, sell stocks with death cross
    for stock in sell_list:
        if data.can_trade(stock):
            order_target_percent(stock, 0.0)
            context.long_positions.discard(stock)
            context.trades_made += 1

            stock_data = pipeline_data.loc[stock]
            print(f"{current_date.date()} SELL {stock.symbol}: "
                  f"Fast MA: ${stock_data['fast_ma']:.2f}, "
                  f"Slow MA: ${stock_data['slow_ma']:.2f}")

    # Calculate position size
    # Equal weight across all positions, up to MAX_POSITIONS
    available_slots = MAX_POSITIONS - len(context.long_positions)

    if available_slots > 0 and len(buy_list) > 0:
        # Limit to available slots
        new_buys = list(buy_list - context.long_positions)[:available_slots]

        # Calculate weight for each position
        total_positions = len(context.long_positions) + len(new_buys)
        target_weight = 1.0 / total_positions if total_positions > 0 else 0

        # Rebalance existing positions
        for stock in context.long_positions:
            if data.can_trade(stock):
                order_target_percent(stock, target_weight)

        # Buy new positions
        for stock in new_buys:
            if data.can_trade(stock):
                order_target_percent(stock, target_weight)
                context.long_positions.add(stock)
                context.trades_made += 1

                stock_data = pipeline_data.loc[stock]
                print(f"{current_date.date()} BUY {stock.symbol}: "
                      f"Fast MA: ${stock_data['fast_ma']:.2f}, "
                      f"Slow MA: ${stock_data['slow_ma']:.2f}")

    # Record metrics
    record(
        num_positions=len(context.long_positions),
        trades_made=context.trades_made,
        cash=context.portfolio.cash,
        portfolio_value=context.portfolio.portfolio_value,
    )


def analyze(context, perf):
    """
    Called after the backtest completes.
    Prints strategy performance summary.

    Parameters:
    -----------
    context : zipline.TradingAlgorithm
        Context object
    perf : pd.DataFrame
        Performance data from the backtest
    """
    print(f"\n{'='*60}")
    print("SMA CROSSOVER STRATEGY - PERFORMANCE SUMMARY")
    print(f"{'='*60}\n")

    # Calculate returns
    total_return = (perf['portfolio_value'].iloc[-1] / perf['portfolio_value'].iloc[0] - 1) * 100

    # Calculate Sharpe ratio
    returns = perf['returns']
    sharpe = returns.mean() / returns.std() * (252 ** 0.5) if returns.std() > 0 else 0

    # Calculate max drawdown
    cumulative = (1 + returns).cumprod()
    running_max = cumulative.cummax()
    drawdown = (cumulative / running_max) - 1
    max_drawdown = drawdown.min() * 100

    # Win rate
    winning_days = (returns > 0).sum()
    total_days = len(returns)
    win_rate = (winning_days / total_days) * 100

    print(f"Period: {perf.index[0].date()} to {perf.index[-1].date()}")
    print(f"Days: {len(perf)}")
    print(f"\nReturns:")
    print(f"  Total Return: {total_return:+.2f}%")
    print(f"  Sharpe Ratio: {sharpe:.2f}")
    print(f"  Max Drawdown: {max_drawdown:.2f}%")
    print(f"  Win Rate: {win_rate:.1f}%")
    print(f"\nTrading:")
    print(f"  Total Trades: {context.trades_made}")
    print(f"  Avg Positions: {perf['num_positions'].mean():.1f}")
    print(f"  Max Positions: {perf['num_positions'].max()}")
    print(f"\nFinal Portfolio:")
    print(f"  Value: ${perf['portfolio_value'].iloc[-1]:,.2f}")
    print(f"  Cash: ${perf['cash'].iloc[-1]:,.2f}")

    print(f"\n{'='*60}\n")


# If running as a script with zipline CLI
if __name__ == '__main__':
    print("This strategy should be run with:")
    print("  zipline run -f strategies/sma_crossover.py -b sharadar --start 2022-01-01 --end 2023-12-31")
    print("\nOr imported in a Jupyter notebook:")
    print("  from strategies.sma_crossover import initialize, handle_data, before_trading_start")
