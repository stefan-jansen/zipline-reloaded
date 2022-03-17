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
from pandas.tseries.holiday import MO, GoodFriday, Holiday
from pandas.tseries.offsets import DateOffset
from pytz import timezone

from .common_holidays import (
    christmas,
    european_labour_day,
    maundy_thursday,
    new_years_day,
)
from .exchange_calendar import HolidayCalendar, ExchangeCalendar

NewYearsDay = new_years_day()

# Starting in 2007 Constitution Day is observed on the first Monday of Feb.
ConstitutionDay = Holiday("Constitution Day", month=2, day=5, end_date="2007")
ConstitutionDayObserved = Holiday(
    "Constitution Day Observed",
    month=2,
    day=1,
    offset=DateOffset(weekday=MO(1)),
    start_date="2007",
)

# Starting in 2007 Juarez's Birthay is observed on the third Monday of March.
JuarezBirthday = Holiday("Juarez's Birthday", month=3, day=21, end_date="2007")
JuarezBirthdayObserved = Holiday(
    "Juarez's Birthday Observed",
    month=3,
    day=1,
    offset=DateOffset(weekday=MO(3)),
    start_date="2007",
)

MaundyThursday = maundy_thursday()

LabourDay = european_labour_day()

IndependenceDay = Holiday("Independence Day", month=9, day=16)

AllSoulsDay = Holiday("All Souls' Day", month=11, day=2, start_date="2006")

# Starting in 2007 Revolution Day is observed on the third Monday of November.
RevolutionDay = Holiday("Revolution Day", month=11, day=20, end_date="2007")
RevolutionDayObserved = Holiday(
    "Revolution Day Observed",
    month=11,
    day=1,
    offset=DateOffset(weekday=MO(3)),
    start_date="2007",
)

BankingHoliday = Holiday("Banking Holiday", month=12, day=12)

Christmas = christmas()


class XMEXExchangeCalendar(ExchangeCalendar):
    """
    Calendar for the Mexican Stock Exchange (Bolsa Mexicana de Valores) in
    Mexico City.

    Open Time: 8:30 AM, CT (Central Time)
    Close Time: 3:00 PM, CT (Central Time)

    Regularly-Observed Holidays:
      - New Year's Day
      - Constitution Day
      - Juarez's Birthday
      - Maundy Thursday
      - Good Friday
      - Labour Day
      - Independence Day
      - All Souls' Day
      - Mexican Revolution
      - Banking Holiday
      - Christmas Day

    Holidays No Longer Observed:
      - None

    Early Closes:
      - None
    """

    name = "XMEX"
    tz = timezone("America/Mexico_City")

    open_times = ((None, time(8, 30)),)
    close_times = ((None, time(15)),)

    @property
    def regular_holidays(self):
        return HolidayCalendar(
            [
                NewYearsDay,
                ConstitutionDay,
                ConstitutionDayObserved,
                JuarezBirthday,
                JuarezBirthdayObserved,
                MaundyThursday,
                GoodFriday,
                LabourDay,
                IndependenceDay,
                AllSoulsDay,
                RevolutionDay,
                RevolutionDayObserved,
                BankingHoliday,
                Christmas,
            ]
        )

    @property
    def adhoc_holidays(self):
        return [
            # Bicentennial Celebration.
            pd.Timestamp("2010-09-17"),
        ]
