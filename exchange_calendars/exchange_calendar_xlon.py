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
from pandas.tseries.holiday import (
    MO,
    DateOffset,
    EasterMonday,
    GoodFriday,
    Holiday,
    previous_friday,
    weekend_to_monday,
)
from pytz import timezone

from .common_holidays import (
    boxing_day,
    christmas,
    new_years_day,
    weekend_boxing_day,
    weekend_christmas,
)
from .exchange_calendar import HolidayCalendar, ExchangeCalendar

# Regular Holidays
# ----------------
# New Year's Day
LSENewYearsDay = new_years_day(observance=weekend_to_monday)

# Early May bank holiday has two exceptions based on the 50th and 75th
# anniversary of VE-Day
# 1995-05-01 Early May bank holiday removed for VE-day 50th anniversary
# 2020-05-04 Early May bank holiday removed for VE-day 75th anniversary

# Early May bank holiday pre-1995
MayBank_pre_1995 = Holiday(
    "Early May Bank Holiday",
    month=5,
    offset=DateOffset(weekday=MO(1)),
    day=1,
    end_date=pd.Timestamp("1994-12-31"),
)

# Early May bank holiday post-1995 and pre-2020
MayBank_post_1995_pre_2020 = Holiday(
    "Early May Bank Holiday",
    month=5,
    offset=DateOffset(weekday=MO(1)),
    day=1,
    start_date=pd.Timestamp("1996-01-01"),
    end_date=pd.Timestamp("2019-12-31"),
)

# Early May bank holiday post 2020
MayBank_post_2020 = Holiday(
    "Early May Bank Holiday",
    month=5,
    offset=DateOffset(weekday=MO(1)),
    day=1,
    start_date=pd.Timestamp("2021-01-01"),
)


# Spring bank holiday has two exceptions based on the Golden & Diamond Jubilee
# 2002-05-27 Spring bank holiday removed for Golden Jubilee
# 2012-05-28 Spring bank holiday removed for Diamond Jubilee

# Spring bank holiday
SpringBank_pre_2002 = Holiday(
    "Spring Bank Holiday",
    month=5,
    day=31,
    offset=DateOffset(weekday=MO(-1)),
    end_date=pd.Timestamp("2001-12-31"),
)

SpringBank_post_2002_pre_2012 = Holiday(
    "Spring Bank Holiday",
    month=5,
    day=31,
    offset=DateOffset(weekday=MO(-1)),
    start_date=pd.Timestamp("2003-01-01"),
    end_date=pd.Timestamp("2011-12-31"),
)

SpringBank_post_2012 = Holiday(
    "Spring Bank Holiday",
    month=5,
    day=31,
    offset=DateOffset(weekday=MO(-1)),
    start_date=pd.Timestamp("2013-01-01"),
)

# Summer bank holiday
SummerBank = Holiday(
    "Summer Bank Holiday",
    month=8,
    day=31,
    offset=DateOffset(weekday=MO(-1)),
)

Christmas = christmas()

WeekendChristmas = weekend_christmas()

BoxingDay = boxing_day()

WeekendBoxingDay = weekend_boxing_day()

# Early Closes
# ------------
# If Christmas Eve falls on a weekday, that day is a half day.
# If it falls on a weekend, the preceding Friday is a half day.
ChristmasEve = Holiday(
    "Christmas Eve",
    month=12,
    day=24,
    observance=previous_friday,
)
# New Year's eve (or the preceding Friday if it falls on a weekend)
# is a half day. Except for 1999-12-31, when the Queen declared a
# bank holiday.
NewYearsEvePre1999 = Holiday(
    "New Year's Eve",
    month=12,
    day=31,
    observance=previous_friday,
    end_date=pd.Timestamp("1999-01-01"),
)
NewYearsEvePost2000 = Holiday(
    "New Year's Eve",
    month=12,
    day=31,
    observance=previous_friday,
    start_date=pd.Timestamp("2000-01-01"),
)


class XLONExchangeCalendar(ExchangeCalendar):
    """
    Exchange calendar for the London Stock Exchange (XLON).

    Open Time: 8:00 AM, GMT
    Close Time: 4:30 PM, GMT

    Regularly-Observed Holidays:
    - New Years Day (observed on first business day on/after)
    - Good Friday
    - Easter Monday
    - Early May Bank Holiday (first Monday in May)
    - Spring Bank Holiday (last Monday in May)
    - Summer Bank Holiday (last Monday in May)
    - Christmas Day
    - Dec. 27th (if Christmas is on a weekend)
    - Boxing Day
    - Dec. 28th (if Boxing Day is on a weekend)

    Early Closes:
    - Christmas Eve
    - New Year's Eve
    """

    regular_early_close = time(12, 30)

    name = "XLON"

    tz = timezone("Europe/London")

    open_times = ((None, time(8)),)

    close_times = ((None, time(16, 30)),)

    @property
    def regular_holidays(self):
        return HolidayCalendar(
            [
                LSENewYearsDay,
                GoodFriday,
                EasterMonday,
                MayBank_pre_1995,
                MayBank_post_1995_pre_2020,
                MayBank_post_2020,
                SpringBank_pre_2002,
                SpringBank_post_2002_pre_2012,
                SpringBank_post_2012,
                SummerBank,
                Christmas,
                WeekendChristmas,
                BoxingDay,
                WeekendBoxingDay,
            ]
        )

    @property
    def adhoc_holidays(self):
        return [
            # VE-Day Anniversary
            pd.Timestamp("1995-05-08"),  # 50th Anniversary
            pd.Timestamp("2020-05-08"),  # 75th Anniversary
            # Queen Elizabeth II Jubilees
            # Silver Jubilee
            pd.Timestamp("1977-06-07"),
            # Golden Jubilee
            pd.Timestamp("2002-06-03"),
            pd.Timestamp("2002-06-04"),
            # Diamond Jubilee
            pd.Timestamp("2012-06-04"),
            pd.Timestamp("2012-06-05"),
            # Royal Weddings
            # Wedding Day of Princess Anne and Mark Phillips
            pd.Timestamp("1973-11-14"),
            # Wedding Day of Prince Charles and Diana Spencer
            pd.Timestamp("1981-07-29"),
            # Wedding Day of Prince William and Catherine Middleton
            pd.Timestamp("2011-04-29"),
            # Miscellaneous
            # Eve of 3rd Millenium A.D.
            pd.Timestamp("1999-12-31"),
        ]

    @property
    def special_closes(self):
        return [
            (
                self.regular_early_close,
                HolidayCalendar(
                    [
                        ChristmasEve,
                        NewYearsEvePre1999,
                        NewYearsEvePost2000,
                    ]
                ),
            )
        ]
