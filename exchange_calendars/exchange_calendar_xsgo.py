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

import pandas as pd
from pandas.tseries.holiday import Easter, GoodFriday, Holiday
from pandas.tseries.offsets import Day
from pytz import timezone

from .common_holidays import (
    all_saints_day,
    assumption_day,
    christmas,
    christmas_eve,
    european_labour_day,
    immaculate_conception,
    maundy_thursday,
    new_years_day,
    new_years_eve,
    saint_peter_and_saint_paul_day,
)
from .exchange_calendar import (
    FRIDAY,
    MONDAY,
    THURSDAY,
    TUESDAY,
    WEDNESDAY,
    WEEKDAYS,
    HolidayCalendar,
    ExchangeCalendar,
)


def nearest_monday(dt):
    """
    If the holiday falls on a Saturday, Sunday or Monday then the date is
    unchanged (Sat/Sun observances are not made up), otherwise use the closest
    Monday to the date.
    """
    day = dt.weekday()

    if day in (TUESDAY, WEDNESDAY, THURSDAY):
        return dt - timedelta(day - MONDAY)
    elif day == FRIDAY:
        return dt + timedelta(3)
    return dt


def tuesday_and_wednesday_to_friday(dt):
    """
    If Evangelical Church Day (Halloween) falls on a Tuesday, it is observed
    the preceding Friday. If it falls on a Wednesday, it is observed the next
    Friday. If it falls on Thu, Fri, Sat, Sun, or Mon the date is unchanged.
    """
    day = dt.weekday()

    if day == TUESDAY:
        return dt - timedelta(4)
    elif day == WEDNESDAY:
        return dt + timedelta(2)
    return dt


def not_2010(holidays):
    """
    In 2010 Independence Day fell on a Saturday. Normally this would mean that
    Friday is a half day, but instead it is a full day off, so we need to
    exclude it from the usual half day rules.
    """
    return holidays[holidays.year != 2010]


NewYearsDay = new_years_day()

MaundyThursday = maundy_thursday()
MondayPriorToCorpusChristi = Holiday(
    "Monday Prior to Corpus Christi",
    month=1,
    day=1,
    offset=[Easter(), Day(57)],
    end_date="2008",
)

LabourDay = european_labour_day()

NavyDay = Holiday("Navy Day", month=5, day=21)

SaintPeterAndSaintPaulDay = saint_peter_and_saint_paul_day(
    observance=nearest_monday,
)

OurLadyOfMountCarmelDay = Holiday(
    "Our Lady of Mount Carmel's Day",
    month=7,
    day=16,
    start_date="2008",
)

AssumptionDay = assumption_day()

PublicHolidayMonday = Holiday(
    "Public Holiday Preceeding a Tuesday Independence Day",
    month=9,
    day=17,
    start_date="2003",
    days_of_week=(MONDAY,),
)
DayBeforeIndependenceDay = Holiday(
    "Day Before Independence Day",
    month=9,
    day=17,
    observance=not_2010,
    days_of_week=(TUESDAY, WEDNESDAY, THURSDAY, FRIDAY),
)
IndependenceDay = Holiday("Independence Day", month=9, day=18)
ArmyDay = Holiday("Army Day", month=9, day=19)
PublicHolidayFriday = Holiday(
    "Public Holiday Following a Thursday Army Day",
    month=9,
    day=20,
    start_date="2003",
    days_of_week=(FRIDAY,),
)

DiaDeLaRaza = Holiday(
    "Dia de la Raza",
    month=10,
    day=12,
    observance=nearest_monday,
)

EvangelicalChurchDay = Holiday(
    "Evangelical Church Day",
    month=10,
    day=31,
    observance=tuesday_and_wednesday_to_friday,
    start_date="2008",
)
AllSaintsDay = all_saints_day()

ImmaculateConception = immaculate_conception()

ChristmasEve = christmas_eve(days_of_week=WEEKDAYS)
Christmas = christmas()

DayBeforeBankHoliday = Holiday(
    "Day Before Bank Holiday",
    month=12,
    day=30,
    days_of_week=WEEKDAYS,
)
BankHoliday = new_years_eve()


class XSGOExchangeCalendar(ExchangeCalendar):
    """
    Calendar for the Santiago Stock Exchange (Bolsa de Comercio de Santiago) in
    Chile.

    Open Time: 9:30 AM, CLT/CLST (Chile Standard Time/Chile Summer Time)
    Close Time: 4:00 PM, CLT (March to October)
                5:00 PM, CLST (November to February)

    Regularly-Observed Holidays:
      - New Year's Day
      - Good Friday
      - Corpus Christi (until 2007, inclusive)
      - Labour Day
      - Navy Day
      - Saint Peter and Saint Paul Day
      - Feast Day of Our Lady of Mount Carmel (starting 2008)
      - Assumption Day
      - Independence Day
      - Army Day
      - Dia de la Raza
      - Evangelical Church Day
      - All Saints' Day
      - Immaculate Conception
      - Christmas Day
      - Bank Holiday

    Holidays No Longer Observed:
      - N/A

    Early Closes:
      - Maundy Thursday
      - Day before Independence Day
      - Christmas Eve
      - Day before Bank Holiday
    """

    name = "XSGO"
    tz = timezone("America/Santiago")

    open_times = ((None, time(9, 30)),)
    early_close_1230 = time(12, 30)
    early_close_130 = time(13, 30)

    @property
    def close_times(self):
        # The equity market close time changes twice per year. In March it
        # changes to 4:00PM for winter and in November it changes to 5PM for
        # summer.
        return tuple(self._starting_dates_and_close_times())

    @property
    def regular_holidays(self):
        return HolidayCalendar(
            [
                NewYearsDay,
                GoodFriday,
                MondayPriorToCorpusChristi,
                LabourDay,
                NavyDay,
                SaintPeterAndSaintPaulDay,
                OurLadyOfMountCarmelDay,
                AssumptionDay,
                PublicHolidayMonday,
                IndependenceDay,
                ArmyDay,
                PublicHolidayFriday,
                DiaDeLaRaza,
                EvangelicalChurchDay,
                AllSaintsDay,
                ImmaculateConception,
                Christmas,
                BankHoliday,
            ]
        )

    @property
    def adhoc_holidays(self):
        return [
            # Bicentennial Celebration.
            pd.Timestamp("2010-09-17"),
            pd.Timestamp("2010-09-20"),
            # New Year's Day Observed. It is unclear why this happened only for
            # this one year.
            pd.Timestamp("2017-01-02"),
            # Census Day.
            pd.Timestamp("2017-04-19"),
            # Pope Visit.
            pd.Timestamp("2018-01-16"),
        ]

    @property
    def special_closes(self):
        return [
            (
                self.early_close_1230,
                HolidayCalendar([ChristmasEve, DayBeforeBankHoliday]),
            ),
            (
                self.early_close_130,
                HolidayCalendar([MaundyThursday, DayBeforeIndependenceDay]),
            ),
        ]

    def _starting_dates_and_close_times(self):
        yield ((None, time(17)))
        for year in range(1980, 2050):
            yield (pd.Timestamp("{}-03-01".format(year)), time(16))
            yield (pd.Timestamp("{}-11-01".format(year)), time(17))
