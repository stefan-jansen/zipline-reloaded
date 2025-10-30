#!/bin/bash
# Setup script for Sharadar bundle branch

set -e  # Exit on error

echo "========================================"
echo "Sharadar Branch Setup"
echo "========================================"

# 1. Fetch remote branches
echo "1. Fetching remote branches..."
git fetch origin

# 2. Checkout the feature branch
echo "2. Checking out feature branch..."
git checkout -b claude/implement-custom-data-011CUXBP4M1HT2VGQGmKJkVf origin/claude/implement-custom-data-011CUXBP4M1HT2VGQGmKJkVf 2>/dev/null || git checkout claude/implement-custom-data-011CUXBP4M1HT2VGQGmKJkVf

# 3. Verify branch
CURRENT_BRANCH=$(git branch --show-current)
echo "✓ Current branch: $CURRENT_BRANCH"

# 4. Verify fix is present
if grep -q "previous year" src/zipline/data/bundles/sharadar_bundle.py; then
    echo "✓ Year-end cap fix is present"
else
    echo "✗ Warning: Fix not found in bundle file"
    exit 1
fi

# 5. Show latest commits
echo -e "\nLatest commits:"
git log --oneline -3

# 6. Install zipline
echo -e "\n3. Installing zipline with dependencies..."
pip install -e . > /dev/null 2>&1 && echo "✓ Zipline installed" || echo "✗ Installation failed"

echo -e "\n========================================"
echo "Setup Complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Set your API key:"
echo "   export NASDAQ_DATA_LINK_API_KEY='your_key_here'"
echo ""
echo "2. Run ingestion:"
echo "   python scripts/manage_data.py setup --source sharadar --tickers AAPL,MSFT,GOOGL"
echo ""
