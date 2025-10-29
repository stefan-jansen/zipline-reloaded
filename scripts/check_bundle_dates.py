"""
Check Bundle Data Range - Notebook Helper
==========================================

This script helps you find out what date range you have for your ingested bundles.
Run this in a Jupyter notebook cell or as a standalone script.
"""

import pandas as pd
from pathlib import Path
import sqlite3

def check_bundle_data_range(bundle_name='sharadar'):
    """
    Check the date range available in a specific bundle.

    Parameters:
    -----------
    bundle_name : str
        Name of the bundle (e.g., 'sharadar', 'yahoo', 'yahoo-tech')
    """
    # Find the bundle directory
    bundle_dir = Path.home() / '.zipline' / 'data' / bundle_name

    if not bundle_dir.exists():
        print(f"❌ Bundle '{bundle_name}' not found!")
        print(f"   Looking in: {bundle_dir}")
        print("\n   Available bundles:")
        data_dir = Path.home() / '.zipline' / 'data'
        if data_dir.exists():
            bundles = [d.name for d in data_dir.iterdir() if d.is_dir()]
            for b in bundles:
                print(f"     - {b}")
        else:
            print("     None (no data ingested yet)")
        return None

    # Get the most recent ingestion
    ingestions = sorted([d for d in bundle_dir.iterdir() if d.is_dir()], reverse=True)
    if not ingestions:
        print(f"❌ No ingestion data found for bundle '{bundle_name}'")
        return None

    latest_ingestion = ingestions[0]
    print(f"✅ Bundle: {bundle_name}")
    print(f"   Ingestion: {latest_ingestion.name}\n")

    # Check the asset database
    asset_db_path = latest_ingestion / 'assets-8.db'
    if not asset_db_path.exists():
        # Try older version
        asset_db_path = latest_ingestion / 'assets-7.db'

    if not asset_db_path.exists():
        print(f"❌ Asset database not found in {latest_ingestion}")
        return None

    # Connect to the database
    conn = sqlite3.connect(str(asset_db_path))

    # Get symbols and their date ranges
    query = """
    SELECT
        symbol,
        MIN(start_date) as first_date,
        MAX(end_date) as last_date
    FROM equities
    WHERE asset_type = 'equity'
    GROUP BY symbol
    ORDER BY symbol
    """

    df = pd.read_sql_query(query, conn)

    if len(df) == 0:
        print("❌ No equity data found in bundle")
        conn.close()
        return None

    # Convert Unix timestamps to dates
    df['first_date'] = pd.to_datetime(df['first_date'], unit='s')
    df['last_date'] = pd.to_datetime(df['last_date'], unit='s')

    # Overall date range
    overall_start = df['first_date'].min()
    overall_end = df['last_date'].max()

    print("="*70)
    print("📊 OVERALL DATE RANGE")
    print("="*70)
    print(f"   Earliest data: {overall_start.date()}")
    print(f"   Latest data:   {overall_end.date()}")
    print(f"   Total symbols: {len(df)}")
    print()

    print("="*70)
    print("📋 PER-SYMBOL DATE RANGES (First 20 symbols)")
    print("="*70)
    print(f"{'Symbol':<10} {'First Date':<15} {'Last Date':<15} {'Days':<10}")
    print("-"*70)

    for idx, row in df.head(20).iterrows():
        days = (row['last_date'] - row['first_date']).days
        print(f"{row['symbol']:<10} {str(row['first_date'].date()):<15} "
              f"{str(row['last_date'].date()):<15} {days:<10}")

    if len(df) > 20:
        print(f"\n... and {len(df) - 20} more symbols")

    print("\n" + "="*70)
    print("💡 RECOMMENDED BACKTEST DATES")
    print("="*70)

    # Find the common date range where most symbols have data
    # Use the 90th percentile of start dates and 10th percentile of end dates
    common_start = df['first_date'].quantile(0.9)
    common_end = df['last_date'].quantile(0.1)

    print(f"   For best coverage, use:")
    print(f"   START_DATE = pd.Timestamp('{common_start.date()}')")
    print(f"   END_DATE = pd.Timestamp('{common_end.date()}')")
    print(f"   BUNDLE_NAME = '{bundle_name}'")

    conn.close()

    return {
        'bundle': bundle_name,
        'symbols': len(df),
        'earliest': overall_start,
        'latest': overall_end,
        'recommended_start': common_start,
        'recommended_end': common_end,
        'symbol_details': df
    }


if __name__ == '__main__':
    import sys

    # Check which bundles to examine
    bundle_name = sys.argv[1] if len(sys.argv) > 1 else None

    if bundle_name:
        check_bundle_data_range(bundle_name)
    else:
        # Check all available bundles
        data_dir = Path.home() / '.zipline' / 'data'
        if data_dir.exists():
            bundles = [d.name for d in data_dir.iterdir() if d.is_dir()]

            if bundles:
                print(f"Found {len(bundles)} bundle(s). Checking each...\n")
                for bundle in bundles:
                    check_bundle_data_range(bundle)
                    print("\n" + "="*70 + "\n")
            else:
                print("❌ No bundles found!")
                print("\n📋 To ingest data, run:")
                print("   python scripts/manage_data.py setup --source yahoo")
                print("   OR")
                print("   python scripts/manage_data.py setup --source sharadar --tickers AAPL,MSFT,GOOGL")
        else:
            print("❌ No .zipline/data directory found!")
            print("   You need to ingest data first.")
