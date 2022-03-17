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
    boxing_day,
    christmas,
    christmas_eve,
    european_labour_day,
    new_years_day,
    new_years_eve,
)
from .exchange_calendar import HolidayCalendar, ExchangeCalendar

NewYearsDay = new_years_day()

LabourDay = european_labour_day()

Ferragosto = Holiday("Ferragosto", month=8, day=15)

ChristmasEve = christmas_eve()
Christmas = christmas()
BoxingDay = boxing_day()

NewYearsEve = new_years_eve()


class XMILExchangeCalendar(ExchangeCalendar):
    """
    Calendar for the Borsa Italiana in Milan, Italy.

    Open Time: 9:00 AM, CET (Central European Time)
    Close Time: 5:30 PM, CET (Central European Time)

    Regularly-Observed Holidays:
      - New Year's Day
      - Good Friday
      - Easter Monday
      - Labour Day
      - Ferragosto
      - Christmas Eve
      - Christmas Day
      - Boxing Day
      - New Year's Eve

    Early Closes:
      - None
    """

    name = "XMIL"

    # Rome is the same timezone as Milan.
    tz = timezone("Europe/Rome")

    open_times = ((None, time(9)),)

    close_times = ((None, time(17, 30)),)

    @property
    def regular_holidays(self):
        return HolidayCalendar(
            [
                NewYearsDay,
                GoodFriday,
                EasterMonday,
                LabourDay,
                Ferragosto,
                ChristmasEve,
                Christmas,
                BoxingDay,
                NewYearsEve,
            ]
        )
