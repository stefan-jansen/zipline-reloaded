#
# Copyright 2018 Quantopian, Inc.
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

from datetime import time

import pandas as pd
from pytz import timezone
from pandas.tseries.holiday import Holiday

from .exchange_calendar import HolidayCalendar
from .precomputed_exchange_calendar import PrecomputedExchangeCalendar
from .xkrx_holidays import (
    krx_regular_holiday_rules,
    precomputed_krx_holidays,
    precomputed_csat_days,
)
from .pandas_extensions.korean_holiday import next_business_day


class XKRXExchangeCalendar(PrecomputedExchangeCalendar):
    """
    Calendar for the Korea exchange, and the primary calendar for
    the country of South Korea.

    Open Time: 9:00 AM, KST (Korean Standard Time)
    Close Time: 3:30 PM, KST (Korean Standard Time)

    NOTE: Korea observes Standard Time year-round.

    Due to the complexity around the Korean holidays, we are hardcoding
    a list of holidays covering 1986-2019, inclusive.

    Regularly-Observed Holidays:
    - Seollal (New Year's Day)
    - Independence Movement Day
    - Labor Day
    - Buddha's Birthday
    - Memorial Day
    - Provincial Election Day
    - Liberation Day
    - Chuseok (Korean Thanksgiving)
    - National Foundation Day
    - Christmas Day
    - End of Year Holiday

    NOTE: Hangeul Day became a national holiday in 2013
    - Hangeul Proclamation Day
    """

    name = "XKRX"

    tz = timezone("Asia/Seoul")

    # KRX schedule change history
    # https://blog.naver.com/daishin_blog/220724111002

    # 1956-03-03: 0930~1130, 1330~1530
    # 1978-04-??: 1000~1200, 1330~1530
    # 1986-04-??: 0940~1200, 1320~1520
    # 1987-03-??: 0940~1140, 1320~1520
    # 1995-01-01: 0930~1130, 1300~1500
    # 1998-12-07: 0900~1200, 1300~1500
    # 2000-05-22: 0900~1500
    # 2016-08-01: 0900~1530

    # Break time disappears since 2000-05-22
    # https://www.donga.com/news/Economy/article/all/20000512/7534650/1

    # Closing time became 30mins late since 2016-08-01
    # https://biz.chosun.com/site/data/html_dir/2016/07/24/2016072400309.html

    open_times = (
        (None, time(9, 30)),
        (pd.Timestamp("1978-04-01"), time(10, 0)),
        (pd.Timestamp("1986-04-01"), time(9, 40)),
        (pd.Timestamp("1995-01-01"), time(9, 30)),
        (pd.Timestamp("1998-12-07"), time(9, 0)),
    )
    break_start_times = (
        (None, time(11, 30)),
        (pd.Timestamp("1978-04-01"), time(12, 0)),
        (pd.Timestamp("1987-03-01"), time(11, 40)),
        (pd.Timestamp("1995-01-01"), time(11, 30)),
        (pd.Timestamp("1998-12-07"), time(12, 0)),
        (pd.Timestamp("2000-05-22"), None),
    )
    break_end_times = (
        (None, time(13, 30)),
        (pd.Timestamp("1986-04-01"), time(13, 20)),
        (pd.Timestamp("1995-01-01"), time(13, 0)),
        (pd.Timestamp("2000-05-22"), None),
    )
    close_times = (
        (None, time(15, 30)),
        (pd.Timestamp("1986-04-01"), time(15, 20)),
        (pd.Timestamp("1995-01-01"), time(15, 0)),
        (pd.Timestamp("2016-08-01"), time(15, 30)),
    )

    # Saterday became holiday since 1998-12-07
    # https://www.hankyung.com/finance/article/1998080301961

    weekmask = "1111100"

    @property
    def special_weekmasks(self):
        return [
            (None, pd.Timestamp("1998-12-06"), "1111110"),
        ]

    @property
    def _earliest_precomputed_year(self) -> int:
        return 1956

    @property
    def _latest_precomputed_year(self) -> int:
        return 2050

    # KRX regular and precomputed adhoc holidays

    @property
    def regular_holidays(self):
        return HolidayCalendar(krx_regular_holiday_rules)

    @property
    def precomputed_holidays(self) -> pd.DatetimeIndex:
        return precomputed_krx_holidays.tolist()

    # The first business day of each year:
    #  opening schedule is delayed by an hour.

    @property
    def special_offsets(self):
        return [
            (
                pd.Timedelta(1, unit="h"),
                None,
                None,
                None,
                HolidayCalendar(
                    [
                        Holiday(
                            "First Business Day of Year",
                            month=1,
                            day=1,
                            observance=next_business_day,
                        )
                    ]
                ),
            ),
        ]

    # Every year's CSAT day, all schedules are delayed by:
    #  before 1998-11-18: 30 minutes
    #  after  1998-11-18: 1 hour

    @property
    def special_offsets_adhoc(self):
        return [
            (
                pd.Timedelta(30, unit="m"),
                pd.Timedelta(30, unit="m"),
                pd.Timedelta(30, unit="m"),
                pd.Timedelta(30, unit="m"),
                precomputed_csat_days[
                    precomputed_csat_days.slice_indexer("1993-08-20", "1998-11-17")
                ],
            ),
            (
                pd.Timedelta(1, unit="h"),
                pd.Timedelta(1, unit="h"),
                pd.Timedelta(1, unit="h"),
                pd.Timedelta(1, unit="h"),
                precomputed_csat_days[
                    precomputed_csat_days.slice_indexer("1998-11-18", None)
                ],
            ),
        ]


class PrecomputedXKRXExchangeCalendar(PrecomputedExchangeCalendar):
    """
    Calendar for the Korea exchange, and the primary calendar for
    the country of South Korea.

    Open Time: 9:00 AM, KST (Korean Standard Time)
    Close Time: 3:30 PM, KST (Korean Standard Time)

    NOTE: Korea observes Standard Time year-round.

    Due to the complexity around the Korean holidays, we are hardcoding
    a list of holidays covering 1986-2019, inclusive.

    Regularly-Observed Holidays:
    - Seollal (New Year's Day)
    - Independence Movement Day
    - Labor Day
    - Buddha's Birthday
    - Memorial Day
    - Provincial Election Day
    - Liberation Day
    - Chuseok (Korean Thanksgiving)
    - National Foundation Day
    - Christmas Day
    - End of Year Holiday

    NOTE: Hangeul Day became a national holiday in 2013
    - Hangeul Proclamation Day
    """

    name = "XKRX"

    tz = timezone("Asia/Seoul")

    open_times = ((None, time(9)),)
    close_times = ((None, time(15, 30)),)

    @property
    def precomputed_holidays(self):
        return precomputed_krx_holidays
