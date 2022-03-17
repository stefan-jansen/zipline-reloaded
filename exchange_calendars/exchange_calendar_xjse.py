#
# Copyright 2019 Quantopian, Inc.
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

from pandas import Timestamp
from pandas.tseries.holiday import Easter, GoodFriday, Holiday, sunday_to_monday
from pandas.tseries.offsets import Day
from pytz import timezone

from .common_holidays import new_years_day
from .exchange_calendar import HolidayCalendar, ExchangeCalendar


class XJSEExchangeCalendar(ExchangeCalendar):
    """
    Exchange calendar for the Johannesburg Stock Exchange (XJSE).

    Open Time: 09:00, SAST
    Close Time: 17:00, SAST

    Regularly-Observed Holidays:
    - New Year's Day (Jan 1)
    - Human Rights Day (Mar 31)
    - Good Friday (Friday before Easter)
    - Family Day (Monday after Easter)
    - Freedom Day (Apr 27)
    - Workers' Day (a.k.a. Labour Day, May 1)
    - Youth Day (Jun 16)
    - National Women's Day (Aug 19)
    - Heritage Day (Sep 24)
    - Day of Reconciliation (Dec 19)
    - Christmas (Dec 25)
    - Day of Goodwill (Dec 26)

    If a holiday falls on a Saturday, it is not observed.
    If a holiday falls on a Sunday, it is observed on Monday.

    If two holiday observations occur on the same trading day, the
    following trading day may or may not be declared a holiday: if so,
    it should be added to ``adhoc_holidays``.
    """

    name = "XJSE"

    tz = timezone("Africa/Johannesburg")

    open_times = ((None, time(9)),)

    close_times = ((None, time(17, 00)),)

    @property
    def regular_holidays(self):
        return HolidayCalendar(
            [
                new_years_day(
                    observance=sunday_to_monday,
                ),
                Holiday(
                    "Human Rights Day",
                    month=3,
                    day=21,
                    observance=sunday_to_monday,
                ),
                GoodFriday,
                Holiday(
                    "Family Day",
                    month=1,
                    day=1,
                    offset=[Easter(), Day(1)],
                ),
                Holiday(
                    "Freedom Day",
                    month=4,
                    day=27,
                    observance=sunday_to_monday,
                ),
                Holiday(
                    "Workers' Day",
                    month=5,
                    day=1,
                    observance=sunday_to_monday,
                ),
                Holiday(
                    "Youth Day",
                    month=6,
                    day=16,
                    observance=sunday_to_monday,
                ),
                Holiday(
                    "National Women's Day",
                    month=8,
                    day=9,
                    observance=sunday_to_monday,
                ),
                Holiday(
                    "Heritage Day",
                    month=9,
                    day=24,
                    observance=sunday_to_monday,
                ),
                Holiday(
                    "Day of Reconciliation",
                    month=12,
                    day=16,
                    observance=sunday_to_monday,
                ),
                Holiday(
                    "Christmas",
                    month=12,
                    day=25,
                    observance=sunday_to_monday,
                ),
                Holiday(
                    "Day of Goodwill",
                    month=12,
                    day=26,
                    observance=sunday_to_monday,
                ),
            ]
        )

    @property
    def adhoc_holidays(self):
        return [
            Timestamp(date)
            for date in [
                # Election holidays
                "2004-04-14",
                "2006-03-01",
                "2009-04-22",
                "2011-05-18",
                "2014-05-07",
                "2016-08-03",
                "2019-05-08",
                # In 2008, Human Rights Day fell on the same day as Good
                # Friday (March 21), so the "Bridge Public Holiday" was
                # observed on May 2.
                "2008-05-02",
                # In 2011 and 2016, Christmas fell on Sunday, which would
                # ordinarily cause it to be observed on Monday; but Day of
                # Goodwill fell on Monday, which resulted in only 11
                # scheduled holidays for the year instead of the usual 12.
                # In these years, the 27th was declared a bonus holiday: it
                # may or may not be repeated in 2022 and onward.
                "2011-12-27",
                "2016-12-27",
            ]
        ]
