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

import pandas as pd
from pandas.tseries.holiday import EasterMonday, GoodFriday, Holiday
from pytz import timezone

from .common_holidays import (
    all_saints_day,
    boxing_day,
    christmas,
    christmas_eve,
    corpus_christi,
    epiphany,
    european_labour_day,
    new_years_day,
    new_years_eve,
)
from .exchange_calendar import HolidayCalendar, ExchangeCalendar


def not_2004(datetime_index):
    """
    Christmas Eve is a holiday every year except for whatever reason it was a
    trading day in 2004.
    """
    return datetime_index[datetime_index.year != 2004]


NewYearsDay = new_years_day()

Epiphany = epiphany(start_date="2011")

LabourDay = european_labour_day()

May3ConstitutionDay = Holiday(
    "Celabration of Declaration of the Constitution of 3 May",
    month=5,
    day=3,
)

CorpusChristi = corpus_christi()

ArmedForcesDay = Holiday(
    "Armed Forces Day",
    month=8,
    day=15,
)

AllSaintsDay = all_saints_day()

IndependenceDay = Holiday(
    "National Independence Day",
    month=11,
    day=11,
)

ChristmasEve = christmas_eve(observance=not_2004)
Christmas = christmas()
BoxingDay = boxing_day()

NewYearsEve = new_years_eve(start_date="2011")


class XWARExchangeCalendar(ExchangeCalendar):
    """
    Exchange calendar for the Warsaw Stock Exchange (WSE).

    Open Time: 9:00 AM, Central European Time (CET)
    Close Time: 5:00 PM, Central European Time (CET)

    Regularly-Observed Holidays:
      - New Year's Day
      - Epiphany
      - Good Friday
      - Easter Monday
      - Labour Day
      - Constitution Day
      - Corpus Christi
      - Armed Forces Day
      - All Saints' Day
      - Independence Day
      - Christmas Eve
      - Christmas Day
      - Boxing Day
      - New Year's Eve

    Holidays No Longer Observed:
      - None

    Early Closes:
      - None
    """

    name = "XWAR"

    tz = timezone("Europe/Warsaw")

    open_times = ((None, time(9)),)
    close_times = ((None, time(17)),)

    @property
    def regular_holidays(self):
        return HolidayCalendar(
            [
                NewYearsDay,
                Epiphany,
                GoodFriday,
                EasterMonday,
                LabourDay,
                May3ConstitutionDay,
                CorpusChristi,
                ArmedForcesDay,
                AllSaintsDay,
                IndependenceDay,
                ChristmasEve,
                Christmas,
                BoxingDay,
                NewYearsEve,
            ]
        )

    @property
    def adhoc_holidays(self):
        return [
            pd.Timestamp("2005-04-08"),  # Pope's Funeral.
            pd.Timestamp("2007-12-31"),  # New Year's Eve (adhoc).
            pd.Timestamp("2008-05-02"),  # Exchange Holiday.
            pd.Timestamp("2009-01-02"),  # Exchange Holiday.
            pd.Timestamp("2013-04-16"),  # Exchange Holiday.
            pd.Timestamp("2018-01-02"),  # Exchange Holiday.
            pd.Timestamp("2018-11-12"),  # Independence Holiday.
        ]
