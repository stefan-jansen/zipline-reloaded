# CustomData Database Storage

This guide covers persistent database storage for CustomData, enabling efficient storage and retrieval of custom pipeline data using SQLite.

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Database Creation](#database-creation)
4. [Data Insertion](#data-insertion)
5. [Loading from Database](#loading-from-database)
6. [Querying Data](#querying-data)
7. [Database Management](#database-management)
8. [Complete Examples](#complete-examples)
9. [Best Practices](#best-practices)
10. [API Reference](#api-reference)

## Overview

Database-backed CustomData provides:

- **Persistent Storage**: Data survives across runs and doesn't need to fit in RAM
- **Efficient Querying**: Only loads date/sid ranges needed for pipelines
- **Incremental Updates**: Update existing data without reloading everything
- **Easy Management**: List, inspect, query, and delete databases
- **Seamless Integration**: Works exactly like in-memory CustomData

### When to Use Database Storage

| Use Case | Recommendation |
|----------|---------------|
| Development & testing | In-memory (MultiColumnDataFrameLoader) |
| Small datasets (< 100MB) | In-memory |
| Frequently changing data | In-memory |
| Production pipelines | **Database** |
| Large datasets (> 100MB) | **Database** |
| Historical data | **Database** |
| Shared data across strategies | **Database** |

## Quick Start

```python
from zipline.pipeline.data import (
    create_custom_db,
    insert_custom_data,
    from_db,
)
from zipline.pipeline import Pipeline
import pandas as pd
import numpy as np

# 1. Create database (once)
create_custom_db(
    'my-fundamentals',
    columns={
        'pe_ratio': float,
        'market_cap': float,
        'sector': int,
    }
)

# 2. Insert data (whenever you have new data)
dates = pd.bdate_range('2020-01-01', '2023-12-31')
sids = [1, 2, 3]

data = pd.DataFrame({
    ('pe_ratio', sid): np.random.uniform(5, 30, len(dates))
    for sid in sids
}, index=dates)
data.columns = pd.MultiIndex.from_tuples(
    data.columns, names=['field', 'sid']
)

insert_custom_data('my-fundamentals', data)

# 3. Load and use (every time)
MyData = from_db('my-fundamentals')

pipe = Pipeline(
    columns={
        'pe': MyData.pe_ratio.latest,
        'undervalued': MyData.pe_ratio.latest < 15,
    }
)
```

## Database Creation

### Basic Database

```python
from zipline.pipeline.data import create_custom_db

db_path = create_custom_db(
    'fundamentals-daily',
    columns={
        'pe_ratio': float,
        'market_cap': float,
        'revenue_growth': float,
    }
)

print(f"Created database at: {db_path}")
# Created database at: /home/user/.zipline/custom_data/fundamentals-daily.db
```

### Database with All Column Types

```python
create_custom_db(
    'comprehensive-data',
    columns={
        'price': float,           # Floating point
        'volume': int,            # Integer
        'ticker': str,            # String/text
        'is_active': bool,        # Boolean
        'timestamp': 'datetime',  # Datetime
    },
    bar_size='1h',  # Optional metadata
)
```

### Database Naming Rules

```python
# Valid codes (lowercase, numbers, hyphens)
'my-data'  # ✓
'fundamentals-1d'  # ✓
'alt-data-2023'  # ✓

# Invalid codes
'My-Data'  # ✗ No uppercase
'my_data'  # ✗ No underscores
'123-data'  # ✗ Must start with letter
```

### Custom Database Directory

```python
import os

# Specify custom directory
custom_dir = '/path/to/my/databases'

create_custom_db(
    'my-data',
    columns={'metric': float},
    db_dir=custom_dir,
)
```

## Data Insertion

### MultiIndex Format (Recommended)

For databases with multiple columns, use MultiIndex (field, sid):

```python
import pandas as pd
import numpy as np

dates = pd.bdate_range('2020-01-01', periods=100)
sids = [1, 2, 3]

# Create data with (field, sid) MultiIndex
data = pd.DataFrame({
    ('pe_ratio', 1): np.random.uniform(5, 30, 100),
    ('pe_ratio', 2): np.random.uniform(5, 30, 100),
    ('pe_ratio', 3): np.random.uniform(5, 30, 100),
    ('market_cap', 1): np.random.uniform(1e9, 1e11, 100),
    ('market_cap', 2): np.random.uniform(1e9, 1e11, 100),
    ('market_cap', 3): np.random.uniform(1e9, 1e11, 100),
}, index=dates)

data.columns = pd.MultiIndex.from_tuples(
    data.columns,
    names=['field', 'sid']
)

insert_custom_data('fundamentals-daily', data)
```

### Building MultiIndex from Separate DataFrames

```python
# You have separate DataFrames per metric
pe_df = pd.DataFrame(...)  # shape: (dates, sids)
cap_df = pd.DataFrame(...)  # shape: (dates, sids)

# Convert to MultiIndex format
def to_multiindex(df, field_name):
    """Convert simple DataFrame to (field, sid) MultiIndex."""
    result = pd.DataFrame({
        (field_name, col): df[col]
        for col in df.columns
    }, index=df.index)
    result.columns = pd.MultiIndex.from_tuples(
        result.columns,
        names=['field', 'sid']
    )
    return result

pe_multi = to_multiindex(pe_df, 'pe_ratio')
cap_multi = to_multiindex(cap_df, 'market_cap')

# Insert separately with mode='update'
insert_custom_data('fundamentals-daily', pe_multi, mode='update')
insert_custom_data('fundamentals-daily', cap_multi, mode='update')
```

### Insertion Modes

```python
# Replace: Delete all existing data, insert new data
insert_custom_data('my-db', data, mode='replace')

# Append: Insert only new records, fail if already exists
insert_custom_data('my-db', data, mode='append')

# Update: Update existing records, insert new ones (default)
insert_custom_data('my-db', data, mode='update')
```

### Incremental Updates

```python
# Initial load: all historical data
insert_custom_data('my-db', historical_data, mode='replace')

# Daily updates: just today's data
today_data = fetch_todays_data()
insert_custom_data('my-db', today_data, mode='update')
```

## Loading from Database

### Basic Loading

```python
from zipline.pipeline.data import from_db

# Load dataset from database
MyData = from_db('my-fundamentals')

# Access columns
print(MyData.pe_ratio)
print(MyData.market_cap)

# Check metadata
print(MyData.__doc__)
```

### Using in Pipelines

```python
from zipline.pipeline import Pipeline

MyData = from_db('my-fundamentals')

pipe = Pipeline(
    columns={
        'pe': MyData.pe_ratio.latest,
        'cap': MyData.market_cap.latest,
        'undervalued': MyData.pe_ratio.latest < 15,
    },
    screen=MyData.pe_ratio.latest < 20,
)
```

### Manual Loader Creation

```python
MyData = from_db('my-fundamentals')

# Get the loader
loader = MyData.get_loader()

# Use with pipeline engine
from zipline.pipeline.engine import SimplePipelineEngine

def get_loader(column):
    if column.dataset == MyData:
        return MyData.get_loader()
    # ... other datasets

engine = SimplePipelineEngine(get_loader, asset_finder)
```

## Querying Data

### Query All Data

```python
from zipline.pipeline.data import query_custom_data

df = query_custom_data('my-fundamentals')
print(df.head())
```

### Query by Date Range

```python
import pandas as pd

# Specific date range
q1_data = query_custom_data(
    'my-fundamentals',
    start_date=pd.Timestamp('2023-01-01'),
    end_date=pd.Timestamp('2023-03-31'),
)

# From start date onwards
recent = query_custom_data(
    'my-fundamentals',
    start_date=pd.Timestamp('2023-01-01'),
)

# Up to end date
historical = query_custom_data(
    'my-fundamentals',
    end_date=pd.Timestamp('2022-12-31'),
)
```

### Query Specific Assets

```python
# Specific stocks
stock_data = query_custom_data(
    'my-fundamentals',
    sids=[1, 2, 3, 4, 5],
)

# Single stock
single = query_custom_data(
    'my-fundamentals',
    sids=[1],
)
```

### Query Specific Columns

```python
# Just PE ratio
pe_only = query_custom_data(
    'my-fundamentals',
    columns=['pe_ratio'],
)

# Multiple specific columns
subset = query_custom_data(
    'my-fundamentals',
    columns=['pe_ratio', 'market_cap'],
)
```

### Combined Queries

```python
# Specific stocks, date range, and columns
result = query_custom_data(
    'my-fundamentals',
    start_date=pd.Timestamp('2023-01-01'),
    end_date=pd.Timestamp('2023-12-31'),
    sids=[1, 2, 3],
    columns=['pe_ratio'],
)
```

## Database Management

### List All Databases

```python
from zipline.pipeline.data import list_custom_dbs

dbs = list_custom_dbs()

for db in dbs:
    print(f"Database: {db['code']}")
    print(f"  Columns: {list(db['columns'].keys())}")
    print(f"  Rows: {db['row_count']:,}")
    print(f"  Size: {db['size_mb']} MB")
    print(f"  Created: {db['created_at']}")
    print()
```

### Get Database Info

```python
from zipline.pipeline.data import get_custom_db_info

info = get_custom_db_info('my-fundamentals')

print(f"Bar size: {info['bar_size']}")
print(f"Columns: {info['columns']}")
print(f"Path: {info['path']}")
```

### Delete Database

```python
from zipline.pipeline.data import drop_custom_db

# Permanently delete database
drop_custom_db('old-data')

# Verify deletion
dbs = list_custom_dbs()
print([db['code'] for db in dbs])
```

## Complete Examples

### Example 1: Fundamental Analysis Pipeline

```python
from zipline.pipeline.data import create_custom_db, insert_custom_data, from_db
from zipline.pipeline import Pipeline
import pandas as pd
import numpy as np

# Create database
create_custom_db(
    'fundamentals',
    columns={
        'pe_ratio': float,
        'roe': float,
        'debt_equity': float,
        'revenue_growth': float,
    }
)

# Generate and insert data
dates = pd.bdate_range('2020-01-01', '2023-12-31')
sids = list(range(1, 101))  # 100 stocks

for field in ['pe_ratio', 'roe', 'debt_equity', 'revenue_growth']:
    data = pd.DataFrame({
        (field, sid): np.random.uniform(0, 1, len(dates))
        for sid in sids
    }, index=dates)
    data.columns = pd.MultiIndex.from_tuples(
        data.columns, names=['field', 'sid']
    )
    insert_custom_data('fundamentals', data, mode='update')

# Load and create pipeline
Fundamentals = from_db('fundamentals')

value_pipeline = Pipeline(
    columns={
        'pe': Fundamentals.pe_ratio.latest,
        'roe': Fundamentals.roe.latest,
        'de': Fundamentals.debt_equity.latest,
        'growth': Fundamentals.revenue_growth.latest,
    },
    screen=(
        (Fundamentals.pe_ratio.latest < 0.5) &
        (Fundamentals.roe.latest > 0.15) &
        (Fundamentals.debt_equity.latest < 0.5)
    )
)
```

### Example 2: Daily Data Updates

```python
import schedule
import time

def daily_update():
    """Update database with today's data."""
    # Fetch today's data from your source
    today_data = fetch_data_from_source()

    # Convert to MultiIndex format
    data = pd.DataFrame({
        (field, sid): today_data[field][sid]
        for field in ['metric1', 'metric2']
        for sid in today_data['sids']
    }, index=[pd.Timestamp.now()])
    data.columns = pd.MultiIndex.from_tuples(
        data.columns, names=['field', 'sid']
    )

    # Update database
    insert_custom_data('my-db', data, mode='update')
    print(f"Updated database at {pd.Timestamp.now()}")

# Schedule daily updates
schedule.every().day.at("18:00").do(daily_update)

while True:
    schedule.run_pending()
    time.sleep(60)
```

### Example 3: Multiple Data Sources

```python
# Create separate databases for different data sources
create_custom_db(
    'sharadar-fundamentals',
    columns={'pe': float, 'eps': float}
)

create_custom_db(
    'quandl-sentiment',
    columns={'sentiment': float, 'volume': int}
)

create_custom_db(
    'custom-signals',
    columns={'signal1': float, 'signal2': float}
)

# Load all datasets
Fundamentals = from_db('sharadar-fundamentals')
Sentiment = from_db('quandl-sentiment')
Signals = from_db('custom-signals')

# Combine in single pipeline
combined_pipeline = Pipeline(
    columns={
        'pe': Fundamentals.pe.latest,
        'sentiment': Sentiment.sentiment.latest,
        'signal1': Signals.signal1.latest,
        'combined_score': (
            Fundamentals.pe.latest * 0.4 +
            Sentiment.sentiment.latest * 0.3 +
            Signals.signal1.latest * 0.3
        ),
    }
)
```

## Best Practices

### 1. Database Organization

```python
# Good: Separate databases by update frequency
create_custom_db('fundamentals-quarterly', ...)
create_custom_db('prices-daily', ...)
create_custom_db('sentiment-hourly', ...)

# Good: Separate by data source
create_custom_db('sharadar-fundamentals', ...)
create_custom_db('quandl-prices', ...)
create_custom_db('twitter-sentiment', ...)

# Avoid: Mixing unrelated data
create_custom_db('everything', ...)  # Too broad
```

### 2. Data Insertion

```python
# Good: Incremental updates
insert_custom_data('my-db', new_data, mode='update')

# Good: Replace when starting fresh
insert_custom_data('my-db', all_data, mode='replace')

# Avoid: Repeatedly replacing large datasets
for day in dates:
    data = get_data(day)
    insert_custom_data('my-db', data, mode='replace')  # Inefficient!
```

### 3. Database Naming

```python
# Good: Descriptive, includes frequency
'fundamentals-quarterly'
'prices-daily'
'sentiment-1h'

# Good: Includes data source
'sharadar-sf1'
'quandl-wiki'
'alpha-vantage'

# Avoid: Generic names
'data'
'custom'
'test'
```

### 4. Regular Maintenance

```python
# Periodically check database sizes
dbs = list_custom_dbs()
large_dbs = [db for db in dbs if db['size_mb'] > 1000]

if large_dbs:
    print("Large databases:")
    for db in large_dbs:
        print(f"  {db['code']}: {db['size_mb']} MB")

# Clean up old databases
old_dbs = ['test-db', 'experiment-1', 'backup-old']
for code in old_dbs:
    try:
        drop_custom_db(code)
        print(f"Dropped {code}")
    except CustomDatabaseError:
        pass
```

### 5. Error Handling

```python
from zipline.pipeline.data import CustomDatabaseError

try:
    MyData = from_db('my-fundamentals')
except CustomDatabaseError as e:
    print(f"Database error: {e}")
    print("Creating new database...")
    create_custom_db('my-fundamentals', columns={...})
    MyData = from_db('my-fundamentals')
```

## API Reference

### create_custom_db

```python
create_custom_db(
    code: str,
    columns: Dict[str, Union[str, type, np.dtype]],
    bar_size: str = "1d",
    db_dir: Optional[str] = None,
) -> str
```

Create a SQLite database for custom data storage.

### insert_custom_data

```python
insert_custom_data(
    code: str,
    data: pd.DataFrame,
    mode: str = "replace",
    db_dir: Optional[str] = None,
)
```

Insert data into a custom database. Modes: 'replace', 'append', 'update'.

### from_db

```python
from_db(
    code: str,
    db_dir: Optional[str] = None,
) -> type
```

Load a DataSet class from a database.

### query_custom_data

```python
query_custom_data(
    code: str,
    start_date: Optional[pd.Timestamp] = None,
    end_date: Optional[pd.Timestamp] = None,
    sids: Optional[List[int]] = None,
    columns: Optional[List[str]] = None,
    db_dir: Optional[str] = None,
) -> pd.DataFrame
```

Query data from a custom database.

### list_custom_dbs

```python
list_custom_dbs(
    db_dir: Optional[str] = None,
) -> List[Dict[str, Any]]
```

List all custom databases with metadata.

### get_custom_db_info

```python
get_custom_db_info(
    code: str,
    db_dir: Optional[str] = None,
) -> Dict[str, Any]
```

Get detailed information about a specific database.

### drop_custom_db

```python
drop_custom_db(
    code: str,
    db_dir: Optional[str] = None,
)
```

Permanently delete a custom database.

## Troubleshooting

### Database Already Exists

```python
# Error: CustomDatabaseError: Database 'my-db' already exists

# Solution 1: Use a different name
create_custom_db('my-db-v2', columns={...})

# Solution 2: Delete existing database
drop_custom_db('my-db')
create_custom_db('my-db', columns={...})
```

### Wrong Column Format for Insertion

```python
# Error: CustomDatabaseError: Database has multiple columns.
#        Please provide data with MultiIndex columns

# Solution: Use MultiIndex format (field, sid)
data = pd.DataFrame({
    ('field1', 1): values,
    ('field1', 2): values,
}, index=dates)
data.columns = pd.MultiIndex.from_tuples(
    data.columns, names=['field', 'sid']
)
```

### Database Not Found

```python
# Error: CustomDatabaseError: Database 'my-db' does not exist

# Solution: Check database name and create if needed
dbs = list_custom_dbs()
print([db['code'] for db in dbs])

if 'my-db' not in [db['code'] for db in dbs]:
    create_custom_db('my-db', columns={...})
```

## See Also

- [CustomData User Guide](CUSTOM_DATA.md) - In-memory CustomData usage
- [Pipeline Tutorial](https://zipline-reloaded.io/beginner-tutorial.html)
- [Data Bundles](https://zipline-reloaded.io/bundles.html)
