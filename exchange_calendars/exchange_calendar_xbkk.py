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

from pytz import timezone

from .exchange_calendar import HolidayCalendar, ExchangeCalendar
from .xbkk_holidays import (
    ChakriMemorialDay,
    ChulalongkornDay,
    CoronationDay2016AndBefore,
    CoronationDay2019AndAfter,
    HalfYearHoliday,
    HMKingsBirthday,
    HMQueenMothersBirthday,
    HMQueensBirthday,
    KingBhumibolsBirthday,
    LabourDay,
    NewYearsDay,
    NewYearsEve,
    SongkranFestival1,
    SongkranFestival2,
    SongkranFestival3,
    ThailandConstitutionDay,
    ThePassingOfKingBhumibol,
    asanha_bucha,
    asanha_bucha_bridge_days,
    coronation_bridge_days,
    makha_bucha,
    misc_adhoc,
    new_years_bridge_days,
    queens_birthday_bridge_days,
    vesak,
    vesak_bridge_days,
)


class XBKKExchangeCalendar(ExchangeCalendar):
    """
    Calendar for the Stock Exchange of Thailand in Bangkok.

    Open Time: 10:00 AM, Indochina Time (ICT)
    Close Time: 4:30 PM, Indochina Time (ICT)

    Regularly-Observed Holidays:
      - New Year's Day
      - Makha Bucha
      - Chakri Memorial Day
      - Songkran Festival
      - Labour Day
      - Coronation Day
      - Vesak
      - Her Majesty The Queen's Birthday
      - Asanha Bucha
      - His Majesty The King's Birthday
      - Her Majesty The Queen Mother's Birthday
      - The Passing of King Bhumibol
      - Chulalongkorn Day
      - King Bhumibol's Birthday
      - Thailand Constitution Day
      - New Year's Eve

    Early Closes:
      - None
    """

    name = "XBKK"

    tz = timezone("Asia/Bangkok")

    open_times = ((None, time(10)),)

    close_times = ((None, time(16, 30)),)

    @property
    def regular_holidays(self):
        return HolidayCalendar(
            [
                NewYearsDay,
                ChakriMemorialDay,
                SongkranFestival1,
                SongkranFestival2,
                SongkranFestival3,
                LabourDay,
                CoronationDay2016AndBefore,
                CoronationDay2019AndAfter,
                HMQueensBirthday,
                HMKingsBirthday,
                HMQueenMothersBirthday,
                HalfYearHoliday,
                ThePassingOfKingBhumibol,
                ChulalongkornDay,
                KingBhumibolsBirthday,
                ThailandConstitutionDay,
                NewYearsEve,
            ]
        )

    @property
    def adhoc_holidays(self):
        return list(
            chain(
                makha_bucha,
                vesak,
                asanha_bucha,
                new_years_bridge_days,
                asanha_bucha_bridge_days,
                queens_birthday_bridge_days,
                coronation_bridge_days,
                vesak_bridge_days,
                misc_adhoc,
            ),
        )
