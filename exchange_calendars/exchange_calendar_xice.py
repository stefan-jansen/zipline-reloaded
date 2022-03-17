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

from pandas.tseries.holiday import MO, TH, DateOffset, EasterMonday, GoodFriday, Holiday
from pytz import timezone

from .common_holidays import (
    ascension_day,
    boxing_day,
    christmas,
    christmas_eve,
    european_labour_day,
    maundy_thursday,
    new_years_day,
    new_years_eve,
    whit_monday,
)
from .exchange_calendar import HolidayCalendar, ExchangeCalendar

NewYearsDay = new_years_day()

# This falls on the first Thursday after 18 April.
FirstDayOfSummer = Holiday(
    "First Day of Summer",
    month=4,
    day=19,
    offset=DateOffset(weekday=TH(1)),
)

LabourDay = european_labour_day()

MaundyThursday = maundy_thursday()
AscensionDay = ascension_day()
WhitMonday = whit_monday()

NationalDay = Holiday("Icelandic Republic Day", month=6, day=17)

# This falls on the first Monday of August.
CommerceDay = Holiday(
    "Commerce Day",
    month=8,
    day=1,
    offset=DateOffset(weekday=MO(1)),
)

ChristmasEve = christmas_eve()
Christmas = christmas()
BoxingDay = boxing_day()

NewYearsEve = new_years_eve()


class XICEExchangeCalendar(ExchangeCalendar):
    """
    Calendar for the Iceland Exchange.

    Open Time: 9:30 AM, GMT (Greenwich Mean Time)
    Close Time: 3:30 PM, GMT (Greenwich Mean Time)

    Regularly-Observed Holidays:
      - New Year's Day
      - Maundy Thursday
      - Good Friday
      - Easter Monday
      - First Day of Summer
      - Labour Day
      - Ascension Day
      - Whit Monday
      - National Day
      - Commerce Day
      - Christmas Eve
      - Christmas Day
      - Boxing Day
      - New Year's Eve

    Early Closes:
      - None
    """

    name = "XICE"
    tz = timezone("Atlantic/Reykjavik")
    open_times = ((None, time(9, 30)),)
    close_times = ((None, time(15, 30)),)

    @property
    def regular_holidays(self):
        return HolidayCalendar(
            [
                NewYearsDay,
                MaundyThursday,
                GoodFriday,
                EasterMonday,
                FirstDayOfSummer,
                LabourDay,
                AscensionDay,
                WhitMonday,
                NationalDay,
                CommerceDay,
                ChristmasEve,
                Christmas,
                BoxingDay,
                NewYearsEve,
            ]
        )
