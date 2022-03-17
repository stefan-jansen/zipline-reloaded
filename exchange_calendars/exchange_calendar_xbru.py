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
    new_years_day,
    new_years_eve,
    whit_monday,
)
from .exchange_calendar import WEEKDAYS, HolidayCalendar, ExchangeCalendar

NewYearsDay = new_years_day()

AscensionDay = ascension_day(end_date="2001")
WhitMonday = whit_monday(end_date="2002")

LabourDay = european_labour_day()

BelgiumIndependenceDay = Holiday(
    "Belgium Independence Day",
    month=7,
    day=21,
    end_date="2002",
)

ChristmasEve = christmas_eve(days_of_week=WEEKDAYS)
Christmas = christmas()
BoxingDay = boxing_day()

NewYearsEveBefore2002 = new_years_eve(end_date="2002")
NewYearsEveInOrAfter2002 = new_years_eve(
    start_date="2002",
    days_of_week=WEEKDAYS,
)


class XBRUExchangeCalendar(ExchangeCalendar):
    """
    Calendar for the Euronext Brussels exchange, and the primary calendar for
    the country of Belgium.

    Open Time: 9:00 AM, CET (Central European Time)
    Close Time: 5:30 PM, CET (Central European Time)

    Regularly-Observed Holidays:
      - New Year's Day
      - Good Friday
      - Easter Monday
      - Labour Day
      - Christmas Day
      - Boxing Day

    Early Closes:
      - Christmas Eve
      - New Year's Eve

    Other countries on the Euronext:
      - France
      - Netherlands
      - Portugal
    """

    # Source: https://www.euronext.com/en/calendars-hours
    regular_early_close = time(14, 5)

    @property
    def name(self):
        # Euronext Brussels
        return "XBRU"

    tz = timezone("Europe/Brussels")

    open_times = ((None, time(9)),)

    close_times = ((None, time(17, 30)),)

    @property
    def regular_holidays(self):
        return HolidayCalendar(
            [
                NewYearsDay,
                GoodFriday,
                EasterMonday,
                AscensionDay,
                WhitMonday,
                LabourDay,
                BelgiumIndependenceDay,
                Christmas,
                BoxingDay,
                NewYearsEveBefore2002,
            ]
        )

    @property
    def special_closes(self):
        return [
            (
                self.regular_early_close,
                HolidayCalendar([ChristmasEve, NewYearsEveInOrAfter2002]),
            ),
        ]
