"""
Yahoo Finance Bundle for Zipline
=================================

This module provides a data bundle for zipline that fetches data from Yahoo Finance
using the yfinance package and stores it in zipline's native bundle format for backtesting.

Usage:
    # Register the bundle in your extension.py or notebook
    from zipline.data.bundles import register
    from zipline.data.bundles.yahoo_bundle import yahoo_bundle

    register(
        'yahoo',
        yahoo_bundle(
            tickers=['AAPL', 'MSFT', 'GOOGL'],
        ),
    )

    # Ingest the bundle
    # zipline ingest -b yahoo

Requirements:
    - yfinance package
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Optional

try:
    import yfinance as yf
except ImportError:
    yf = None


def yahoo_bundle(
    tickers: Optional[List[str]] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
):
    """
    Create a zipline data bundle from Yahoo Finance.

    Parameters
    ----------
    tickers : list of str, optional
        List of ticker symbols to fetch. If not provided, will use a default set
        of popular stocks.
    start_date : str, optional
        Start date for data fetch (YYYY-MM-DD). Defaults to 10 years ago.
    end_date : str, optional
        End date for data fetch (YYYY-MM-DD). Defaults to today.

    Returns
    -------
    callable
        A bundle ingest function compatible with zipline's bundle system.

    Examples
    --------
    >>> from zipline.data.bundles import register
    >>> from zipline.data.bundles.yahoo_bundle import yahoo_bundle
    >>>
    >>> # Register with default settings
    >>> register('yahoo', yahoo_bundle())
    >>>
    >>> # Register with custom tickers
    >>> register('yahoo-tech', yahoo_bundle(
    ...     tickers=['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA'],
    ... ))
    """

    # Default tickers if not provided
    if tickers is None:
        tickers = [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA',
            'NVDA', 'META', 'JPM', 'V', 'WMT',
            'MA', 'JNJ', 'UNH', 'HD', 'PG',
            'XOM', 'BAC', 'ABBV', 'KO', 'PFE',
        ]

    # Default date range
    if start_date is None:
        start_date = (datetime.now() - timedelta(days=365*10)).strftime('%Y-%m-%d')

    if end_date is None:
        end_date = datetime.now().strftime('%Y-%m-%d')

    def ingest(
        environ,
        asset_db_writer,
        minute_bar_writer,
        daily_bar_writer,
        adjustment_writer,
        calendar,
        start_session,
        end_session,
        cache,
        show_progress,
        output_dir,
    ):
        """
        Bundle ingest function.

        This function is called by zipline's bundle ingestion system.
        """

        if yf is None:
            raise ImportError(
                "yfinance package is required. "
                "Install with: pip install yfinance"
            )

        # Metadata for assets
        metadata = []

        # Fetch data for each ticker
        all_data = []
        dividends_data = []
        splits_data = []

        print(f"\nFetching data from Yahoo Finance...")
        print(f"Date range: {start_date} to {end_date}")
        print(f"Tickers: {len(tickers)}\n")

        for i, ticker in enumerate(tickers, 1):
            print(f"  [{i}/{len(tickers)}] Fetching {ticker}...", end=" ")

            try:
                # Create ticker object
                stock = yf.Ticker(ticker)

                # Fetch historical data
                df = stock.history(start=start_date, end=end_date, auto_adjust=False)

                if df.empty:
                    print("❌ No data")
                    continue

                # Prepare data for zipline format
                # Yahoo Finance returns: Open, High, Low, Close, Volume, Dividends, Stock Splits
                ohlcv = pd.DataFrame({
                    'open': df['Open'],
                    'high': df['High'],
                    'low': df['Low'],
                    'close': df['Close'],
                    'volume': df['Volume'],
                })

                # Add symbol and sid
                ohlcv['symbol'] = ticker
                ohlcv['sid'] = i

                # Ensure no NaN values
                ohlcv = ohlcv.fillna(method='ffill').fillna(method='bfill')

                # Remove any remaining NaN rows
                ohlcv = ohlcv.dropna()

                if ohlcv.empty:
                    print("❌ No valid data after cleaning")
                    continue

                all_data.append(ohlcv)

                # Extract dividends
                if 'Dividends' in df.columns:
                    divs = df[df['Dividends'] > 0]['Dividends']
                    if not divs.empty:
                        div_df = pd.DataFrame({
                            'sid': i,
                            'amount': divs.values,
                            'ex_date': divs.index,
                            'record_date': divs.index,
                            'declared_date': divs.index,
                            'pay_date': divs.index,
                        })
                        dividends_data.append(div_df)

                # Extract splits
                if 'Stock Splits' in df.columns:
                    splits = df[df['Stock Splits'] != 0]['Stock Splits']
                    if not splits.empty:
                        # Convert split ratio (e.g., 0.5 for 2:1 split)
                        split_df = pd.DataFrame({
                            'sid': i,
                            'ratio': splits.values,
                            'effective_date': splits.index,
                        })
                        splits_data.append(split_df)

                # Add to metadata
                metadata.append({
                    'symbol': ticker,
                    'asset_name': ticker,
                    'start_date': ohlcv.index[0],
                    'end_date': ohlcv.index[-1],
                    'exchange': 'YAHOO',
                    'sid': i,
                })

                print(f"✓ {len(ohlcv)} days")

            except Exception as e:
                print(f"❌ Error: {e}")

        if not all_data:
            raise ValueError("No data was fetched. Check your ticker list and internet connection.")

        print(f"\n✓ Successfully fetched {len(all_data)} stocks")

        # Write metadata
        print("\nWriting asset metadata...")
        metadata_df = pd.DataFrame(metadata)
        asset_db_writer.write(equities=metadata_df)

        # Write daily bars
        print("Writing daily bars...")
        combined_data = pd.concat(all_data, ignore_index=False)

        def data_generator():
            for sid in sorted(combined_data['sid'].unique()):
                symbol_data = combined_data[combined_data['sid'] == sid]
                symbol_data = symbol_data.drop(['symbol', 'sid'], axis=1)
                symbol_data.index = pd.to_datetime(symbol_data.index)

                # Ensure timezone-naive
                if symbol_data.index.tz is not None:
                    symbol_data.index = symbol_data.index.tz_localize(None)

                # Ensure all required columns are present and properly typed
                yield sid, symbol_data[['open', 'high', 'low', 'close', 'volume']]

        daily_bar_writer.write(data_generator(), show_progress=show_progress)

        # Write adjustments (dividends and splits)
        print("Writing adjustments...")

        if dividends_data:
            dividends_df = pd.concat(dividends_data, ignore_index=True)
            dividends_df['ex_date'] = pd.to_datetime(dividends_df['ex_date'])
            dividends_df['record_date'] = pd.to_datetime(dividends_df['record_date'])
            dividends_df['declared_date'] = pd.to_datetime(dividends_df['declared_date'])
            dividends_df['pay_date'] = pd.to_datetime(dividends_df['pay_date'])

            # Remove timezone info
            for col in ['ex_date', 'record_date', 'declared_date', 'pay_date']:
                if dividends_df[col].dt.tz is not None:
                    dividends_df[col] = dividends_df[col].dt.tz_localize(None)
        else:
            dividends_df = pd.DataFrame(columns=['sid', 'amount', 'ex_date', 'record_date', 'declared_date', 'pay_date'])

        if splits_data:
            splits_df = pd.concat(splits_data, ignore_index=True)
            splits_df['effective_date'] = pd.to_datetime(splits_df['effective_date'])

            # Remove timezone info
            if splits_df['effective_date'].dt.tz is not None:
                splits_df['effective_date'] = splits_df['effective_date'].dt.tz_localize(None)
        else:
            splits_df = pd.DataFrame(columns=['sid', 'ratio', 'effective_date'])

        adjustment_writer.write(
            splits=splits_df if not splits_df.empty else None,
            dividends=dividends_df if not dividends_df.empty else None,
        )

        print("\n✓ Bundle ingestion complete!")
        print(f"  Total stocks: {len(metadata)}")
        print(f"  Total bars: {len(combined_data):,}")
        print(f"  Dividends: {len(dividends_df)}")
        print(f"  Splits: {len(splits_df)}")

    return ingest


# Pre-configured bundles for common use cases

def yahoo_sp500_bundle():
    """
    Yahoo Finance bundle for major S&P 500 stocks.

    Note: This is a subset - full S&P 500 would require all 500 tickers.
    """
    sp500_tickers = [
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA',
        'TSLA', 'META', 'BRK-B', 'V', 'JNJ',
        'WMT', 'JPM', 'MA', 'PG', 'UNH',
        'HD', 'CVX', 'MRK', 'ABBV', 'PEP',
        'KO', 'COST', 'AVGO', 'TMO', 'DIS',
    ]

    return yahoo_bundle(tickers=sp500_tickers)


def yahoo_tech_bundle():
    """
    Yahoo Finance bundle for major tech stocks.
    """
    tech_tickers = [
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META',
        'NVDA', 'TSLA', 'NFLX', 'ADBE', 'CRM',
        'INTC', 'AMD', 'ORCL', 'CSCO', 'AVGO',
    ]

    return yahoo_bundle(tickers=tech_tickers)


def yahoo_dow_bundle():
    """
    Yahoo Finance bundle for Dow Jones Industrial Average stocks.
    """
    dow_tickers = [
        'AAPL', 'MSFT', 'UNH', 'GS', 'HD',
        'CAT', 'BA', 'MCD', 'AMGN', 'V',
        'HON', 'TRV', 'AXP', 'JPM', 'CVX',
        'IBM', 'CRM', 'JNJ', 'PG', 'WMT',
        'MRK', 'DIS', 'NKE', 'MMM', 'DOW',
        'KO', 'CSCO', 'INTC', 'VZ', 'WBA',
    ]

    return yahoo_bundle(tickers=dow_tickers)
