"""
Database-backed loader for custom pipeline data.

Efficiently loads custom data from SQLite databases with support for
date and asset filtering.
"""

import sqlite3
from typing import Optional

import numpy as np
import pandas as pd

from zipline.lib.adjusted_array import AdjustedArray
from .base import PipelineLoader


class DatabaseCustomDataLoader(PipelineLoader):
    """
    A PipelineLoader that reads custom data from SQLite databases.

    This loader efficiently queries only the date/sid ranges needed,
    making it suitable for large datasets that don't fit in memory.

    Parameters
    ----------
    dataset : zipline.pipeline.data.DataSet
        The dataset whose columns will be loaded by this loader.
    db_path : str
        Path to the SQLite database file.
    columns_map : dict[BoundColumn -> str], optional
        Mapping from BoundColumn objects to database column names.
        If None, assumes column names match the BoundColumn names.

    Examples
    --------
    Load data from a database:

    >>> from zipline.pipeline.data import CustomData
    >>> from zipline.pipeline.loaders import DatabaseCustomDataLoader
    >>>
    >>> # Load dataset from database
    >>> MyData = CustomData.from_db('my-custom-data')
    >>>
    >>> # The loader is automatically created and configured
    >>> # But you can also create it manually:
    >>> loader = DatabaseCustomDataLoader(MyData, '/path/to/db.db')
    """

    def __init__(
        self,
        dataset,
        db_path: str,
        columns_map: Optional[dict] = None,
    ):
        self.dataset = dataset
        self.db_path = db_path

        # Map columns to database column names
        if columns_map is None:
            self.columns_map = {
                getattr(dataset, col_name): col_name
                for col_name in dataset._column_names
            }
        else:
            self.columns_map = columns_map

        # Verify database exists and has expected structure
        self._verify_database()

    def _verify_database(self):
        """Verify that the database exists and has the expected structure."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Check that data table exists
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='data'"
            )
            if not cursor.fetchone():
                raise ValueError(
                    f"Database at {self.db_path} does not have a 'data' table"
                )

            # Get column names
            cursor.execute("PRAGMA table_info(data)")
            db_columns = {row[1] for row in cursor.fetchall()}

            # Verify required columns exist
            required = {'date', 'sid'}
            missing = required - db_columns
            if missing:
                raise ValueError(
                    f"Database missing required columns: {missing}"
                )

            # Verify dataset columns exist in database
            for bound_col, db_col_name in self.columns_map.items():
                if db_col_name not in db_columns:
                    raise ValueError(
                        f"Column '{db_col_name}' for {bound_col.qualname} "
                        f"not found in database"
                    )

            conn.close()

        except sqlite3.Error as e:
            raise ValueError(f"Database error: {e}") from e

    def load_adjusted_array(self, domain, columns, dates, sids, mask):
        """
        Load data for the requested columns from the database.

        Parameters
        ----------
        domain : zipline.pipeline.domain.Domain
            Domain for which to load data.
        columns : list[zipline.pipeline.data.BoundColumn]
            Columns to load.
        dates : pd.DatetimeIndex
            Dates for which to load data.
        sids : pd.Int64Index
            Asset IDs for which to load data.
        mask : np.ndarray[bool]
            Mask array indicating which (date, sid) pairs to load.

        Returns
        -------
        arrays : dict[BoundColumn -> AdjustedArray]
            Mapping from columns to loaded arrays.
        """
        # Build query to fetch only needed data
        min_date = dates.min().strftime('%Y-%m-%d')
        max_date = dates.max().strftime('%Y-%m-%d')

        # Get column names to fetch
        db_col_names = [self.columns_map[col] for col in columns]

        # Build SQL query
        sid_placeholders = ','.join(['?'] * len(sids))
        query_cols = ['date', 'sid'] + db_col_names

        query = f"""
            SELECT {', '.join(query_cols)}
            FROM data
            WHERE date >= ? AND date <= ?
            AND sid IN ({sid_placeholders})
            ORDER BY date, sid
        """

        params = [min_date, max_date] + list(sids)

        # Execute query
        conn = sqlite3.connect(self.db_path)
        try:
            df = pd.read_sql_query(query, conn, params=params)
        finally:
            conn.close()

        # Process results
        out = {}

        if df.empty:
            # No data found - return arrays filled with missing values
            shape = (len(dates), len(sids))
            for column in columns:
                data = np.full(shape, column.missing_value, dtype=column.dtype)
                out[column] = AdjustedArray(
                    data=data,
                    adjustments={},
                    missing_value=column.missing_value,
                )
            return out

        # Convert date column to datetime
        df['date'] = pd.to_datetime(df['date'])

        # Create output arrays
        shape = (len(dates), len(sids))

        for column in columns:
            # Initialize with missing values
            data = np.full(shape, column.missing_value, dtype=column.dtype)

            # Get database column name
            db_col_name = self.columns_map[column]

            # Fill in available data
            for _, row in df.iterrows():
                try:
                    date_idx = dates.get_loc(row['date'])
                    sid_idx = sids.get_loc(row['sid'])

                    # Only fill if mask is True
                    if mask[date_idx, sid_idx]:
                        value = row[db_col_name]
                        if pd.notna(value):
                            data[date_idx, sid_idx] = value
                except (KeyError, ValueError):
                    # Date or sid not in requested range
                    continue

            out[column] = AdjustedArray(
                data=data,
                adjustments={},  # TODO: Support adjustments from database
                missing_value=column.missing_value,
            )

        return out


__all__ = [
    'DatabaseCustomDataLoader',
]
