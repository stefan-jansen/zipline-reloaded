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

from pandas.tseries.holiday import Easter, EasterMonday, Holiday
from pandas.tseries.offsets import Day
from pytz import timezone

from .common_holidays import (
    all_saints_day,
    christmas,
    christmas_eve,
    european_labour_day,
    new_years_day,
    new_years_eve,
    whit_monday,
)
from .exchange_calendar import THURSDAY, TUESDAY, HolidayCalendar, ExchangeCalendar


def four_day_weekend0(dt, include_mon: bool = True, include_fri: bool = True):
    """
    Custom observance function as for almost all holidays in the XBUD calendar,
    if the holiday falls on a Tuesday the previous Monday also becomes a holiday,
    and if the holiday falls on a Thursday the following Friday also becomes a holiday.

    Parameters
    ----------
    dt : datetime
         Unadjusted raw holiday datetimes
    include_mon : boolean
         If holiday falls on a Tuesday, previous Monday becomes a holiday.
    include_fri : boolean
         If holiday falls on a Thursday, following Friday becomes a holiday.
    """
    print(type(dt))
    mon = dt[include_mon & (dt.weekday == TUESDAY)] - timedelta(1)  # mv Tues back one day
    fri = dt[include_fri & (dt.weekday == THURSDAY)] + timedelta(1)  # mv Thurs ahead one day
    return dt.append([mon, fri])


def four_day_weekend(dt):
    return four_day_weekend0(dt, include_mon=True, include_fri=True)


NewYearsDay = new_years_day(observance=four_day_weekend)

NationalHoliday1 = Holiday(
    "National Day", month=3, day=15, observance=four_day_weekend
)

# Need custom start year so can't use pandas GoodFriday
GoodFriday = Holiday(
    "Good Friday", month=1, day=1, offset=[Easter(), Day(-2)], start_date="2012"
)

LabourDay = european_labour_day(observance=four_day_weekend)

WhitMonday = whit_monday()

StStephensDay = Holiday(
    "St. Stephen's Day",
    month=8,
    day=20,
    observance=four_day_weekend,
)

NationalHoliday2 = Holiday(
    "National Day",
    month=10,
    day=23,
    observance=four_day_weekend,
)

AllSaintsDay = all_saints_day(observance=four_day_weekend)

# Christmas Eve does not follow the four day weekend rule
ChristmasEve = christmas_eve()

ChristmasDay = christmas()

# XBUD always has a holiday for the second day of Christmas (26th),
# but starting in 2013 if the 26th falls on a Thursday then the
# 27th (Friday) is also taken off
SecondDayOfChristmas = Holiday(
    "Second Day of Christmas (w/ no added Friday off)",
    month=12,
    day=26,
    end_date="2013",
)

SecondDayOfChristmasAddFriday = Holiday(
    "Second Day of Christmas (w/ added Friday off)",
    month=12,
    day=26,
    start_date="2013",
    # Don't apply the rule here where the previous Monday also becomes a holiday if this falls onto a Tuesday.
    # Rationale: The previous Monday in this case is Christmas which is already defined as a holiday above.
    # Apply the other rule where the following Friday becomes a holiday if it falls onto a Thursday as usual.
    observance=lambda dt: four_day_weekend0(dt, include_mon=False, include_fri=True),
)

# Starting in 2011, New Year's Eve is observed as a holiday every year.
# In some cases pre-2011, the 31st becomes a holiday due to the four day
# weekend rule (when Jan 1 falls on a Tuesday).
# Also, when NYE starts being observed as a holiday it does NOT follow
# the four day weekend rule (no 30ths are holidays)
NewYearsEve = new_years_eve(start_date="2011")


class XBUDExchangeCalendar(ExchangeCalendar):
    """
    Exchange calendar for the Budapest Stock Exchange (XBUD).

    Open Time: 9:00 AM, CET
    Close Time: 5:00 PM, CET

    Regularly-Observed Holidays:
    - New Year's Day
    - National Holiday (Mar 15)
    - Good Friday
    - Easter Monday
    - Labour Day (May 1)
    - Whit Monday (50 days after Easter Sunday)
    - St. Stephen's Day (Aug 20)
    - National Holiday (Oct 23)
    - All Saint's Day (Nov 1)
    - Christmas Eve
    - Christmas Day
    - Second Day of Christmas (Dec 26)
    - New Year's Eve

    Early Closes:
    - None
    """

    name = "XBUD"

    tz = timezone("Europe/Budapest")

    open_times = ((None, time(9)),)

    close_times = ((None, time(17, 00)),)

    @property
    def regular_holidays(self):
        return HolidayCalendar(
            [
                NewYearsDay,
                NationalHoliday1,
                GoodFriday,
                EasterMonday,
                LabourDay,
                WhitMonday,
                StStephensDay,
                NationalHoliday2,
                AllSaintsDay,
                ChristmasEve,
                ChristmasDay,
                SecondDayOfChristmas,
                SecondDayOfChristmasAddFriday,
                NewYearsEve,
            ]
        )
