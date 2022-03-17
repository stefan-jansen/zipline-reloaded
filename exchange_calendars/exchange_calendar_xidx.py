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
from pandas.tseries.holiday import GoodFriday, Holiday
from pytz import timezone

from .common_holidays import ascension_day, christmas, new_years_day, new_years_eve
from .lunisolar_holidays import chinese_lunar_new_year_dates
from .exchange_calendar import HolidayCalendar, ExchangeCalendar


class XIDXExchangeCalendar(ExchangeCalendar):
    """
    Exchange calendar for the Indonesia Stock Exchange (XIDX).

    Open Time: 09:00, Western Indonesian Time (WIB)
    Close Time: 15:50, Western Indonesian Time (WIB)

    Regularly-Observed Holidays:
    - New Year's Day(Jan 1)
    - Good Friday (Friday before Easter)
    - Labor Day (May 1)
    - Ascension Day Of Jesus Christ (39 days after Easter, always Thursday)
    - Pancasila Day (Jun 1)
    - Independence Day (Aug 17)
    - Christmas Day (Dec 25)
    - New Year's Eve (called "Trading Holiday", Dec 31)
    - Chinese New Year (from Gregorian year 2002 onward)
    - Islamic New Year
    - Eid al-Fitr (Festival of Breaking the Fast)
    - Eid al-Adha (Festival of the Sacrifice)
    - Isra Mikraj of the Prophet Muhammad
    - Birth of the Prophet Muhammad
    - Vesak Day
    - Hindu Saka New Year (also called Nyepi, or Balinese Day of Silence)

    Election holidays are also observed, as well as additional "common
    leave" days around many holidays.
    """

    name = "XIDX"

    tz = timezone("Asia/Jakarta")

    open_times = ((None, time(9)),)

    close_times = ((None, time(15, 50)),)

    @property
    def regular_holidays(self):
        return HolidayCalendar(
            [
                new_years_day(),
                GoodFriday,
                Holiday(
                    "Labor Day",
                    month=5,
                    day=1,
                    start_date="2014-05-01",
                ),
                # XXX: The Indonesia Stock Exchange was open on Ascension
                # Day 2003, but closed the next day. We are not sure why.
                # (The 2003-05-30 closure is listed in adhoc_holidays.)
                ascension_day(end_date="2003"),
                ascension_day(start_date="2004"),
                Holiday(
                    "Pancasila Day",
                    month=6,
                    day=1,
                    start_date="2017-06-01",
                ),
                Holiday(
                    "Independence Day",
                    month=8,
                    day=17,
                ),
                # Christmas Eve is not an official Indonesian holiday, but
                # December 24th and 26th are frequently observed as common
                # leave. These dates are listed in adhoc_holidays.
                christmas(),
                new_years_eve(),
            ]
        )

    chinese_new_year = chinese_lunar_new_year_dates[
        # The Indonesia Stock Exchange did not close for Chinese New
        # Year in 1998, 1999, or 2001. (It fell on a Saturday in 2000.)
        chinese_lunar_new_year_dates.year
        >= 2002
    ]

    common_leave = pd.to_datetime(
        [
            # Indonesia sometimes observes additional "common leave" days
            # around the usual observed dates of holidays.
            # Common leave for New Year's Day.
            "2002-12-30",
            "2005-12-30",
            "2009-01-02",
            "2017-01-02",
            # Common leave for Chinese New Year.
            "2008-02-08",
            # Common leave for Ascension Day.
            "2003-05-30",
            "2006-05-26",
            "2007-05-18",
            # Common leave for Independence Day.
            "2003-08-18",
            "2006-08-18",
            "2008-08-18",
            # Common leave for Christmas.
            "2002-12-24",
            "2002-12-26",
            "2003-12-24",
            "2003-12-26",
            "2004-12-24",
            "2005-12-26",
            "2007-12-24",
            "2009-12-24",
            "2010-12-24",
            "2011-12-26",
            "2012-12-24",
            "2013-12-26",
            "2014-12-26",
            "2016-12-26",
            "2017-12-26",
            "2018-12-24",
            "2019-12-24",
            "2020-12-24",
        ]
    )

    islamic_new_year = pd.to_datetime(
        [
            # Islamic/Hijri/Hijriyah New Year.
            # Includes common leave.
            "2002-03-15",
            "2003-03-03",
            "2004-02-23",
            "2005-02-10",
            "2006-01-31",
            "2008-01-10",  # First Islamic New Year of 2008.
            "2008-01-11",
            "2008-12-29",  # Second Islamic New Year of 2008.
            "2009-12-18",
            "2010-12-07",
            "2012-11-15",
            "2012-11-16",
            "2013-11-05",
            "2015-10-14",
            "2017-09-21",
            "2018-09-11",
            "2020-08-20",
        ]
    )

    eid_al_fitr = pd.to_datetime(
        [
            # Eid al-Fitr (Festival of Breaking the Fast).
            # Includes common leave.
            "2002-12-05",
            "2002-12-06",
            "2002-12-09",
            "2002-12-10",
            "2003-11-24",
            "2003-11-25",
            "2003-11-26",
            "2003-11-27",
            "2003-11-28",
            "2004-11-15",
            "2004-11-16",
            "2004-11-17",
            "2004-11-18",
            "2004-11-19",
            "2005-11-02",
            "2005-11-03",
            "2005-11-04",
            "2005-11-07",
            "2005-11-08",
            "2006-10-23",
            "2006-10-24",
            "2006-10-25",
            "2006-10-26",
            "2006-10-27",
            "2007-10-12",
            "2007-10-15",
            "2007-10-16",
            "2008-09-30",
            "2008-10-01",
            "2008-10-02",
            "2008-10-03",
            "2009-09-18",
            "2009-09-21",
            "2009-09-22",
            "2009-09-23",
            "2010-09-08",
            "2010-09-09",
            "2010-09-10",
            "2010-09-13",
            "2010-09-14",
            "2011-08-29",
            "2011-08-30",
            "2011-08-31",
            "2011-09-01",
            "2011-09-02",
            "2012-08-20",
            "2012-08-21",
            "2012-08-22",
            "2013-08-05",
            "2013-08-06",
            "2013-08-07",
            "2013-08-08",
            "2013-08-09",
            "2014-07-28",
            "2014-07-29",
            "2014-07-30",
            "2014-07-31",
            "2014-08-01",
            "2015-07-16",
            "2015-07-17",
            "2015-07-20",
            "2015-07-21",
            "2016-07-04",
            "2016-07-05",
            "2016-07-06",
            "2016-07-07",
            "2016-07-08",
            "2017-06-23",
            "2017-06-26",
            "2017-06-27",
            "2017-06-28",
            "2017-06-29",
            "2017-06-30",
            "2018-06-11",
            "2018-06-12",
            "2018-06-13",
            "2018-06-14",
            "2018-06-15",
            "2018-06-18",
            "2018-06-19",
            "2019-06-03",
            "2019-06-04",
            "2019-06-05",
            "2019-06-06",
            "2019-06-07",
            "2020-05-22",
            "2020-05-25",
            "2020-05-26",
            "2020-05-27",
        ]
    )

    eid_al_adha = pd.to_datetime(
        [
            # Eid al-Adha (Festival of the Sacrifice).
            # Includes common leave.
            "2002-02-22",
            "2003-02-12",
            "2004-02-02",
            "2005-01-21",
            "2006-01-10",
            "2006-12-29",
            # NOTE: Eid al-Adha occured twice in 2006, on Tuesday 01-10 and
            # Sunday 12-31. The exchange was closed on Friday 2006-12-29 as
            # a make-up holiday.
            "2007-12-20",
            "2007-12-21",
            "2008-12-08",
            "2009-11-27",
            "2009-11-28",
            "2010-11-17",
            "2012-10-26",
            "2013-10-14",
            "2013-10-15",
            "2015-09-24",
            "2016-09-12",
            "2017-09-01",
            "2018-08-22",
            "2020-07-31",
        ]
    )

    isra_mikraj = pd.to_datetime(
        [
            # Isra and Mi'raj (Ascension of the Prophet Muhammad).
            # Called "Isra Mikraj" in Indonesia.
            #
            # Occurs on 27 Rajab on the Hijri calendar, but the mapping of
            # Hijri to Gregorian dates varies. For example, in 2018 many
            # countries observed this holiday on Friday 04-13; but by
            # Indonesian reckoning it fell on Saturday 04-14 that year.
            #
            # See https://www.idx.co.id/en-us/news/trading-holiday/
            #
            # Includes common leave.
            "2002-10-04",
            "2003-09-22",
            "2004-09-13",
            "2005-09-02",
            "2006-08-21",
            "2008-07-30",
            "2009-07-20",
            "2011-06-29",
            "2012-05-18",
            "2013-06-06",
            "2014-05-27",
            "2016-05-06",
            "2017-04-24",
            "2019-04-03",
        ]
    )

    birth_of_prophet_muhammad = pd.to_datetime(
        [
            # Birth of the Prophet Muhammad.
            # Includes common leave.
            "2003-05-15",
            "2004-05-03",
            "2005-04-22",
            "2006-04-10",
            "2008-03-20",
            "2009-03-09",
            "2010-02-26",
            "2011-02-15",
            "2013-01-24",
            "2014-01-14",
            "2015-12-24",
            "2016-12-12",
            "2017-12-01",
            "2018-11-20",
            "2020-10-29",
        ]
    )

    vesak_day = pd.to_datetime(
        [
            # Vesak Day (Buddha's Birthday).
            # Sometimes called "Hari Raya Waisak" in Indonesia.
            # Includes common leave.
            "2003-05-16",
            "2004-06-03",
            "2005-05-24",
            "2007-06-01",
            "2008-05-20",
            "2010-05-28",
            "2011-05-17",
            "2014-05-15",
            "2015-06-02",
            "2017-05-11",
            "2018-05-29",
            "2020-05-07",
        ]
    )

    hindu_saka_new_year = pd.to_datetime(
        [
            # Hindu Saka New Year (also called Nyepi, or Balinese Day of Silence).
            # Includes common leave.
            "2003-04-02",
            "2004-03-22",
            "2005-03-11",
            "2006-03-30",
            "2006-03-31",
            "2007-03-19",
            "2008-03-07",
            "2009-03-26",
            "2010-03-16",
            "2012-03-23",
            "2013-03-12",
            "2014-03-31",
            "2016-03-09",
            "2017-03-28",
            "2019-03-07",
            "2020-03-25",
        ]
    )

    spontaneous_closures = pd.to_datetime(
        [
            # Trading suspension due to global financial crisis.
            "2008-10-09",
            "2008-10-10",
        ]
    )

    election_holidays = pd.to_datetime(
        [
            # Local and gubernatorial election holidays.
            "2004-04-05",
            "2004-07-05",
            "2004-09-20",
            "2009-04-09",
            "2009-07-08",
            "2014-04-09",
            "2014-07-09",
            "2015-12-09",
            "2017-02-15",
            "2017-04-19",
            "2019-04-17",
        ]
    )

    @property
    def adhoc_holidays(self):
        return list(
            chain(
                self.chinese_new_year,
                self.common_leave,
                self.islamic_new_year,
                self.eid_al_fitr,
                self.eid_al_adha,
                self.isra_mikraj,
                self.birth_of_prophet_muhammad,
                self.vesak_day,
                self.hindu_saka_new_year,
                self.spontaneous_closures,
                self.election_holidays,
            )
        )
