"""
Example: Using CustomData to integrate custom data sources into Zipline pipelines.

This example demonstrates how to:
1. Define a custom dataset with CustomData
2. Load custom data using MultiColumnDataFrameLoader
3. Use custom data in a Pipeline
4. Combine custom data with built-in data sources
"""

import numpy as np
import pandas as pd

from zipline.pipeline import Pipeline
from zipline.pipeline.data import CustomData, USEquityPricing
from zipline.pipeline.domain import US_EQUITIES
from zipline.pipeline.factors import SimpleMovingAverage
from zipline.pipeline.loaders import MultiColumnDataFrameLoader


# ============================================================================
# Example 1: Basic CustomData Definition
# ============================================================================

print("=" * 70)
print("Example 1: Defining a Custom Dataset")
print("=" * 70)

# Define a custom dataset with multiple columns
FundamentalData = CustomData(
    'FundamentalData',
    columns={
        'pe_ratio': float,          # Price-to-earnings ratio
        'market_cap': float,        # Market capitalization
        'revenue_growth': float,    # Revenue growth rate
        'debt_ratio': float,        # Debt-to-equity ratio
        'sector': int,              # Sector code
        'is_profitable': bool,      # Profitability flag
    },
    missing_values={
        'sector': -1,  # Required for int columns
    },
    doc="""
    Fundamental financial metrics for equity analysis.
    Data is updated quarterly and sourced from financial statements.
    """
)

print(f"Created dataset: {FundamentalData}")
print(f"Columns: {sorted(FundamentalData._column_names)}")
print(f"Documentation: {FundamentalData.__doc__[:100]}...")

# Access columns
print(f"\nPE Ratio column: {FundamentalData.pe_ratio}")
print(f"PE Ratio dtype: {FundamentalData.pe_ratio.dtype}")


# ============================================================================
# Example 2: Creating Sample Data
# ============================================================================

print("\n" + "=" * 70)
print("Example 2: Preparing Custom Data for Loading")
print("=" * 70)

# Create sample data
dates = pd.bdate_range('2022-01-01', '2022-12-31')
sids = list(range(1, 11))  # 10 stocks

print(f"Date range: {dates[0]} to {dates[-1]}")
print(f"Number of dates: {len(dates)}")
print(f"Stock IDs (sids): {sids}")

# Generate random fundamental data
np.random.seed(42)

pe_ratios = pd.DataFrame(
    np.random.uniform(5, 30, (len(dates), len(sids))),
    index=dates,
    columns=sids
)

market_caps = pd.DataFrame(
    np.random.uniform(1e9, 1e11, (len(dates), len(sids))),
    index=dates,
    columns=sids
)

revenue_growth = pd.DataFrame(
    np.random.uniform(-0.1, 0.3, (len(dates), len(sids))),
    index=dates,
    columns=sids
)

debt_ratios = pd.DataFrame(
    np.random.uniform(0, 2, (len(dates), len(sids))),
    index=dates,
    columns=sids
)

sectors = pd.DataFrame(
    np.random.randint(1, 12, (len(dates), len(sids))),
    index=dates,
    columns=sids
)

profitability = pd.DataFrame(
    np.random.choice([True, False], (len(dates), len(sids))),
    index=dates,
    columns=sids
)

print(f"\nSample PE Ratios (first 5 dates, first 3 stocks):")
print(pe_ratios.iloc[:5, :3])


# ============================================================================
# Example 3: Creating a Loader
# ============================================================================

print("\n" + "=" * 70)
print("Example 3: Creating MultiColumnDataFrameLoader")
print("=" * 70)

# Create loader with all our data
loader = MultiColumnDataFrameLoader(
    FundamentalData,
    {
        FundamentalData.pe_ratio: pe_ratios,
        FundamentalData.market_cap: market_caps,
        FundamentalData.revenue_growth: revenue_growth,
        FundamentalData.debt_ratio: debt_ratios,
        FundamentalData.sector: sectors,
        FundamentalData.is_profitable: profitability,
    }
)

print(f"Loader created for dataset: {loader.dataset}")
print(f"Number of columns loaded: {len(loader._baselines)}")
print(f"Columns: {[col.name for col in loader._baselines.keys()]}")


# ============================================================================
# Example 4: Building a Pipeline
# ============================================================================

print("\n" + "=" * 70)
print("Example 4: Building a Value Investing Pipeline")
print("=" * 70)

# Create a value investing pipeline using custom fundamental data
value_pipeline = Pipeline(
    columns={
        # Raw metrics
        'pe_ratio': FundamentalData.pe_ratio.latest,
        'market_cap': FundamentalData.market_cap.latest,
        'revenue_growth': FundamentalData.revenue_growth.latest,
        'debt_ratio': FundamentalData.debt_ratio.latest,
        'sector': FundamentalData.sector.latest,

        # Computed metrics
        'is_undervalued': FundamentalData.pe_ratio.latest < 15,
        'is_growing': FundamentalData.revenue_growth.latest > 0.1,
        'is_stable': FundamentalData.debt_ratio.latest < 1.0,

        # Combined conditions
        'is_value_stock': (
            (FundamentalData.pe_ratio.latest < 15) &
            (FundamentalData.revenue_growth.latest > 0.1) &
            (FundamentalData.debt_ratio.latest < 1.0) &
            (FundamentalData.is_profitable.latest == True)
        ),
    },
    # Filter to only profitable companies
    screen=FundamentalData.is_profitable.latest,
)

print("Pipeline created with columns:")
for col_name in value_pipeline.columns.keys():
    print(f"  - {col_name}")


# ============================================================================
# Example 5: Alternative Data Example
# ============================================================================

print("\n" + "=" * 70)
print("Example 5: Alternative Data - Social Sentiment")
print("=" * 70)

# Define alternative data source
SocialSentiment = CustomData(
    'SocialSentiment',
    columns={
        'twitter_sentiment': float,      # -1 to 1
        'reddit_mentions': int,          # Count of mentions
        'news_sentiment': float,         # -1 to 1
        'social_volume': int,            # Total social activity
    },
    missing_values={
        'reddit_mentions': 0,
        'social_volume': 0,
    },
    doc="Social media sentiment and activity metrics"
)

print(f"Created alternative dataset: {SocialSentiment}")
print(f"Columns: {sorted(SocialSentiment._column_names)}")

# Generate sample sentiment data
twitter_sentiment = pd.DataFrame(
    np.random.uniform(-1, 1, (len(dates), len(sids))),
    index=dates,
    columns=sids
)

reddit_mentions = pd.DataFrame(
    np.random.poisson(50, (len(dates), len(sids))),
    index=dates,
    columns=sids
)

news_sentiment = pd.DataFrame(
    np.random.uniform(-1, 1, (len(dates), len(sids))),
    index=dates,
    columns=sids
)

social_volume = pd.DataFrame(
    np.random.poisson(100, (len(dates), len(sids))),
    index=dates,
    columns=sids
)

sentiment_loader = MultiColumnDataFrameLoader(
    SocialSentiment,
    {
        SocialSentiment.twitter_sentiment: twitter_sentiment,
        SocialSentiment.reddit_mentions: reddit_mentions,
        SocialSentiment.news_sentiment: news_sentiment,
        SocialSentiment.social_volume: social_volume,
    }
)

# Create sentiment-based pipeline
sentiment_pipeline = Pipeline(
    columns={
        'twitter': SocialSentiment.twitter_sentiment.latest,
        'reddit': SocialSentiment.reddit_mentions.latest,
        'news': SocialSentiment.news_sentiment.latest,
        'volume': SocialSentiment.social_volume.latest,
        'positive_sentiment': (
            (SocialSentiment.twitter_sentiment.latest > 0.5) &
            (SocialSentiment.news_sentiment.latest > 0.5)
        ),
        'high_activity': SocialSentiment.social_volume.latest > 100,
    },
    screen=(
        (SocialSentiment.twitter_sentiment.latest > 0.3) |
        (SocialSentiment.reddit_mentions.latest > 50)
    )
)

print("\nSentiment pipeline created successfully!")


# ============================================================================
# Example 6: Domain-Specific Data
# ============================================================================

print("\n" + "=" * 70)
print("Example 6: Domain-Specific Datasets")
print("=" * 70)

# Create US-specific dataset
USData = CustomData(
    'USData',
    columns={'us_metric': float},
    domain=US_EQUITIES,
    doc="US equities specific metrics"
)

print(f"US Dataset domain: {USData.domain}")

# Generic dataset (works with any domain)
GlobalData = CustomData(
    'GlobalData',
    columns={'global_metric': float},
    doc="Cross-market metrics"
)

print(f"Global Dataset domain: {GlobalData.domain}")


# ============================================================================
# Example 7: Currency-Aware Data
# ============================================================================

print("\n" + "=" * 70)
print("Example 7: Currency-Aware Columns")
print("=" * 70)

PriceData = CustomData(
    'PriceData',
    columns={
        'price_usd': float,
        'price_local': float,
        'market_cap_local': float,
    },
    currency_aware={
        'price_local': True,
        'market_cap_local': True,
    },
    doc="Price data with currency conversion support"
)

print(f"USD price currency-aware: {PriceData.price_usd.currency_aware}")
print(f"Local price currency-aware: {PriceData.price_local.currency_aware}")
print(f"Local market cap currency-aware: {PriceData.market_cap_local.currency_aware}")


# ============================================================================
# Summary
# ============================================================================

print("\n" + "=" * 70)
print("Summary")
print("=" * 70)

print("""
CustomData makes it easy to integrate your own data sources into Zipline:

1. Define datasets with CustomData() factory function
2. Specify column types (float, int, str, bool, datetime)
3. Load data using MultiColumnDataFrameLoader
4. Use in pipelines just like built-in datasets (USEquityPricing, etc.)
5. Combine with factors, filters, and other pipeline features

Key features:
- Simple API for dataset definition
- Support for all numpy data types
- Currency-aware columns for FX conversion
- Domain-specific datasets (US_EQUITIES, GB_EQUITIES, etc.)
- Metadata support for documentation
- Works seamlessly with existing Zipline infrastructure

For more information, see docs/CUSTOM_DATA.md
""")

print("=" * 70)
print("Example completed successfully!")
print("=" * 70)
