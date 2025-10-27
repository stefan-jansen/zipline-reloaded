"""
Database storage for custom pipeline data.

This module provides SQLite-based persistent storage for custom datasets,
similar to QuantRocket's create_custom_db() functionality.
"""

import os
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
import json

import numpy as np
import pandas as pd

from zipline.utils.numpy_utils import (
    bool_dtype,
    datetime64ns_dtype,
    float64_dtype,
    int64_dtype,
    object_dtype,
)


# Database configuration
DEFAULT_DB_DIR = os.path.expanduser("~/.zipline/custom_data")


# Type mapping for database columns
DTYPE_TO_SQL = {
    float64_dtype: "REAL",
    int64_dtype: "INTEGER",
    bool_dtype: "INTEGER",  # SQLite doesn't have BOOLEAN
    object_dtype: "TEXT",
    datetime64ns_dtype: "TEXT",  # Store as ISO format string
}

SQL_TO_DTYPE = {
    "REAL": float64_dtype,
    "INTEGER": int64_dtype,
    "TEXT": object_dtype,
}


class CustomDatabaseError(Exception):
    """Exception raised for custom database errors."""
    pass


def _get_db_path(code: str, db_dir: Optional[str] = None) -> Path:
    """
    Get the path to a custom database file.

    Parameters
    ----------
    code : str
        Database identifier.
    db_dir : str, optional
        Directory for database files. Defaults to ~/.zipline/custom_data

    Returns
    -------
    path : Path
        Path to the database file.
    """
    if db_dir is None:
        db_dir = DEFAULT_DB_DIR

    db_path = Path(db_dir)
    db_path.mkdir(parents=True, exist_ok=True)

    return db_path / f"{code}.db"


def _validate_code(code: str):
    """Validate database code format."""
    if not code:
        raise ValueError("Database code cannot be empty")

    # Check for valid characters (lowercase alphanumeric and hyphens)
    import re
    if not re.match(r'^[a-z0-9-]+$', code):
        raise ValueError(
            f"Database code '{code}' must contain only lowercase letters, "
            "numbers, and hyphens"
        )


def _validate_columns(columns: Dict[str, Union[str, np.dtype]]) -> Dict[str, np.dtype]:
    """
    Validate and normalize column specifications.

    Parameters
    ----------
    columns : dict
        Mapping of column names to data types.

    Returns
    -------
    normalized : dict
        Mapping of column names to numpy dtypes.
    """
    from .custom_data import _normalize_dtype

    normalized = {}

    for col_name, dtype_spec in columns.items():
        # Validate column name
        if not col_name:
            raise ValueError("Column name cannot be empty")

        import re
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', col_name):
            raise ValueError(
                f"Column name '{col_name}' must start with a letter and "
                "contain only letters, numbers, and underscores"
            )

        # Normalize dtype
        dtype = _normalize_dtype(dtype_spec)
        normalized[col_name] = dtype

    return normalized


def create_custom_db(
    code: str,
    columns: Dict[str, Union[str, type, np.dtype]],
    bar_size: str = "1d",
    db_dir: Optional[str] = None,
) -> str:
    """
    Create a custom database for storing pipeline data.

    This creates a SQLite database optimized for storing time-series data
    indexed by date and asset ID (sid).

    Parameters
    ----------
    code : str
        Database identifier. Must contain only lowercase letters, numbers,
        and hyphens (e.g., 'my-custom-data', 'fundamentals-1d').
    columns : dict[str -> dtype]
        Dictionary mapping column names to their data types.
        Supported types: float, int, bool, str, datetime.
        Column names must start with a letter and contain only letters,
        numbers, and underscores.
    bar_size : str, optional
        Time frequency of the data (e.g., '1d', '1h', '5min').
        This is stored as metadata but does not affect database structure.
    db_dir : str, optional
        Directory for database files. Defaults to ~/.zipline/custom_data

    Returns
    -------
    db_path : str
        Path to the created database file.

    Raises
    ------
    CustomDatabaseError
        If database already exists or creation fails.
    ValueError
        If code or column specifications are invalid.

    Examples
    --------
    Create a database for fundamental data:

    >>> create_custom_db(
    ...     'fundamentals-daily',
    ...     columns={
    ...         'pe_ratio': float,
    ...         'market_cap': float,
    ...         'sector': int,
    ...         'ticker': str,
    ...     }
    ... )
    '/home/user/.zipline/custom_data/fundamentals-daily.db'

    Create a database for alternative data:

    >>> create_custom_db(
    ...     'social-sentiment',
    ...     columns={
    ...         'twitter_sentiment': float,
    ...         'mentions': int,
    ...         'is_trending': bool,
    ...     },
    ...     bar_size='1h'
    ... )
    """
    # Validate inputs
    _validate_code(code)
    normalized_columns = _validate_columns(columns)

    # Get database path
    db_path = _get_db_path(code, db_dir)

    # Check if database already exists
    if db_path.exists():
        raise CustomDatabaseError(
            f"Database '{code}' already exists at {db_path}. "
            "Use drop_custom_db() to delete it first."
        )

    # Create database and tables
    conn = sqlite3.connect(str(db_path))
    try:
        cursor = conn.cursor()

        # Create metadata table
        cursor.execute("""
            CREATE TABLE metadata (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)

        # Store metadata
        metadata = {
            'code': code,
            'bar_size': bar_size,
            'columns': json.dumps({
                name: str(dtype) for name, dtype in normalized_columns.items()
            }),
            'created_at': pd.Timestamp.now().isoformat(),
        }

        for key, value in metadata.items():
            cursor.execute(
                "INSERT INTO metadata (key, value) VALUES (?, ?)",
                (key, value)
            )

        # Build data table schema
        # Always include: date, sid, timestamp
        column_defs = [
            "date TEXT NOT NULL",  # YYYY-MM-DD format
            "sid INTEGER NOT NULL",
            "timestamp TEXT",  # ISO format for precise timing
        ]

        # Add custom columns
        for col_name, dtype in normalized_columns.items():
            sql_type = DTYPE_TO_SQL.get(dtype, "TEXT")
            column_defs.append(f"{col_name} {sql_type}")

        # Create data table with primary key on (date, sid)
        create_table_sql = f"""
            CREATE TABLE data (
                {', '.join(column_defs)},
                PRIMARY KEY (date, sid)
            )
        """
        cursor.execute(create_table_sql)

        # Create indices for efficient querying
        cursor.execute("CREATE INDEX idx_date ON data(date)")
        cursor.execute("CREATE INDEX idx_sid ON data(sid)")

        conn.commit()

        return str(db_path)

    except Exception as e:
        # Clean up on failure
        conn.close()
        if db_path.exists():
            db_path.unlink()
        raise CustomDatabaseError(f"Failed to create database: {e}") from e

    finally:
        conn.close()


def list_custom_dbs(db_dir: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    List all custom databases.

    Parameters
    ----------
    db_dir : str, optional
        Directory containing database files.

    Returns
    -------
    databases : list[dict]
        List of database information dictionaries containing:
        - code: Database identifier
        - path: Full path to database file
        - bar_size: Data frequency
        - columns: Dictionary of column names and types
        - created_at: Creation timestamp
        - size_mb: File size in megabytes

    Examples
    --------
    >>> dbs = list_custom_dbs()
    >>> for db in dbs:
    ...     print(f"{db['code']}: {db['columns']}")
    """
    if db_dir is None:
        db_dir = DEFAULT_DB_DIR

    db_path = Path(db_dir)
    if not db_path.exists():
        return []

    databases = []

    for db_file in db_path.glob("*.db"):
        try:
            conn = sqlite3.connect(str(db_file))
            cursor = conn.cursor()

            # Read metadata
            cursor.execute("SELECT key, value FROM metadata")
            metadata = dict(cursor.fetchall())

            # Get file size
            size_mb = db_file.stat().st_size / (1024 * 1024)

            # Get row count
            cursor.execute("SELECT COUNT(*) FROM data")
            row_count = cursor.fetchone()[0]

            databases.append({
                'code': metadata.get('code', db_file.stem),
                'path': str(db_file),
                'bar_size': metadata.get('bar_size', 'unknown'),
                'columns': json.loads(metadata.get('columns', '{}')),
                'created_at': metadata.get('created_at', 'unknown'),
                'size_mb': round(size_mb, 2),
                'row_count': row_count,
            })

            conn.close()

        except Exception:
            # Skip invalid database files
            continue

    return sorted(databases, key=lambda x: x['code'])


def get_custom_db_info(code: str, db_dir: Optional[str] = None) -> Dict[str, Any]:
    """
    Get information about a custom database.

    Parameters
    ----------
    code : str
        Database identifier.
    db_dir : str, optional
        Directory containing database files.

    Returns
    -------
    info : dict
        Database information.

    Raises
    ------
    CustomDatabaseError
        If database does not exist.
    """
    db_path = _get_db_path(code, db_dir)

    if not db_path.exists():
        raise CustomDatabaseError(f"Database '{code}' does not exist")

    dbs = list_custom_dbs(db_dir)
    for db in dbs:
        if db['code'] == code:
            return db

    raise CustomDatabaseError(f"Database '{code}' not found")


def drop_custom_db(code: str, db_dir: Optional[str] = None):
    """
    Delete a custom database.

    Parameters
    ----------
    code : str
        Database identifier.
    db_dir : str, optional
        Directory containing database files.

    Raises
    ------
    CustomDatabaseError
        If database does not exist.

    Examples
    --------
    >>> drop_custom_db('old-data')
    """
    db_path = _get_db_path(code, db_dir)

    if not db_path.exists():
        raise CustomDatabaseError(f"Database '{code}' does not exist")

    db_path.unlink()


def insert_custom_data(
    code: str,
    data: pd.DataFrame,
    mode: str = "replace",
    db_dir: Optional[str] = None,
):
    """
    Insert data into a custom database.

    Parameters
    ----------
    code : str
        Database identifier.
    data : pd.DataFrame
        Data to insert. Must have:
        - Index: DatetimeIndex (dates)
        - Columns: Int64Index (sids/asset IDs)
        - Optional: MultiIndex columns for multiple fields
    mode : {'replace', 'append', 'update'}, default 'replace'
        - 'replace': Delete existing data and insert new data
        - 'append': Add new data, fail if dates/sids already exist
        - 'update': Update existing records, insert new ones
    db_dir : str, optional
        Directory containing database files.

    Raises
    ------
    CustomDatabaseError
        If database does not exist or insert fails.

    Examples
    --------
    Insert data with single column:

    >>> dates = pd.date_range('2020-01-01', periods=100)
    >>> sids = [1, 2, 3]
    >>> data = pd.DataFrame(
    ...     np.random.randn(100, 3),
    ...     index=dates,
    ...     columns=sids
    ... )
    >>> insert_custom_data('my-db', data, mode='replace')

    Insert data with multiple columns:

    >>> data = pd.DataFrame({
    ...     ('pe_ratio', 1): values1,
    ...     ('pe_ratio', 2): values2,
    ...     ('market_cap', 1): values3,
    ...     ('market_cap', 2): values4,
    ... })
    >>> data.columns = pd.MultiIndex.from_tuples(
    ...     data.columns, names=['field', 'sid']
    ... )
    >>> insert_custom_data('my-db', data, mode='update')
    """
    db_path = _get_db_path(code, db_dir)

    if not db_path.exists():
        raise CustomDatabaseError(f"Database '{code}' does not exist")

    # Get database metadata
    info = get_custom_db_info(code, db_dir)
    db_columns = info['columns']

    # Convert DataFrame to long format
    if isinstance(data.columns, pd.MultiIndex):
        # MultiIndex: (field, sid)
        records = []
        for date in data.index:
            for field, sid in data.columns:
                value = data.loc[date, (field, sid)]
                if pd.notna(value):
                    records.append({
                        'date': date.strftime('%Y-%m-%d'),
                        'sid': int(sid),
                        'timestamp': date.isoformat(),
                        field: value,
                    })
    else:
        # Simple columns: sid
        # Assumes single column in database or data needs column name
        if len(db_columns) == 1:
            field_name = list(db_columns.keys())[0]
        else:
            # Need to figure out which field this data belongs to
            # For now, assume it's specified in data or error
            raise CustomDatabaseError(
                "Database has multiple columns. Please provide data "
                "with MultiIndex columns in format (field, sid)"
            )

        records = []
        for date in data.index:
            for sid in data.columns:
                value = data.loc[date, sid]
                if pd.notna(value):
                    records.append({
                        'date': date.strftime('%Y-%m-%d'),
                        'sid': int(sid),
                        'timestamp': date.isoformat(),
                        field_name: value,
                    })

    if not records:
        return  # Nothing to insert

    # Insert records
    conn = sqlite3.connect(str(db_path))
    try:
        cursor = conn.cursor()

        if mode == 'replace':
            # Delete all existing data
            cursor.execute("DELETE FROM data")

        # Prepare insert statement
        # Group records by date/sid to handle multiple fields
        grouped = {}
        for record in records:
            key = (record['date'], record['sid'])
            if key not in grouped:
                grouped[key] = {
                    'date': record['date'],
                    'sid': record['sid'],
                    'timestamp': record['timestamp'],
                }
            # Add field values
            for k, v in record.items():
                if k not in ('date', 'sid', 'timestamp'):
                    grouped[key][k] = v

        # Build insert SQL
        all_columns = ['date', 'sid', 'timestamp'] + list(db_columns.keys())
        placeholders = ', '.join(['?'] * len(all_columns))

        if mode == 'update':
            # Use INSERT OR REPLACE
            insert_sql = f"""
                INSERT OR REPLACE INTO data ({', '.join(all_columns)})
                VALUES ({placeholders})
            """
        else:  # append
            insert_sql = f"""
                INSERT INTO data ({', '.join(all_columns)})
                VALUES ({placeholders})
            """

        # Insert all records
        for record in grouped.values():
            values = [record.get(col) for col in all_columns]
            cursor.execute(insert_sql, values)

        conn.commit()

    except sqlite3.IntegrityError as e:
        raise CustomDatabaseError(
            f"Data already exists for some date/sid combinations. "
            f"Use mode='update' to update existing records. Error: {e}"
        ) from e
    except Exception as e:
        raise CustomDatabaseError(f"Failed to insert data: {e}") from e
    finally:
        conn.close()


def query_custom_data(
    code: str,
    start_date: Optional[pd.Timestamp] = None,
    end_date: Optional[pd.Timestamp] = None,
    sids: Optional[List[int]] = None,
    columns: Optional[List[str]] = None,
    db_dir: Optional[str] = None,
) -> pd.DataFrame:
    """
    Query data from a custom database.

    Parameters
    ----------
    code : str
        Database identifier.
    start_date : pd.Timestamp, optional
        Start date for query (inclusive).
    end_date : pd.Timestamp, optional
        End date for query (inclusive).
    sids : list[int], optional
        Asset IDs to query. If None, query all assets.
    columns : list[str], optional
        Columns to return. If None, return all columns.
    db_dir : str, optional
        Directory containing database files.

    Returns
    -------
    data : pd.DataFrame
        Query results with MultiIndex (date, sid) and columns for each field.

    Examples
    --------
    >>> df = query_custom_data(
    ...     'my-db',
    ...     start_date=pd.Timestamp('2020-01-01'),
    ...     end_date=pd.Timestamp('2020-12-31'),
    ...     sids=[1, 2, 3]
    ... )
    """
    db_path = _get_db_path(code, db_dir)

    if not db_path.exists():
        raise CustomDatabaseError(f"Database '{code}' does not exist")

    # Build query
    where_clauses = []
    params = []

    if start_date:
        where_clauses.append("date >= ?")
        params.append(start_date.strftime('%Y-%m-%d'))

    if end_date:
        where_clauses.append("date <= ?")
        params.append(end_date.strftime('%Y-%m-%d'))

    if sids:
        placeholders = ','.join(['?'] * len(sids))
        where_clauses.append(f"sid IN ({placeholders})")
        params.extend(sids)

    where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"

    if columns:
        select_cols = ['date', 'sid'] + columns
    else:
        select_cols = ['*']

    query_sql = f"SELECT {', '.join(select_cols)} FROM data WHERE {where_sql} ORDER BY date, sid"

    # Execute query
    conn = sqlite3.connect(str(db_path))
    try:
        df = pd.read_sql_query(query_sql, conn, params=params)

        if not df.empty:
            df['date'] = pd.to_datetime(df['date'])
            df = df.set_index(['date', 'sid'])

        return df

    finally:
        conn.close()


__all__ = [
    'create_custom_db',
    'list_custom_dbs',
    'get_custom_db_info',
    'drop_custom_db',
    'insert_custom_data',
    'query_custom_data',
    'CustomDatabaseError',
]
