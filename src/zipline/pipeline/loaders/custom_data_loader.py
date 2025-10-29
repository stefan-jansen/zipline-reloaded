"""
Custom Data Loader for Pipeline.

Provides loaders for custom datasets, supporting efficient loading of
multiple columns from a single data source.
"""

from functools import partial
from typing import Dict, Optional, Union

import numpy as np
import pandas as pd

from zipline.lib.adjusted_array import AdjustedArray
from zipline.lib.adjustment import make_adjustment_from_labels
from zipline.utils.numpy_utils import as_column
from .base import PipelineLoader

ADJUSTMENT_COLUMNS = pd.Index(
    [
        "sid",
        "value",
        "kind",
        "start_date",
        "end_date",
        "apply_date",
    ]
)


class MultiColumnDataFrameLoader(PipelineLoader):
    """
    A PipelineLoader that reads multiple columns from DataFrames.

    This loader can efficiently load data for an entire DataSet from
    a collection of DataFrames, one per column. It's designed to work
    seamlessly with custom datasets created via CustomData().

    Parameters
    ----------
    dataset : zipline.pipeline.data.DataSet
        The dataset whose columns will be loaded by this loader.
    data : dict[BoundColumn -> pd.DataFrame] or pd.DataFrame
        Either:
        - A dictionary mapping BoundColumn objects to DataFrames, or
        - A single DataFrame whose columns correspond to dataset columns.

        DataFrames should have:
        - Index: DatetimeIndex with dates when data is available
        - Columns: Int64Index with asset IDs (sids)

        Dates should be labeled with the first date on which a value would be
        **available** to an algorithm. OHLCV data should generally be shifted
        back by a trading day.

    adjustments : dict[BoundColumn -> pd.DataFrame] or pd.DataFrame, optional
        Adjustments to apply to the data. Either:
        - A dictionary mapping BoundColumn objects to adjustment DataFrames, or
        - A single DataFrame with an additional 'column' field to identify
          which column the adjustment applies to.

        Each adjustment DataFrame should have columns:
            sid : int
            value : any
            kind : int (zipline.pipeline.loaders.frame.ADJUSTMENT_TYPES)
            start_date : datetime64 (can be NaT)
            end_date : datetime64 (must be set)
            apply_date : datetime64 (must be set)

    Examples
    --------
    Load from a single DataFrame with multiple columns:

    >>> from zipline.pipeline.data import CustomData
    >>> from zipline.pipeline.loaders import MultiColumnDataFrameLoader
    >>>
    >>> # Create a custom dataset
    >>> MyData = CustomData(
    ...     'MyData',
    ...     columns={'metric1': float, 'metric2': float}
    ... )
    >>>
    >>> # Create sample data (rows=dates, columns=multi-index(sid, field))
    >>> import pandas as pd
    >>> import numpy as np
    >>> dates = pd.date_range('2020-01-01', periods=10, freq='D')
    >>> sids = [1, 2, 3]
    >>>
    >>> # Wide format: each column is a metric
    >>> data = pd.DataFrame({
    ...     'metric1': {(d, sid): np.random.randn()
    ...                 for d in dates for sid in sids},
    ...     'metric2': {(d, sid): np.random.randn()
    ...                 for d in dates for sid in sids},
    ... })
    >>>
    >>> # Or use separate DataFrames per column
    >>> data_dict = {
    ...     MyData.metric1: pd.DataFrame(
    ...         np.random.randn(10, 3),
    ...         index=dates,
    ...         columns=sids,
    ...     ),
    ...     MyData.metric2: pd.DataFrame(
    ...         np.random.randn(10, 3),
    ...         index=dates,
    ...         columns=sids,
    ...     ),
    ... }
    >>>
    >>> loader = MultiColumnDataFrameLoader(MyData, data_dict)
    """

    def __init__(
        self,
        dataset,
        data: Union[Dict, pd.DataFrame],
        adjustments: Optional[Union[Dict, pd.DataFrame]] = None,
    ):
        self.dataset = dataset

        # Normalize data input
        if isinstance(data, pd.DataFrame):
            # Single DataFrame - need to map to columns
            self._data_frames = self._split_dataframe_by_column(dataset, data)
        else:
            # Dictionary of column -> DataFrame
            self._data_frames = data

        # Normalize adjustments input
        if adjustments is None:
            self._adjustments = {
                col: pd.DataFrame(
                    index=pd.DatetimeIndex([]),
                    columns=ADJUSTMENT_COLUMNS,
                )
                for col in self._data_frames.keys()
            }
        elif isinstance(adjustments, pd.DataFrame):
            # Single DataFrame with 'column' field
            self._adjustments = self._split_adjustments_by_column(adjustments)
        else:
            # Dictionary of column -> adjustments DataFrame
            self._adjustments = adjustments

        # Pre-process each column's data
        self._baselines = {}
        self._dates = {}
        self._assets = {}
        self._adjustment_data = {}

        for column, df in self._data_frames.items():
            self._baselines[column] = df.values.astype(column.dtype)
            self._dates[column] = df.index
            self._assets[column] = df.columns

            # Process adjustments for this column
            adj_df = self._adjustments.get(
                column,
                pd.DataFrame(
                    index=pd.DatetimeIndex([]),
                    columns=ADJUSTMENT_COLUMNS,
                ),
            )
            adj_df = adj_df.reindex(ADJUSTMENT_COLUMNS, axis=1)
            adj_df.sort_values(["apply_date", "sid"], inplace=True)

            self._adjustment_data[column] = {
                "df": adj_df,
                "apply_dates": pd.DatetimeIndex(adj_df.apply_date),
                "end_dates": pd.DatetimeIndex(adj_df.end_date),
                "sids": pd.Index(adj_df.sid, dtype="int64"),
            }

    def _split_dataframe_by_column(self, dataset, df):
        """
        Split a single multi-column DataFrame into per-column DataFrames.
        """
        result = {}

        for col_name in dataset._column_names:
            bound_col = getattr(dataset, col_name)

            if col_name in df.columns:
                # Column exists in the DataFrame
                col_data = df[col_name]

                # If it's a multi-index DataFrame (date, sid) as index
                if isinstance(df.index, pd.MultiIndex):
                    col_data = col_data.unstack(level=-1)

                result[bound_col] = col_data

        return result

    def _split_adjustments_by_column(self, adj_df):
        """
        Split a single adjustments DataFrame into per-column DataFrames.
        """
        if "column" not in adj_df.columns:
            raise ValueError(
                "Adjustments DataFrame must have a 'column' field to "
                "identify which column each adjustment applies to."
            )

        result = {}
        for col_name, group in adj_df.groupby("column"):
            # Find the corresponding BoundColumn
            for bound_col in self._data_frames.keys():
                if bound_col.name == col_name:
                    result[bound_col] = group.drop("column", axis=1)
                    break

        return result

    def load_adjusted_array(self, domain, columns, dates, sids, mask):
        """
        Load data for the requested columns.

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
        out = {}

        for column in columns:
            self._validate_column(column)

            # Get data for this column
            baseline = self._baselines[column]
            col_dates = self._dates[column]
            col_assets = self._assets[column]

            # Create indexers to align our data with requested dates/sids
            date_indexer = col_dates.get_indexer(dates)
            assets_indexer = col_assets.get_indexer(sids)

            # Boolean arrays with True on matched entries
            good_dates = date_indexer != -1
            good_assets = assets_indexer != -1

            # Extract the requested subset of data
            data = baseline[np.ix_(date_indexer, assets_indexer)]
            data_mask = (good_assets & as_column(good_dates)) & mask

            # Fill missing values
            data[~data_mask] = column.missing_value

            # Format adjustments for this column
            adjustments = self._format_adjustments(column, dates, sids)

            out[column] = AdjustedArray(
                data=data,
                adjustments=adjustments,
                missing_value=column.missing_value,
            )

        return out

    def _format_adjustments(self, column, dates, assets):
        """
        Build a dict of Adjustment objects for a specific column.

        Returns a dict of the form:
        {
            date_index: [Adjustment1, Adjustment2, ...],
            ...
        }
        """
        adj_data = self._adjustment_data[column]
        adj_df = adj_data["df"]

        if len(adj_df) == 0:
            return {}

        make_adjustment = partial(make_adjustment_from_labels, dates, assets)

        min_date, max_date = dates[[0, -1]]

        # Filter adjustments by date range
        date_bounds = adj_data["apply_dates"].slice_indexer(min_date, max_date)
        dates_filter = np.zeros(len(adj_df), dtype="bool")
        dates_filter[date_bounds] = True
        dates_filter &= adj_data["end_dates"] >= min_date

        # Filter adjustments by assets
        sids_filter = adj_data["sids"].isin(assets.values)

        adjustments_to_use = adj_df.loc[dates_filter & sids_filter].set_index(
            "apply_date"
        )

        # Build adjustment dict
        out = {}
        previous_apply_date = object()
        for row in adjustments_to_use.itertuples():
            apply_date, sid, value, kind, start_date, end_date = row

            if apply_date != previous_apply_date:
                row_loc = dates.get_indexer([apply_date], method="bfill")[0]
                current_date_adjustments = out[row_loc] = []
                previous_apply_date = apply_date

            current_date_adjustments.append(
                make_adjustment(start_date, end_date, sid, kind, value)
            )

        return out

    def _validate_column(self, column):
        """Validate that a column belongs to our dataset."""
        if column.dataset != self.dataset and column.dataset != self.dataset.unspecialize():
            raise ValueError(
                f"Column {column.qualname} does not belong to dataset "
                f"{self.dataset.qualname}"
            )

        if column not in self._baselines:
            raise ValueError(
                f"No data provided for column {column.qualname}. "
                f"Available columns: {list(self._baselines.keys())}"
            )


__all__ = [
    "MultiColumnDataFrameLoader",
]
