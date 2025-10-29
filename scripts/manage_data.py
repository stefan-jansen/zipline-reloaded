#!/usr/bin/env python
"""
Zipline Data Management Script
===============================

This script provides a unified interface for managing zipline data bundles,
including initial setup, daily updates, and maintenance.

Usage:
    # Initial setup - register and ingest bundles
    python scripts/manage_data.py setup --source yahoo

    # Daily update - update existing bundle with latest data
    python scripts/manage_data.py update --bundle yahoo

    # List available bundles
    python scripts/manage_data.py list

    # Clean old bundle data
    python scripts/manage_data.py clean --bundle yahoo --keep-last 5

Examples:
    # Setup Yahoo Finance bundle with custom tickers
    python scripts/manage_data.py setup --source yahoo --tickers AAPL,MSFT,GOOGL

    # Setup NASDAQ Data Link bundle (requires API key)
    export NASDAQ_DATA_LINK_API_KEY=your_key
    python scripts/manage_data.py setup --source nasdaq --dataset EOD

    # Setup Sharadar bundle (requires premium subscription)
    export NASDAQ_DATA_LINK_API_KEY=your_key
    python scripts/manage_data.py setup --source sharadar --tickers AAPL,MSFT,GOOGL

    # Update all bundles
    python scripts/manage_data.py update --all

    # Schedule daily updates (add to crontab)
    # Run at 5 PM ET after market close, Mon-Fri
    # 0 17 * * 1-5 cd /path/to/zipline && python scripts/manage_data.py update --all
"""

import os
import sys
import argparse
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))


def setup_bundle(source, tickers=None, dataset=None, bundle_name=None):
    """
    Register and ingest a new bundle.

    Parameters
    ----------
    source : str
        Data source: 'yahoo', 'nasdaq', or 'sharadar'
    tickers : list of str, optional
        Custom ticker list
    dataset : str, optional
        For NASDAQ: 'EOD' or 'WIKI'
        (Not used for Sharadar - it only uses SEP table)
    bundle_name : str, optional
        Custom bundle name (default: source name)
    """
    from zipline.data.bundles import register

    if bundle_name is None:
        bundle_name = source

    print(f"\n{'='*70}")
    print(f"SETTING UP {source.upper()} BUNDLE: {bundle_name}")
    print(f"{'='*70}\n")

    # Prepare ticker list
    ticker_list = None
    if tickers:
        ticker_list = [t.strip() for t in tickers.split(',')]
        print(f"Custom tickers: {', '.join(ticker_list)}")

    # Register the appropriate bundle
    if source == 'yahoo':
        from zipline.data.bundles.yahoo_bundle import yahoo_bundle

        print("Registering Yahoo Finance bundle...")

        if ticker_list:
            register(bundle_name, yahoo_bundle(tickers=ticker_list))
        else:
            register(bundle_name, yahoo_bundle())

    elif source == 'nasdaq':
        from zipline.data.bundles.nasdaq_bundle import nasdaq_bundle

        # Check for API key
        api_key = os.environ.get('NASDAQ_DATA_LINK_API_KEY')
        if not api_key:
            print("ERROR: NASDAQ_DATA_LINK_API_KEY environment variable not set!")
            print("\nPlease set your API key:")
            print("  export NASDAQ_DATA_LINK_API_KEY='your_key_here'")
            print("\nOr add to .env file:")
            print("  NASDAQ_DATA_LINK_API_KEY=your_key_here")
            sys.exit(1)

        print(f"Registering NASDAQ Data Link bundle (dataset: {dataset or 'EOD'})...")

        kwargs = {}
        if ticker_list:
            kwargs['tickers'] = ticker_list
        if dataset:
            kwargs['dataset'] = dataset

        register(bundle_name, nasdaq_bundle(**kwargs))

    elif source == 'sharadar':
        from zipline.data.bundles.sharadar_bundle import sharadar_bundle

        # Check for API key
        api_key = os.environ.get('NASDAQ_DATA_LINK_API_KEY')
        if not api_key:
            print("ERROR: NASDAQ_DATA_LINK_API_KEY environment variable not set!")
            print("\nSharadar requires a NASDAQ Data Link API key with Sharadar subscription.")
            print("\nPlease set your API key:")
            print("  export NASDAQ_DATA_LINK_API_KEY='your_key_here'")
            print("\nOr add to .env file:")
            print("  NASDAQ_DATA_LINK_API_KEY=your_key_here")
            print("\nSubscribe to Sharadar at:")
            print("  https://data.nasdaq.com/databases/SFA")
            sys.exit(1)

        print("Registering Sharadar Equity Prices bundle...")
        if not ticker_list:
            print("\n⚠️  WARNING: No tickers specified - will download ALL US equities!")
            print("   This will take 10-30 minutes and use 10-20 GB storage.")
            print("   For testing, specify tickers with --tickers")
            print("   Example: --tickers AAPL,MSFT,GOOGL,AMZN,TSLA\n")
            response = input("Continue with ALL tickers? [y/N]: ")
            if response.lower() != 'y':
                print("Aborted. Specify tickers with --tickers to continue.")
                sys.exit(0)

        kwargs = {}
        if ticker_list:
            kwargs['tickers'] = ticker_list

        register(bundle_name, sharadar_bundle(**kwargs))

    else:
        print(f"ERROR: Unknown source '{source}'. Use 'yahoo', 'nasdaq', or 'sharadar'")
        sys.exit(1)

    print(f"✓ Bundle '{bundle_name}' registered\n")

    # Ingest the bundle
    print(f"Ingesting {bundle_name} bundle...")
    print(f"This may take several minutes...\n")

    result = subprocess.run(
        ['zipline', 'ingest', '-b', bundle_name],
        capture_output=False,
    )

    if result.returncode == 0:
        print(f"\n{'='*70}")
        print(f"✓ SUCCESS: {bundle_name} bundle is ready!")
        print(f"{'='*70}\n")
        print(f"You can now use this bundle in backtests:")
        print(f"  zipline run -f strategy.py -b {bundle_name}")
        print()
    else:
        print(f"\n{'='*70}")
        print(f"❌ ERROR: Bundle ingestion failed")
        print(f"{'='*70}\n")
        sys.exit(1)


def update_bundle(bundle_name):
    """
    Update an existing bundle with latest data.

    Parameters
    ----------
    bundle_name : str
        Name of bundle to update
    """
    print(f"\n{'='*70}")
    print(f"UPDATING BUNDLE: {bundle_name}")
    print(f"{'='*70}\n")

    print(f"Fetching latest data...")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    result = subprocess.run(
        ['zipline', 'ingest', '-b', bundle_name],
        capture_output=False,
    )

    if result.returncode == 0:
        print(f"\n✓ SUCCESS: {bundle_name} updated!")
    else:
        print(f"\n❌ ERROR: Update failed for {bundle_name}")
        sys.exit(1)


def list_bundles():
    """List all available bundles."""
    print(f"\n{'='*70}")
    print("AVAILABLE BUNDLES")
    print(f"{'='*70}\n")

    result = subprocess.run(
        ['zipline', 'bundles'],
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        print(result.stdout)
    else:
        print("ERROR: Could not list bundles")
        print(result.stderr)


def clean_bundle(bundle_name, keep_last=3):
    """
    Clean old bundle ingestion data.

    Parameters
    ----------
    bundle_name : str
        Name of bundle to clean
    keep_last : int
        Number of recent ingestions to keep
    """
    print(f"\n{'='*70}")
    print(f"CLEANING BUNDLE: {bundle_name}")
    print(f"{'='*70}\n")

    print(f"Keeping last {keep_last} ingestions...")
    print(f"Removing older data...\n")

    result = subprocess.run(
        ['zipline', 'clean', '-b', bundle_name, '--keep-last', str(keep_last)],
        capture_output=False,
    )

    if result.returncode == 0:
        print(f"\n✓ SUCCESS: {bundle_name} cleaned!")
    else:
        print(f"\n❌ ERROR: Cleaning failed for {bundle_name}")


def main():
    parser = argparse.ArgumentParser(
        description='Manage zipline data bundles',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # Setup command
    setup_parser = subparsers.add_parser('setup', help='Register and ingest a new bundle')
    setup_parser.add_argument(
        '--source',
        required=True,
        choices=['yahoo', 'nasdaq', 'sharadar'],
        help='Data source: yahoo, nasdaq, or sharadar',
    )
    setup_parser.add_argument(
        '--tickers',
        help='Comma-separated list of tickers (e.g., AAPL,MSFT,GOOGL)',
    )
    setup_parser.add_argument(
        '--dataset',
        choices=['EOD', 'WIKI'],
        help='NASDAQ dataset (EOD=premium, WIKI=free)',
    )
    setup_parser.add_argument(
        '--name',
        help='Custom bundle name (default: source name)',
    )

    # Update command
    update_parser = subparsers.add_parser('update', help='Update existing bundle(s)')
    update_parser.add_argument(
        '--bundle',
        help='Bundle name to update',
    )
    update_parser.add_argument(
        '--all',
        action='store_true',
        help='Update all bundles',
    )

    # List command
    subparsers.add_parser('list', help='List available bundles')

    # Clean command
    clean_parser = subparsers.add_parser('clean', help='Clean old bundle data')
    clean_parser.add_argument(
        '--bundle',
        required=True,
        help='Bundle name to clean',
    )
    clean_parser.add_argument(
        '--keep-last',
        type=int,
        default=3,
        help='Number of recent ingestions to keep (default: 3)',
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Execute command
    if args.command == 'setup':
        setup_bundle(
            source=args.source,
            tickers=args.tickers,
            dataset=args.dataset,
            bundle_name=args.name,
        )

    elif args.command == 'update':
        if args.all:
            # Get list of bundles and update each
            result = subprocess.run(
                ['zipline', 'bundles'],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                # Parse bundle names from output
                # This is a simplified parser - may need adjustment
                bundles = []
                for line in result.stdout.split('\n'):
                    if line.strip() and not line.startswith('='):
                        parts = line.split()
                        if parts:
                            bundles.append(parts[0])

                print(f"Found {len(bundles)} bundles to update\n")

                for bundle in bundles:
                    try:
                        update_bundle(bundle)
                    except Exception as e:
                        print(f"Warning: Failed to update {bundle}: {e}")
                        continue
            else:
                print("ERROR: Could not list bundles")
                sys.exit(1)
        elif args.bundle:
            update_bundle(args.bundle)
        else:
            print("ERROR: Specify --bundle or --all")
            sys.exit(1)

    elif args.command == 'list':
        list_bundles()

    elif args.command == 'clean':
        clean_bundle(args.bundle, args.keep_last)


if __name__ == '__main__':
    main()
