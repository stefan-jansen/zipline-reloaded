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

from pandas.tseries.holiday import EasterMonday, GoodFriday, Holiday
from pytz import timezone

from .common_holidays import (
    ascension_day,
    boxing_day,
    christmas,
    christmas_eve,
    epiphany,
    european_labour_day,
    midsummer_eve,
    new_years_day,
    new_years_eve,
)
from .exchange_calendar import HolidayCalendar, ExchangeCalendar

NewYearsDay = new_years_day()

Epiphany = epiphany()

LabourDay = european_labour_day()

AscensionDay = ascension_day()

MidsummerEve = midsummer_eve()

IndependenceDay = Holiday("Finland Independence Day", month=12, day=6)

ChristmasEve = christmas_eve()
Christmas = christmas()
BoxingDay = boxing_day()

NewYearsEve = new_years_eve()


class XHELExchangeCalendar(ExchangeCalendar):
    """
    Calendar for the Helsinki Stock Exchange in Finland.

    Open Time: 10:00 AM, CET (Eastern European Time)
    Close Time: 6:30 PM, CET (Eastern European Time)

    Regularly-Observed Holidays:
      - New Year's Day
      - Epiphany
      - Good Friday
      - Easter Monday
      - Labour Day
      - Ascension Day
      - Midsummer Eve
      - Independence Day
      - Christmas Eve
      - Christmas Day
      - Boxing Day
      - New Year's Eve

    Early Closes:
      - None
    """

    name = "XHEL"
    tz = timezone("Europe/Helsinki")
    open_times = ((None, time(10)),)
    close_times = ((None, time(18, 30)),)

    @property
    def regular_holidays(self):
        return HolidayCalendar(
            [
                NewYearsDay,
                Epiphany,
                GoodFriday,
                EasterMonday,
                LabourDay,
                AscensionDay,
                MidsummerEve,
                IndependenceDay,
                ChristmasEve,
                Christmas,
                BoxingDay,
                NewYearsEve,
            ]
        )
