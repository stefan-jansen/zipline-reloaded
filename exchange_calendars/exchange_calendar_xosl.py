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
    european_labour_day,
    holy_wednesday,
    maundy_thursday,
    new_years_day,
    new_years_eve,
    whit_monday,
)
from .exchange_calendar import WEEKDAYS, HolidayCalendar, ExchangeCalendar

NewYearsDay = new_years_day()

HolyWednesday = holy_wednesday(start_date="2011", days_of_week=WEEKDAYS)
MaundyThursday = maundy_thursday()
AscensionDay = ascension_day()
WhitMonday = whit_monday()

LabourDay = european_labour_day()

ConstitutionDay = Holiday("Constitution Day", month=5, day=17)

ChristmasEve = christmas_eve()
Christmas = christmas()
BoxingDay = boxing_day()

NewYearsEve = new_years_eve()


class XOSLExchangeCalendar(ExchangeCalendar):
    """
    Calendar for the Oslo Stock Exchange in Norway.

    Open Time: 9:00 AM, CET (Central European Time)
    Close Time: 4:20 PM, CET (Central European Time)

    Regularly-Observed Holidays:
      - New Year's Day
      - Maundy Thursday
      - Good Friday
      - Easter Monday
      - Labour Day
      - Ascension Day
      - Constitution Day
      - Whit Monday
      - Christmas Eve
      - Christmas Day
      - Boxing Day
      - New Year's Eve

    Early Closes:
      - Holy Wednesday
    """

    name = "XOSL"
    tz = timezone("Europe/Oslo")
    open_times = ((None, time(9)),)
    close_times = ((None, time(16, 20)),)
    regular_early_close = time(13)

    @property
    def regular_holidays(self):
        return HolidayCalendar(
            [
                NewYearsDay,
                MaundyThursday,
                GoodFriday,
                EasterMonday,
                LabourDay,
                AscensionDay,
                ConstitutionDay,
                WhitMonday,
                ChristmasEve,
                Christmas,
                BoxingDay,
                NewYearsEve,
            ]
        )

    @property
    def special_closes(self):
        return [(self.regular_early_close, HolidayCalendar([HolyWednesday]))]
