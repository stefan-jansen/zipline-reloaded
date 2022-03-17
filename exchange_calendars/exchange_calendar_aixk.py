from datetime import time
from itertools import chain

import pandas as pd
from pandas.tseries.holiday import (
    Holiday,
    next_monday,
    nearest_workday,
    next_workday,
)
from pytz import timezone

from .common_holidays import new_years_day, eid_al_adha_first_day
from .exchange_calendar import (
    HolidayCalendar,
    ExchangeCalendar,
)


NewYearsDay = new_years_day()

NewYearHoliday = Holiday(
    "New Year Holiday",
    month=1,
    day=2,
)

OrthodoxChristmasDay = Holiday(
    "Orthodox Christmas Day",
    month=1,
    day=7,
)

InternationalWomensDay = Holiday(
    "International Women's Day",
    month=3,
    day=8,
    observance=nearest_workday,
)

NauryzHoliday1 = Holiday(
    "Nauryz Holiday",
    month=3,
    day=21,
    observance=next_monday,
)

NauryzHoliday2 = Holiday(
    "Nauryz Holiday",
    month=3,
    day=21,
    observance=lambda dt: next_workday(next_monday(dt)),
)

NauryzHoliday3 = Holiday(
    "Nauryz Holiday",
    month=3,
    day=21,
    observance=lambda dt: next_workday(next_workday(next_monday(dt))),
)

KazakhstanPeopleSolidarityDay = Holiday(
    "Kazakhstan People Solidarity Day",
    month=5,
    day=1,
    observance=next_monday,
)

DefendersDay = Holiday(
    "Defender's Day",
    month=5,
    day=7,
    observance=next_monday,
    start_date=pd.Timestamp("2013-01-01"),
)

VictoryDayHoliday = Holiday(
    "Victory Day Holiday",
    month=5,
    day=9,
    observance=nearest_workday,
)

CapitalCityDay = Holiday(
    "Capital City Day",
    month=7,
    day=6,
    observance=next_monday,
)

ConstitutionDay = Holiday(
    "Constitution Day",
    month=8,
    day=30,
    observance=next_monday,
)

FirstPresidentDay = Holiday(
    "First President Day",
    month=12,
    day=1,
    observance=next_monday,
    start_date=pd.Timestamp("2013-01-01"),
)

IndependenceDay = Holiday(
    "Independence Day",
    month=12,
    day=16,
    observance=next_monday,
)

IndependenceDayHoliday = Holiday(
    "Independence Day",
    month=12,
    day=17,
    observance=next_monday,
)


class AIXKExchangeCalendar(ExchangeCalendar):
    """
    Exchange calendar for the Astana International Exchange (XIST).
                Available here: https://www.aix.kz/trading/trading-calendar/


    Regularly-Observed Holidays:
      - New Year's Day
      - New Year Holiday
      - Orthodox Christmas Day
      - International Women's Day
      - Nauryz Holiday
      - Nauryz Holiday
      - Nauryz Holiday
      - Kazakhstan People Solidarity Day
      - Defender’s Day
      - Victory Day Holiday
      - Capital City Day
      - Capital City Day
      - Kurban Ait Holiday (Eid-al-Adha)
      - Constitution Day
      - First President Day
      - Independence Day
      - Independence Day Holiday
    Early Closes:
      - None
    """

    name = "AIXK"

    tz = timezone("Asia/Almaty")

    open_times = ((None, time(11)),)

    close_times = ((None, time(17, 00)),)

    @property
    def bound_start(self) -> pd.Timestamp:
        return pd.Timestamp("2017-01-01", tz="UTC")

    def _bound_start_error_msg(self, start: pd.Timestamp) -> str:
        msg = super()._bound_start_error_msg(start)
        return msg + f" (The exchange {self.name} was founded in 2017.)"

    @property
    def regular_holidays(self):
        return HolidayCalendar(
            [
                NewYearsDay,
                NewYearHoliday,
                OrthodoxChristmasDay,
                InternationalWomensDay,
                NauryzHoliday1,
                NauryzHoliday2,
                NauryzHoliday3,
                KazakhstanPeopleSolidarityDay,
                DefendersDay,
                VictoryDayHoliday,
                CapitalCityDay,
                ConstitutionDay,
                FirstPresidentDay,
                IndependenceDay,
                IndependenceDayHoliday,
            ]
        )

    @property
    def adhoc_holidays(self):
        # It is common in Kazakhstan to have holidays also on days
        # between regular holiday and weekend
        misc_holidays = [
            # Bridge Day between Women's day - Weekend
            pd.Timestamp("2018-03-09"),
            # Bridge Day between Weekend - Kazakhstan People Solidarity Day
            pd.Timestamp("2018-04-30"),
            # Bridge Day between Defender's Day - Victory Day
            pd.Timestamp("2018-05-08"),
            # Bridge Day between Constitution Day - Weekend
            pd.Timestamp("2018-08-31"),
            # Bridge Day between New Year's Eve - New Year's day
            pd.Timestamp("2018-12-31"),
            # Bridge Day between Victory Day - Weekend
            pd.Timestamp("2019-05-10"),
            # Bridge Day between New Year's day - Weekend
            pd.Timestamp("2020-01-03"),
            # Bridge Day between Independence day - Weekend
            pd.Timestamp("2020-12-18"),
            # Bridge Day between Weekend - Capital City day
            pd.Timestamp("2021-06-05"),
            # Bridge Day between Weekend - Women's day
            pd.Timestamp("2022-03-07"),
        ]
        return list(chain(misc_holidays, eid_al_adha_first_day))
