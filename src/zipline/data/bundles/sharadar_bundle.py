"""
Sharadar Equity Prices bundle for Zipline.

This bundle uses NASDAQ Data Link's Sharadar dataset, which provides
high-quality US equity pricing and fundamental data.

Sharadar is a PREMIUM dataset that requires a subscription.
Sign up at: https://data.nasdaq.com/databases/SFA

The bundle uses two main tables:
- SEP (Sharadar Equity Prices): Daily OHLCV pricing data
- ACTIONS: Corporate actions (splits, dividends, etc.)

Example usage:
    from zipline.data.bundles import register
    from zipline.data.bundles.sharadar_bundle import sharadar_bundle

    register('sharadar', sharadar_bundle())

    # Then ingest:
    # zipline ingest -b sharadar
"""

import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Optional, List
import time
import requests
from io import BytesIO
from zipfile import ZipFile

from zipline.data.bundles import core as bundles


def sharadar_bundle(
    tickers: Optional[List[str]] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    api_key: Optional[str] = None,
):
    """
    Create a zipline data bundle from Sharadar Equity Prices.

    Parameters
    ----------
    tickers : list of str, optional
        List of ticker symbols to include. If None, downloads all available tickers.
        Note: Downloading all tickers requires significant storage (~10GB+) and time.
        It's recommended to start with a subset.
    start_date : str, optional
        Start date in 'YYYY-MM-DD' format. If None, defaults to 10 years ago.
    end_date : str, optional
        End date in 'YYYY-MM-DD' format. If None, defaults to today.
    api_key : str, optional
        NASDAQ Data Link API key. If None, will use NASDAQ_DATA_LINK_API_KEY
        environment variable.

    Returns
    -------
    callable
        Bundle ingest function for zipline.

    Examples
    --------
    # All tickers (large download)
    register('sharadar', sharadar_bundle())

    # Specific tickers
    register('sharadar-tech', sharadar_bundle(
        tickers=['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META'],
    ))

    # Date range
    register('sharadar-recent', sharadar_bundle(
        start_date='2020-01-01',
    ))

    Notes
    -----
    Sharadar is a PREMIUM dataset. You need a paid subscription from:
    https://data.nasdaq.com/databases/SFA

    The SEP table contains comprehensive US equity pricing data with
    corporate action adjustments already applied.
    """
    # Get API key
    if api_key is None:
        api_key = os.environ.get('NASDAQ_DATA_LINK_API_KEY')
        if api_key is None:
            raise ValueError(
                "NASDAQ Data Link API key required. "
                "Set NASDAQ_DATA_LINK_API_KEY environment variable or pass api_key parameter."
            )

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
        Ingest Sharadar data into zipline format.
        """
        print(f"\n{'='*60}")
        print("Sharadar Bundle Ingestion")
        print(f"{'='*60}")
        print(f"Date range: {start_date} to {end_date}")
        if tickers:
            print(f"Tickers: {len(tickers)} symbols")
        else:
            print("Tickers: ALL (this may take a while and use significant storage)")
        print(f"{'='*60}\n")

        # Download SEP (pricing) data
        print("Step 1/3: Downloading Sharadar Equity Prices (SEP table)...")
        sep_data = download_sharadar_table(
            table='SEP',
            api_key=api_key,
            tickers=tickers,
            start_date=start_date,
            end_date=end_date,
        )

        if sep_data.empty:
            raise ValueError("No pricing data downloaded. Check your subscription and filters.")

        print(f"Downloaded {len(sep_data):,} price records for {sep_data['ticker'].nunique()} tickers")

        # Download ACTIONS (corporate actions) data
        print("\nStep 2/3: Downloading corporate actions (ACTIONS table)...")
        actions_data = download_sharadar_table(
            table='ACTIONS',
            api_key=api_key,
            tickers=tickers,
            start_date=start_date,
            end_date=end_date,
        )

        if not actions_data.empty:
            print(f"Downloaded {len(actions_data):,} corporate action records")
        else:
            print("No corporate actions data available")

        # Process data
        print("\nStep 3/3: Processing data for zipline...")

        # Prepare metadata first (to get sid assignments)
        print("Preparing asset metadata...")
        metadata = prepare_asset_metadata(sep_data, start_date, end_date)

        # Create symbol to sid mapping
        symbol_to_sid = {row['symbol']: idx for idx, row in metadata.iterrows()}

        # Add sid to pricing data
        sep_data['sid'] = sep_data['ticker'].map(symbol_to_sid)

        # Write metadata
        print("Writing asset metadata...")
        asset_db_writer.write(equities=metadata)

        # Prepare and write pricing data
        print("Writing daily bars...")
        def data_generator():
            """Generator that yields (sid, dataframe) for each symbol"""
            for sid in sorted(sep_data['sid'].unique()):
                if pd.isna(sid):
                    continue  # Skip any unmapped tickers

                symbol_data = sep_data[sep_data['sid'] == sid].copy()

                # Set date as index
                symbol_data = symbol_data.set_index('date')

                # Ensure timezone-naive
                if symbol_data.index.tz is not None:
                    symbol_data.index = symbol_data.index.tz_localize(None)

                # Use closeunadj for close (adjustments handled separately)
                symbol_data['close'] = symbol_data['closeunadj']

                # Ensure all required columns and proper types
                required_cols = ['open', 'high', 'low', 'close', 'volume']
                symbol_data = symbol_data[required_cols].copy()

                # Convert to float
                for col in required_cols:
                    symbol_data[col] = symbol_data[col].astype(float)

                # Remove any NaN rows
                symbol_data = symbol_data.dropna()

                # Sort by date
                symbol_data = symbol_data.sort_index()

                yield int(sid), symbol_data

        daily_bar_writer.write(data_generator(), show_progress=show_progress)

        # Prepare and write adjustments
        print("Writing adjustments...")
        adjustments = prepare_adjustments(actions_data, symbol_to_sid)
        adjustment_writer.write(**adjustments)

        print(f"\n{'='*60}")
        print("✓ Sharadar bundle ingestion complete!")
        print(f"{'='*60}\n")

    return ingest


def download_sharadar_table(
    table: str,
    api_key: str,
    tickers: Optional[List[str]] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> pd.DataFrame:
    """
    Download a Sharadar table using bulk download API.

    Parameters
    ----------
    table : str
        Table name (e.g., 'SEP', 'ACTIONS', 'SF1', 'TICKERS')
    api_key : str
        NASDAQ Data Link API key
    tickers : list of str, optional
        Filter by tickers
    start_date : str, optional
        Start date filter
    end_date : str, optional
        End date filter

    Returns
    -------
    pd.DataFrame
        Downloaded data
    """
    # Build URL for bulk download
    base_url = f'https://data.nasdaq.com/api/v3/datatables/SHARADAR/{table}.json'
    params = {
        'qopts.export': 'true',
        'api_key': api_key,
    }

    # Add filters if provided
    if tickers:
        params['ticker'] = ','.join(tickers)
    if start_date:
        params['date.gte'] = start_date
    if end_date:
        params['date.lte'] = end_date

    # Request bulk download
    print(f"  Requesting bulk download for {table} table...")
    response = requests.get(base_url, params=params)
    response.raise_for_status()

    result = response.json()

    # Check if bulk download is available
    if 'datatable_bulk_download' not in result:
        # Fall back to paginated download for small datasets
        print(f"  Bulk download not available, using paginated download...")
        return download_paginated(table, api_key, params)

    bulk_info = result['datatable_bulk_download']
    file_status = bulk_info['file']['status']
    file_link = bulk_info['file']['link']

    # Wait for file to be ready
    max_wait = 300  # 5 minutes
    waited = 0
    valid_statuses = ['fresh']
    wait_statuses = ['regenerating', 'creating']

    while file_status in wait_statuses and waited < max_wait:
        if file_status == 'creating':
            print(f"  File is being created, waiting... ({waited}s)")
        else:
            print(f"  File is regenerating, waiting... ({waited}s)")

        time.sleep(10)
        waited += 10

        # Check status again
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        result = response.json()
        file_status = result['datatable_bulk_download']['file']['status']
        file_link = result['datatable_bulk_download']['file']['link']

    if file_status not in valid_statuses:
        raise RuntimeError(f"Bulk download file not ready after {waited}s. Status: {file_status}")

    # Download the file
    print(f"  Downloading {table} data from {file_link}...")
    download_response = requests.get(file_link)
    download_response.raise_for_status()

    # Extract from zip
    print(f"  Extracting {table} data...")
    with ZipFile(BytesIO(download_response.content)) as zf:
        # Get the CSV filename (usually SHARADAR_TABLE.csv)
        csv_filename = zf.namelist()[0]
        with zf.open(csv_filename) as csv_file:
            df = pd.read_csv(csv_file, parse_dates=['date'])

    print(f"  ✓ Downloaded {len(df):,} records from {table}")
    return df


def download_paginated(table: str, api_key: str, base_params: dict) -> pd.DataFrame:
    """
    Download data using paginated API (for smaller datasets).

    Parameters
    ----------
    table : str
        Table name
    api_key : str
        API key
    base_params : dict
        Base query parameters

    Returns
    -------
    pd.DataFrame
        Downloaded data
    """
    all_data = []
    cursor_id = None

    base_url = f'https://data.nasdaq.com/api/v3/datatables/SHARADAR/{table}.json'

    while True:
        params = base_params.copy()
        if cursor_id:
            params['qopts.cursor_id'] = cursor_id

        response = requests.get(base_url, params=params)
        response.raise_for_status()
        result = response.json()

        # Extract data
        datatable = result['datatable']
        columns = [col['name'] for col in datatable['columns']]
        data = datatable['data']

        if not data:
            break

        df_chunk = pd.DataFrame(data, columns=columns)
        all_data.append(df_chunk)

        # Check if there's more data
        meta = result['meta']
        if meta.get('next_cursor_id'):
            cursor_id = meta['next_cursor_id']
            print(f"  Downloaded {len(df_chunk)} records, fetching more...")
        else:
            break

    if not all_data:
        return pd.DataFrame()

    df = pd.concat(all_data, ignore_index=True)

    # Parse date column if it exists
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])

    return df


def prepare_asset_metadata(
    sep_data: pd.DataFrame,
    start_date: str,
    end_date: str,
) -> pd.DataFrame:
    """
    Prepare asset metadata for zipline.

    Parameters
    ----------
    sep_data : pd.DataFrame
        Raw SEP data
    start_date : str
        Bundle start date
    end_date : str
        Bundle end date

    Returns
    -------
    pd.DataFrame
        Asset metadata
    """
    # Get first and last date for each ticker
    metadata = sep_data.groupby('ticker').agg({
        'date': ['min', 'max'],
    }).reset_index()

    metadata.columns = ['symbol', 'start_date', 'end_date']

    # Add required columns
    metadata['exchange'] = 'NASDAQ'  # Sharadar is primarily NASDAQ/NYSE
    metadata['asset_name'] = metadata['symbol']

    # Convert dates to pandas Timestamp
    metadata['start_date'] = pd.to_datetime(metadata['start_date'])
    metadata['end_date'] = pd.to_datetime(metadata['end_date'])

    # Ensure dates are within bundle range
    bundle_start = pd.Timestamp(start_date)
    bundle_end = pd.Timestamp(end_date)

    metadata['start_date'] = metadata['start_date'].clip(lower=bundle_start)
    metadata['end_date'] = metadata['end_date'].clip(upper=bundle_end)

    return metadata


def prepare_adjustments(
    actions_data: pd.DataFrame,
    ticker_to_sid: dict,
) -> dict:
    """
    Prepare splits and dividends from ACTIONS table.

    Parameters
    ----------
    actions_data : pd.DataFrame
        Corporate actions data
    ticker_to_sid : dict
        Mapping of ticker symbols to sid integers

    Returns
    -------
    dict
        Dictionary with 'splits' and 'dividends' DataFrames
    """
    if actions_data.empty:
        # Return empty adjustments
        return {
            'splits': pd.DataFrame(columns=['sid', 'ratio', 'effective_date']),
            'dividends': pd.DataFrame(columns=['sid', 'amount', 'ex_date', 'record_date', 'declared_date', 'pay_date']),
        }

    # Process splits
    splits = actions_data[actions_data['action'] == 'Split'].copy()
    if not splits.empty:
        splits['sid'] = splits['ticker'].map(ticker_to_sid)
        splits['ratio'] = splits['value'].astype(float)
        splits['effective_date'] = pd.to_datetime(splits['date'])
        splits = splits[['sid', 'ratio', 'effective_date']].dropna()
    else:
        splits = pd.DataFrame(columns=['sid', 'ratio', 'effective_date'])

    # Process dividends
    dividends = actions_data[actions_data['action'] == 'Dividend'].copy()
    if not dividends.empty:
        dividends['sid'] = dividends['ticker'].map(ticker_to_sid)
        dividends['amount'] = dividends['value'].astype(float)
        dividends['ex_date'] = pd.to_datetime(dividends['date'])
        # Sharadar doesn't provide record/declared/pay dates, use ex_date for all
        dividends['record_date'] = dividends['ex_date']
        dividends['declared_date'] = dividends['ex_date']
        dividends['pay_date'] = dividends['ex_date']
        dividends = dividends[['sid', 'amount', 'ex_date', 'record_date', 'declared_date', 'pay_date']].dropna()
    else:
        dividends = pd.DataFrame(columns=['sid', 'amount', 'ex_date', 'record_date', 'declared_date', 'pay_date'])

    return {
        'splits': splits,
        'dividends': dividends,
    }


# Pre-configured bundle variants
def sharadar_tech_bundle():
    """Sharadar bundle with major tech stocks."""
    return sharadar_bundle(
        tickers=[
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META',
            'NVDA', 'TSLA', 'NFLX', 'ADBE', 'CRM',
            'INTC', 'AMD', 'ORCL', 'CSCO', 'AVGO',
        ],
    )


def sharadar_sp500_sample_bundle():
    """Sharadar bundle with S&P 500 sample (top 30 by market cap)."""
    return sharadar_bundle(
        tickers=[
            # Top tech
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA',
            'META', 'TSLA', 'BRK.B', 'V', 'UNH',
            # Financials
            'JPM', 'JNJ', 'WMT', 'MA', 'PG',
            'XOM', 'CVX', 'HD', 'MRK', 'ABBV',
            # Others
            'PFE', 'KO', 'PEP', 'COST', 'AVGO',
            'TMO', 'DIS', 'CSCO', 'ABT', 'ACN',
        ],
    )


def sharadar_all_bundle():
    """
    Sharadar bundle with ALL tickers.

    WARNING: This downloads ALL US equities (~8,000+ tickers).
    - Download time: 10-30 minutes
    - Storage: 10-20 GB
    - Recommended for production use only.
    """
    return sharadar_bundle(tickers=None)  # None = all tickers


# Register default bundles
def register_sharadar_bundles():
    """Register common Sharadar bundle configurations."""
    from zipline.data.bundles import register

    register('sharadar-tech', sharadar_tech_bundle())
    register('sharadar-sp500', sharadar_sp500_sample_bundle())
    register('sharadar-all', sharadar_all_bundle())
