from datetime import timedelta

import pandas as pd
from pandas.tseries.holiday import Holiday, sunday_to_monday

from .common_holidays import christmas, european_labour_day, new_years_day
from .lunisolar_holidays import chinese_lunar_new_year_dates
from .exchange_calendar import WEEKENDS

# In Malaysia, Nuzul Al'Quran is the 17th day of Ramadan
#   Starts 2014
malaysia_nuzul_al_quran = pd.to_datetime(
    [
        "2014-07-15",
        "2015-07-04",
        "2016-06-22",
        "2017-06-12",
        "2018-06-02",
        "2019-05-22",
        "2020-05-10",
        "2021-04-29",
        "2022-04-18",
        "2023-04-08",
        "2024-03-27",
        "2025-03-17",
        "2026-03-06",
        "2027-02-24",
        "2028-02-13",
        "2029-02-01",
        "2030-01-21",
        "2031-01-11",
        "2031-12-31",
        "2032-12-20",
        "2033-12-09",
        "2034-11-28",
        "2035-11-17",
        "2036-11-05",
        "2037-10-26",
        "2038-10-16",
        "2039-10-05",
        "2040-09-23",
        "2041-09-13",
        "2042-09-02",
        "2043-08-22",
        "2044-08-11",
        "2045-07-31",
        "2046-07-21",
        "2047-07-10",
        "2048-06-28",
        "2049-06-18",
    ]
)

# Muharram is New Year's Day for the Islamic Lunar Calendar
muharram = pd.to_datetime(
    [
        "1980-11-09",
        "1981-10-28",
        "1982-10-18",
        "1983-10-07",
        "1984-09-26",
        "1985-09-15",
        "1986-09-05",
        "1987-08-25",
        "1988-08-13",
        "1989-08-02",
        "1990-07-23",
        "1991-07-12",
        "1992-07-01",
        "1993-06-21",
        "1994-06-10",
        "1995-05-30",
        "1996-05-18",
        "1997-05-07",
        "1998-04-27",
        "1999-04-17",
        "2000-04-06",
        "2001-03-26",
        "2002-03-15",
        "2003-03-04",
        "2004-02-22",
        "2005-02-11",
        "2006-02-01",
        "2007-01-20",
        "2008-01-10",
        "2008-12-29",
        "2009-12-18",
        "2010-12-07",
        "2011-11-27",
        "2012-11-15",
        "2013-11-05",
        "2014-10-25",
        "2015-10-14",
        "2016-10-02",
        "2017-09-22",
        "2018-09-11",
        "2019-09-01",
        "2020-08-20",
        "2021-08-10",
        "2022-07-30",
        "2023-07-19",
        "2024-07-07",
        "2025-06-26",
        "2026-06-16",
        "2027-06-06",
        "2028-05-25",
        "2029-05-14",
        "2030-05-03",
        "2031-04-23",
        "2032-04-11",
        "2033-04-01",
        "2034-03-21",
        "2035-03-11",
        "2036-02-28",
        "2037-02-16",
        "2038-02-05",
        "2039-01-26",
        "2040-01-15",
        "2041-01-04",
        "2041-12-24",
        "2042-12-14",
        "2043-12-03",
        "2044-11-21",
        "2045-11-10",
        "2046-10-31",
        "2047-10-20",
        "2048-10-09",
    ]
)

# Prophet Muhammad's Birthday (Mawlid) is observed as the 12th day of
# the 3rd month in the Islamic Lunar Calendar
muhammad_birthday = pd.to_datetime(
    [
        "1981-01-18",
        "1982-01-07",
        "1982-12-27",
        "1983-12-16",
        "1984-12-04",
        "1985-11-24",
        "1986-11-14",
        "1987-11-03",
        "1988-10-22",
        "1989-10-11",
        "1990-10-01",
        "1991-09-20",
        "1992-09-09",
        "1993-08-29",
        "1994-08-19",
        "1995-08-08",
        "1996-07-27",
        "1997-07-16",
        "1998-07-06",
        "1999-06-26",
        "2000-06-14",
        "2001-06-04",
        "2002-05-27",
        "2003-05-14",
        "2004-05-03",
        "2005-04-21",
        "2006-04-11",
        "2007-03-31",
        "2008-03-20",
        "2009-03-09",
        "2010-02-26",
        "2011-02-15",
        "2012-02-06",
        "2013-01-24",
        "2014-01-14",
        "2015-12-24",
        "2016-12-11",
        "2017-12-01",
        "2018-11-20",
        "2019-11-09",
        "2020-10-29",
        "2021-10-19",
        "2022-10-08",
        "2023-09-27",
        "2024-09-15",
        "2025-09-04",
        "2026-08-25",
        "2027-08-14",
        "2028-08-03",
        "2029-07-24",
        "2030-07-13",
        "2031-07-02",
        "2032-06-20",
        "2033-06-09",
        "2034-05-30",
        "2035-05-20",
        "2036-05-08",
        "2037-04-28",
        "2038-04-17",
        "2039-04-06",
        "2040-03-25",
        "2041-03-15",
        "2042-03-04",
        "2043-02-22",
        "2044-02-11",
        "2045-01-30",
        "2046-01-19",
        "2047-01-08",
        "2047-12-29",
        "2048-12-18",
    ]
)

# Malaysia's observances of Eid al-Fitr
malaysia_eid_al_fitr_first_day = pd.to_datetime(
    [
        "1981-08-01",
        "1982-07-21",
        "1983-07-11",
        "1984-06-30",
        "1985-06-19",
        "1986-06-08",
        "1987-05-28",
        "1988-05-16",
        "1989-05-06",
        "1990-04-26",
        "1991-04-15",
        "1992-04-04",
        "1993-03-24",
        "1994-03-13",
        "1995-03-02",
        "1996-02-19",
        "1997-02-08",
        "1998-01-29",
        "1999-01-18",
        "2000-01-08",
        "2000-12-27",
        "2001-12-16",
        "2002-12-05",
        "2003-11-25",
        "2004-11-14",
        "2005-11-03",
        "2006-10-23",
        "2007-10-13",
        "2008-10-01",
        "2009-09-20",
        "2010-09-10",
        "2011-08-30",
        "2012-08-19",
        "2013-08-08",
        "2014-07-28",
        "2015-07-17",
        "2016-07-06",
        "2017-06-25",
        "2018-06-15",
        "2019-06-05",
        "2020-05-24",
        "2021-05-13",
        "2022-05-02",
        "2023-04-21",
        "2024-04-10",
        "2025-03-30",
        "2026-03-20",
        "2027-03-09",
        "2028-02-26",
        "2029-02-14",
        "2030-02-04",
        "2031-01-24",
        "2032-01-14",
        "2033-01-02",
        "2033-12-23",
        "2034-12-12",
        "2035-12-01",
        "2036-11-19",
        "2037-11-08",
        "2038-10-29",
        "2039-10-19",
        "2040-10-07",
        "2041-09-26",
        "2042-09-15",
        "2043-09-04",
        "2044-08-24",
        "2045-08-14",
        "2046-08-03",
        "2047-07-24",
        "2048-07-12",
        "2049-07-01",
    ]
)

# Malaysia's observances of Eid al-Adha
malaysia_eid_al_adha = pd.to_datetime(
    [
        "1981-10-08",
        "1982-09-27",
        "1983-09-17",
        "1984-09-05",
        "1985-08-26",
        "1986-08-15",
        "1987-08-04",
        "1988-07-23",
        "1989-07-13",
        "1990-07-02",
        "1991-06-22",
        "1992-06-11",
        "1993-05-31",
        "1994-05-20",
        "1995-05-09",
        "1996-04-27",
        "1997-04-17",
        "1998-04-07",
        "1999-03-27",
        "2000-03-16",
        "2001-03-05",
        "2002-02-23",
        "2003-02-12",
        "2004-02-03",
        "2005-01-21",
        "2006-01-10",
        "2007-01-02",
        "2007-12-20",
        "2008-12-08",
        "2009-11-27",
        "2010-11-17",
        "2011-11-06",
        "2012-10-26",
        "2013-10-15",
        "2014-10-05",
        "2015-09-24",
        "2016-09-12",
        "2017-09-01",
        "2018-08-22",
        "2019-08-11",
        "2020-07-31",
        "2021-07-20",
        "2022-07-09",
        "2023-06-28",
        "2024-06-16",
        "2025-06-06",
        "2026-05-27",
        "2027-05-16",
        "2028-05-05",
        "2029-04-24",
        "2030-04-13",
        "2031-04-02",
        "2032-03-22",
        "2033-03-11",
        "2034-03-01",
        "2035-02-18",
        "2036-02-07",
        "2037-01-26",
        "2038-01-16",
        "2039-01-05",
        "2039-12-26",
        "2040-12-14",
        "2041-12-04",
        "2042-11-23",
        "2043-11-12",
        "2044-10-31",
        "2045-10-21",
        "2046-10-10",
        "2047-09-30",
        "2048-09-19",
        "2049-09-08",
    ]
)

# Malaysia's observances of Deepavali (Hindu Lunar Calendar)
deepavali = pd.to_datetime(
    [
        "2002-11-04",
        "2003-10-24",
        "2004-11-11",
        "2004-11-12",
        "2005-11-01",
        "2007-11-08",
        "2008-10-27",
        "2010-11-05",
        "2011-10-26",
        "2012-11-13",
        "2014-10-22",
        "2015-11-10",
        "2017-10-18",
        "2018-11-06",
        "2019-10-28",
        "2020-11-14",
        "2021-11-04",
        "2022-10-24",
        "2023-11-12",
        "2024-10-31",
    ]
)

# Malaysia's observances of Thaipusam (Tamil Calendar)
thaipusam = pd.to_datetime(
    [
        "2008-01-23",
        "2009-02-09",
        "2010-01-30",
        "2011-01-20",
        "2012-02-07",
        "2013-01-28",
        "2014-01-17",
        "2015-02-03",
        "2016-01-25",
        "2017-02-09",
        "2018-01-31",
        "2019-01-21",
        "2020-02-08",
        "2021-01-28",
        "2022-01-18",
        "2023-02-04",
        "2024-01-25",
    ]
)

# Malaysia's observances of Wesak Day (Chinese Lunar Calendar)
# source: https://publicholidays.com.my/wesak-day/
wesak_day = pd.to_datetime(
    [
        "2003-05-15",
        "2004-05-04",
        "2005-05-23",
        "2006-05-12",
        "2007-05-02",
        "2008-05-19",
        "2010-05-28",
        "2011-05-17",
        "2013-05-24",
        "2014-05-13",
        "2015-05-04",
        "2017-05-10",
        "2018-05-29",
        "2019-05-20",
        "2020-05-07",
        "2021-05-26",
        "2022-05-15",
        "2023-05-04",
        "2024-05-22"
    ]
)

misc_adhoc = pd.to_datetime(
    [
        "2024-06-03",  # Yang di-Pertuan Agong's Birthday
        "2023-06-05",  # Yang di-Pertuan Agong's Birthday
        "2022-06-06",  # Yang di-Pertuan Agong's Birthday
        "2021-06-07",  # Yang di-Pertuan Agong's Birthday
        "2020-06-08",  # Yang di-Pertuan Agong's Birthday
        "2019-09-09",  # Yang di-Pertuan Agong's Birthday
        "2019-07-30",  # Installation of Yang di-Pertuan Agong
        "2018-09-10",  # Yang di-Pertuan Agong's Birthday
        "2018-05-11",  # Special Holiday (probably post election holiday?)
        "2018-05-10",  # Special Holiday (same as above)
        "2018-05-09",  # Election Day
        "2017-09-04",  # Public Holiday for success in Sea Games
        "2017-04-24",  # Installation of Yang di-Pertuan Agong
        "2014-02-03",  # 2nd Day Chinese New Year (made up on Tues?)
        "2012-04-11",  # Installation of Yang di-Pertuan Agong
        "2011-09-01",  # Eid al-Fitr extra day
        "2010-12-31",  # New Year's Eve Observed
        "2008-07-03",  # Trading suspended
        "2007-04-26",  # Installation of Yang di-Pertuan Agong
        "2006-10-25",  # Eid al-Fitr extra day
        "2006-02-02",  # Federal Territory Day made up b.c. Muharram
        "2004-01-21",  # Chinese New Year extra day
        "2003-11-24",  # Eid al-Fitr extra day
        "2003-02-04",  # Chinese New Year extra day
        "2003-01-31",  # Chinese New Year extra day
        "2002-04-25",  # Installation of Yang di-Pertuan Agong
        "2002-02-11",  # Chinese New Year extra day
    ]
)


NewYearsDay = new_years_day(observance=sunday_to_monday)

Thaipusam = thaipusam

FederalTerritoryDay = Holiday(
    "Federal Territory Day",
    month=2,
    day=1,
    observance=sunday_to_monday,
)

ChineseNewYear = pd.to_datetime(
    chinese_lunar_new_year_dates.map(lambda d: sunday_to_monday(d))
)

ChineseNewYearDay2 = (ChineseNewYear + timedelta(1)).map(lambda d: sunday_to_monday(d))

LabourDay = european_labour_day(observance=sunday_to_monday)

WesakDay = wesak_day

NuzulAlQuran = malaysia_nuzul_al_quran.map(lambda d: sunday_to_monday(d))

EidAlFitrDay1 = pd.to_datetime(
    malaysia_eid_al_fitr_first_day.map(lambda d: sunday_to_monday(d))
)

EidAlFitrDay2 = (EidAlFitrDay1 + timedelta(1)).map(lambda d: sunday_to_monday(d))

EidAlAdha = malaysia_eid_al_adha.map(lambda d: sunday_to_monday(d))

NationalDay = Holiday(
    "National Day",
    month=8,
    day=31,
    observance=sunday_to_monday,
)

Muharram = muharram.map(lambda d: sunday_to_monday(d))

MalaysiaDay = Holiday(
    "Malaysia Day",
    month=9,
    day=16,
    start_date="2010",
    observance=sunday_to_monday,
)

Deepavali = deepavali

MuhammadBirthday = muhammad_birthday.map(lambda d: sunday_to_monday(d))

ChristmasDay = christmas(observance=sunday_to_monday)

# Early closes - Chinese New Year's Eve and Eid al-Fitr Eve
ChineseNewYearsEve = ChineseNewYear - timedelta(1)

ChineseNewYearsHalfDay = [
    day for day in ChineseNewYearsEve if day.weekday() not in WEEKENDS
]

EidAlFitrEve = EidAlFitrDay1 - timedelta(1)

EidAlFitrHalfDay = [day for day in EidAlFitrEve if day.weekday() not in WEEKENDS]
