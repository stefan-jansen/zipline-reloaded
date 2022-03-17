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
from pandas.tseries.holiday import Holiday
from pytz import timezone

from .common_holidays import european_labour_day
from .exchange_calendar import HolidayCalendar, ExchangeCalendar


class XKARExchangeCalendar(ExchangeCalendar):
    """
    Exchange calendar for the Pakistan Stock Exchange (XKAR).

    Frequently abbreviated as 'PSX'; not to be confused with the
    the NASDAQ OMX PSX exchange, whose market identifier code is 'XPSX'.

    Open Time: 09:32 Monday-Thursday; 09:17 Friday
    Close Time: 15:30 Monday-Thursday; 16:30 Friday

    Regularly-Observed Holidays:
    - Kashmir Day (Feb 5)
    - Pakistan Day (Mar 23)
    - Labour Day (May 1)
    - Juma-Tul-Wida (last Friday of Ramadan)
    - Eil-ul-Fitr (1st-3rd Shawwal)
    - Eid-ul-Azha (10th-11th Zil-Hajj)
    - Independence Day (Aug 14)
    - Ashura (9th & 10th Muharram)
    - Eid Milad-un-Nabi (12th Rabi-ul-Awal)
    - Birthday of Quaid-e-Azam & Christmas (Dec 25)

    Formerly-Observed Holidays:
    - Iqbal Day (Nov 9; ended in 2012)

    Occasional election and bank holidays are also observed.
    """

    name = "XKAR"

    tz = timezone("Asia/Karachi")

    # NOTE: The Pakistan Stock Exchange is open from 09:32-15:30
    # Monday-Thursday, and from 09:17-12:00 AND 14:32-16:30 on Friday
    # (which is less total trading time); however, the ExchangeCalendar
    # class does not currently model intra-day closures.
    #
    # See https://www.psx.com.pk/psx/exchange/general/trading-hours

    open_times = (
        (None, time(9, 32)),
        # TODO: 09:17 on Fridays
    )

    close_times = (
        (None, time(15, 30)),
        # TODO: 16:30 on Fridays
    )

    @property
    def regular_holidays(self):
        return HolidayCalendar(
            [
                Holiday(
                    "Kashmir Day",
                    month=2,
                    day=5,
                ),
                Holiday(
                    "Pakistan Day",
                    month=3,
                    day=23,
                ),
                european_labour_day(),
                Holiday(
                    "Independence Day",
                    month=8,
                    day=14,
                ),
                Holiday(
                    "Iqbal Day",
                    month=11,
                    day=9,
                    end_date="2013",
                ),
                Holiday(
                    "Birthday of Quaid-e-Azam & Christmas",
                    month=12,
                    day=25,
                ),
            ]
        )

    juma_tul_wida = pd.to_datetime(
        [
            # Juma-Tul-Wida (last Friday of Ramadan before Eid-ul-Fitr)
            "2002-12-06",
            # '2003-11-21',  # NOTE: Apparently not observed in 2003.
            "2004-11-11",  # NOTE: Observed on Thursday instead of Friday (??)
            "2005-10-28",
            "2006-10-20",
            "2007-10-12",
            "2008-09-26",
            # '2009-09-18',  # NOTE: Apparently not observed in 2009.
            "2010-09-10",
            "2011-08-26",
            "2012-08-17",
            "2013-08-02",
            "2014-07-25",
            "2015-07-17",
            "2016-07-01",
            "2017-06-23",
            "2018-06-08",
            "2019-05-31",
            "2020-05-22",
        ]
    )

    eid_ul_fitr = pd.to_datetime(
        [
            # Eid-ul-Fitr (Festival of Breaking the Fast, 1st-3rd Shawwal).
            "2002-12-03",  # Tuesday  (??)
            "2002-12-05",  # Thursday
            "2003-11-26",  # Wednesday
            "2003-11-27",
            "2003-11-28",
            "2004-11-15",  # Monday
            "2004-11-16",
            "2004-11-17",
            "2005-11-03",  # Thursday
            "2005-11-04",
            "2006-10-23",  # Monday
            "2006-10-24",
            "2006-10-25",
            "2007-10-10",  # Wednesday (??)
            "2007-10-15",  # Monday
            "2007-10-16",
            "2008-10-01",  # Wednesday
            "2008-10-02",
            "2008-10-03",
            "2009-09-21",  # Monday
            "2009-09-22",
            "2009-09-23",
            "2010-09-13",  # Monday
            "2011-08-31",  # Wednesday
            "2011-09-01",
            "2011-09-02",
            "2012-08-20",  # Monday
            "2012-08-21",
            "2012-08-22",
            "2013-08-08",  # Thursday
            "2013-08-09",
            "2014-07-29",  # Tuesday
            "2014-07-30",
            "2014-07-31",
            "2014-08-01",
            "2015-07-20",  # Monday
            "2015-07-21",
            "2016-07-05",  # Tuesday
            "2016-07-06",
            "2016-07-07",
            "2016-07-08",
            "2017-06-26",  # Wednesday
            "2017-06-27",
            "2017-06-28",
            "2018-06-15",  # Friday
            "2018-06-18",  # Monday
            "2019-06-04",  # Tuesday
            "2019-06-05",
            "2019-06-06",
            "2019-06-07",
            "2020-05-25",  # Monday
            "2020-05-26",
            "2020-05-27",
        ]
    )

    eid_ul_azha = pd.to_datetime(
        [
            # Eid-ul-Azha (Festival of the Sacrifice, 10th-11th Zil-Hajj).
            "2002-02-25",
            "2003-02-11",
            "2003-02-12",
            "2003-02-13",
            "2003-02-14",
            "2004-02-02",
            "2004-02-03",
            "2004-02-04",
            "2005-01-20",
            "2005-01-21",
            "2006-01-10",
            "2006-01-11",
            "2006-01-12",
            "2006-01-13",
            # NOTE: Some countries observed this occurrence of Eid-ul-Azha
            # at the end of December 2006.
            "2007-01-01",  # NOTE: occurred on New Year's Day.
            "2007-01-02",
            "2007-12-20",
            "2007-12-21",
            "2008-12-08",
            "2008-12-09",
            "2008-12-10",
            "2008-12-11",
            "2009-11-27",  # Friday
            "2009-11-30",  # Monday
            "2010-11-17",
            "2010-11-18",
            "2010-11-19",
            "2011-11-07",
            "2011-11-08",
            "2012-10-26",
            "2013-10-15",
            "2013-10-16",
            "2013-10-17",
            "2013-10-18",
            "2014-10-06",
            "2014-10-07",
            "2014-10-08",
            "2015-09-24",
            "2015-09-25",
            "2016-09-12",
            "2016-09-13",
            "2016-09-14",
            "2017-09-01",
            "2017-09-04",
            "2018-08-21",
            "2018-08-22",
            "2018-08-23",
            "2019-08-12",
            "2019-08-13",
            "2019-08-15",
            "2020-07-31",
        ]
    )

    ashura = pd.to_datetime(
        [
            # Ashura (9th & 10th Muharram)
            "2002-03-25",  # Monday make-up?
            "2003-03-13",
            "2003-03-14",
            "2004-03-01",
            "2004-03-02",
            "2006-02-08",
            "2006-02-09",
            "2009-01-07",
            "2009-01-08",
            "2009-12-28",
            "2010-12-16",
            "2010-12-17",
            "2011-12-05",
            "2011-12-06",
            "2013-11-14",
            "2013-11-15",
            "2014-11-03",
            "2014-11-04",
            "2015-10-23",
            "2016-10-11",
            "2016-10-12",
            "2018-09-20",
            "2018-09-21",
            "2019-09-09",
            "2019-09-10",
        ]
    )

    eid_milad_un_nabi = pd.to_datetime(
        [
            # Eid Milad-un-Nabi a.k.a. Mawlid (12th Rabi-ul-Awal)
            # Birth of the Prophet Muhammad
            "2002-05-23",
            "2003-05-15",
            "2005-04-22",
            "2006-04-11",
            "2008-03-21",
            "2009-03-10",
            "2011-02-16",
            "2013-01-25",
            "2014-01-14",
            "2015-12-24",
            "2016-12-12",
            "2017-12-01",
            "2018-11-21",
            "2020-10-30",
        ]
    )

    new_years_day = pd.to_datetime(
        [
            # NOTE: New Year's Day is not included in the Pakistan Stock
            # Exchange's official list of holidays, although the exchange
            # has been closed on that date a few times.
            "2002-01-01",  # (Tue): closed
            # 2003-01-01 (Wed): open
            "2004-01-01",  # (Thu): closed
            # 2005-01-01 (Sat): closed for the weekend
            # 2006-01-01 (Sun): closed for the weekend
            # 2007-01-01 (Mon): closed for Eid-ul-Azha
            # 2008-01-01 (Tue): open
            # 2009-01-01 (Thu): open
            "2010-01-01",  # (Fri): closed
            # 2011-01-01 (Sat): closed for the weekend
            # 2012-01-01 (Sun): closed for the weekend
            # 2013-01-01 (Tue): open
            # 2014-01-01 (Wed): open
            # 2015-01-01 (Thu): open
            # 2016-01-01 (Fri): open
            # 2017-01-01 (Sun): closed for the weekend
            # 2018-01-01 (Mon): open
            # 2019-01-01 (Tue): open
            # 2020-01-01 (Wed): open
        ]
    )

    miscellaneous_closures = pd.to_datetime(
        [
            "2002-02-22",  # Friday
            "2002-10-10",  # Election day
            "2003-04-10",  # Thursday
            "2004-05-03",  # Monday (Labour Day make-up?)
            "2005-08-18",  # Thursday
            "2005-11-01",  # Tuesday
            "2006-04-12",  # Wednesday
            "2006-10-26",  # Thursday
            "2006-10-27",  # Friday
            "2007-01-29",  # Monday
            "2007-01-30",  # Tuesday
            "2007-12-28",  # Friday
            "2008-02-18",  # Monday
            "2011-11-11",  # Friday
            "2011-10-24",  # Death of Begum Nusrat Bhutto
            "2012-10-29",  # Birthday of Guru Balmik Sawami Ji
            "2012-09-21",  # Day of Love for the Prophet Muhammad
            "2018-07-25",  # Election day
        ]
    )

    @property
    def adhoc_holidays(self):
        return list(
            chain(
                self.new_years_day,
                self.juma_tul_wida,
                self.eid_ul_fitr,
                self.eid_ul_azha,
                self.ashura,
                self.eid_milad_un_nabi,
                self.miscellaneous_closures,
            )
        )
