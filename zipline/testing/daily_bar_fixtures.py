#
# Copyright 2015 Quantopian, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from itertools import cycle, islice
from sys import maxsize

from parameterized import parameterized
import numpy as np
import pandas as pd
from toolz import merge
from trading_calendars import get_calendar


from zipline.testing import powerset
from zipline.testing.fixtures import (
    ZiplineTestCase,
    WithEquityDailyBarData,
    WithSeededRandomState,
)
from zipline.testing.predicates import assert_equal
from zipline.utils.classproperty import classproperty

from zipline.pipeline.loaders.synthetic import (
    asset_start,
    asset_end,
    expected_bar_value_with_holes,
    expected_bar_values_2d,
    make_bar_data,
)

# NOTE: All sids here are odd, so we can test querying for unknown sids
#       with evens.
us_info = pd.DataFrame(
    [
        # 1) The equity's trades start and end before query.
        {"start_date": "2015-06-01", "end_date": "2015-06-05"},
        # 3) The equity's trades start and end after query.
        {"start_date": "2015-06-22", "end_date": "2015-06-30"},
        # 5) The equity's data covers all dates in range (but we define
        #    a hole for it on 2015-06-17).
        {"start_date": "2015-06-02", "end_date": "2015-06-30"},
        # 7) The equity's trades start before the query start, but stop
        #    before the query end.
        {"start_date": "2015-06-01", "end_date": "2015-06-15"},
        # 9) The equity's trades start and end during the query.
        {"start_date": "2015-06-12", "end_date": "2015-06-18"},
        # 11) The equity's trades start during the query, but extend through
        #    the whole query.
        {"start_date": "2015-06-15", "end_date": "2015-06-25"},
    ],
    index=np.arange(1, 12, step=2),
    columns=["start_date", "end_date"],
).astype("datetime64[ns]")

us_info["exchange"] = "NYSE"

ca_info = pd.DataFrame(
    [
        # 13) The equity's trades start and end before query.
        {"start_date": "2015-06-01", "end_date": "2015-06-05"},
        # 15) The equity's trades start and end after query.
        {"start_date": "2015-06-22", "end_date": "2015-06-30"},
        # 17) The equity's data covers all dates in range.
        {"start_date": "2015-06-02", "end_date": "2015-06-30"},
        # 19) The equity's trades start before the query start, but stop
        #    before the query end.
        {"start_date": "2015-06-01", "end_date": "2015-06-15"},
        # 21) The equity's trades start and end during the query.
        {"start_date": "2015-06-12", "end_date": "2015-06-18"},
        # 23) The equity's trades start during the query, but extend through
        #    the whole query.
        {"start_date": "2015-06-15", "end_date": "2015-06-25"},
    ],
    index=np.arange(13, 24, step=2),
    columns=["start_date", "end_date"],
).astype("datetime64[ns]")

ca_info["exchange"] = "TSX"

EQUITY_INFO = pd.concat([us_info, ca_info])
EQUITY_INFO["symbol"] = [chr(ord("A") + x) for x in range(len(EQUITY_INFO))]

TEST_CALENDAR_START = pd.Timestamp("2015-06-01", tz="UTC")
TEST_CALENDAR_STOP = pd.Timestamp("2015-06-30", tz="UTC")

TEST_QUERY_START = pd.Timestamp("2015-06-10", tz="UTC")
TEST_QUERY_STOP = pd.Timestamp("2015-06-19", tz="UTC")


HOLES = {
    "US": {5: (pd.Timestamp("2015-06-17", tz="UTC"),)},
    "CA": {17: (pd.Timestamp("2015-06-17", tz="UTC"),)},
}


class _DailyBarsTestCase(
    WithEquityDailyBarData,
    WithSeededRandomState,
    ZiplineTestCase,
):
    EQUITY_DAILY_BAR_START_DATE = TEST_CALENDAR_START
    EQUITY_DAILY_BAR_END_DATE = TEST_CALENDAR_STOP

    # The country under which these tests should be run.
    DAILY_BARS_TEST_QUERY_COUNTRY_CODE = "US"

    # Currencies to use for assets in these tests.
    DAILY_BARS_TEST_CURRENCIES = {"US": ["USD"], "CA": ["USD", "CAD"]}

    @classmethod
    def init_class_fixtures(cls):
        super(_DailyBarsTestCase, cls).init_class_fixtures()

        cls.sessions = cls.trading_calendar.sessions_in_range(
            cls.trading_calendar.minute_to_session_label(TEST_CALENDAR_START),
            cls.trading_calendar.minute_to_session_label(TEST_CALENDAR_STOP),
        )

    @classmethod
    def make_equity_info(cls):
        return EQUITY_INFO

    @classmethod
    def make_exchanges_info(cls, *args, **kwargs):
        return pd.DataFrame({"exchange": ["NYSE", "TSX"], "country_code": ["US", "CA"]})

    @classmethod
    def make_equity_daily_bar_data(cls, country_code, sids):
        # Create the data for all countries.
        return make_bar_data(
            EQUITY_INFO.loc[list(sids)],
            cls.equity_daily_bar_days,
            holes=merge(HOLES.values()),
        )

    @classmethod
    def make_equity_daily_bar_currency_codes(cls, country_code, sids):
        # Evenly distribute choices among ``sids``.
        choices = cls.DAILY_BARS_TEST_CURRENCIES[country_code]
        codes = list(islice(cycle(choices), len(sids)))
        return pd.Series(index=sids, data=np.array(codes, dtype=object))

    @classproperty
    def holes(cls):
        return HOLES[cls.DAILY_BARS_TEST_QUERY_COUNTRY_CODE]

    @property
    def assets(self):
        return list(
            self.asset_finder.equities_sids_for_country_code(
                self.DAILY_BARS_TEST_QUERY_COUNTRY_CODE
            )
        )

    def trading_days_between(self, start, end):
        return self.sessions[self.sessions.slice_indexer(start, end)]

    def asset_start(self, asset_id):
        return asset_start(EQUITY_INFO, asset_id)

    def asset_end(self, asset_id):
        return asset_end(EQUITY_INFO, asset_id)

    def dates_for_asset(self, asset_id):
        start, end = self.asset_start(asset_id), self.asset_end(asset_id)
        return self.trading_days_between(start, end)



    def _check_read_results(self, columns, assets, start_date, end_date):
        results = self.daily_bar_reader.load_raw_arrays(
            columns,
            start_date,
            end_date,
            assets,
        )
        dates = self.trading_days_between(start_date, end_date)
        for column, result in zip(columns, results):
            assert_equal(
                result,
                expected_bar_values_2d(
                    dates,
                    assets,
                    EQUITY_INFO.loc[self.assets],
                    column,
                    holes=self.holes,
                ),
            )

