"""
Quick Data Range Checker for Jupyter Notebooks
===============================================

Run this file from the notebooks directory to check your bundle data ranges.

Usage in Jupyter Terminal:
    cd /home/user/zipline-reloaded/notebooks
    python check_data_range.py

Or in a notebook cell:
    %run check_data_range.py
"""

import sys
from pathlib import Path

# Add parent directory to path so we can import the main script
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from scripts.check_bundle_dates import check_bundle_data_range

if __name__ == '__main__':
    bundle_name = sys.argv[1] if len(sys.argv) > 1 else None

    if bundle_name:
        print(f"Checking bundle: {bundle_name}\n")
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
                print("\n📋 To ingest data, run in a terminal:")
                print("   cd /home/user/zipline-reloaded")
                print("   python scripts/manage_data.py setup --source yahoo")
                print("\n   OR")
                print("   python scripts/manage_data.py setup --source sharadar --tickers AAPL,MSFT,GOOGL")
        else:
            print("❌ No .zipline/data directory found!")
            print("   You need to ingest data first.")
            print("\n📋 To ingest data, run in a terminal:")
            print("   cd /home/user/zipline-reloaded")
            print("   python scripts/manage_data.py setup --source yahoo")
