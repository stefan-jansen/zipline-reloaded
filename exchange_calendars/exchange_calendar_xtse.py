from datetime import time
from itertools import chain

import pandas as pd
from pandas.tseries.holiday import (
    MO,
    DateOffset,
    GoodFriday,
    Holiday,
    weekend_to_monday,
)
from pytz import timezone

from .common_holidays import (
    boxing_day,
    christmas,
    new_years_day,
    weekend_boxing_day,
    weekend_christmas,
)
from .exchange_calendar import (
    FRIDAY,
    MONDAY,
    THURSDAY,
    TUESDAY,
    WEDNESDAY,
    HolidayCalendar,
    ExchangeCalendar,
)

# New Year's Day
XTSENewYearsDay = new_years_day(observance=weekend_to_monday)

# Ontario Family Day
FamilyDay = Holiday(
    "Family Day",
    month=2,
    day=1,
    offset=DateOffset(weekday=MO(3)),
    start_date="2008-01-01",
)
# Victoria Day
VictoriaDay = Holiday(
    "Victoria Day",
    month=5,
    day=24,
    offset=DateOffset(weekday=MO(-1)),
)
# Canada Day
CanadaDay = Holiday(
    "Canada Day",
    month=7,
    day=1,
    observance=weekend_to_monday,
)
# Civic Holiday
CivicHoliday = Holiday(
    "Civic Holiday",
    month=8,
    day=1,
    offset=DateOffset(weekday=MO(1)),
)
# Labor Day
LaborDay = Holiday(
    "Labor Day",
    month=9,
    day=1,
    offset=DateOffset(weekday=MO(1)),
)
# Canadian Thanksgiving
CanadianThanksgiving = Holiday(
    "Canadian Thanksgiving",
    month=10,
    day=1,
    offset=DateOffset(weekday=MO(2)),
)

ChristmasEveEarlyClose2010Onwards = Holiday(
    "Christmas Eve Early Close",
    month=12,
    day=24,
    days_of_week=(MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY),
    start_date=pd.Timestamp("2010-01-01"),
)

Christmas = christmas()

WeekendChristmas = weekend_christmas()

BoxingDay = boxing_day()

WeekendBoxingDay = weekend_boxing_day()

September11ClosingsCanada = pd.date_range("2001-09-11", "2001-09-12")


class XTSEExchangeCalendar(ExchangeCalendar):
    """
    Exchange calendar for the Toronto Stock Exchange (XTSE).

    Open Time: 9:30 AM, EST
    Close Time: 4:00 PM, EST

    Regularly-Observed Holidays:
    - New Years Day (observed on first business day on/after)
    - Family Day (Third Monday in February, starting in 2008)
    - Good Friday
    - Victoria Day (Monday before May 25th)
    - Canada Day (July 1st, observed first business day after)
    - Civic Holiday (First Monday in August)
    - Labor Day (First Monday in September)
    - Thanksgiving (Second Monday in October)
    - Christmas Day
        - Dec. 26th if Christmas is on a Sunday
        - Dec. 27th if Christmas is on a weekend
    - Boxing Day
        - Dec. 27th if Christmas is on a Sunday
        - Dec. 28th if Boxing Day is on a weekend

    Early closes:
    - Starting in 2010, if Christmas Eve falls on a weekday, the market
      closes at 1:00 pm that day. If it falls on a weekend, there is no
      early close.
    """

    regular_early_close = time(13)

    name = "XTSE"

    tz = timezone("America/Toronto")

    open_times = ((None, time(9, 30)),)

    close_times = ((None, time(16)),)

    @property
    def regular_holidays(self):
        return HolidayCalendar(
            [
                XTSENewYearsDay,
                FamilyDay,
                GoodFriday,
                VictoriaDay,
                CanadaDay,
                CivicHoliday,
                LaborDay,
                CanadianThanksgiving,
                Christmas,
                WeekendChristmas,
                BoxingDay,
                WeekendBoxingDay,
            ]
        )

    @property
    def adhoc_holidays(self):
        # NOTE: change the name of this property
        return list(chain(September11ClosingsCanada))

    @property
    def special_closes(self):
        return [
            (
                self.regular_early_close,
                HolidayCalendar([ChristmasEveEarlyClose2010Onwards]),
            )
        ]
