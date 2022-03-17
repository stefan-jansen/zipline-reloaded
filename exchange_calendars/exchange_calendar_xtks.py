from datetime import time
from itertools import chain

import pandas as pd
from pytz import UTC, timezone

from .exchange_calendar import HolidayCalendar, ExchangeCalendar
from .xtks_holidays import (
    AutumnalEquinoxes,
    ChildrensDay,
    CitizensHolidayGoldenWeek,
    CitizensHolidaySilverWeek,
    ComingOfAgeDay2000Onwards,
    ComingOfAgeDayThrough1999,
    ConstitutionMemorialDay,
    CultureDay,
    EmperorAkihitoBirthday,
    EmperorNaruhitoBirthday,
    EquityTradingSystemFailure,
    GreeneryDay2007Onwards,
    GreeneryDayThrough2006,
    HealthAndSportsDay2000OnwardsThrough2019,
    HealthAndSportsDay2020,
    HealthAndSportsDay2021,
    HealthAndSportsDay2022Onwards,
    HealthAndSportsDayThrough1999,
    LaborThanksgivingDay,
    MarineDay2003OnwardsThrough2019,
    MarineDay2020,
    MarineDay2021,
    MarineDay2022Onwards,
    MarineDayThrough2002,
    Misc2019Holidays,
    MountainDay2020,
    MountainDay2021,
    MountainDay2022Onwards,
    MountainDayThrough2019,
    NationalFoundationDay,
    NewYearsHolidayDec31,
    NewYearsHolidayJan1,
    NewYearsHolidayJan2,
    NewYearsHolidayJan3,
    RespectForTheAgedDay2003Onwards,
    RespectForTheAgedDayThrough2002,
    ShowaDay,
    VernalEquinoxes,
)


class XTKSExchangeCalendar(ExchangeCalendar):
    """
    Exchange calendar for the Tokyo Stock Exchange

    First session: 9:00am - 11:30am
    Lunch
    Second session: 12:30pm - 3:00pm

    NOTE: we are treating the two sessions per day as one session for now,
    because we will not be handling minutely data in the immediate future.

    Regularly-Observed Holidays (see xtks_holidays.py for more info):
    - New Year's Holidays (Dec. 31 - Jan. 3)
    - Coming of Age Day (second Monday of January)
    - National Foundation Day (Feb. 11)
    - Vernal Equinox (usually Mar 20-22)
    - Greenery Day (Apr. 29 2000-2006, May 4 2007-present)
    - Showa Day (Apr. 29 2007-present)
    - Constitution Memorial Day (May 3)
    - Citizen's Holiday (May 4 2000-2006, later replaced by Greenery Day)
    - Children's Day (May 5)
    - Marine Day (July 20 2000-2002, third Monday of July 2003-present)
    - Respect for the Aged Day (Sep. 15 2000-2002, third Monday
      of Sep. 2003-present)
    - Autumnal Equinox (usually Sept. 22-24)
    - Health-Sports Day (second Monday of October)
    - Culture Day (November 3)
    - Labor Thanksgiving Day (Nov. 23)
    - Emperor's Birthday (Dec. 23)

    Additional Irregularities:
    - Closed on October 1, 2020 due to equity trading system failure
    """

    name = "XTKS"

    tz = timezone("Asia/Tokyo")

    open_times = ((None, time(9)),)

    close_times = ((None, time(15)),)

    @property
    def bound_start(self) -> pd.Timestamp:
        # not tracking holiday info farther back than 1997
        return pd.Timestamp("1997-01-01", tz=UTC)

    @property
    def regular_holidays(self):
        return HolidayCalendar(
            [
                NewYearsHolidayDec31,
                NewYearsHolidayJan1,
                NewYearsHolidayJan2,
                NewYearsHolidayJan3,
                ComingOfAgeDayThrough1999,
                ComingOfAgeDay2000Onwards,
                NationalFoundationDay,
                GreeneryDayThrough2006,
                ShowaDay,
                ConstitutionMemorialDay,
                GreeneryDay2007Onwards,
                CitizensHolidayGoldenWeek,
                ChildrensDay,
                MarineDayThrough2002,
                MarineDay2003OnwardsThrough2019,
                MarineDay2020,
                MarineDay2021,
                MarineDay2022Onwards,
                MountainDayThrough2019,
                MountainDay2020,
                MountainDay2021,
                MountainDay2022Onwards,
                RespectForTheAgedDayThrough2002,
                RespectForTheAgedDay2003Onwards,
                HealthAndSportsDayThrough1999,
                HealthAndSportsDay2000OnwardsThrough2019,
                HealthAndSportsDay2020,
                HealthAndSportsDay2021,
                HealthAndSportsDay2022Onwards,
                CultureDay,
                LaborThanksgivingDay,
                EmperorAkihitoBirthday,
                EmperorNaruhitoBirthday,
            ]
        )

    @property
    def adhoc_holidays(self):
        return list(
            chain(
                VernalEquinoxes,
                AutumnalEquinoxes,
                CitizensHolidaySilverWeek,
                Misc2019Holidays,
                EquityTradingSystemFailure,
            )
        )
