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
from pandas.tseries.holiday import MO, Easter, GoodFriday, Holiday
from pandas.tseries.offsets import Day
from pytz import timezone

from .common_holidays import (
    christmas,
    christmas_eve,
    european_labour_day,
    immaculate_conception,
    maundy_thursday,
    new_years_day,
)
from .exchange_calendar import (
    MONDAY,
    TUESDAY,
    WEDNESDAY,
    WEEKDAYS,
    HolidayCalendar,
    ExchangeCalendar,
)


def nearest_monday(dt):
    """
    If a holiday falls on Tuesday or Wednesday, it is observed on the
    previous Monday.  If it falls on Thursday, Friday or a weekend,
    it is observed on the following Monday.
    """
    day = dt.weekday()

    if day in (MONDAY, TUESDAY, WEDNESDAY):
        return dt - timedelta(day)

    while dt.weekday() != MONDAY:
        dt += timedelta(1)

    return dt


def cultural_diversity_observance(holidays):
    """
    Apply the nearest monday rule, and also exclude 2012 (Day of
    Respect for Cultural Diversity breaks the nearest monday rule
    in 2012).
    """
    holidays = pd.to_datetime(holidays.map(nearest_monday))
    return holidays[holidays.year != 2012]


def not_2018(holidays):
    """
    Exclude the year 2018 from the holiday list.
    """
    return holidays[holidays.year != 2018]


NewYearsDay = new_years_day()

CarnivalMonday = Holiday(
    "Carnival Monday",
    month=1,
    day=1,
    start_date="2011",
    offset=[Easter(), -Day(48)],
)

CarnivalTuesday = Holiday(
    "Carnival Tuesday",
    month=1,
    day=1,
    start_date="2011",
    offset=[Easter(), -Day(47)],
)

TruthAndJusticeMemorialDay = Holiday(
    "Truth and Justice Memorial Day",
    month=3,
    day=24,
    start_date="2005",
)

MalvinasDayTo2004 = Holiday(
    "Malvinas Day (up to 2004)",
    month=3,
    day=31,
    end_date="2005",
    offset=pd.DateOffset(weekday=MO(1)),
)

MalvinasDayFrom2005 = Holiday(
    "Malvinas Day (2005-present)", month=4, day=2, start_date="2005"
)

MaundyThursday = maundy_thursday()

LabourDay = european_labour_day()

MayDayRevolution = Holiday(
    "May Day Revolution",
    month=5,
    day=25,
)

MartinMiguelDeGuemesDay = Holiday(
    "Martin Miguel de Guemes Day",
    month=6,
    day=17,
    start_date="2016",
)

NationalFlagDayTo2010 = Holiday(
    "National Flag Day (up to 2010)",
    month=6,
    day=1,
    end_date="2011",
    offset=pd.DateOffset(weekday=MO(3)),
)

NationalFlagDayFrom2011 = Holiday(
    "National Flag Day (2011-present)",
    month=6,
    day=20,
    start_date="2011",
)

IndependenceDay = Holiday(
    "Independence Day",
    month=7,
    day=9,
)

SanMartinsDayTo2010 = Holiday(
    "San Martin's Day",
    month=8,
    day=1,
    end_date="2011",
    offset=pd.DateOffset(weekday=MO(3)),
)

SanMartinsDayFrom2012 = Holiday(
    "San Martin's Day",
    month=8,
    day=1,
    start_date="2012",
    offset=pd.DateOffset(weekday=MO(3)),
)

DayOfRespectForCulturalDiversity = Holiday(
    "Day of Respect for Cultural Diversity",
    month=10,
    day=12,
    observance=cultural_diversity_observance,
)

BankHoliday = Holiday(
    "Bank Holiday",
    month=11,
    day=6,
    end_date="2018",
)

DayOfNationalSovereigntyTo2014 = Holiday(
    "Day of National Sovereignty (2010-2014)",
    month=11,
    day=1,
    start_date="2010",
    end_date="2015",
    offset=pd.DateOffset(weekday=MO(4)),
)

DayOfNationalSovereigntyFrom2017 = Holiday(
    "Day of National Sovereignty (2017-present)",
    month=11,
    day=17,
    start_date="2017",
    offset=pd.DateOffset(weekday=MO(1)),
)

ImmaculateConception = immaculate_conception()

ChristmasEve = christmas_eve(
    days_of_week=WEEKDAYS,
    observance=not_2018,
)

ChristmasDay = christmas()

NewYearsEve = Holiday(
    "New Year's Eve",
    month=12,
    day=31,
    days_of_week=WEEKDAYS,
    observance=not_2018,
)


class XBUEExchangeCalendar(ExchangeCalendar):
    """
    Exchange calendar for the Buenos Aires Stock Exchange (XBUE).

    Open Time: 11:00 AM, AST
    Close Time: 5:00 PM, AST

    Regularly-Observed Holidays:
    - New Year's Day
    - Carnival Monday (48 days before Easter)
    - Carnival Tuesday (47 days before Easter)
    - Truth and Justice Memorial Day (Mar 24)
    - Malvinas Day (until 2004 first Monday after Mar 31, 2005-present Apr 2)
    - Good Friday
    - Labour Day
    - May Day Revolution (May 25)
    - Martin Miguel de Guemes Day (Jun 17, 2016-present)
    - National Flag Day (until 2010 3rd Monday in Jun, 2011-present Jun 20)
    - Independence Day (Jul 9)
    - San Martin's Day (3rd Monday in Aug)
    - Day of Respect for Cultural Diversity (2nd Monday in Oct)
    - Bank Holiday (Nov 6)
    - Day of National Sovereignty (4th Monday in Nov)
    - Immaculate Conception
    - Christmas Eve (2005-present)
    - Christmas Day
    - Last Trading Day of Year (2005-present)


    Early Closes:
    Note - we are unsure if these are early closes or holidays
    - Christmas Eve
    - New Year's Eve
    """

    name = "XBUE"

    tz = timezone("America/Argentina/Buenos_Aires")

    open_times = ((None, time(11)),)

    close_times = ((None, time(17, 00)),)

    # TODO: Verify early close time
    regular_early_close = time(13)

    @property
    def regular_holidays(self):
        return HolidayCalendar(
            [
                NewYearsDay,
                CarnivalMonday,
                CarnivalTuesday,
                TruthAndJusticeMemorialDay,
                MalvinasDayTo2004,
                MalvinasDayFrom2005,
                MaundyThursday,
                GoodFriday,
                LabourDay,
                MayDayRevolution,
                MartinMiguelDeGuemesDay,
                NationalFlagDayTo2010,
                NationalFlagDayFrom2011,
                IndependenceDay,
                SanMartinsDayTo2010,
                SanMartinsDayFrom2012,
                DayOfRespectForCulturalDiversity,
                BankHoliday,
                DayOfNationalSovereigntyTo2014,
                DayOfNationalSovereigntyFrom2017,
                ImmaculateConception,
                ChristmasDay,
            ]
        )

    @property
    def adhoc_holidays(self):
        misc_adhocs = [
            "2009-07-10",
            "2010-05-24",
            "2010-10-27",
            "2012-01-02",
            "2012-02-27",
            "2012-09-24",
            "2013-01-31",
            "2013-02-20",
            "2018-11-30",
        ]

        # There was a string of market closures in January, 2002
        market_closures_2002_jan = [
            "2002-01-{:02d}".format(day) for day in range(7, 17)
        ]

        # There was a string of market closures in April, 2002
        market_closures_2002_apr = [
            "2002-04-{:02d}".format(day) for day in range(22, 27)
        ]

        # There are occasionally "bridge days" that make long weekends when
        # a holiday falls on a Tuesday/Thursday, but these days are chosen
        # inconsistently.
        bridge_days = [
            "2011-03-25",
            "2011-12-09",
            "2012-04-30",
            "2013-04-01",
            "2013-06-21",
            "2014-05-02",
            "2014-12-26",
            "2015-03-23",
            "2015-12-07",
            "2016-07-08",
            "2016-12-09",
            "2018-04-30",
            "2018-12-24",
            "2018-12-31",
            "2019-07-08",
            "2019-08-19",
            "2019-10-14",
        ]

        irregular_observances = [
            "2012-10-08",  # Cultural Diversity Day
            "2011-08-22",  # San Martin's Day
            "2015-11-27",  # Day of National Sovereignty
            "2016-11-28",  # Day of National Sovereignty
        ]

        return list(
            chain(
                misc_adhocs,
                market_closures_2002_jan,
                market_closures_2002_apr,
                bridge_days,
                irregular_observances,
            )
        )

    @property
    def special_closes(self):
        return [
            (
                self.regular_early_close,
                HolidayCalendar(
                    [
                        ChristmasEve,
                        NewYearsEve,
                    ]
                ),
            ),
        ]
