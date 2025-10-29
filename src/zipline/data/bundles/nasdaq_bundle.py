"""
NASDAQ Data Link Bundle for Zipline
====================================

This module provides a data bundle for zipline that fetches data from NASDAQ Data Link
(formerly Quandl) and stores it in zipline's native bundle format for backtesting.

Usage:
    # Register the bundle in your extension.py or notebook
    from zipline.data.bundles import register
    from zipline.data.bundles.nasdaq_bundle import nasdaq_bundle

    register(
        'nasdaq',
        nasdaq_bundle(
            api_key='your_api_key',
            tickers=['AAPL', 'MSFT', 'GOOGL'],
            dataset='EOD',  # or 'WIKI'
        ),
    )

    # Ingest the bundle
    # zipline ingest -b nasdaq

Requirements:
    - nasdaq-data-link package
    - NASDAQ_DATA_LINK_API_KEY environment variable or pass api_key parameter
"""

import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Optional, Dict

try:
    import nasdaqdatalink
except ImportError:
    nasdaqdatalink = None


def nasdaq_bundle(
    api_key: Optional[str] = None,
    tickers: Optional[List[str]] = None,
    dataset: str = 'EOD',
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
):
    """
    Create a zipline data bundle from NASDAQ Data Link.

    Parameters
    ----------
    api_key : str, optional
        NASDAQ Data Link API key. If not provided, will use NASDAQ_DATA_LINK_API_KEY
        environment variable.
    tickers : list of str, optional
        List of ticker symbols to fetch. If not provided, will use a default set
        of popular stocks.
    dataset : str, default 'EOD'
        NASDAQ Data Link dataset to use. Options:
        - 'EOD': End of Day US Stock Prices (Premium, current data)
        - 'WIKI': Wiki EOD Stock Prices (FREE but DISCONTINUED March 2018)

        **IMPORTANT**: WIKI dataset was discontinued in March 2018 and contains
        NO data after March 27, 2018. It's only useful for historical backtests
        before 2018. For current data, you need a premium subscription to EOD.
    start_date : str, optional
        Start date for data fetch (YYYY-MM-DD). Defaults to 10 years ago.
        For WIKI dataset, end_date is automatically capped at 2018-03-27.
    end_date : str, optional
        End date for data fetch (YYYY-MM-DD). Defaults to today.
        For WIKI dataset, this is automatically capped at 2018-03-27.

    Returns
    -------
    callable
        A bundle ingest function compatible with zipline's bundle system.

    Examples
    --------
    >>> from zipline.data.bundles import register
    >>> from zipline.data.bundles.nasdaq_bundle import nasdaq_bundle
    >>>
    >>> # Register with default settings
    >>> register('nasdaq', nasdaq_bundle())
    >>>
    >>> # Register with custom tickers
    >>> register('nasdaq-tech', nasdaq_bundle(
    ...     tickers=['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA'],
    ...     dataset='EOD',
    ... ))
    """

    # Get API key
    if api_key is None:
        api_key = os.environ.get('NASDAQ_DATA_LINK_API_KEY')

    if not api_key:
        raise ValueError(
            "NASDAQ Data Link API key required. Set NASDAQ_DATA_LINK_API_KEY "
            "environment variable or pass api_key parameter."
        )

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

    # WIKI dataset was discontinued on March 27, 2018
    # Automatically cap dates to prevent errors
    if dataset == 'WIKI':
        wiki_end_date = '2018-03-27'
        if pd.Timestamp(end_date) > pd.Timestamp(wiki_end_date):
            print(f"\n⚠️  WARNING: WIKI dataset was discontinued on March 27, 2018")
            print(f"   Automatically capping end_date from {end_date} to {wiki_end_date}")
            print(f"   For current data, use dataset='EOD' (requires premium subscription)")
            print(f"   Or use the Yahoo Finance bundle (free)\n")
            end_date = wiki_end_date

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

        if nasdaqdatalink is None:
            raise ImportError(
                "nasdaq-data-link package is required. "
                "Install with: pip install nasdaq-data-link"
            )

        # Configure API
        nasdaqdatalink.ApiConfig.api_key = api_key

        # Metadata for assets
        metadata = []

        # Fetch data for each ticker
        all_data = []
        dividends_data = []
        splits_data = []

        print(f"\nFetching data from NASDAQ Data Link ({dataset})...")
        print(f"Date range: {start_date} to {end_date}")
        print(f"Tickers: {len(tickers)}\n")

        for i, ticker in enumerate(tickers, 1):
            print(f"  [{i}/{len(tickers)}] Fetching {ticker}...", end=" ")

            try:
                # Fetch data from NASDAQ Data Link
                nasdaq_code = f"{dataset}/{ticker}"
                df = nasdaqdatalink.get(
                    nasdaq_code,
                    start_date=start_date,
                    end_date=end_date,
                )

                if df.empty:
                    print("❌ No data")
                    continue

                # Standardize column names
                column_mapping = {
                    'Adj. Open': 'Adj_Open',
                    'Adj. High': 'Adj_High',
                    'Adj. Low': 'Adj_Low',
                    'Adj. Close': 'Adj_Close',
                    'Adj. Volume': 'Adj_Volume',
                    'Ex-Dividend': 'Dividend',
                    'Split Ratio': 'Split',
                }
                df = df.rename(columns=column_mapping)

                # Prepare data for zipline format
                # Zipline expects: open, high, low, close, volume
                ohlcv = pd.DataFrame({
                    'open': df.get('Adj_Open', df['Open']),
                    'high': df.get('Adj_High', df['High']),
                    'low': df.get('Adj_Low', df['Low']),
                    'close': df.get('Adj_Close', df['Close']),
                    'volume': df.get('Adj_Volume', df['Volume']),
                })

                # Add symbol and sid
                ohlcv['symbol'] = ticker
                ohlcv['sid'] = i

                # Ensure no NaN values
                ohlcv = ohlcv.fillna(method='ffill').fillna(method='bfill')

                all_data.append(ohlcv)

                # Extract dividends if available
                if 'Dividend' in df.columns:
                    divs = df[df['Dividend'] > 0]['Dividend']
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

                # Extract splits if available
                if 'Split' in df.columns:
                    splits = df[df['Split'] != 1.0]['Split']
                    if not splits.empty:
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
                    'start_date': df.index[0],
                    'end_date': df.index[-1],
                    'exchange': 'NYSE',  # Default, should be enhanced
                    'sid': i,
                })

                print(f"✓ {len(df)} days")

            except nasdaqdatalink.errors.quandl_error.NotFoundError:
                print(f"❌ Not found in {dataset}")
            except nasdaqdatalink.errors.quandl_error.ForbiddenError:
                print(f"❌ Access denied (premium required)")
            except Exception as e:
                print(f"❌ Error: {e}")

        if not all_data:
            raise ValueError("No data was fetched. Check your API key and ticker list.")

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
        else:
            dividends_df = pd.DataFrame(columns=['sid', 'amount', 'ex_date', 'record_date', 'declared_date', 'pay_date'])

        if splits_data:
            splits_df = pd.concat(splits_data, ignore_index=True)
            splits_df['effective_date'] = pd.to_datetime(splits_df['effective_date'])
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

def nasdaq_free_bundle():
    """
    Free tier NASDAQ bundle using WIKI dataset.

    Note: WIKI dataset is discontinued but still available for historical data.
    """
    return nasdaq_bundle(
        dataset='WIKI',
        tickers=['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA'],
    )


def nasdaq_premium_bundle():
    """
    Premium NASDAQ bundle using EOD dataset.

    Requires premium NASDAQ Data Link subscription.
    """
    return nasdaq_bundle(
        dataset='EOD',
        tickers=[
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA',
            'NVDA', 'META', 'JPM', 'V', 'WMT',
            'MA', 'JNJ', 'UNH', 'HD', 'PG',
            'XOM', 'BAC', 'ABBV', 'KO', 'PFE',
        ],
    )


def nasdaq_sp500_bundle():
    """
    NASDAQ bundle for S&P 500 stocks.

    Requires premium NASDAQ Data Link subscription.
    Note: This is a subset - full S&P 500 would require all 500 tickers.
    """
    sp500_tickers = [
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA',
        'TSLA', 'META', 'BRK.B', 'V', 'JNJ',
        'WMT', 'JPM', 'MA', 'PG', 'UNH',
        'HD', 'CVX', 'MRK', 'ABBV', 'PEP',
        'KO', 'COST', 'AVGO', 'TMO', 'DIS',
    ]

    return nasdaq_bundle(
        dataset='EOD',
        tickers=sp500_tickers,
    )
