"""
Tests for database-backed custom data.
"""

import numpy as np
import pandas as pd
import pytest
import tempfile
import shutil
from pathlib import Path

from zipline.pipeline.data import (
    create_custom_db,
    drop_custom_db,
    from_db,
    get_custom_db_info,
    insert_custom_data,
    list_custom_dbs,
    query_custom_data,
    CustomDatabaseError,
)
from zipline.pipeline.loaders import DatabaseCustomDataLoader


class TestCustomDatabase:
    """Tests for custom database creation and management."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test database directory."""
        self.db_dir = tempfile.mkdtemp()
        yield
        # Cleanup
        shutil.rmtree(self.db_dir, ignore_errors=True)

    def test_create_database(self):
        """Test creating a custom database."""
        db_path = create_custom_db(
            'test-db',
            columns={'metric1': float, 'metric2': float},
            db_dir=self.db_dir,
        )

        assert Path(db_path).exists()
        assert 'test-db.db' in db_path

    def test_create_database_invalid_code(self):
        """Test that invalid database codes raise errors."""
        with pytest.raises(ValueError, match="lowercase"):
            create_custom_db(
                'Test-DB',  # Uppercase not allowed
                columns={'metric': float},
                db_dir=self.db_dir,
            )

        with pytest.raises(ValueError, match="lowercase"):
            create_custom_db(
                'test_db',  # Underscore not allowed
                columns={'metric': float},
                db_dir=self.db_dir,
            )

    def test_create_database_invalid_column_name(self):
        """Test that invalid column names raise errors."""
        with pytest.raises(ValueError, match="start with a letter"):
            create_custom_db(
                'test-db',
                columns={'1metric': float},  # Starts with number
                db_dir=self.db_dir,
            )

        with pytest.raises(ValueError, match="start with a letter"):
            create_custom_db(
                'test-db',
                columns={'metric-1': float},  # Contains hyphen
                db_dir=self.db_dir,
            )

    def test_create_duplicate_database(self):
        """Test that creating duplicate database raises error."""
        create_custom_db(
            'test-db',
            columns={'metric': float},
            db_dir=self.db_dir,
        )

        with pytest.raises(CustomDatabaseError, match="already exists"):
            create_custom_db(
                'test-db',
                columns={'metric': float},
                db_dir=self.db_dir,
            )

    def test_list_databases_empty(self):
        """Test listing databases when none exist."""
        dbs = list_custom_dbs(db_dir=self.db_dir)
        assert dbs == []

    def test_list_databases(self):
        """Test listing databases."""
        create_custom_db(
            'db1',
            columns={'metric1': float},
            db_dir=self.db_dir,
        )
        create_custom_db(
            'db2',
            columns={'metric2': float},
            db_dir=self.db_dir,
        )

        dbs = list_custom_dbs(db_dir=self.db_dir)
        assert len(dbs) == 2
        assert {db['code'] for db in dbs} == {'db1', 'db2'}

    def test_get_database_info(self):
        """Test getting database information."""
        create_custom_db(
            'test-db',
            columns={'metric1': float, 'metric2': int},
            bar_size='1d',
            db_dir=self.db_dir,
        )

        info = get_custom_db_info('test-db', db_dir=self.db_dir)
        assert info['code'] == 'test-db'
        assert info['bar_size'] == '1d'
        assert 'metric1' in info['columns']
        assert 'metric2' in info['columns']
        assert info['row_count'] == 0  # No data inserted yet

    def test_get_nonexistent_database_info(self):
        """Test getting info for nonexistent database raises error."""
        with pytest.raises(CustomDatabaseError, match="does not exist"):
            get_custom_db_info('nonexistent', db_dir=self.db_dir)

    def test_drop_database(self):
        """Test dropping a database."""
        create_custom_db(
            'test-db',
            columns={'metric': float},
            db_dir=self.db_dir,
        )

        dbs_before = list_custom_dbs(db_dir=self.db_dir)
        assert len(dbs_before) == 1

        drop_custom_db('test-db', db_dir=self.db_dir)

        dbs_after = list_custom_dbs(db_dir=self.db_dir)
        assert len(dbs_after) == 0

    def test_drop_nonexistent_database(self):
        """Test dropping nonexistent database raises error."""
        with pytest.raises(CustomDatabaseError, match="does not exist"):
            drop_custom_db('nonexistent', db_dir=self.db_dir)


class TestCustomDataInsertion:
    """Tests for inserting data into custom databases."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test database."""
        self.db_dir = tempfile.mkdtemp()

        create_custom_db(
            'test-db',
            columns={'metric1': float, 'metric2': float},
            db_dir=self.db_dir,
        )

        self.dates = pd.bdate_range('2020-01-01', periods=10)
        self.sids = [1, 2, 3]

        yield
        shutil.rmtree(self.db_dir, ignore_errors=True)

    def test_insert_data_multiindex(self):
        """Test inserting data with MultiIndex columns."""
        # Create data with (field, sid) MultiIndex
        data = pd.DataFrame({
            ('metric1', 1): np.random.randn(10),
            ('metric1', 2): np.random.randn(10),
            ('metric1', 3): np.random.randn(10),
        }, index=self.dates)
        data.columns = pd.MultiIndex.from_tuples(
            data.columns,
            names=['field', 'sid']
        )

        insert_custom_data('test-db', data, db_dir=self.db_dir)

        # Verify data was inserted
        info = get_custom_db_info('test-db', db_dir=self.db_dir)
        assert info['row_count'] > 0

    def test_insert_data_replace_mode(self):
        """Test replacing existing data."""
        # Insert initial data
        data1 = pd.DataFrame({
            ('metric1', 1): [1.0] * 10,
        }, index=self.dates)
        data1.columns = pd.MultiIndex.from_tuples(
            data1.columns,
            names=['field', 'sid']
        )

        insert_custom_data('test-db', data1, mode='replace', db_dir=self.db_dir)

        # Insert replacement data
        data2 = pd.DataFrame({
            ('metric1', 1): [2.0] * 10,
        }, index=self.dates)
        data2.columns = pd.MultiIndex.from_tuples(
            data2.columns,
            names=['field', 'sid']
        )

        insert_custom_data('test-db', data2, mode='replace', db_dir=self.db_dir)

        # Query and verify
        result = query_custom_data(
            'test-db',
            columns=['metric1'],
            db_dir=self.db_dir,
        )

        # Should have new values
        assert result['metric1'].iloc[0] == 2.0

    def test_insert_data_update_mode(self):
        """Test updating existing data."""
        # Insert initial data
        data1 = pd.DataFrame({
            ('metric1', 1): [1.0],
        }, index=[self.dates[0]])
        data1.columns = pd.MultiIndex.from_tuples(
            data1.columns,
            names=['field', 'sid']
        )

        insert_custom_data('test-db', data1, mode='update', db_dir=self.db_dir)

        # Update with new value
        data2 = pd.DataFrame({
            ('metric1', 1): [2.0],
        }, index=[self.dates[0]])
        data2.columns = pd.MultiIndex.from_tuples(
            data2.columns,
            names=['field', 'sid']
        )

        insert_custom_data('test-db', data2, mode='update', db_dir=self.db_dir)

        # Query and verify
        result = query_custom_data(
            'test-db',
            start_date=self.dates[0],
            end_date=self.dates[0],
            sids=[1],
            columns=['metric1'],
            db_dir=self.db_dir,
        )

        assert result['metric1'].iloc[0] == 2.0

    def test_insert_nonexistent_database(self):
        """Test inserting into nonexistent database raises error."""
        data = pd.DataFrame({
            ('metric1', 1): [1.0],
        }, index=[self.dates[0]])
        data.columns = pd.MultiIndex.from_tuples(
            data.columns,
            names=['field', 'sid']
        )

        with pytest.raises(CustomDatabaseError, match="does not exist"):
            insert_custom_data('nonexistent', data, db_dir=self.db_dir)


class TestCustomDataQuery:
    """Tests for querying data from custom databases."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test database with data."""
        self.db_dir = tempfile.mkdtemp()

        create_custom_db(
            'test-db',
            columns={'metric1': float, 'metric2': float},
            db_dir=self.db_dir,
        )

        self.dates = pd.bdate_range('2020-01-01', periods=20)
        self.sids = [1, 2, 3, 4, 5]

        # Insert test data
        for field in ['metric1', 'metric2']:
            data = pd.DataFrame({
                (field, sid): np.random.randn(20)
                for sid in self.sids
            }, index=self.dates)
            data.columns = pd.MultiIndex.from_tuples(
                data.columns,
                names=['field', 'sid']
            )
            insert_custom_data('test-db', data, mode='update', db_dir=self.db_dir)

        yield
        shutil.rmtree(self.db_dir, ignore_errors=True)

    def test_query_all_data(self):
        """Test querying all data."""
        result = query_custom_data('test-db', db_dir=self.db_dir)

        assert not result.empty
        assert 'metric1' in result.columns
        assert 'metric2' in result.columns

    def test_query_date_range(self):
        """Test querying specific date range."""
        result = query_custom_data(
            'test-db',
            start_date=self.dates[5],
            end_date=self.dates[10],
            db_dir=self.db_dir,
        )

        # Check that we got the right date range
        result_dates = result.index.get_level_values('date').unique()
        assert result_dates.min() >= self.dates[5]
        assert result_dates.max() <= self.dates[10]

    def test_query_specific_sids(self):
        """Test querying specific assets."""
        result = query_custom_data(
            'test-db',
            sids=[1, 2],
            db_dir=self.db_dir,
        )

        result_sids = result.index.get_level_values('sid').unique()
        assert set(result_sids) == {1, 2}

    def test_query_specific_columns(self):
        """Test querying specific columns."""
        result = query_custom_data(
            'test-db',
            columns=['metric1'],
            db_dir=self.db_dir,
        )

        assert 'metric1' in result.columns
        assert 'metric2' not in result.columns

    def test_query_combined_filters(self):
        """Test combining multiple query filters."""
        result = query_custom_data(
            'test-db',
            start_date=self.dates[5],
            end_date=self.dates[10],
            sids=[1, 2],
            columns=['metric1'],
            db_dir=self.db_dir,
        )

        result_dates = result.index.get_level_values('date').unique()
        result_sids = result.index.get_level_values('sid').unique()

        assert result_dates.min() >= self.dates[5]
        assert result_dates.max() <= self.dates[10]
        assert set(result_sids) == {1, 2}
        assert list(result.columns) == ['metric1']


class TestFromDb:
    """Tests for from_db() functionality."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test database."""
        self.db_dir = tempfile.mkdtemp()

        create_custom_db(
            'test-db',
            columns={'metric1': float, 'metric2': int},
            bar_size='1d',
            db_dir=self.db_dir,
        )

        yield
        shutil.rmtree(self.db_dir, ignore_errors=True)

    def test_from_db_creates_dataset(self):
        """Test that from_db creates a DataSet class."""
        TestData = from_db('test-db', db_dir=self.db_dir)

        assert TestData is not None
        assert hasattr(TestData, 'metric1')
        assert hasattr(TestData, 'metric2')

    def test_from_db_dataset_has_loader(self):
        """Test that dataset has get_loader method."""
        TestData = from_db('test-db', db_dir=self.db_dir)

        assert hasattr(TestData, 'get_loader')

        loader = TestData.get_loader()
        assert isinstance(loader, DatabaseCustomDataLoader)

    def test_from_db_nonexistent_database(self):
        """Test loading from nonexistent database raises error."""
        with pytest.raises(CustomDatabaseError):
            from_db('nonexistent', db_dir=self.db_dir)

    def test_from_db_dataset_metadata(self):
        """Test that dataset has database metadata attached."""
        TestData = from_db('test-db', db_dir=self.db_dir)

        assert hasattr(TestData, '_db_code')
        assert TestData._db_code == 'test-db'
        assert hasattr(TestData, '_db_path')
        assert hasattr(TestData, '_db_dir')


class TestDatabaseLoader:
    """Tests for DatabaseCustomDataLoader."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test database with data."""
        self.db_dir = tempfile.mkdtemp()

        create_custom_db(
            'test-db',
            columns={'metric': float},
            db_dir=self.db_dir,
        )

        self.dates = pd.bdate_range('2020-01-01', periods=10)
        self.sids = [1, 2, 3]

        # Insert test data
        data = pd.DataFrame({
            ('metric', sid): np.arange(10, dtype=float) + sid
            for sid in self.sids
        }, index=self.dates)
        data.columns = pd.MultiIndex.from_tuples(
            data.columns,
            names=['field', 'sid']
        )

        insert_custom_data('test-db', data, db_dir=self.db_dir)

        # Load dataset
        self.TestData = from_db('test-db', db_dir=self.db_dir)
        self.loader = self.TestData.get_loader()

        yield
        shutil.rmtree(self.db_dir, ignore_errors=True)

    def test_loader_initialization(self):
        """Test loader initializes correctly."""
        assert self.loader.dataset == self.TestData
        assert Path(self.loader.db_path).exists()

    def test_loader_load_data(self):
        """Test loader can load data."""
        from zipline.pipeline.domain import GENERIC

        mask = np.ones((len(self.dates), len(self.sids)), dtype=bool)
        sids = pd.Index(self.sids, dtype='int64')

        result = self.loader.load_adjusted_array(
            GENERIC,
            [self.TestData.metric],
            self.dates,
            sids,
            mask,
        )

        assert self.TestData.metric in result
        array = result[self.TestData.metric]

        # Check shape
        assert array.data.shape == (len(self.dates), len(self.sids))

        # Check values
        for i, sid in enumerate(self.sids):
            expected = np.arange(10, dtype=float) + sid
            np.testing.assert_array_almost_equal(array.data[:, i], expected)
