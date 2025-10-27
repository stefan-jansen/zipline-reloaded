# CustomData - User Guide

The `CustomData` functionality in zipline-reloaded makes it easy to integrate your own data sources into Zipline pipelines, similar to QuantRocket's CustomData API.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Basic Usage](#basic-usage)
3. [Advanced Features](#advanced-features)
4. [Loading Data](#loading-data)
5. [Integration with Pipelines](#integration-with-pipelines)
6. [Complete Examples](#complete-examples)

## Quick Start

```python
from zipline.pipeline.data import CustomData
from zipline.pipeline import Pipeline
import pandas as pd
import numpy as np

# Step 1: Define your custom dataset
MyData = CustomData(
    'MyData',
    columns={
        'revenue': float,
        'earnings': float,
        'growth_rate': float,
    }
)

# Step 2: Create a pipeline using your custom data
pipe = Pipeline(
    columns={
        'revenue': MyData.revenue.latest,
        'high_growth': MyData.growth_rate.latest > 0.1,
    }
)
```

## Basic Usage

### Creating a Custom Dataset

The `CustomData` factory function creates a new `DataSet` class with the columns you specify:

```python
from zipline.pipeline.data import CustomData

# Simple dataset with float columns
SimpleData = CustomData(
    'SimpleData',
    columns={
        'metric1': float,
        'metric2': float,
        'metric3': float,
    }
)
```

### Supported Data Types

You can specify column types in several ways:

```python
# Using Python types
Data1 = CustomData(
    'Data1',
    columns={
        'price': float,      # Floating point numbers
        'volume': int,       # Integers
        'ticker': str,       # Strings
        'active': bool,      # Booleans
    },
    missing_values={
        'volume': 0,         # Required for int columns
    }
)

# Using string names
Data2 = CustomData(
    'Data2',
    columns={
        'metric': 'float',
        'count': 'int',
        'name': 'str',
        'flag': 'bool',
        'timestamp': 'datetime',
    },
    missing_values={
        'count': -1,
    }
)

# Using NumPy dtypes
import numpy as np

Data3 = CustomData(
    'Data3',
    columns={
        'col1': np.dtype('float64'),
        'col2': np.dtype('int64'),
    },
    missing_values={
        'col2': -999,
    }
)
```

### Important Notes on Data Types

- **Float columns**: Use NaN as the default missing value
- **Boolean columns**: Use False as the default missing value
- **String columns**: Use None as the default missing value
- **Integer columns**: **Must** specify a missing value (NumPy has no native NaN for integers)

```python
# This will work
GoodData = CustomData(
    'GoodData',
    columns={'sector': int},
    missing_values={'sector': -1}
)

# This will raise an error at runtime
BadData = CustomData(
    'BadData',
    columns={'sector': int}
    # Missing: missing_values={'sector': -1}
)
```

## Advanced Features

### Domain-Specific Datasets

Restrict your dataset to a specific market domain:

```python
from zipline.pipeline.domain import US_EQUITIES, GB_EQUITIES

# US-only dataset
USData = CustomData(
    'USData',
    columns={'metric': float},
    domain=US_EQUITIES
)

# UK-only dataset
UKData = CustomData(
    'UKData',
    columns={'metric': float},
    domain=GB_EQUITIES
)

# Generic dataset (works with any domain)
from zipline.pipeline.domain import GENERIC

GenericData = CustomData(
    'GenericData',
    columns={'metric': float},
    domain=GENERIC  # This is the default
)
```

### Currency-Aware Columns

For columns containing currency-denominated data:

```python
PriceData = CustomData(
    'PriceData',
    columns={
        'price_usd': float,      # Already in USD
        'price_local': float,    # In local currency
        'market_cap': float,     # In local currency
    },
    currency_aware={
        'price_usd': False,      # No conversion needed
        'price_local': True,     # Needs conversion
        'market_cap': True,      # Needs conversion
    }
)

# Now you can convert currencies
from zipline.currency import Currency

# Get price in EUR
price_eur = PriceData.price_local.fx(Currency('EUR'))
```

### Column Metadata

Attach metadata to columns for documentation or processing:

```python
FinancialData = CustomData(
    'FinancialData',
    columns={
        'revenue': float,
        'earnings': float,
    },
    metadata={
        'revenue': {
            'source': 'bloomberg',
            'frequency': 'quarterly',
            'units': 'millions',
        },
        'earnings': {
            'source': 'bloomberg',
            'frequency': 'quarterly',
            'units': 'millions',
        },
    }
)

# Access metadata
print(FinancialData.revenue.metadata)
# {'source': 'bloomberg', 'frequency': 'quarterly', 'units': 'millions'}
```

### Custom Documentation

Add documentation to your dataset:

```python
DocumentedData = CustomData(
    'DocumentedData',
    columns={'metric': float},
    doc="""
    This dataset contains custom metrics from our proprietary data source.

    Data is updated daily and covers all US equities.
    """
)

print(DocumentedData.__doc__)
```

## Loading Data

Use `MultiColumnDataFrameLoader` to load your custom data into pipelines:

### Basic Loading

```python
from zipline.pipeline.loaders import MultiColumnDataFrameLoader
import pandas as pd
import numpy as np

# Create your custom dataset
MyData = CustomData(
    'MyData',
    columns={
        'metric1': float,
        'metric2': float,
    }
)

# Prepare your data
dates = pd.date_range('2020-01-01', periods=100, freq='D')
sids = [1, 2, 3, 4, 5]  # Asset IDs

# Create DataFrames for each column
data1 = pd.DataFrame(
    np.random.randn(100, 5),
    index=dates,
    columns=sids
)

data2 = pd.DataFrame(
    np.random.randn(100, 5),
    index=dates,
    columns=sids
)

# Create the loader
loader = MultiColumnDataFrameLoader(
    MyData,
    {
        MyData.metric1: data1,
        MyData.metric2: data2,
    }
)

# Register the loader with your pipeline engine
def get_loader(column):
    if column.dataset == MyData:
        return loader
    # ... handle other datasets
```

### Alternative: Single DataFrame Format

You can also provide a single DataFrame with multi-level columns:

```python
# Single DataFrame with all metrics
combined_data = pd.DataFrame({
    'metric1': {(d, sid): np.random.randn()
                for d in dates for sid in sids},
    'metric2': {(d, sid): np.random.randn()
                for d in dates for sid in sids},
})

loader = MultiColumnDataFrameLoader(MyData, combined_data)
```

### Loading from CSV Files

```python
import pandas as pd

# Load from CSV files
metric1_df = pd.read_csv(
    'metric1.csv',
    index_col='date',
    parse_dates=True
)

metric2_df = pd.read_csv(
    'metric2.csv',
    index_col='date',
    parse_dates=True
)

loader = MultiColumnDataFrameLoader(
    MyData,
    {
        MyData.metric1: metric1_df,
        MyData.metric2: metric2_df,
    }
)
```

### Data Adjustments

Apply adjustments (splits, dividends, etc.) to your custom data:

```python
from zipline.lib.adjustment import MULTIPLY, ADD, OVERWRITE

# Create adjustments DataFrame
adjustments = pd.DataFrame({
    'sid': [1, 2],
    'value': [0.5, 1.0],           # Adjustment values
    'kind': [MULTIPLY, ADD],        # Adjustment types
    'start_date': [pd.NaT, pd.NaT],
    'end_date': [dates[50], dates[50]],
    'apply_date': [dates[50], dates[50]],
})

loader = MultiColumnDataFrameLoader(
    MyData,
    {MyData.metric1: data1, MyData.metric2: data2},
    adjustments={MyData.metric1: adjustments}
)
```

## Integration with Pipelines

### Using Custom Data in Pipelines

```python
from zipline.pipeline import Pipeline
from zipline.pipeline.factors import SimpleMovingAverage

MyData = CustomData(
    'MyData',
    columns={'price': float, 'volume': float}
)

# Create factors using custom data
sma_10 = SimpleMovingAverage(
    inputs=[MyData.price],
    window_length=10
)

sma_30 = SimpleMovingAverage(
    inputs=[MyData.price],
    window_length=30
)

# Build pipeline
pipe = Pipeline(
    columns={
        'price': MyData.price.latest,
        'volume': MyData.volume.latest,
        'sma_10': sma_10,
        'sma_30': sma_30,
        'golden_cross': sma_10 > sma_30,
    }
)
```

### Combining with Built-in Data

```python
from zipline.pipeline.data import USEquityPricing

MyData = CustomData(
    'MyData',
    columns={'fundamental_score': float}
)

# Combine custom and built-in data
pipe = Pipeline(
    columns={
        'close': USEquityPricing.close.latest,
        'volume': USEquityPricing.volume.latest,
        'score': MyData.fundamental_score.latest,
        'high_score': MyData.fundamental_score.latest > 0.7,
    }
)
```

### Custom Filters

```python
from zipline.pipeline.filters import StaticAssets

MyData = CustomData(
    'MyData',
    columns={'quality_score': float, 'is_active': bool}
)

# Create filters from custom data
high_quality = MyData.quality_score.latest > 0.8
active_stocks = MyData.is_active.latest

# Use in pipeline
pipe = Pipeline(
    columns={
        'score': MyData.quality_score.latest,
    },
    screen=high_quality & active_stocks
)
```

## Complete Examples

### Example 1: Fundamental Analysis

```python
from zipline.pipeline.data import CustomData
from zipline.pipeline import Pipeline
from zipline.pipeline.loaders import MultiColumnDataFrameLoader
from zipline.pipeline.factors import SimpleMovingAverage
import pandas as pd
import numpy as np

# Define fundamental data
Fundamentals = CustomData(
    'Fundamentals',
    columns={
        'pe_ratio': float,
        'roe': float,
        'debt_equity': float,
        'revenue_growth': float,
    },
    doc="Fundamental metrics for value investing"
)

# Load some example data
dates = pd.bdate_range('2020-01-01', '2023-12-31')
sids = list(range(1, 101))  # 100 stocks

fundamental_data = {
    Fundamentals.pe_ratio: pd.DataFrame(
        np.random.uniform(5, 30, (len(dates), len(sids))),
        index=dates,
        columns=sids
    ),
    Fundamentals.roe: pd.DataFrame(
        np.random.uniform(0.05, 0.25, (len(dates), len(sids))),
        index=dates,
        columns=sids
    ),
    Fundamentals.debt_equity: pd.DataFrame(
        np.random.uniform(0, 2, (len(dates), len(sids))),
        index=dates,
        columns=sids
    ),
    Fundamentals.revenue_growth: pd.DataFrame(
        np.random.uniform(-0.1, 0.3, (len(dates), len(sids))),
        index=dates,
        columns=sids
    ),
}

loader = MultiColumnDataFrameLoader(Fundamentals, fundamental_data)

# Create value investing pipeline
value_pipe = Pipeline(
    columns={
        'pe': Fundamentals.pe_ratio.latest,
        'roe': Fundamentals.roe.latest,
        'de': Fundamentals.debt_equity.latest,
        'growth': Fundamentals.revenue_growth.latest,
    },
    screen=(
        (Fundamentals.pe_ratio.latest < 15) &
        (Fundamentals.roe.latest > 0.15) &
        (Fundamentals.debt_equity.latest < 1.0) &
        (Fundamentals.revenue_growth.latest > 0.05)
    )
)
```

### Example 2: Alternative Data

```python
from zipline.pipeline.data import CustomData
from zipline.pipeline import Pipeline
import pandas as pd

# Define alternative data sources
SocialSentiment = CustomData(
    'SocialSentiment',
    columns={
        'twitter_sentiment': float,
        'reddit_mentions': int,
        'news_sentiment': float,
    },
    missing_values={
        'reddit_mentions': 0,
    },
    doc="Social media and news sentiment data"
)

WebTraffic = CustomData(
    'WebTraffic',
    columns={
        'daily_visitors': int,
        'page_views': int,
        'growth_rate': float,
    },
    missing_values={
        'daily_visitors': 0,
        'page_views': 0,
    },
    doc="Website traffic metrics"
)

# Create alternative data pipeline
alt_pipe = Pipeline(
    columns={
        'sentiment': SocialSentiment.twitter_sentiment.latest,
        'mentions': SocialSentiment.reddit_mentions.latest,
        'traffic': WebTraffic.daily_visitors.latest,
        'momentum': WebTraffic.growth_rate.latest,
    },
    screen=(
        (SocialSentiment.twitter_sentiment.latest > 0.6) &
        (WebTraffic.growth_rate.latest > 0.1)
    )
)
```

### Example 3: Multi-Market Data

```python
from zipline.pipeline.data import CustomData
from zipline.pipeline.domain import US_EQUITIES, GB_EQUITIES

# US-specific data
USFundamentals = CustomData(
    'USFundamentals',
    columns={'metric': float},
    domain=US_EQUITIES
)

# UK-specific data
UKFundamentals = CustomData(
    'UKFundamentals',
    columns={'metric': float},
    domain=GB_EQUITIES
)

# Generic data that works across markets
GlobalData = CustomData(
    'GlobalData',
    columns={'esg_score': float}
)

# Use in domain-specific pipelines
us_pipe = Pipeline(
    columns={
        'us_metric': USFundamentals.metric.latest,
        'esg': GlobalData.esg_score.latest,
    },
    domain=US_EQUITIES
)

uk_pipe = Pipeline(
    columns={
        'uk_metric': UKFundamentals.metric.latest,
        'esg': GlobalData.esg_score.latest,
    },
    domain=GB_EQUITIES
)
```

## Best Practices

1. **Always provide missing values for integer columns**
   ```python
   # Good
   Data = CustomData('Data', columns={'count': int}, missing_values={'count': -1})

   # Bad - will fail when NaN encountered
   Data = CustomData('Data', columns={'count': int})
   ```

2. **Use float for semantically numeric data**
   ```python
   # Preferred - NaN handling works naturally
   Data = CustomData('Data', columns={'market_cap': float})

   # Not recommended - requires explicit missing value
   Data = CustomData('Data', columns={'market_cap': int}, missing_values={'market_cap': -1})
   ```

3. **Document your datasets**
   ```python
   Data = CustomData(
       'Data',
       columns={'metric': float},
       doc="Description of data source, update frequency, and coverage"
   )
   ```

4. **Use domain specialization when appropriate**
   ```python
   # If data only covers US equities
   USData = CustomData('USData', columns={'metric': float}, domain=US_EQUITIES)
   ```

5. **Align data dates correctly**
   - Date indices should represent when data is **available** to algorithms
   - For OHLCV data, shift dates back by one trading day
   - For fundamental data, use the release date, not the period end date

## Troubleshooting

### "No data provided for column X"

Make sure you've provided data for all columns you're trying to load:

```python
loader = MultiColumnDataFrameLoader(
    MyData,
    {
        MyData.col1: df1,
        MyData.col2: df2,  # Don't forget any columns!
    }
)
```

### "Column does not belong to dataset"

Ensure you're loading columns from the correct dataset:

```python
# Wrong
loader1 = MultiColumnDataFrameLoader(Dataset1, {Dataset2.col: df})

# Right
loader1 = MultiColumnDataFrameLoader(Dataset1, {Dataset1.col: df})
```

### Missing values not handled correctly

For integer columns, always specify a missing value:

```python
Data = CustomData(
    'Data',
    columns={'count': int},
    missing_values={'count': -1}  # Required!
)
```

## API Reference

### CustomData

```python
CustomData(
    name: str,
    columns: Dict[str, Union[type, str, np.dtype]],
    missing_values: Optional[Dict[str, Any]] = None,
    domain: Domain = GENERIC,
    metadata: Optional[Dict[str, Dict[str, Any]]] = None,
    currency_aware: Optional[Dict[str, bool]] = None,
    doc: Optional[str] = None,
) -> type
```

### MultiColumnDataFrameLoader

```python
MultiColumnDataFrameLoader(
    dataset: DataSet,
    data: Union[Dict[BoundColumn, pd.DataFrame], pd.DataFrame],
    adjustments: Optional[Union[Dict[BoundColumn, pd.DataFrame], pd.DataFrame]] = None,
)
```

## See Also

- [Pipeline Tutorial](https://zipline-reloaded.io/beginner-tutorial.html)
- [Custom Factors](https://zipline-reloaded.io/pipeline-factors.html)
- [Data Bundles](https://zipline-reloaded.io/bundles.html)
