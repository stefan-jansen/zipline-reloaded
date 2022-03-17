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
from .xkls_holidays import (
    ChineseNewYear,
    ChineseNewYearDay2,
    ChineseNewYearsHalfDay,
    ChristmasDay,
    Deepavali,
    EidAlAdha,
    EidAlFitrDay1,
    EidAlFitrDay2,
    EidAlFitrHalfDay,
    FederalTerritoryDay,
    LabourDay,
    MalaysiaDay,
    MuhammadBirthday,
    Muharram,
    NationalDay,
    NewYearsDay,
    NuzulAlQuran,
    Thaipusam,
    WesakDay,
    misc_adhoc,
)


class XKLSExchangeCalendar(ExchangeCalendar):
    """
    Exchange calendar for the Malaysia Stock Exchange (XKLS).

    Open Time: 9:00 AM, MYT
    Close Time: 5:00 PM, MYT

    Regularly-Observed Holidays:
    - New Year's Day
    - Thaipusam (Tamil Calendar)
    - Federal Territory Day (Feb 1)
    - Chinese New Year (2 days)
    - Labour Day (May 1)
    - Wesak Day (Chinese Lunar Calendar)
    - Nuzul Al'Quran (Islamic Lunar Calendar)
    - Eid al-Fitr (2 days)
    - Eid al-Adha
    - National Day (Aug 31)
    - Muharram (Lunar Calendar)
    - Malaysia Day (Sep 16)
    - Deepavali
    - Prophet Muhammad's Birthday
    - Christmas Day

    Early Closes:
    - Chinese New Year's Eve
    - Eid al-Fitr Eve

    TODO: XKLS takes a two hour lunch break from 12:30-2:30pm, but we are
    ignoring this for now.
    """

    name = "XKLS"

    tz = timezone("Asia/Kuala_Lumpur")

    open_times = ((None, time(9)),)

    close_times = ((None, time(17, 00)),)

    regular_early_close = time(12, 30)

    @property
    def regular_holidays(self):
        return HolidayCalendar(
            [
                NewYearsDay,
                FederalTerritoryDay,
                LabourDay,
                NationalDay,
                MalaysiaDay,
                ChristmasDay,
            ]
        )

    @property
    def adhoc_holidays(self):

        return list(
            chain(
                misc_adhoc,
                ChineseNewYear,
                ChineseNewYearDay2,
                NuzulAlQuran,
                EidAlFitrDay1,
                EidAlFitrDay2,
                EidAlAdha,
                Muharram,
                MuhammadBirthday,
                Deepavali,
                Thaipusam,
                WesakDay,
            )
        )

    @property
    def special_closes_adhoc(self):
        # Regular early closes on Chinese New Years Eve, Eid al-Fitr Eve
        early_close_days = list(set(ChineseNewYearsHalfDay + EidAlFitrHalfDay))
        return [(self.regular_early_close, early_close_days)]
