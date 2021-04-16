import pandas as pd

from zipline.data.fx import DEFAULT_FX_RATE
from zipline.testing.predicates import assert_equal
import zipline.testing.fixtures as zp_fixtures
import pytest


class InMemoryFXReaderTestCase(zp_fixtures._FXReaderTestCase):
    @property
    def reader(self):
        return self.in_memory_fx_rate_reader


class HDF5FXReaderTestCase(zp_fixtures.WithTmpDir, zp_fixtures._FXReaderTestCase):
    @classmethod
    def init_class_fixtures(cls):
        super(HDF5FXReaderTestCase, cls).init_class_fixtures()
        path = cls.tmpdir.getpath("fx_rates.h5")
        cls.h5_fx_reader = cls.write_h5_fx_rates(path)

    @property
    def reader(self):
        return self.h5_fx_reader


class FastGetLocTestCase(zp_fixtures.ZiplineTestCase):
    def test_fast_get_loc_ffilled(self):
        dts = pd.to_datetime(
            [
                "2014-01-02",
                "2014-01-03",
                # Skip 2014-01-04
                "2014-01-05",
                "2014-01-06",
            ]
        )

        for dt in pd.date_range("2014-01-02", "2014-01-08"):
            result = zp_fixtures.fast_get_loc_ffilled(dts.values, dt.asm8)
            expected = dts.get_loc(dt, method="ffill")
            assert_equal(result, expected)

        with pytest.raises(KeyError):
            dts.get_loc(pd.Timestamp("2014-01-01"), method="ffill")

        with pytest.raises(KeyError):
            zp_fixtures.fast_get_loc_ffilled(dts, pd.Timestamp("2014-01-01"))
