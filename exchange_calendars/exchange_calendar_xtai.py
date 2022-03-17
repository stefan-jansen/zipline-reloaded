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

from datetime import time, timedelta
from itertools import chain

import pandas as pd
from pandas.tseries.holiday import (
    Holiday,
    nearest_workday,
    next_monday,
    previous_friday,
)
from pytz import timezone

from .common_holidays import european_labour_day, new_years_day
from .lunisolar_holidays import (
    chinese_lunar_new_year_dates,
    dragon_boat_festival_dates,
    mid_autumn_festival_dates,
    qingming_festival_dates,
)
from .exchange_calendar import (
    SATURDAY,
    SUNDAY,
    THURSDAY,
    TUESDAY,
    HolidayCalendar,
    ExchangeCalendar,
)


def before_chinese_new_year_offset(holidays):
    """
    For Holidays that come before Chinese New Year, we subtract a day
    and then move any weekends to previous friday.
    """
    return pd.to_datetime(holidays.map(lambda d: previous_friday(d)))


def chinese_new_year_offset(holidays):
    """
    For Holidays on or after Chinese New Year, we add a day
    and then move any weekends to next monday.
    """
    return pd.to_datetime(holidays.map(lambda d: next_monday(d)))


def nearest_workday_after_2013(dt):
    """
    Nearest workday starting in 2014.
    """
    return nearest_workday(dt) if dt.year > 2013 else dt


def manual_nearest_workday(holidays):
    """
    Nearest workday observance rule for Chinese lunar calendar holidays.
    The nearest workday rule seems to start in 2014 for these holidays.
    """
    return pd.to_datetime(holidays.map(lambda d: nearest_workday_after_2013(d)))


def manual_extra_days(holidays):
    """
    Four day weekend makeup days for Chinese lunar calendar holidays.
    The four day weekend rule seem to start in 2007 for these holidays.
    """
    friday_extras = [
        d + timedelta(1) for d in holidays if d.weekday() == THURSDAY and d.year > 2006
    ]

    monday_extras = [
        d - timedelta(1) for d in holidays if d.weekday() == TUESDAY and d.year > 2006
    ]

    return pd.to_datetime(friday_extras + monday_extras)


def taiwan_makeup_rule(holidays):
    """
    This function attempts to implement what seems to be the Taiwan holiday
    observance rule since 2013.

    Notes
    -----
    If a holiday falls on a Tuesday or Thursday, and extra holiday is observed
    on Monday/Friday to create a four day weekend.  If a holiday falls on a
    weekend, it is observed on the nearest workday (Monday/Friday).
    """
    # Create four day weekends
    mon = holidays[holidays.weekday == TUESDAY] - timedelta(1)
    fri = holidays[holidays.weekday == THURSDAY] + timedelta(1)

    # Nearest workday makeups
    mon_makeups = holidays[holidays.weekday == SUNDAY] + timedelta(1)
    fri_makeups = holidays[holidays.weekday == SATURDAY] - timedelta(1)

    # Only observe rule after 2013
    extras = pd.to_datetime(list(chain(mon, mon_makeups, fri, fri_makeups)))
    extras = extras[extras.year > 2013]

    return holidays.append(extras)


NewYearsDay = new_years_day(observance=taiwan_makeup_rule)

PeaceMemorialDay = Holiday(
    "Peace Memorial Day",
    month=2,
    day=28,
    observance=taiwan_makeup_rule,
)

WomenAndChildrensDay = Holiday(
    "Women and Children's Day",
    month=4,
    day=4,
    start_date="2011",
    observance=taiwan_makeup_rule,
)

LabourDay = european_labour_day(observance=manual_nearest_workday)

NationalDay = Holiday(
    "National Day of the Republic of China",
    month=10,
    day=10,
    observance=taiwan_makeup_rule,
)

chinese_new_year = chinese_new_year_offset(chinese_lunar_new_year_dates)

chinese_new_years_eve = before_chinese_new_year_offset(
    chinese_new_year - timedelta(1),
)

chinese_new_years_eve_2 = before_chinese_new_year_offset(
    chinese_new_years_eve - timedelta(1),
)

chinese_new_year_2 = chinese_new_year_offset(
    chinese_new_year + timedelta(1),
)

chinese_new_year_3 = chinese_new_year_offset(
    chinese_new_year_2 + timedelta(1),
)

tomb_sweeping_day = manual_nearest_workday(qingming_festival_dates)

tomb_sweeping_day_extras = manual_extra_days(tomb_sweeping_day)

dragon_boat_festival = manual_nearest_workday(dragon_boat_festival_dates)

dragon_boat_festival_extras = manual_extra_days(dragon_boat_festival)

mid_autumn_festival = manual_nearest_workday(
    mid_autumn_festival_dates,
)

mid_autumn_festival_extras = manual_extra_days(mid_autumn_festival)

# Taiwan takes multiple days off before and after chinese new year,
# and sometimes it is unclear precisely which days will be holidays.
chinese_new_year_extras = pd.to_datetime(
    [
        "2002-02-07",
        "2002-02-15",
        "2003-01-29",
        "2004-01-19",
        "2005-02-04",
        "2006-02-02",
        "2007-02-22",
        "2007-02-23",
        "2008-02-04",
        "2009-01-29",
        "2009-01-30",
        "2010-02-18",
        "2010-02-19",
        "2011-01-31",
        "2012-01-26",
        "2012-01-27",
        "2013-02-14",
        "2013-02-15",
        "2014-01-28",
        "2015-02-16",
        "2016-02-11",
        "2016-02-12",
        "2017-01-25",
        "2018-02-13",
        "2019-01-31",
        "2019-02-08",
        "2020-01-21",
        "2020-01-22",
        "2021-02-08",
        "2021-02-09",
    ]
)

# Some abnormal observances of regularly observed holidays.
extra_holidays = pd.to_datetime(
    [
        "2021-04-02",  # Women And Childrens Day
        "2020-04-02",  # Tomb Sweeping Day
        "2016-04-05",  # Tomb Sweeping Day
        "2012-12-31",  # New Year's Eve
        "2012-02-27",  # Peace Memorial Day
        "2009-01-02",  # New Year's Day
        "2006-10-09",  # National Day
        "2005-09-01",  # Bank Holiday
    ]
)

typhoons = pd.to_datetime(
    [
        "2019-09-30",
        "2019-08-09",
        "2016-09-28",
        "2016-09-27",
        "2016-07-08",
        "2015-09-29",
        "2015-07-10",
        "2014-07-23",
        "2013-08-21",
        "2012-08-02",
        "2009-08-07",
        "2008-09-29",
        "2008-07-28",
        "2007-09-18",
        "2005-08-05",
        "2005-07-18",
        "2004-10-25",
        "2004-08-25",
        "2004-08-24",
        "2002-09-06",
    ]
)


class XTAIExchangeCalendar(ExchangeCalendar):
    """
    Exchange calendar for the Taiwan Stock Exchange Corporation (XTAI).

    Open Time: 9:00 AM, CST
    Close Time: 1:30 PM, CST

    Regularly-Observed Holidays:
    - New Year's Day
    - Chinese New Year's Eve
    - Chinese New Year
    - Peace Memorial Day (Feb 28)
    - Women and Children's Day (Apr 4)
    - Tomb Sweeping Day (Lunar Calendar)
    - Labour Day (May 1)
    - Dragon Boat Festival (Lunar Calendar)
    - Mid-Autumn Festival (Lunar Calendar)
    - National Day of the Republic of China (Oct 10)


    Early Closes:
    - None
    """

    name = "XTAI"

    tz = timezone("Asia/Taipei")

    open_times = ((None, time(9)),)

    close_times = ((None, time(13, 30)),)

    @property
    def regular_holidays(self):
        return HolidayCalendar(
            [
                NewYearsDay,
                PeaceMemorialDay,
                WomenAndChildrensDay,
                LabourDay,
                NationalDay,
            ]
        )

    @property
    def adhoc_holidays(self):
        return list(
            chain(
                extra_holidays,
                typhoons,
                chinese_new_years_eve,
                chinese_new_years_eve_2,
                chinese_new_year,
                chinese_new_year_2,
                chinese_new_year_3,
                chinese_new_year_extras,
                tomb_sweeping_day,
                tomb_sweeping_day_extras,
                dragon_boat_festival,
                dragon_boat_festival_extras,
                mid_autumn_festival,
                mid_autumn_festival_extras,
            )
        )
