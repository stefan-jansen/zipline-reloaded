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

from datetime import time
from itertools import chain

import pandas as pd
from pandas.tseries.holiday import MO, DateOffset, GoodFriday, Holiday
from pytz import timezone

from .common_holidays import (
    all_saints_day,
    christmas,
    christmas_eve,
    european_labour_day,
    maundy_thursday,
    new_years_day,
    new_years_eve,
)
from .lunisolar_holidays import chinese_lunar_new_year_dates
from .exchange_calendar import FRIDAY, HolidayCalendar, ExchangeCalendar


def only_friday(dt):
    """
    Only keeps the holidays that fall on a Friday.  Useful
    for defining holidays that add a Friday to make a 4-day weekend
    when falling on a Thursday.
    """
    return dt[dt.weekday == FRIDAY]


# All pre-2011 holidays are pre-computed, so we define Holidays starting
# in 2011.
NewYearsDay = new_years_day(start_date="2011")

# Chinese New Year's only observed after 2011
ChineseNewYear = chinese_lunar_new_year_dates

ChineseNewYearAfter2011 = ChineseNewYear[ChineseNewYear.year > 2011]

PeoplePowerRevolution = Holiday(
    "People Power Revolution",
    month=2,
    day=25,
    start_date="2016",
)

ArawNgKagitingan = Holiday(
    "Araw Ng Kagitingan",
    month=4,
    day=9,
    start_date="2011",
)

MaundyThursday = maundy_thursday(start_date="2011")

LabourDay = european_labour_day(start_date="2011")

IndependenceDay = Holiday(
    "Independence Day",
    month=6,
    day=12,
    start_date="2011",
)

NinoyAquinoDay = Holiday(
    "Ninoy Aquino Day",
    month=8,
    day=21,
    start_date="2011",
)

NationalHeroesDay = Holiday(
    "National Heroes Day",
    month=8,
    day=31,
    offset=DateOffset(weekday=MO(-1)),
    start_date="2011",
)

AllSaintsDay = all_saints_day(start_date="2011")

AllSaintsDayExtra = Holiday(
    "Friday after All Saint's Day",
    month=11,
    day=2,
    start_date="2011",
    observance=only_friday,
)

BonifacioDay = Holiday(
    "Bonifacio Day",
    month=11,
    day=30,
    start_date="2011",
)

ChristmasEve = christmas_eve(start_date="2011")

Christmas = christmas(start_date="2011")

RizalDay = Holiday(
    "Rizal Day",
    month=12,
    day=30,
    start_date="2011",
)

NewYearsEve = new_years_eve(start_date="2011")

# These dates were initially calculated using the ummalqura Python
# package (https://pypi.org/project/ummalqura/), and then tweaked
# to fit Philippines' observance of Eid al-Fitr.  Other countries that
# observe Eid al-Fitr might use slightly different dates
philippines_eid_al_fitr = pd.to_datetime(
    [
        "2011-08-30",
        "2012-08-20",
        "2013-08-09",
        "2014-07-29",
        "2015-07-17",
        "2016-07-06",
        "2017-06-26",
        "2018-06-15",
        "2019-06-05",
    ]
)

# These dates were initially calculated using the ummalqura Python
# package (https://pypi.org/project/ummalqura/), and then tweaked
# to fit Philippines' observance of Eid al-Adha.  Other countries that
# observe Eid al-Adha might use slightly different dates
philippines_eid_al_adha = pd.to_datetime(
    [
        "2011-11-07",
        "2012-10-26",
        "2013-10-15",
        "2014-10-06",
        "2015-09-25",
        "2016-09-12",
        "2017-09-01",
        "2018-08-21",
        "2019-08-12",
    ]
)


class XPHSExchangeCalendar(ExchangeCalendar):
    """
    Exchange calendar for the Philippine Stock Exchange (XPHS).

    Open Time: 9:30 AM, PHT
    Close Time: 3:30 PM, PHT

    Regularly-Observed Holidays:
    - New Year's Day
    - Chinese New Year's Day
    - Araw Ng Kagitingan (Apr 9)
    - Maundy Thursday (Thurs before Easter)
    - Good Friday (Friday before Easter)
    - Labour Day (May 1)
    - Eid-ul-Fitr (Islamic Lunar Calendar)
    - Independence Day (Jun 12)
    - Eid-al-Adha
    - Ninoy Aquino Day (Aug 21)
    - National Heroes' Day (last Monday of August)
    - All Saint's Day (Nov 1)
    - Bonifacio Day (Nov 30)
    - Christmas Eve (Dec 24)
    - Christmas Day (Dec 25)
    - Rizal Day (Dec 30)
    - New Year's Eve (Dec 31)


    Early Closes:
    - None
    """

    name = "XPHS"

    tz = timezone("Asia/Manila")

    open_times = ((None, time(9, 30)),)

    close_times = ((None, time(15, 30)),)

    @property
    def regular_holidays(self):
        return HolidayCalendar(
            [
                NewYearsDay,
                PeoplePowerRevolution,
                ArawNgKagitingan,
                MaundyThursday,
                GoodFriday,
                LabourDay,
                IndependenceDay,
                NinoyAquinoDay,
                NationalHeroesDay,
                AllSaintsDay,
                AllSaintsDayExtra,
                BonifacioDay,
                ChristmasEve,
                Christmas,
                RizalDay,
                NewYearsEve,
            ]
        )

    @property
    def adhoc_holidays(self):
        misc_adhoc = [
            "2017-04-28",
            "2017-10-16",
            "2015-11-18",
            "2015-11-19",
            "2013-08-19",
            "2013-08-20",
            "2013-10-28",
            "2011-06-20",
            # Election Day
            "2019-05-13",
            "2018-05-14",
            "2016-05-09",
            "2013-05-13",
            # Typhoon
            "2017-09-12",
            "2014-12-08",
            "2014-09-19",
            "2014-07-16",
            "2012-08-07",
            "2011-09-27",
            # Pope's Visit
            "2015-01-15",
            "2015-01-16",
            # Christmas Makeups
            "2017-12-26",
            "2016-12-26",
            "2014-12-26",
            # New Years Makeups
            "2018-01-02",
            "2017-01-02",
            "2015-01-02",
            # Other Makeups
            "2017-10-31",  # All Saint's Makeup
            "2016-10-31",  # All Saint's Makeup
            "2011-10-31",  # All Saint's Makeup
        ]

        # Before 2011, there are a few holidays that follow makeup day
        # rules that are inconsistent/challenging to model. Starting
        # in 2011, the rules become much more consistent. For convenience
        # we are hardcoding pre-2011 holidays and defining holidays in
        # 2011-present
        pre_2011_holidays = [
            "2002-01-01",
            "2002-02-25",
            "2002-03-28",
            "2002-03-29",
            "2002-04-08",
            "2002-05-01",
            "2002-06-12",
            "2002-07-15",
            "2002-10-31",
            "2002-11-01",
            "2002-12-06",
            "2002-12-24",
            "2002-12-25",
            "2002-12-30",
            "2002-12-31",
            "2003-01-01",
            "2003-02-25",
            "2003-04-07",
            "2003-04-17",
            "2003-04-18",
            "2003-05-01",
            "2003-05-02",
            "2003-06-13",
            "2003-08-22",
            "2003-11-26",
            "2003-12-24",
            "2003-12-25",
            "2003-12-26",
            "2003-12-31",
            "2004-01-01",
            "2004-01-02",
            "2004-02-25",
            "2004-04-07",
            "2004-04-08",
            "2004-04-09",
            "2004-05-10",
            "2004-11-01",
            "2004-11-15",
            "2004-11-29",
            "2004-12-03",
            "2004-12-24",
            "2004-12-27",
            "2004-12-30",
            "2004-12-31",
            "2005-02-25",
            "2005-03-23",
            "2005-03-24",
            "2005-03-25",
            "2005-05-02",
            "2005-06-13",
            "2005-07-25",
            "2005-08-29",
            "2005-10-31",
            "2005-11-01",
            "2005-11-04",
            "2005-11-28",
            "2005-12-26",
            "2005-12-30",
            "2006-04-13",
            "2006-04-14",
            "2006-05-01",
            "2006-06-12",
            "2006-07-24",
            "2006-08-21",
            "2006-09-28",
            "2006-09-29",
            "2006-10-24",
            "2006-11-01",
            "2006-12-01",
            "2006-12-25",
            "2006-12-26",
            "2007-01-01",
            "2007-04-05",
            "2007-04-06",
            "2007-04-09",
            "2007-05-01",
            "2007-05-14",
            "2007-06-11",
            "2007-08-20",
            "2007-08-27",
            "2007-10-12",
            "2007-10-29",
            "2007-11-01",
            "2007-11-02",
            "2007-11-30",
            "2007-12-24",
            "2007-12-25",
            "2007-12-31",
            "2008-01-01",
            "2008-02-25",
            "2008-03-20",
            "2008-03-21",
            "2008-04-07",
            "2008-05-01",
            "2008-06-09",
            "2008-08-18",
            "2008-08-25",
            "2008-10-01",
            "2008-12-01",
            "2008-12-25",
            "2008-12-26",
            "2008-12-29",
            "2008-12-30",
            "2008-12-31",
            "2009-01-01",
            "2009-01-02",
            "2009-04-06",
            "2009-04-09",
            "2009-04-10",
            "2009-05-01",
            "2009-06-12",
            "2009-07-17",
            "2009-08-05",
            "2009-08-21",
            "2009-08-31",
            "2009-09-07",
            "2009-09-21",
            "2009-11-02",
            "2009-11-30",
            "2009-12-24",
            "2009-12-25",
            "2009-12-30",
            "2009-12-31",
            "2010-01-01",
            "2010-04-01",
            "2010-04-02",
            "2010-04-09",
            "2010-05-03",
            "2010-05-10",
            "2010-06-14",
            "2010-06-30",
            "2010-08-30",
            "2010-09-10",
            "2010-10-25",
            "2010-11-01",
            "2010-11-16",
            "2010-11-29",
            "2010-12-24",
            "2010-12-27",
            "2010-12-31",
        ]

        return list(
            chain(
                misc_adhoc,
                pre_2011_holidays,
                ChineseNewYearAfter2011,
                philippines_eid_al_adha,
                philippines_eid_al_fitr,
            )
        )
