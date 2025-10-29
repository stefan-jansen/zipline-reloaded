#!/usr/bin/env python3
"""
Setup Zipline Extension File

This script creates the ~/.zipline/extension.py file that registers
all available data bundles automatically when zipline starts.

Run this inside the Docker container:
    docker exec -it zipline-reloaded-jupyter python /scripts/setup_extension.py
"""

import os
from pathlib import Path


EXTENSION_CONTENT = '''"""
Zipline Extension File

This file is automatically loaded by zipline on startup.
It registers all available data bundles.
"""

from zipline.data.bundles import register

# Import bundle functions
try:
    from zipline.data.bundles.yahoo_bundle import (
        yahoo_bundle,
        yahoo_tech_bundle,
        yahoo_dow_bundle,
        yahoo_sp500_bundle,
    )

    # Register Yahoo Finance bundles
    register('yahoo', yahoo_bundle())
    register('yahoo-tech', yahoo_tech_bundle())
    register('yahoo-dow', yahoo_dow_bundle())
    register('yahoo-sp500', yahoo_sp500_bundle())

    print("✓ Yahoo Finance bundles registered")
except ImportError as e:
    print(f"⚠ Yahoo Finance bundles not available: {e}")

# Register NASDAQ Data Link bundles
try:
    from zipline.data.bundles.nasdaq_bundle import (
        nasdaq_bundle,
        nasdaq_premium_bundle,
        nasdaq_free_bundle,
        nasdaq_sp500_bundle,
    )

    register('nasdaq', nasdaq_bundle())
    register('nasdaq-premium', nasdaq_premium_bundle())
    register('nasdaq-free', nasdaq_free_bundle())
    register('nasdaq-sp500', nasdaq_sp500_bundle())

    print("✓ NASDAQ Data Link bundles registered")
except ImportError as e:
    print(f"⚠ NASDAQ Data Link bundles not available: {e}")

# Register Sharadar bundles
try:
    from zipline.data.bundles.sharadar_bundle import (
        sharadar_bundle,
        sharadar_tech_bundle,
        sharadar_sp500_sample_bundle,
        sharadar_all_bundle,
    )

    register('sharadar', sharadar_bundle())
    register('sharadar-tech', sharadar_tech_bundle())
    register('sharadar-sp500', sharadar_sp500_sample_bundle())
    register('sharadar-all', sharadar_all_bundle())

    print("✓ Sharadar bundles registered")
except ImportError as e:
    print(f"⚠ Sharadar bundles not available: {e}")

print("\\nAvailable bundles:")
print("  - yahoo, yahoo-tech, yahoo-dow, yahoo-sp500")
print("  - nasdaq, nasdaq-premium, nasdaq-free, nasdaq-sp500")
print("  - sharadar, sharadar-tech, sharadar-sp500, sharadar-all")
print("\\nUse 'zipline bundles' to see which bundles have been ingested.")
'''


def main():
    # Get zipline root directory
    zipline_root = Path.home() / '.zipline'

    # Create directory if it doesn't exist
    zipline_root.mkdir(parents=True, exist_ok=True)
    print(f"✓ Zipline directory: {zipline_root}")

    # Create extension.py file
    ext_file = zipline_root / 'extension.py'

    if ext_file.exists():
        print(f"⚠ Extension file already exists: {ext_file}")
        response = input("Overwrite? [y/N]: ")
        if response.lower() != 'y':
            print("Aborted.")
            return

    # Write extension file
    ext_file.write_text(EXTENSION_CONTENT)
    print(f"✓ Created extension file: {ext_file}")

    print("\n" + "="*70)
    print("ZIPLINE EXTENSION SETUP COMPLETE")
    print("="*70)
    print("\nAll bundles are now registered and available:")
    print("  - Yahoo Finance: yahoo, yahoo-tech, yahoo-dow, yahoo-sp500")
    print("  - NASDAQ Data Link: nasdaq, nasdaq-premium, nasdaq-free, nasdaq-sp500")
    print("  - Sharadar: sharadar, sharadar-tech, sharadar-sp500, sharadar-all")
    print("\nNext steps:")
    print("  1. Ingest a bundle: zipline ingest -b sharadar")
    print("  2. Or use manage_data.py: python /scripts/manage_data.py setup --source sharadar --tickers AAPL,MSFT")
    print("  3. Check status: zipline bundles")
    print()


if __name__ == '__main__':
    main()
