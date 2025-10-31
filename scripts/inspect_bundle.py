#!/usr/bin/env python
"""
Detailed Bundle Inspector
=========================

Shows comprehensive information about your Sharadar bundle data.

Usage:
    python scripts/inspect_bundle.py
    python scripts/inspect_bundle.py --ticker AAPL
"""

import sys
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import pandas as pd
from zipline.utils.calendar_utils import get_calendar
from zipline.data import bundles


def inspect_bundle(bundle_name='sharadar', ticker=None):
    """Inspect bundle data in detail."""

    print("\n" + "="*70)
    print("SHARADAR BUNDLE INSPECTOR")
    print("="*70)

    try:
        # Load the bundle
        bundle_data = bundles.load(bundle_name)

        # Get asset finder
        asset_finder = bundle_data.asset_finder

        # Get all equities
        equities = asset_finder.retrieve_all(asset_finder.sids)

        print(f"\n📊 ASSET SUMMARY")
        print("-" * 70)
        print(f"  Total assets: {len(equities):,}")

        # Get tickers
        tickers = [eq.symbol for eq in equities if hasattr(eq, 'symbol')]
        print(f"  Tickers: {len(tickers):,}")

        # Get date ranges
        start_dates = [eq.start_date for eq in equities if hasattr(eq, 'start_date')]
        end_dates = [eq.end_date for eq in equities if hasattr(eq, 'end_date')]

        if start_dates and end_dates:
            earliest_start = min(start_dates)
            latest_end = max(end_dates)

            print(f"\n📅 DATE RANGE")
            print("-" * 70)
            print(f"  Earliest start: {earliest_start}")
            print(f"  Latest end:     {latest_end}")
            print(f"  Total span:     {(latest_end - earliest_start).days:,} days")

        # Get trading calendar
        calendar = get_calendar('XNYS')
        if start_dates and end_dates:
            trading_days = calendar.sessions_in_range(earliest_start, latest_end)
            print(f"  Trading days:   {len(trading_days):,}")

        # Show sample of tickers
        print(f"\n📋 SAMPLE TICKERS (first 20)")
        print("-" * 70)
        sample_tickers = sorted(tickers)[:20]
        for i in range(0, len(sample_tickers), 5):
            print("  " + "  ".join(f"{t:6s}" for t in sample_tickers[i:i+5]))

        if len(tickers) > 20:
            print(f"  ... and {len(tickers) - 20:,} more")

        # If specific ticker requested, show details
        if ticker:
            print(f"\n🔍 TICKER DETAILS: {ticker}")
            print("-" * 70)

            # Find asset
            try:
                asset = asset_finder.lookup_symbol(ticker, None)
                print(f"  Symbol:      {asset.symbol}")
                print(f"  Asset name:  {asset.asset_name if hasattr(asset, 'asset_name') else 'N/A'}")
                print(f"  Exchange:    {asset.exchange if hasattr(asset, 'exchange') else 'N/A'}")
                print(f"  Start date:  {asset.start_date}")
                print(f"  End date:    {asset.end_date}")
                print(f"  SID:         {asset.sid}")

                # Get trading days for this asset
                asset_sessions = calendar.sessions_in_range(asset.start_date, asset.end_date)
                print(f"  Trading days: {len(asset_sessions):,}")

                # Try to get some price data
                try:
                    equity_daily_bar_reader = bundle_data.equity_daily_bar_reader

                    # Get latest 5 trading days
                    recent_sessions = asset_sessions[-5:]

                    print(f"\n  Recent prices (last 5 days):")
                    print(f"  {'Date':<12} {'Open':>10} {'High':>10} {'Low':>10} {'Close':>10} {'Volume':>12}")
                    print("  " + "-" * 66)

                    for session in recent_sessions:
                        try:
                            bar = equity_daily_bar_reader.load_raw_arrays(
                                ['open', 'high', 'low', 'close', 'volume'],
                                session,
                                session,
                                [asset.sid]
                            )

                            date_str = str(session.date())
                            open_price = bar[0][0][0]
                            high_price = bar[1][0][0]
                            low_price = bar[2][0][0]
                            close_price = bar[3][0][0]
                            volume = bar[4][0][0]

                            print(f"  {date_str:<12} {open_price:>10.2f} {high_price:>10.2f} {low_price:>10.2f} {close_price:>10.2f} {volume:>12,.0f}")
                        except Exception as e:
                            print(f"  {session.date()}: Could not load data")

                except Exception as e:
                    print(f"\n  Could not load price data: {e}")

            except Exception as e:
                print(f"  ❌ Ticker not found: {e}")

        print(f"\n💾 STORAGE LOCATION")
        print("-" * 70)
        bundle_path = Path.home() / '.zipline' / 'data' / bundle_name
        print(f"  {bundle_path}")

        # Get size
        if bundle_path.exists():
            total_size = sum(f.stat().st_size for f in bundle_path.rglob('*') if f.is_file())
            size_mb = total_size / (1024 * 1024)
            size_gb = size_mb / 1024

            if size_gb >= 1:
                print(f"  Size: {size_gb:.2f} GB")
            else:
                print(f"  Size: {size_mb:.2f} MB")

        print("\n" + "="*70)
        print("✓ Inspection complete")
        print("="*70)
        print()

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("\nMake sure you have ingested the bundle first:")
        print("  python scripts/manage_sharadar.py ingest --tickers AAPL,MSFT,GOOGL")
        print()
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Inspect Sharadar bundle data in detail',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        '--bundle',
        default='sharadar',
        help='Bundle name (default: sharadar)',
    )

    parser.add_argument(
        '--ticker',
        help='Show detailed info for specific ticker (e.g., AAPL)',
    )

    args = parser.parse_args()

    inspect_bundle(bundle_name=args.bundle, ticker=args.ticker)


if __name__ == '__main__':
    main()
