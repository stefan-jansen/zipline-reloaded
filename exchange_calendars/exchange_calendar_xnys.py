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
from itertools import chain

from pandas import DatetimeIndex
from pandas.tseries.holiday import GoodFriday, USLaborDay
from pytz import UTC, timezone

from .exchange_calendar import HolidayCalendar, ExchangeCalendar
from .us_holidays import (
    August45VictoryOverJapan,
    Christmas,
    ChristmasBefore1954,
    ChristmasEveBefore1993,
    ChristmasEveInOrAfter1993,
    ChristmasEvesAdhoc,
    DayAfterChristmasAdhoc,
    DayAfterIndependenceDayAdhoc,
    DayBeforeDecorationAdhoc,
    FirstLunarLandingClosing,
    FridayAfterIndependenceDayPre2013,
    HurricaneGloriaClosing,
    HurricaneSandyClosings,
    LincolnsBirthDayAdhoc,
    March33BankHoliday,
    MonTuesThursBeforeIndependenceDay,
    NewYorkCityBlackout77,
    November29BacklogRelief,
    PaperworkCrisis68,
    September11Closings,
    USBlackFridayBefore1993,
    USBlackFridayInOrAfter1993,
    USColumbusDayBefore1954,
    USElectionDay1848to1967,
    USElectionDay1968to1980,
    USIndependenceDay,
    USIndependenceDayBefore1954,
    USLincolnsBirthDayBefore1954,
    USMartinLutherKingJrAfter1998,
    USMemorialDay,
    USMemorialDay1964to1969,
    USMemorialDayBefore1964,
    USNationalDaysofMourning,
    USNewYearsDay,
    USPresidentsDay,
    USThanksgivingDay,
    USThanksgivingDay1939to1941,
    USThanksgivingDayBefore1939,
    USVeteransDay1934to1953,
    USWashingtonsBirthDay1964to1970,
    USWashingtonsBirthDayBefore1964,
    WeatherSnowClosing,
    WednesdayBeforeIndependenceDayPost2013,
)

# Useful resources for making changes to this file:
# http://www.nyse.com/pdfs/closings.pdf
# http://www.stevemorse.org/jcal/whendid.html


class XNYSExchangeCalendar(ExchangeCalendar):
    """
    Regularly-Observed Holidays:
    - New Years Day (observed on monday when Jan 1 is a Sunday)
    - Martin Luther King Jr. Day (3rd Monday in January, only after 1998)
    - Lincoln's Birthday (February 12th, only before 1954)
    - Washington's Birthday (February 22nd, before 1971 with rule change in
      1964)
    - Washington's Birthday (aka President's Day, 3rd Monday in February,
      after 1970)
    - Good Friday (two days before Easter Sunday)
    - Memorial Day (May 30th, before 1970, with rule change in 1964)
    - Memorial Day (last Monday in May, after 1970)
    - Independence Day (July 4th Sunday to Monday, before 1954)
    - Independence Day (observed on the nearest weekday to July 4th, after
      1953)
    - Election Day (First Tuesday starting on November 2nd, between 1848 and
      1967)
    - Election Day (Every four years, first Tuesday starting on November 2nd,
      between 1968 and 1980)
    - Veterans Day (November 11th, between 1934 and 1953)
    - Columbus Day (October 12th, before 1954)
    - Labor Day (first Monday in September)
    - Thanksgiving (last Thursday in November, before 1939)
    - Thanksgiving (second to last Thursday in November, between 1939 and 1941)
    - Thanksgiving (fourth Thursday in November, after 1941)
    - Christmas (December 25th, Sunday to Monday, before 1954)
    - Christmas (observed on nearest weekday to December 25, after 1953)

    NOTE: The NYSE does not observe the following US Federal Holidays:
    - Columbus Day (after 1953)
    - Veterans Day (after 1953)

    Regularly-Observed Early Closes:
    - July 3rd (Mondays, Tuesdays, and Thursdays, 1995 onward)
    - July 5th (Fridays, 1995 onward, except 2013)
    - Christmas Eve (except on Fridays, when the exchange is closed entirely)
    - Day After Thanksgiving (aka Black Friday, observed from 1992 onward)

    NOTE: Until 1993, the standard early close time for the NYSE was 2:00 PM.
    From 1993 onward, it has been 1:00 PM.

    Additional Irregularities:
    - Closed on 11/1/1929 and 11/29/1929 for backlog relief.
    - Closed between 3/6/1933 and 3/14/1933 due to bank holiday.
    - Closed on 8/15/1945 and 8/16/1945 following victory over Japan.
    - Closed on Christmas Eve in 1945 and 1946.
    - Closed on December 26th in 1958.
    - Closed the day before Memorial Day in 1961.
    - Closed on 11/25/1963 due to John F. Kennedy's death.
    - Closed for Lincoln's Birthday in 1968.
    - Closed a number of days between June 12th and  December 24th in 1968
      due to paperwork crisis.
    - Closed on 4/9/1968 due to Martin Luther King's death.
    - Closed the day after Independence Day in 1968.
    - Closed on 2/10/1969 due to weather (snow).
    - Closed on 3/31/1969 due to Dwight D. Eisenhower's death.
    - Closed on 7/21/1969 following the first lunar landing.
    - Closed on 12/28/1972 due to Harry S. Truman's death.
    - Closed on 1/25/1973 due to Lyndon B. Johnson's death.
    - Closed on 7/14/1977 due to New York City blackout.
    - Closed on 9/27/1985 due to Hurricane Gloria.
    - Closed on 4/27/1994 due to Richard Nixon's death.
    - Closed from 9/11/2001 to 9/16/2001 due to terrorist attacks in NYC.
    - Closed on 6/11/2004 due to Ronald Reagan's death.
    - Closed on 1/2/2007 due to Gerald Ford's death.
    - Closed on 10/29/2012 and 10/30/2012 due to Hurricane Sandy.
    - Closed on 12/5/2018 due to George H.W. Bush's death.
    - Closed at 1:00 PM on Wednesday, July 3rd, 2013
    - Closed at 1:00 PM on Friday, December 31, 1999
    - Closed at 1:00 PM on Friday, December 26, 1997
    - Closed at 1:00 PM on Friday, December 26, 2003

    NOTE: The exchange was **not** closed early on Friday December 26, 2008,
    nor was it closed on Friday December 26, 2014. The next Thursday Christmas
    will be in 2025.  If someone is still maintaining this code in 2025, then
    we've done alright...and we should check if it's a half day.
    """

    regular_early_close = time(13)

    name = "XNYS"

    tz = timezone("America/New_York")

    open_times = ((None, time(9, 30)),)

    close_times = ((None, time(16)),)

    @property
    def regular_holidays(self):
        return HolidayCalendar(
            [
                USNewYearsDay,
                USMartinLutherKingJrAfter1998,
                USLincolnsBirthDayBefore1954,
                USWashingtonsBirthDayBefore1964,
                USWashingtonsBirthDay1964to1970,
                USPresidentsDay,
                GoodFriday,
                USMemorialDayBefore1964,
                USMemorialDay1964to1969,
                USMemorialDay,
                USIndependenceDayBefore1954,
                USIndependenceDay,
                USLaborDay,
                USThanksgivingDayBefore1939,
                USThanksgivingDay1939to1941,
                USThanksgivingDay,
                USElectionDay1848to1967,
                USElectionDay1968to1980,
                USVeteransDay1934to1953,
                USColumbusDayBefore1954,
                ChristmasBefore1954,
                Christmas,
            ]
        )

    @property
    def adhoc_holidays(self):
        return list(
            chain(
                November29BacklogRelief,
                March33BankHoliday,
                August45VictoryOverJapan,
                ChristmasEvesAdhoc,
                DayAfterChristmasAdhoc,
                DayBeforeDecorationAdhoc,
                LincolnsBirthDayAdhoc,
                PaperworkCrisis68,
                DayAfterIndependenceDayAdhoc,
                WeatherSnowClosing,
                FirstLunarLandingClosing,
                September11Closings,
                NewYorkCityBlackout77,
                HurricaneGloriaClosing,
                HurricaneSandyClosings,
                USNationalDaysofMourning,
            )
        )

    @property
    def special_closes(self):
        return [
            (
                self.regular_early_close,
                HolidayCalendar(
                    [
                        MonTuesThursBeforeIndependenceDay,
                        FridayAfterIndependenceDayPre2013,
                        WednesdayBeforeIndependenceDayPost2013,
                        USBlackFridayInOrAfter1993,
                        ChristmasEveInOrAfter1993,
                    ]
                ),
            ),
            (
                time(14),
                HolidayCalendar(
                    [
                        ChristmasEveBefore1993,
                        USBlackFridayBefore1993,
                    ]
                ),
            ),
        ]

    @property
    def special_closes_adhoc(self):
        return [
            (
                self.regular_early_close,
                DatetimeIndex(
                    [
                        "1997-12-26",
                        "1999-12-31",
                        "2003-12-26",
                    ],
                    tz=UTC,
                ),
            )
        ]
