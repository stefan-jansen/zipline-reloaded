"""
Tests for CustomData factory and MultiColumnDataFrameLoader.
"""

import numpy as np
import pandas as pd
import pytest
from numpy.testing import assert_array_equal

from zipline.pipeline.data import Column, CustomData, DataSet
from zipline.pipeline.domain import GENERIC, US_EQUITIES
from zipline.pipeline.loaders import MultiColumnDataFrameLoader
from zipline.utils.calendar_utils import get_calendar
from zipline.utils.numpy_utils import (
    bool_dtype,
    float64_dtype,
    int64_dtype,
    object_dtype,
)


class TestCustomDataFactory:
    """Tests for the CustomData factory function."""

    def test_basic_creation(self):
        """Test creating a simple custom dataset."""
        MyData = CustomData(
            "MyData",
            columns={
                "metric1": float,
                "metric2": float,
            },
        )

        # Check it's a DataSet subclass
        assert issubclass(MyData, DataSet)
        assert MyData.__name__ == "MyData"

        # Check columns exist and have correct types
        assert hasattr(MyData, "metric1")
        assert hasattr(MyData, "metric2")

        assert MyData.metric1.dtype == float64_dtype
        assert MyData.metric2.dtype == float64_dtype

    def test_mixed_types(self):
        """Test creating a dataset with mixed column types."""
        MixedData = CustomData(
            "MixedData",
            columns={
                "price": float,
                "sector": int,
                "ticker": str,
                "active": bool,
            },
            missing_values={
                "sector": -1,
            },
        )

        assert MixedData.price.dtype == float64_dtype
        assert MixedData.sector.dtype == int64_dtype
        assert MixedData.sector.missing_value == -1
        assert MixedData.ticker.dtype == object_dtype
        assert MixedData.active.dtype == bool_dtype

    def test_string_dtype_specs(self):
        """Test that string dtype specifications work."""
        StringData = CustomData(
            "StringData",
            columns={
                "col1": "float",
                "col2": "int",
                "col3": "bool",
                "col4": "str",
            },
            missing_values={"col2": 0},
        )

        assert StringData.col1.dtype == float64_dtype
        assert StringData.col2.dtype == int64_dtype
        assert StringData.col3.dtype == bool_dtype
        assert StringData.col4.dtype == object_dtype

    def test_numpy_dtype_specs(self):
        """Test that numpy dtype specifications work."""
        NumpyData = CustomData(
            "NumpyData",
            columns={
                "col1": np.dtype("float64"),
                "col2": np.dtype("int64"),
                "col3": np.dtype("bool"),
            },
            missing_values={"col2": -999},
        )

        assert NumpyData.col1.dtype == float64_dtype
        assert NumpyData.col2.dtype == int64_dtype
        assert NumpyData.col3.dtype == bool_dtype

    def test_domain_specification(self):
        """Test specifying a domain for the dataset."""
        USData = CustomData(
            "USData",
            columns={"metric": float},
            domain=US_EQUITIES,
        )

        assert USData.domain == US_EQUITIES

    def test_generic_domain_default(self):
        """Test that GENERIC domain is the default."""
        GenericData = CustomData(
            "GenericData",
            columns={"metric": float},
        )

        assert GenericData.domain == GENERIC

    def test_column_metadata(self):
        """Test adding metadata to columns."""
        MetaData = CustomData(
            "MetaData",
            columns={"metric": float},
            metadata={
                "metric": {"source": "bloomberg", "frequency": "daily"},
            },
        )

        metadata = MetaData.metric.metadata
        assert metadata["source"] == "bloomberg"
        assert metadata["frequency"] == "daily"

    def test_currency_aware_columns(self):
        """Test creating currency-aware columns."""
        CurrencyData = CustomData(
            "CurrencyData",
            columns={
                "price_usd": float,
                "price_local": float,
            },
            currency_aware={
                "price_local": True,
            },
        )

        assert not CurrencyData.price_usd.currency_aware
        assert CurrencyData.price_local.currency_aware

    def test_custom_docstring(self):
        """Test setting a custom docstring."""
        doc = "This is my custom dataset."
        DocData = CustomData(
            "DocData",
            columns={"metric": float},
            doc=doc,
        )

        assert doc in DocData.__doc__

    def test_invalid_dtype(self):
        """Test that invalid dtype raises an error."""
        with pytest.raises(ValueError, match="Unknown dtype specification"):
            CustomData(
                "BadData",
                columns={"metric": "invalid_type"},
            )

    def test_column_access(self):
        """Test that columns can be accessed and used."""
        TestData = CustomData(
            "TestData",
            columns={
                "col1": float,
                "col2": float,
            },
        )

        # Should be able to access columns
        col1 = TestData.col1
        col2 = TestData.col2

        # Should be able to get .latest
        latest1 = col1.latest
        latest2 = col2.latest

        # Columns should know their dataset
        assert col1.dataset == TestData
        assert col2.dataset == TestData

    def test_specialization(self):
        """Test that custom datasets can be specialized."""
        GenericData = CustomData(
            "GenericData",
            columns={"metric": float},
            domain=GENERIC,
        )

        # Should be able to specialize to a specific domain
        USData = GenericData.specialize(US_EQUITIES)

        assert USData.domain == US_EQUITIES
        assert GenericData.domain == GENERIC

        # Columns should work on specialized version
        assert hasattr(USData, "metric")

    def test_multiple_instances(self):
        """Test creating multiple independent custom datasets."""
        Data1 = CustomData("Data1", columns={"a": float})
        Data2 = CustomData("Data2", columns={"b": float})

        assert Data1 != Data2
        assert hasattr(Data1, "a")
        assert not hasattr(Data1, "b")
        assert hasattr(Data2, "b")
        assert not hasattr(Data2, "a")


class TestMultiColumnDataFrameLoader:
    """Tests for MultiColumnDataFrameLoader."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test data."""
        self.trading_day = get_calendar("NYSE").day
        self.nsids = 5
        self.ndates = 20
        self.sids = pd.Index(range(self.nsids), dtype="int64")
        self.dates = pd.date_range(
            start="2014-01-02",
            freq=self.trading_day,
            periods=self.ndates,
        )
        self.mask = np.ones((len(self.dates), len(self.sids)), dtype=bool)

        # Create a custom dataset
        self.TestData = CustomData(
            "TestData",
            columns={
                "metric1": float,
                "metric2": float,
                "metric3": int,
            },
            missing_values={
                "metric3": -1,
            },
        )

    def test_load_from_dict(self):
        """Test loading data from a dict of DataFrames."""
        # Create test data
        data1 = np.arange(100).reshape(self.ndates, self.nsids).astype(float)
        data2 = (
            np.arange(100, 200).reshape(self.ndates, self.nsids).astype(float)
        )
        data3 = np.arange(200, 300).reshape(self.ndates, self.nsids).astype(int)

        df1 = pd.DataFrame(data1, index=self.dates, columns=self.sids)
        df2 = pd.DataFrame(data2, index=self.dates, columns=self.sids)
        df3 = pd.DataFrame(data3, index=self.dates, columns=self.sids)

        loader = MultiColumnDataFrameLoader(
            self.TestData,
            {
                self.TestData.metric1: df1,
                self.TestData.metric2: df2,
                self.TestData.metric3: df3,
            },
        )

        # Load all columns
        result = loader.load_adjusted_array(
            US_EQUITIES,
            [self.TestData.metric1, self.TestData.metric2, self.TestData.metric3],
            self.dates,
            self.sids,
            self.mask,
        )

        # Check results
        assert len(result) == 3
        assert_array_equal(result[self.TestData.metric1].data, data1)
        assert_array_equal(result[self.TestData.metric2].data, data2)
        assert_array_equal(result[self.TestData.metric3].data, data3)

    def test_load_subset_of_dates_and_sids(self):
        """Test loading a subset of dates and sids."""
        data = np.arange(100).reshape(self.ndates, self.nsids).astype(float)
        df = pd.DataFrame(data, index=self.dates, columns=self.sids)

        loader = MultiColumnDataFrameLoader(
            self.TestData,
            {self.TestData.metric1: df},
        )

        # Load a subset
        dates_slice = slice(5, 15)
        sids_slice = slice(1, 4)

        result = loader.load_adjusted_array(
            US_EQUITIES,
            [self.TestData.metric1],
            self.dates[dates_slice],
            self.sids[sids_slice],
            self.mask[dates_slice, sids_slice],
        )

        expected = data[dates_slice, sids_slice]
        assert_array_equal(result[self.TestData.metric1].data, expected)

    def test_missing_dates(self):
        """Test handling of dates not in the baseline."""
        data = np.arange(50).reshape(10, self.nsids).astype(float)
        df = pd.DataFrame(data, index=self.dates[:10], columns=self.sids)

        loader = MultiColumnDataFrameLoader(
            self.TestData,
            {self.TestData.metric1: df},
        )

        # Request dates beyond what we have
        result = loader.load_adjusted_array(
            US_EQUITIES,
            [self.TestData.metric1],
            self.dates[8:12],  # Partially overlapping
            self.sids,
            self.mask[8:12, :],
        )

        loaded = result[self.TestData.metric1].data

        # First two rows should have data
        assert_array_equal(loaded[:2, :], data[8:10, :])

        # Last two rows should be NaN (missing value for float)
        assert np.all(np.isnan(loaded[2:, :]))

    def test_missing_sids(self):
        """Test handling of sids not in the baseline."""
        data = np.arange(60).reshape(self.ndates, 3).astype(float)
        df = pd.DataFrame(data, index=self.dates, columns=self.sids[:3])

        loader = MultiColumnDataFrameLoader(
            self.TestData,
            {self.TestData.metric1: df},
        )

        # Request more sids than we have
        result = loader.load_adjusted_array(
            US_EQUITIES,
            [self.TestData.metric1],
            self.dates,
            self.sids,  # Request all 5 sids
            self.mask,
        )

        loaded = result[self.TestData.metric1].data

        # First three columns should have data
        assert_array_equal(loaded[:, :3], data)

        # Last two columns should be NaN
        assert np.all(np.isnan(loaded[:, 3:]))

    def test_wrong_column(self):
        """Test that loading wrong column raises an error."""
        data = np.arange(100).reshape(self.ndates, self.nsids).astype(float)
        df = pd.DataFrame(data, index=self.dates, columns=self.sids)

        loader = MultiColumnDataFrameLoader(
            self.TestData,
            {self.TestData.metric1: df},
        )

        # Try to load metric2, which we didn't provide data for
        with pytest.raises(ValueError, match="No data provided"):
            loader.load_adjusted_array(
                US_EQUITIES,
                [self.TestData.metric2],
                self.dates,
                self.sids,
                self.mask,
            )

    def test_wrong_dataset(self):
        """Test that loading from wrong dataset raises an error."""
        OtherData = CustomData("OtherData", columns={"other": float})

        data = np.arange(100).reshape(self.ndates, self.nsids).astype(float)
        df = pd.DataFrame(data, index=self.dates, columns=self.sids)

        loader = MultiColumnDataFrameLoader(
            self.TestData,
            {self.TestData.metric1: df},
        )

        # Try to load from a different dataset
        with pytest.raises(ValueError, match="does not belong to dataset"):
            loader.load_adjusted_array(
                US_EQUITIES,
                [OtherData.other],
                self.dates,
                self.sids,
                self.mask,
            )

    def test_dtype_preservation(self):
        """Test that dtypes are preserved correctly."""
        data1 = np.arange(100).reshape(self.ndates, self.nsids).astype(float)
        data3 = np.arange(200, 300).reshape(self.ndates, self.nsids).astype(int)

        df1 = pd.DataFrame(data1, index=self.dates, columns=self.sids)
        df3 = pd.DataFrame(data3, index=self.dates, columns=self.sids)

        loader = MultiColumnDataFrameLoader(
            self.TestData,
            {
                self.TestData.metric1: df1,
                self.TestData.metric3: df3,
            },
        )

        result = loader.load_adjusted_array(
            US_EQUITIES,
            [self.TestData.metric1, self.TestData.metric3],
            self.dates,
            self.sids,
            self.mask,
        )

        assert result[self.TestData.metric1].data.dtype == float64_dtype
        assert result[self.TestData.metric3].data.dtype == int64_dtype

    def test_missing_value_handling(self):
        """Test that missing values are handled correctly."""
        # Create data with gaps
        data = np.arange(100).reshape(self.ndates, self.nsids).astype(float)
        df = pd.DataFrame(data, index=self.dates, columns=self.sids)

        loader = MultiColumnDataFrameLoader(
            self.TestData,
            {self.TestData.metric1: df},
        )

        # Create a mask that excludes some values
        mask = self.mask.copy()
        mask[5:10, 2:4] = False

        result = loader.load_adjusted_array(
            US_EQUITIES,
            [self.TestData.metric1],
            self.dates,
            self.sids,
            mask,
        )

        loaded = result[self.TestData.metric1].data

        # Masked values should be NaN
        assert np.all(np.isnan(loaded[5:10, 2:4]))

        # Unmasked values should be preserved
        assert_array_equal(loaded[0:5, :], data[0:5, :])


class TestCustomDataIntegration:
    """Integration tests for CustomData with pipelines."""

    def test_custom_data_in_pipeline(self):
        """Test that custom data can be used in a pipeline."""
        from zipline.pipeline import Pipeline

        MyData = CustomData(
            "MyData",
            columns={
                "value1": float,
                "value2": float,
            },
        )

        # Should be able to create a pipeline with custom data
        pipe = Pipeline(
            columns={
                "val1": MyData.value1.latest,
                "val2": MyData.value2.latest,
                "sum": MyData.value1.latest + MyData.value2.latest,
            }
        )

        # Check that columns are correctly set up
        assert "val1" in pipe.columns
        assert "val2" in pipe.columns
        assert "sum" in pipe.columns

    def test_custom_data_with_factors(self):
        """Test using custom data with factors."""
        from zipline.pipeline.factors import SimpleMovingAverage

        PriceData = CustomData(
            "PriceData",
            columns={"price": float},
        )

        # Should be able to create factors from custom data
        sma = SimpleMovingAverage(inputs=[PriceData.price], window_length=10)

        assert sma is not None
