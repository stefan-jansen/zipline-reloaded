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
from itertools import chain

import pandas as pd
from pandas.tseries.holiday import Holiday, weekend_to_monday
from pytz import timezone

from .common_holidays import european_labour_day, new_years_day, new_years_eve
from .exchange_calendar import WEEKDAYS, HolidayCalendar, ExchangeCalendar


def new_years_eve_observance(holidays):
    # For some reason New Year's Eve was not a holiday these years.
    holidays = holidays[(holidays.year != 2008) & (holidays.year != 2009)]

    return pd.to_datetime([weekend_to_monday(day) for day in holidays])


def new_years_holiday_observance(holidays):
    # New Year's Holiday did not follow the next-non-holiday rule in 2016.
    holidays = holidays[(holidays.year != 2016)]

    return pd.to_datetime([weekend_to_monday(day) for day in holidays])


def orthodox_christmas_observance(holidays):
    # Orthodox Christmas did not follow the next-non-holiday rule these years.
    holidays = holidays[(holidays.year != 2012) & (holidays.year != 2017)]

    return pd.to_datetime([weekend_to_monday(day) for day in holidays])


def defender_of_fatherland_observance(holidays):
    # Defender of the Fatherland Day did not follow the next-non-holiday rule
    # these years.
    holidays = holidays[
        (holidays.year != 2013) & (holidays.year != 2014) & (holidays.year != 2019)
    ]

    return pd.to_datetime([weekend_to_monday(day) for day in holidays])


NewYearsDay = new_years_day(observance=weekend_to_monday)
NewYearsHoliday = Holiday(
    "New Year's Holiday",
    month=1,
    day=2,
    observance=new_years_holiday_observance,
)
NewYearsHoliday2 = Holiday(
    "New Year's Holiday",
    month=1,
    day=3,
    start_date="2005",
    end_date="2012",
)
NewYearsHoliday3 = Holiday(
    "New Year's Holiday",
    month=1,
    day=4,
    start_date="2005",
    end_date="2012",
)
NewYearsHoliday4 = Holiday(
    "New Year's Holiday",
    month=1,
    day=5,
    start_date="2005",
    end_date="2012",
)
NewYearsHoliday5 = Holiday(
    "New Year's Holiday",
    month=1,
    day=6,
    start_date="2005",
    end_date="2012",
)

OrthodoxChristmas = Holiday(
    "Orthodox Christmas",
    month=1,
    day=7,
    observance=orthodox_christmas_observance,
)

DefenderOfTheFatherlandDay = Holiday(
    "Defender of the Fatherland Day",
    month=2,
    day=23,
    observance=defender_of_fatherland_observance,
)

WomensDay = Holiday(
    "Women's Day",
    month=3,
    day=8,
    observance=weekend_to_monday,
)

LabourDay = european_labour_day(observance=weekend_to_monday)

VictoryDay = Holiday(
    "Victory Day",
    month=5,
    day=9,
    observance=weekend_to_monday,
)

DayOfRussia = Holiday(
    "Day of Russia",
    month=6,
    day=12,
    observance=weekend_to_monday,
)

UnityDay = Holiday(
    "Unity Day",
    month=11,
    day=4,
    observance=weekend_to_monday,
    start_date="2005",
)

NewYearsEve = new_years_eve(
    observance=new_years_eve_observance,
    days_of_week=WEEKDAYS,
)


# Adhoc Holidays
# --------------

# All of the following "extensions" are bridge holidays, meaning they are
# either a Monday or Friday that is made into a holiday to fill in the gap
# between a Tuesday or Thursday holiday, respectively. Unfortunately having
# these bridge days is not consistently the rule, so they are treated as adhoc.
# This means that in the future there may be manual additions needed here.
new_years_extensions = [
    "2003-01-03",
    "2013-01-03",
    "2013-01-04",
    "2014-01-03",
]

orthodox_christmas_extensions = [
    "2003-01-06",
    "2005-01-10",
    "2008-01-08",
    "2009-01-08",
    "2009-01-09",
    "2010-01-08",
    "2011-01-10",
    "2016-01-08",
]

defender_of_the_fatherland_extensions = [
    "2006-02-24",
    "2010-02-22",
]

womens_day_extensions = [
    "2005-03-07",
    "2011-03-07",
    "2012-03-09",
]

labour_day_extensions = [
    "2002-05-02",
    "2002-05-03",
    "2003-05-02",
    "2004-05-04",
    "2007-04-30",
    "2008-05-02",
    "2012-04-30",
    "2015-05-04",
    "2016-05-03",
]

victory_day_extensions = [
    "2002-05-10",
    "2005-05-10",
    "2006-05-08",
    "2017-05-08",
]

day_of_russia_extensions = [
    "2003-06-13",
    "2007-06-11",
    "2008-06-13",
    "2012-06-11",
    "2014-06-13",
]

unity_day_extensions = [
    "2008-11-03",
    "2010-11-05",
]

misc_adhoc = [
    # Exchange Holidays.
    "2002-11-07",
    "2002-11-08",
    "2002-12-12",
    "2002-12-13",
    "2003-11-07",
    "2003-12-12",
    "2004-11-08",
    "2004-12-13",
    "2008-09-18",
    # Trading Suspended.
    "2008-10-10",
    "2008-10-27",
]


class XMOSExchangeCalendar(ExchangeCalendar):
    """
    Exchange calendar for the Moscow Stock Exchange.

    Open Time: 10:00 AM, MSK (Moscow Standard Time)
    Close Time: 6:45 PM, MSK (Moscow Standard Time)

    Regularly-Observed Holidays:
      - New Year's Day
      - New Year's Holiday
      - Orthodox Christmas Day
      - Defender of the Fatherland Day
      - Women's Day
      - Spring and Labour Day
      - Victory Day
      - Day of Russia
      - Unity Day
      - New Year's Eve

    Holidays No Longer Observed:
      - New Year's Holiday Week

    Early Closes:
      - None
    """

    name = "XMOS"

    tz = timezone("Europe/Moscow")

    open_times = ((None, time(10)),)

    close_times = ((None, time(18, 45)),)

    @property
    def regular_holidays(self):
        return HolidayCalendar(
            [
                NewYearsDay,
                NewYearsHoliday,
                NewYearsHoliday2,
                NewYearsHoliday3,
                NewYearsHoliday4,
                NewYearsHoliday5,
                OrthodoxChristmas,
                DefenderOfTheFatherlandDay,
                WomensDay,
                LabourDay,
                VictoryDay,
                DayOfRussia,
                UnityDay,
                NewYearsEve,
            ]
        )

    @property
    def adhoc_holidays(self):
        return list(
            chain(
                new_years_extensions,
                orthodox_christmas_extensions,
                defender_of_the_fatherland_extensions,
                womens_day_extensions,
                labour_day_extensions,
                victory_day_extensions,
                day_of_russia_extensions,
                unity_day_extensions,
                misc_adhoc,
            ),
        )
