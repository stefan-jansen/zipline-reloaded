"""
Example: Using Database-Backed CustomData for Persistent Storage

This example demonstrates:
1. Creating a custom database for persistent storage
2. Inserting data into the database
3. Loading data from the database into pipelines
4. Managing databases (list, query, delete)
5. Using database-backed data in pipelines
"""

import numpy as np
import pandas as pd
from pathlib import Path
import tempfile

# Use temp directory for this example
TEMP_DB_DIR = tempfile.mkdtemp()
print(f"Using temporary database directory: {TEMP_DB_DIR}\n")

from zipline.pipeline.data import (
    create_custom_db,
    insert_custom_data,
    list_custom_dbs,
    get_custom_db_info,
    query_custom_data,
    drop_custom_db,
    from_db,
    CustomData,
)
from zipline.pipeline import Pipeline


# ============================================================================
# Example 1: Creating a Custom Database
# ============================================================================

print("=" * 70)
print("Example 1: Creating a Custom Database")
print("=" * 70)

# Create a database for fundamental data
db_path = create_custom_db(
    'fundamentals-daily',
    columns={
        'pe_ratio': float,
        'market_cap': float,
        'revenue_growth': float,
        'debt_ratio': float,
        'sector': int,
    },
    bar_size='1d',
    db_dir=TEMP_DB_DIR,
)

print(f"Created database at: {db_path}")
print(f"Database file exists: {Path(db_path).exists()}")


# ============================================================================
# Example 2: Inserting Data into the Database
# ============================================================================

print("\n" + "=" * 70)
print("Example 2: Inserting Data")
print("=" * 70)

# Generate sample data
dates = pd.bdate_range('2022-01-01', '2022-12-31')
sids = list(range(1, 11))  # 10 stocks

print(f"Generating data for {len(dates)} dates and {len(sids)} stocks...")

# For single-column databases, create simple DataFrames
# For multi-column, use MultiIndex columns (field, sid)

# Create data with MultiIndex columns
data_records = []
for date in dates:
    for sid in sids:
        data_records.append({
            'date': date,
            'sid': sid,
            'pe_ratio': np.random.uniform(5, 30),
            'market_cap': np.random.uniform(1e9, 1e11),
            'revenue_growth': np.random.uniform(-0.1, 0.3),
            'debt_ratio': np.random.uniform(0, 2),
            'sector': np.random.randint(1, 12),
        })

df = pd.DataFrame(data_records)
df['date'] = pd.to_datetime(df['date'])
df = df.set_index(['date', 'sid'])

print(f"Created DataFrame with shape: {df.shape}")
print(f"\nFirst few rows:")
print(df.head())

# Alternatively, use per-column format with MultiIndex
pe_ratios_multi = pd.DataFrame({
    ('pe_ratio', sid): {date: np.random.uniform(5, 30) for date in dates}
    for sid in sids
})
pe_ratios_multi.columns = pd.MultiIndex.from_tuples(
    pe_ratios_multi.columns,
    names=['field', 'sid']
)

print(f"\nInserting data into database...")

# For this example, let's insert using wide format
# Create separate DataFrames per field
for field in ['pe_ratio', 'market_cap', 'revenue_growth', 'debt_ratio', 'sector']:
    field_df = df[field].unstack()

    # Create MultiIndex columns
    field_data = pd.DataFrame({
        (field, sid): field_df[sid]
        for sid in sids
    })
    field_data.columns = pd.MultiIndex.from_tuples(
        field_data.columns,
        names=['field', 'sid']
    )

    insert_custom_data(
        'fundamentals-daily',
        field_data,
        mode='update',  # Update existing or insert new
        db_dir=TEMP_DB_DIR,
    )
    print(f"  - Inserted {field}")

print("Data insertion complete!")


# ============================================================================
# Example 3: Listing and Inspecting Databases
# ============================================================================

print("\n" + "=" * 70)
print("Example 3: Listing and Inspecting Databases")
print("=" * 70)

# List all databases
dbs = list_custom_dbs(db_dir=TEMP_DB_DIR)
print(f"Found {len(dbs)} database(s):\n")

for db in dbs:
    print(f"Database: {db['code']}")
    print(f"  Path: {db['path']}")
    print(f"  Bar size: {db['bar_size']}")
    print(f"  Columns: {list(db['columns'].keys())}")
    print(f"  Rows: {db['row_count']:,}")
    print(f"  Size: {db['size_mb']:.2f} MB")
    print(f"  Created: {db['created_at']}")
    print()

# Get detailed info about a specific database
info = get_custom_db_info('fundamentals-daily', db_dir=TEMP_DB_DIR)
print("Detailed info for 'fundamentals-daily':")
print(f"  Columns: {info['columns']}")


# ============================================================================
# Example 4: Querying Data from Database
# ============================================================================

print("\n" + "=" * 70)
print("Example 4: Querying Data")
print("=" * 70)

# Query all data
all_data = query_custom_data(
    'fundamentals-daily',
    db_dir=TEMP_DB_DIR,
)
print(f"Queried all data: {all_data.shape}")
print(f"\nFirst few rows:")
print(all_data.head())

# Query specific date range
q1_data = query_custom_data(
    'fundamentals-daily',
    start_date=pd.Timestamp('2022-01-01'),
    end_date=pd.Timestamp('2022-03-31'),
    db_dir=TEMP_DB_DIR,
)
print(f"\nQ1 2022 data: {q1_data.shape}")

# Query specific stocks
specific_stocks = query_custom_data(
    'fundamentals-daily',
    sids=[1, 2, 3],
    db_dir=TEMP_DB_DIR,
)
print(f"Data for stocks 1-3: {specific_stocks.shape}")

# Query specific columns
pe_data = query_custom_data(
    'fundamentals-daily',
    columns=['pe_ratio', 'market_cap'],
    start_date=pd.Timestamp('2022-06-01'),
    end_date=pd.Timestamp('2022-06-30'),
    sids=[1, 2],
    db_dir=TEMP_DB_DIR,
)
print(f"\nPE ratio and market cap for stocks 1-2 in June: {pe_data.shape}")
print(pe_data.head())


# ============================================================================
# Example 5: Loading Dataset from Database
# ============================================================================

print("\n" + "=" * 70)
print("Example 5: Loading Dataset from Database")
print("=" * 70)

# Load the dataset from database
FundamentalsData = from_db('fundamentals-daily', db_dir=TEMP_DB_DIR)

print(f"Loaded dataset: {FundamentalsData}")
print(f"Dataset name: {FundamentalsData.__name__}")
print(f"Columns: {sorted(FundamentalsData._column_names)}")
print(f"\nDataset documentation:")
print(FundamentalsData.__doc__)

# Access columns
print(f"\nPE Ratio column: {FundamentalsData.pe_ratio}")
print(f"Market Cap column: {FundamentalsData.market_cap}")


# ============================================================================
# Example 6: Using Database-Backed Data in Pipelines
# ============================================================================

print("\n" + "=" * 70)
print("Example 6: Using in Pipelines")
print("=" * 70)

# Create a value investing pipeline
value_pipeline = Pipeline(
    columns={
        'pe_ratio': FundamentalsData.pe_ratio.latest,
        'market_cap': FundamentalsData.market_cap.latest,
        'revenue_growth': FundamentalsData.revenue_growth.latest,
        'debt_ratio': FundamentalsData.debt_ratio.latest,

        # Computed columns
        'is_undervalued': FundamentalsData.pe_ratio.latest < 15,
        'is_growing': FundamentalsData.revenue_growth.latest > 0.1,
        'is_stable': FundamentalsData.debt_ratio.latest < 1.0,

        # Combined filter
        'is_value_stock': (
            (FundamentalsData.pe_ratio.latest < 15) &
            (FundamentalsData.revenue_growth.latest > 0.1) &
            (FundamentalsData.debt_ratio.latest < 1.0)
        ),
    },
    # Screen for low PE and high growth
    screen=(
        (FundamentalsData.pe_ratio.latest < 20) &
        (FundamentalsData.revenue_growth.latest > 0.05)
    )
)

print("Created value investing pipeline with database-backed data")
print(f"Pipeline columns: {list(value_pipeline.columns.keys())}")

# Get the loader for this dataset
loader = FundamentalsData.get_loader()
print(f"\nLoader: {loader}")
print(f"Database path: {loader.db_path}")


# ============================================================================
# Example 7: Creating Multiple Databases
# ============================================================================

print("\n" + "=" * 70)
print("Example 7: Creating Multiple Databases")
print("=" * 70)

# Create a database for social sentiment
create_custom_db(
    'social-sentiment',
    columns={
        'twitter_sentiment': float,
        'reddit_mentions': int,
        'news_sentiment': float,
    },
    bar_size='1h',
    db_dir=TEMP_DB_DIR,
)
print("Created 'social-sentiment' database")

# Create a database for alternative data
create_custom_db(
    'web-traffic',
    columns={
        'daily_visitors': int,
        'page_views': int,
        'bounce_rate': float,
    },
    bar_size='1d',
    db_dir=TEMP_DB_DIR,
)
print("Created 'web-traffic' database")

# List all databases
dbs = list_custom_dbs(db_dir=TEMP_DB_DIR)
print(f"\nNow have {len(dbs)} databases:")
for db in dbs:
    print(f"  - {db['code']}: {list(db['columns'].keys())}")


# ============================================================================
# Example 8: Updating Existing Data
# ============================================================================

print("\n" + "=" * 70)
print("Example 8: Updating Existing Data")
print("=" * 70)

# Query current data for a specific date
original = query_custom_data(
    'fundamentals-daily',
    start_date=pd.Timestamp('2022-01-03'),
    end_date=pd.Timestamp('2022-01-03'),
    sids=[1],
    columns=['pe_ratio'],
    db_dir=TEMP_DB_DIR,
)
print("Original PE ratio for stock 1 on 2022-01-03:")
print(original)

# Update with new data
update_df = pd.DataFrame({
    ('pe_ratio', 1): {pd.Timestamp('2022-01-03'): 25.0}
})
update_df.columns = pd.MultiIndex.from_tuples(
    update_df.columns,
    names=['field', 'sid']
)

insert_custom_data(
    'fundamentals-daily',
    update_df,
    mode='update',  # Update existing record
    db_dir=TEMP_DB_DIR,
)
print("\nUpdated PE ratio to 25.0")

# Query updated data
updated = query_custom_data(
    'fundamentals-daily',
    start_date=pd.Timestamp('2022-01-03'),
    end_date=pd.Timestamp('2022-01-03'),
    sids=[1],
    columns=['pe_ratio'],
    db_dir=TEMP_DB_DIR,
)
print("\nUpdated PE ratio:")
print(updated)


# ============================================================================
# Example 9: Comparing In-Memory vs Database Performance
# ============================================================================

print("\n" + "=" * 70)
print("Example 9: In-Memory vs Database")
print("=" * 70)

print("""
In-Memory Loading (MultiColumnDataFrameLoader):
  + Faster for small datasets that fit in RAM
  + No disk I/O during pipeline execution
  - Must reload data each time
  - Limited by available RAM

Database Loading (DatabaseCustomDataLoader):
  + Persistent storage - load once, use many times
  + Efficient querying - only loads needed date/sid ranges
  + Suitable for large datasets
  + Can incrementally update data
  - Slightly slower due to disk I/O
  - Requires database setup

Recommendation:
- Use in-memory for: Development, small datasets, frequently changing data
- Use database for: Production, large datasets, persistent storage
""")


# ============================================================================
# Example 10: Cleanup
# ============================================================================

print("\n" + "=" * 70)
print("Example 10: Cleanup")
print("=" * 70)

# List databases before cleanup
before = list_custom_dbs(db_dir=TEMP_DB_DIR)
print(f"Databases before cleanup: {[db['code'] for db in before]}")

# Drop a database
drop_custom_db('web-traffic', db_dir=TEMP_DB_DIR)
print("\nDropped 'web-traffic' database")

# List databases after cleanup
after = list_custom_dbs(db_dir=TEMP_DB_DIR)
print(f"Databases after cleanup: {[db['code'] for db in after]}")

# Clean up all test databases
print("\nCleaning up all test databases...")
for db in list_custom_dbs(db_dir=TEMP_DB_DIR):
    drop_custom_db(db['code'], db_dir=TEMP_DB_DIR)
    print(f"  Dropped {db['code']}")

final = list_custom_dbs(db_dir=TEMP_DB_DIR)
print(f"\nRemaining databases: {len(final)}")


# ============================================================================
# Summary
# ============================================================================

print("\n" + "=" * 70)
print("Summary")
print("=" * 70)

print("""
Database-Backed CustomData provides:

1. **Persistent Storage**: Data survives across runs
   - Create once with create_custom_db()
   - Insert data with insert_custom_data()
   - Load anytime with from_db()

2. **Efficient Querying**: Only loads what's needed
   - Automatically queries date/sid ranges
   - Indexed on (date, sid) for fast lookups
   - Suitable for large datasets

3. **Data Management**: Easy to maintain
   - list_custom_dbs() - see all databases
   - get_custom_db_info() - inspect metadata
   - query_custom_data() - ad-hoc queries
   - drop_custom_db() - remove old data

4. **Seamless Integration**: Works like in-memory data
   - from_db() loads dataset class
   - Use in pipelines just like any DataSet
   - Automatic loader creation with .get_loader()

5. **Update Support**: Incrementally update data
   - mode='replace' - fresh start
   - mode='append' - add new data
   - mode='update' - update + insert

Example workflow:
```python
# Setup (once)
create_custom_db('my-data', columns={'metric': float})
insert_custom_data('my-data', df)

# Use (many times)
MyData = from_db('my-data')
pipe = Pipeline(columns={'metric': MyData.metric.latest})
```

For complete documentation, see docs/CUSTOM_DATA.md
""")

print("=" * 70)
print("Example completed successfully!")
print("=" * 70)
