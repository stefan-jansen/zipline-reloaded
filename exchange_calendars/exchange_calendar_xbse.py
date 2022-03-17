from datetime import time, timedelta
from itertools import chain

from pandas.tseries.holiday import Holiday
from pytz import timezone

from .common_holidays import (
    christmas,
    european_labour_day,
    new_years_day,
    orthodox_easter,
)
from .exchange_calendar import HolidayCalendar, ExchangeCalendar

NewYearsDay = new_years_day()

DayAfterNewYearsDay = Holiday("Day After New Year's Day", month=1, day=2)

RomanianPrincipalitiesUnificationDay = Holiday(
    "Romanian Principalities Unification Day", month=1, day=24
)

OrthodoxGoodFriday = orthodox_easter() - timedelta(2)

OrthodoxEasterMonday = orthodox_easter() + timedelta(1)

LabourDay = european_labour_day()


ChildrensDay = Holiday(
    "Children's Day",
    month=6,
    day=1,
)

OrthodoxPentecost = orthodox_easter() + timedelta(49)

DescentOfTheHolySpirit = orthodox_easter() + timedelta(50)

StMarysDay = Holiday(
    "St. Mary's day",
    month=8,
    day=15,
)

StAndrewsDay = Holiday(
    "St. Andrew's day",
    month=11,
    day=30,
)

NationalDay = Holiday(
    "National Day",
    month=12,
    day=1,
)

ChristmasDay = christmas()

SecondDayOfChristmas = Holiday(
    "Second Day of Christmas",
    month=12,
    day=26,
)


class XBSEExchangeCalendar(ExchangeCalendar):
    """
    Exchange calendar for the BUCHAREST Stock Exchange (XBSE).

    Open Time: 10:00 AM, EET
    Close Time: 5:45 PM, EET

    Regularly-Observed Holidays:
      - New Year's Day
      - Day after New Year's Day
      - Romanian Principalities Unification Day
      - Orthodox Good Friday
      - Orthodox Easter
      - Labour Day
      - Orthodox Pentecost
      - Children's Day
      - Assumption of Virgin Mary
      - St Andrew's day
      - Christmas
      - Day after Christmas

    Early Closes:
      - None
    """

    name = "XBSE"

    tz = timezone("Europe/Bucharest")

    open_times = ((None, time(10)),)

    close_times = ((None, time(17, 45)),)

    @property
    def regular_holidays(self):
        return HolidayCalendar(
            [
                NewYearsDay,
                DayAfterNewYearsDay,
                RomanianPrincipalitiesUnificationDay,
                LabourDay,
                ChildrensDay,
                StMarysDay,
                StAndrewsDay,
                NationalDay,
                ChristmasDay,
                SecondDayOfChristmas,
            ]
        )

    @property
    def adhoc_holidays(self):
        return list(
            chain(
                OrthodoxGoodFriday,
                OrthodoxEasterMonday,
                OrthodoxPentecost,
                DescentOfTheHolySpirit,
            )
        )
