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

from pandas import Timestamp
from pandas.tseries.holiday import (
    MO,
    DateOffset,
    EasterMonday,
    GoodFriday,
    Holiday,
    previous_friday,
    weekend_to_monday,
)
from pytz import UTC, timezone

from .common_holidays import (
    boxing_day,
    christmas,
    christmas_eve,
    european_labour_day,
    new_years_day,
    weekend_boxing_day,
    weekend_christmas,
)
from .exchange_calendar import HolidayCalendar, ExchangeCalendar

NewYearsDay = new_years_day(observance=weekend_to_monday)

StPatricksDay = Holiday(
    "St. Patrick's Day",
    month=3,
    day=17,
    end_date="2001",
    observance=weekend_to_monday,
)

LabourDayTo2009 = european_labour_day(
    start_date="2008",
    end_date="2010",
    observance=weekend_to_monday,
)

LabourDayFrom2019 = european_labour_day(
    start_date="2019",
    observance=weekend_to_monday,
)

MayBankHoliday = Holiday(
    "May Bank Holiday",
    month=5,
    day=1,
    end_date="2019",
    offset=DateOffset(weekday=MO(1)),
)
JuneBankHoliday = Holiday(
    "June Bank Holiday",
    month=6,
    day=1,
    end_date="2019",
    offset=DateOffset(weekday=MO(1)),
)

LastTradingDayBeforeChristmas = Holiday(
    "Last Trading Day Before Christmas",
    month=12,
    day=24,
    start_date="2010",
    observance=previous_friday,
)

ChristmasEve = christmas_eve(end_date="2005")
Christmas = christmas()
WeekendChristmas = weekend_christmas()
BoxingDay = boxing_day()
WeekendBoxingDay = weekend_boxing_day()

LastTradingDayOfCalendarYear = Holiday(
    "Last Trading Day Of Calendar Year",
    month=12,
    day=31,
    start_date="2010",
    observance=previous_friday,
)

# Ad hoc closes.
March1BadWeather = Timestamp("2018-03-01", tz=UTC)
# Ad hoc holidays.
March2BadWeather = Timestamp("2018-03-02")


class XDUBExchangeCalendar(ExchangeCalendar):
    """
    Calendar for the Irish Stock Exchange in Dublin.

    Open Time: 8:00 AM, GMT
    Close Time: 4:28 PM, GMT

    Regularly-Observed Holidays:
      - New Years Day
      - Good Friday
      - Easter Monday
      - May Bank Holiday
      - June Bank Holiday
      - Christmas Day
      - St. Stephen's Day (Boxing Day)

    Holidays No Longer Observed:
      - St. Patrick's Day
      - Labour Day

    Early Closes:
      - Christmas Eve
      - New Year's Eve
    """

    name = "XDUB"
    tz = timezone("Europe/Dublin")
    open_times = ((None, time(8)),)
    close_times = ((None, time(16, 28)),)
    regular_early_close = time(12, 28)

    @property
    def regular_holidays(self):
        return HolidayCalendar(
            [
                NewYearsDay,
                StPatricksDay,
                GoodFriday,
                EasterMonday,
                LabourDayTo2009,
                LabourDayFrom2019,
                MayBankHoliday,
                JuneBankHoliday,
                ChristmasEve,
                Christmas,
                WeekendChristmas,
                BoxingDay,
                WeekendBoxingDay,
            ]
        )

    @property
    def adhoc_holidays(self):
        return [March2BadWeather]

    @property
    def special_closes(self):
        return [
            (
                self.regular_early_close,
                HolidayCalendar(
                    [
                        LastTradingDayBeforeChristmas,
                        LastTradingDayOfCalendarYear,
                    ]
                ),
            ),
        ]

    @property
    def special_closes_adhoc(self):
        return [(self.regular_early_close, [March1BadWeather])]
