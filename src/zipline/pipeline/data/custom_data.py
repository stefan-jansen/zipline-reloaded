"""
CustomData - Utilities for creating custom pipeline datasets.

This module provides tools for easily defining and loading custom data sources
into Zipline pipelines, similar to QuantRocket's CustomData functionality.
"""

from typing import Dict, Optional, Union, Any
import numpy as np
import pandas as pd

from zipline.pipeline.domain import Domain, GENERIC
from zipline.utils.numpy_utils import (
    bool_dtype,
    categorical_dtype,
    datetime64ns_dtype,
    float64_dtype,
    int64_dtype,
    object_dtype,
)

from .dataset import Column, DataSet, DataSetMeta


# Mapping of common type specifications to numpy dtypes
DTYPE_MAPPING = {
    # Python types
    float: float64_dtype,
    int: int64_dtype,
    bool: bool_dtype,
    str: object_dtype,
    object: object_dtype,
    # String representations
    "float": float64_dtype,
    "float64": float64_dtype,
    "int": int64_dtype,
    "int64": int64_dtype,
    "bool": bool_dtype,
    "boolean": bool_dtype,
    "str": object_dtype,
    "string": object_dtype,
    "object": object_dtype,
    "datetime": datetime64ns_dtype,
    "datetime64": datetime64ns_dtype,
    "datetime64[ns]": datetime64ns_dtype,
    "categorical": categorical_dtype,
    # NumPy dtypes (pass through)
    np.dtype("float64"): float64_dtype,
    np.dtype("int64"): int64_dtype,
    np.dtype("bool"): bool_dtype,
    np.dtype("object"): object_dtype,
    np.dtype("datetime64[ns]"): datetime64ns_dtype,
}


def _normalize_dtype(dtype_spec):
    """
    Normalize a dtype specification to a numpy dtype.

    Parameters
    ----------
    dtype_spec : type, str, or np.dtype
        A dtype specification.

    Returns
    -------
    dtype : np.dtype
        A normalized numpy dtype.
    """
    if isinstance(dtype_spec, np.dtype):
        return dtype_spec

    try:
        return DTYPE_MAPPING[dtype_spec]
    except KeyError:
        raise ValueError(
            f"Unknown dtype specification: {dtype_spec!r}.\n"
            f"Valid specifications are: {sorted(str(k) for k in DTYPE_MAPPING.keys())}"
        )


def CustomData(
    name: str,
    columns: Dict[str, Union[type, str, np.dtype]],
    missing_values: Optional[Dict[str, Any]] = None,
    domain: Domain = GENERIC,
    metadata: Optional[Dict[str, Dict[str, Any]]] = None,
    currency_aware: Optional[Dict[str, bool]] = None,
    doc: Optional[str] = None,
) -> type:
    """
    Create a custom Pipeline DataSet with the specified columns.

    This is a factory function that dynamically creates a DataSet subclass,
    making it easy to define custom data sources for use in Pipeline expressions.

    Parameters
    ----------
    name : str
        Name for the new DataSet class.
    columns : dict[str -> dtype]
        Dictionary mapping column names to their data types.
        Data types can be specified as:
        - Python types: float, int, bool, str, object
        - String names: 'float', 'int', 'bool', 'str', 'object', 'datetime'
        - NumPy dtypes: np.float64, np.int64, np.bool_, np.object_, etc.
    missing_values : dict[str -> value], optional
        Dictionary mapping column names to their missing values.
        Required for integer columns. If not provided:
        - float columns use NaN
        - bool columns use False
        - object columns use None
        - int columns require explicit specification
    domain : zipline.pipeline.domain.Domain, optional
        Domain for this dataset. Defaults to GENERIC (works with any domain).
    metadata : dict[str -> dict], optional
        Dictionary mapping column names to metadata dictionaries.
    currency_aware : dict[str -> bool], optional
        Dictionary mapping column names to whether they contain currency data.
        Currency-aware columns must have float64 dtype.
    doc : str, optional
        Documentation string for the dataset class.

    Returns
    -------
    dataset_class : type
        A new DataSet subclass with the specified columns.

    Examples
    --------
    Create a simple custom dataset with float columns:

    >>> from zipline.pipeline.data import CustomData
    >>> MyData = CustomData(
    ...     'MyData',
    ...     columns={
    ...         'revenue': float,
    ...         'earnings': float,
    ...         'growth_rate': float,
    ...     }
    ... )
    >>> # Use in a pipeline
    >>> from zipline.pipeline import Pipeline
    >>> pipe = Pipeline(
    ...     columns={
    ...         'revenue': MyData.revenue.latest,
    ...         'high_growth': MyData.growth_rate.latest > 0.1,
    ...     }
    ... )

    Create a dataset with mixed column types:

    >>> CompanyData = CustomData(
    ...     'CompanyData',
    ...     columns={
    ...         'market_cap': float,
    ...         'sector': int,
    ...         'ticker': str,
    ...         'is_listed': bool,
    ...     },
    ...     missing_values={
    ...         'sector': -1,  # Required for int columns
    ...     }
    ... )

    Create a domain-specific dataset:

    >>> from zipline.pipeline.domain import US_EQUITIES
    >>> USCustomData = CustomData(
    ...     'USCustomData',
    ...     columns={'metric': float},
    ...     domain=US_EQUITIES
    ... )

    Create a currency-aware dataset:

    >>> PriceData = CustomData(
    ...     'PriceData',
    ...     columns={
    ...         'price_usd': float,
    ...         'price_local': float,
    ...     },
    ...     currency_aware={
    ...         'price_usd': False,   # Already in USD
    ...         'price_local': True,  # Needs conversion
    ...     }
    ... )

    Notes
    -----
    - The returned class is a proper DataSet subclass and can be further
      specialized or subclassed.
    - Column names must be valid Python identifiers.
    - Integer columns require explicit missing values because NumPy has no
      native NaN representation for integers.
    - Currency-aware columns enable automatic currency conversion via the
      ``.fx()`` method.
    """
    if missing_values is None:
        missing_values = {}

    if metadata is None:
        metadata = {}

    if currency_aware is None:
        currency_aware = {}

    # Build the class dictionary with Column objects
    class_dict = {}

    for col_name, dtype_spec in columns.items():
        # Normalize the dtype
        dtype = _normalize_dtype(dtype_spec)

        # Get missing value for this column
        missing_value = missing_values.get(col_name)

        # Get metadata for this column
        col_metadata = metadata.get(col_name)

        # Get currency awareness for this column
        col_currency_aware = currency_aware.get(col_name, False)

        # Create the Column object
        if missing_value is None:
            # Let Column determine the default missing value
            class_dict[col_name] = Column(
                dtype=dtype,
                metadata=col_metadata,
                currency_aware=col_currency_aware,
            )
        else:
            class_dict[col_name] = Column(
                dtype=dtype,
                missing_value=missing_value,
                metadata=col_metadata,
                currency_aware=col_currency_aware,
            )

    # Set the domain
    class_dict["domain"] = domain

    # Set the docstring
    if doc is not None:
        class_dict["__doc__"] = doc
    else:
        # Generate a default docstring
        column_list = "\n    ".join(
            f"{name} : {columns[name]}" for name in sorted(columns.keys())
        )
        class_dict["__doc__"] = f"""
{name} - Custom Pipeline DataSet

Columns
-------
    {column_list}

Domain
------
    {domain}

This dataset was created using CustomData().
"""

    # Create the new DataSet class
    dataset_class = DataSetMeta(name, (DataSet,), class_dict)

    return dataset_class


__all__ = [
    "CustomData",
    "DTYPE_MAPPING",
]
