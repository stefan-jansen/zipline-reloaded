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

from pandas.tseries.holiday import (
    MO,
    DateOffset,
    Easter,
    GoodFriday,
    Holiday,
    previous_friday,
)
from pandas.tseries.offsets import Day
from pytz import timezone

from .common_holidays import (
    christmas,
    epiphany,
    european_labour_day,
    immaculate_conception,
    maundy_thursday,
    new_years_day,
    new_years_eve,
)
from .exchange_calendar import HolidayCalendar, ExchangeCalendar

# Used for "first Monday on or after date"
next_monday_offset = DateOffset(weekday=MO(1))

NewYearsDay = new_years_day()

Epiphany = epiphany(offset=next_monday_offset)

StJosephsDay = Holiday(
    "St. Joseph's Day (next Monday)",
    month=3,
    day=19,
    offset=next_monday_offset,
)

MaundyThursday = maundy_thursday()

LabourDay = european_labour_day()

MondayAfterAscensionDay = Holiday(
    "Monday After Ascension Day",
    month=1,
    day=1,
    offset=[Easter(), Day(43)],
)

MondayAfterCorpusChristi = Holiday(
    "Monday After Corpus Christi",
    month=1,
    day=1,
    offset=[Easter(), Day(64)],
)

MondayAfterSacredHeart = Holiday(
    "Monday After Sacred Heart",
    month=1,
    day=1,
    offset=[Easter(), Day(71)],
)

StPeterAndStPaulDay = Holiday(
    "St. Peter and St. Paul Day", month=6, day=29, offset=next_monday_offset
)

ColombiaIndependenceDay = Holiday(
    "Colombian Independence Day",
    month=7,
    day=20,
)

BattleOfBoyaca = Holiday(
    "Battle of Boyaca",
    month=8,
    day=7,
)

AssumptionDay = Holiday(
    "Assumption Day (next Monday)",
    month=8,
    day=15,
    offset=next_monday_offset,
)

DiaDeLaRaza = Holiday(
    "Dia de la Raza",
    month=10,
    day=12,
    offset=next_monday_offset,
)

AllSaintsDay = Holiday(
    "All Saint's Day (next Monday)",
    month=11,
    day=1,
    offset=next_monday_offset,
)

CartagenaIndependenceDay = Holiday(
    "Cartagena Independence Day",
    month=11,
    day=11,
    offset=next_monday_offset,
)

ImmaculateConception = immaculate_conception()

ChristmasDay = christmas()

LastTradingDay = new_years_eve(observance=previous_friday)


class XBOGExchangeCalendar(ExchangeCalendar):
    """
    Exchange calendar for the Colombia Stock Exchange (XBOG).

    Open Time: 9:30 AM, EST
    Close Time: 4:00 PM, EST

    Regularly-Observed Holidays:
    - New Years Day
    - Epiphany
    - St. Joseph's Day (first Monday on/after March 19)
    - Maundy Thursday (Thursday before Easter)
    - Good Friday
    - Labour Day (May 1)
    - Ascension Day (first Monday >= 39 days after Easter Sunday)
    - Corpus Christi (first Monday >= 60 days after Easter Sunday)
    - Sacred Heart (first Monday >= 68 days after Easter Sunday)
    - Saint Peter and Saint Paul Day (first Monday on or after June 29)
    - Independence Day (July 20)
    - Battle of Boyaca (August 7)
    - Assumption Day (first Monday on or after August 15)
    - Columbus Day (first Monday on or after October 12)
    - All Saint's Day (first Monday on or after November 1)
    - Cartagena Independence Day (November 11)
    - Immaculate Conception (December 8)
    - Christmas Day

    Early Closes:
    - None
    """

    name = "XBOG"

    # Though Bogota uses Colombia Standard Time, XBOG uses
    # US Eastern for trading times
    tz = timezone("America/New_York")

    open_times = ((None, time(9, 30)),)

    close_times = ((None, time(16)),)

    @property
    def regular_holidays(self):
        return HolidayCalendar(
            [
                NewYearsDay,
                Epiphany,
                StJosephsDay,
                MaundyThursday,
                GoodFriday,
                LabourDay,
                MondayAfterAscensionDay,
                MondayAfterCorpusChristi,
                MondayAfterSacredHeart,
                StPeterAndStPaulDay,
                ColombiaIndependenceDay,
                BattleOfBoyaca,
                AssumptionDay,
                DiaDeLaRaza,
                AllSaintsDay,
                CartagenaIndependenceDay,
                ImmaculateConception,
                ChristmasDay,
                LastTradingDay,
            ]
        )
