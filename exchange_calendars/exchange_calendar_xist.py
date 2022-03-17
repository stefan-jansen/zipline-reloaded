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

from datetime import time, timedelta
from itertools import chain

import pandas as pd
from pandas.tseries.holiday import Holiday
from pytz import timezone

from .common_holidays import (
    eid_al_adha_first_day,
    eid_al_fitr_first_day,
    european_labour_day,
    new_years_day,
)
from .exchange_calendar import WEEKDAYS, WEEKENDS, HolidayCalendar, ExchangeCalendar

NewYearsDay = new_years_day()

NationalSovereigntyAndChildrensDay = Holiday(
    "National Sovereignty and Children's Day",
    month=4,
    day=23,
)

LabourDay = european_labour_day(start_date="2009")

CommemorationOfAttaturkYouthAndSportsDay = Holiday(
    "Commemoration of Attaturk, Youth and Sports Day",
    month=5,
    day=19,
)

EidAlFitr1 = eid_al_fitr_first_day

EidAlFitr2 = eid_al_fitr_first_day + timedelta(1)

EidAlFitr3 = eid_al_fitr_first_day + timedelta(2)

DemocracyAndNationalUnityDay = Holiday(
    "Democracy and National Unity Day", month=7, day=15, start_date="2017"
)

EidAlAdha1 = eid_al_adha_first_day

EidAlAdha2 = eid_al_adha_first_day + timedelta(1)

EidAlAdha3 = eid_al_adha_first_day + timedelta(2)

EidAlAdha4 = eid_al_adha_first_day + timedelta(3)

VictoryDay = Holiday(
    "Victory Day",
    month=8,
    day=30,
)

RepublicDay = Holiday(
    "Republic Day",
    month=10,
    day=29,
)

# Early Closes
DayBeforeEidAlFitr = eid_al_fitr_first_day - timedelta(1)

EidAlFitrHalfDay = [day for day in DayBeforeEidAlFitr if day.weekday() not in WEEKENDS]

DayBeforeEidAlAdha = eid_al_adha_first_day - timedelta(1)

EidAlAdhaHalfDay = [day for day in DayBeforeEidAlAdha if day.weekday() not in WEEKENDS]

RepublicDayHalfDay = Holiday(
    "Republic Day half day",
    month=10,
    day=28,
    days_of_week=WEEKDAYS,
)


class XISTExchangeCalendar(ExchangeCalendar):
    """
    Exchange calendar for the Istanbul Stock Exchange (XIST).

    # Note: Effective as of Nov 14, 2016 according to official website
    Open Time: 10:00 AM, TRT
    Close Time: 6:00 PM, TRT

    Regularly-Observed Holidays:
    - New Year's Day
    - National Sovereignty and Children's Day (Apr 23)
    - Labour Day (May 1)
    - Commemoration of Attaturk, Youth and Sports Day (May 19)
    - Eid-ul-Fitr (Islamic Lunar Calendar)
    - Democracy and National Unity Day (Jul 15)
    - Eid-al-Adha (first day is a half-day, remaining full holidays)
    - Victory Day (Aug 30)
    - Republic Day (Oct 29)

    Early Closes:
    - First Day of Eid-al-Adha
    - Republic Day (Oct 28)
    """

    name = "XIST"

    tz = timezone("Europe/Istanbul")

    open_times = ((None, time(10)),)

    close_times = ((None, time(18, 00)),)

    regular_early_close = time(12, 30)

    @property
    def regular_holidays(self):
        return HolidayCalendar(
            [
                NewYearsDay,
                NationalSovereigntyAndChildrensDay,
                LabourDay,
                CommemorationOfAttaturkYouthAndSportsDay,
                DemocracyAndNationalUnityDay,
                VictoryDay,
                RepublicDay,
            ]
        )

    @property
    def adhoc_holidays(self):
        misc_adhoc = [
            pd.Timestamp("2002-01-04"),  # Market Holiday
            pd.Timestamp("2003-02-14"),  # Eid al Adha extra holiday
            pd.Timestamp("2003-11-21"),  # Terror attacks
            pd.Timestamp("2003-11-24"),  # Eid al Fitr extra holiday
            pd.Timestamp("2003-11-28"),  # Eid al Fitr extra holiday
            pd.Timestamp("2004-01-23"),  # Bad weather
            pd.Timestamp("2004-12-30"),  # Closure for redenomination
            pd.Timestamp("2004-12-31"),  # Closure for redenomination
            pd.Timestamp("2006-01-13"),  # Eid al Adha extra holiday
        ]

        return list(
            chain(
                misc_adhoc,
                EidAlFitr1,
                EidAlFitr2,
                EidAlFitr3,
                EidAlAdha1,
                EidAlAdha2,
                EidAlAdha3,
                EidAlAdha4,
            )
        )

    @property
    def special_closes(self):
        return [
            (
                self.regular_early_close,
                HolidayCalendar([RepublicDayHalfDay]),
            )
        ]

    @property
    def special_closes_adhoc(self):
        early_close_days = EidAlFitrHalfDay + EidAlAdhaHalfDay
        return [(self.regular_early_close, early_close_days)]
