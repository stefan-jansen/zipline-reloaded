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

from dateutil.relativedelta import MO
from pandas import DateOffset, Timestamp
from pandas.tseries.holiday import (
    EasterMonday,
    GoodFriday,
    Holiday,
    previous_friday,
    sunday_to_monday,
    weekend_to_monday,
)
from pytz import timezone

from .common_holidays import (
    anzac_day,
    boxing_day,
    christmas,
    new_years_day,
    weekend_boxing_day,
    weekend_christmas,
)
from .exchange_calendar import HolidayCalendar, ExchangeCalendar

NewYearsDay = new_years_day(observance=weekend_to_monday)

# "Celebrating Australia: A history of Australia Day" Elizabeth Kwan
# https://www.australiaday.org.au/storage/celebratingaustralia.pdf
# present rule follows the 1994 agreement between the States to
# synchronize the holiday with weekends mondayized
AustraliaDay = Holiday(
    "Australia Day",
    month=1,
    day=26,
    start_date=Timestamp("1994-01-01"),
    observance=weekend_to_monday,
)

# prior to 1993 the holiday was observed on the Monday
# following, or on, the 26th of January
AustraliaDayPre88 = Holiday(
    "Australia Day",
    month=1,
    day=26,
    start_date=Timestamp("1960-01-01"),
    end_date=Timestamp("1987-12-31"),
    offset=DateOffset(weekday=MO(1)),
)
# The 1988 Bi-Centennial celebrations saw an extra holiday
# and Australia Day observed on the actual date
AustraliaDay1988 = Holiday(
    "Australia Day",
    month=1,
    day=26,
    start_date=Timestamp("1988-01-01"),
    end_date=Timestamp("1988-12-31"),
)
# ASX did not close for Australia Day in 1993 since
# States observed different dates prior to 1994
AustraliaDayPost88Pre93 = Holiday(
    "Australia Day",
    month=1,
    day=26,
    start_date=Timestamp("1989-01-01"),
    end_date=Timestamp("1992-12-31"),
    offset=DateOffset(weekday=MO(1)),
)

# Anzac Day was observed on Monday when it fell on a Sunday in
# 2010 but that does not appear to have been the case previously.
# ANZAC Day observance was a special case in 2010
AnzacDayNonMondayized = anzac_day(end_date="2010")
AnzacDay2010 = anzac_day(
    observance=sunday_to_monday, start_date="2010", end_date="2011"
)
AnzacDay = anzac_day(start_date="2011")

# When Easter Monday and Anzac Day coincided in 2011, Easter Tuesday was
# also observed as a public holiday. Note that this isn't defined as a
# rule, because it will happen next in 2095 (and then in  2163), and
# there isn't a great way to tell how this will be handled at that point.
EasterTuesday2011AdHoc = Timestamp("2011-04-26")

QueensBirthday = Holiday(
    "Queen's Birthday",
    month=6,
    day=1,
    offset=[DateOffset(weekday=MO(2))],
)

LastTradingDayBeforeChristmas = Holiday(
    "Last Trading Day Before Christmas",
    month=12,
    day=24,
    start_date="2010",
    observance=previous_friday,
)
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

# additional ad-hoc holidays
NYEMonday1984AdHoc = Timestamp("1984-12-31")
NYEMonday1990AdHoc = Timestamp("1990-12-31")
Bicentennial1988 = Timestamp("1988-01-25")
Y2KTesting = Timestamp("1999-12-31")


class XASXExchangeCalendar(ExchangeCalendar):
    """
    Calendar for the Australian Securities Exchange in Sydney.

    Open Time: 10:00 AM, Australian Eastern Time
    Close Time: 4:00 PM, Australian Eastern Time

    Regularly-Observed Holidays:
      - New Year's Day
      - Australia Day
      - Good Friday
      - Easter Monday
      - Anzac Day
      - Queen's Birthday
      - Christmas Day
      - Boxing Day

    Early Closes:
      - Last trading day before Christmas
      - Last trading day of the calendar year
    """

    regular_early_close = time(14, 10)

    name = "XASX"

    tz = timezone("Australia/Sydney")

    open_times = ((None, time(10)),)  # Zipline compatability (10,1); else (10,0)

    close_times = ((None, time(16)),)

    @property
    def regular_holidays(self):
        return HolidayCalendar(
            [
                NewYearsDay,
                AustraliaDay,
                AustraliaDayPre88,
                AustraliaDay1988,
                AustraliaDayPost88Pre93,
                GoodFriday,
                EasterMonday,
                AnzacDayNonMondayized,
                AnzacDay2010,
                AnzacDay,
                QueensBirthday,
                Christmas,
                WeekendChristmas,
                BoxingDay,
                WeekendBoxingDay,
            ]
        )

    @property
    def adhoc_holidays(self):
        return [
            EasterTuesday2011AdHoc,
            NYEMonday1984AdHoc,
            NYEMonday1990AdHoc,
            Bicentennial1988,
            Y2KTesting,
        ]

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
