from datetime import timedelta

import pandas as pd
from pandas.tseries.holiday import (
    Holiday,
    next_monday_or_tuesday,
    sunday_to_monday,
    weekend_to_monday,
)

from .common_holidays import european_labour_day, new_years_day, new_years_eve
from .exchange_calendar import MONDAY, SUNDAY


def new_years_eve_observance(holidays):
    # New Year's Eve is a holiday every year except for 2003 for some reason.
    holidays = holidays[holidays.year != 2003]

    return pd.to_datetime([weekend_to_monday(day) for day in holidays])


def new_years_day_observance(holidays):
    # There was no extra observance of New Year's Day in 2006.
    holidays = holidays[holidays.year != 2006]

    return pd.to_datetime([next_monday_or_tuesday(day) for day in holidays])


def songkran_festival_last_day_observance(dt):
    """
    This function is similar to the pandas function `next_monday_or_tuesday`
    except it does not observe Saturday holidays on Monday.
    """
    if dt.weekday() == SUNDAY or dt.weekday() == MONDAY:
        return dt + timedelta(days=1)
    return dt


NewYearsDay = new_years_day(observance=new_years_day_observance)

ChakriMemorialDay = Holiday(
    "Chakri Memorial Day",
    month=4,
    day=6,
    observance=weekend_to_monday,
)

# Thai New Year. This does not follow the usual observe-next-trading-day rule.
SongkranFestival1 = Holiday("Songkran Festival", month=4, day=13)
SongkranFestival2 = Holiday(
    "Songkran Festival",
    month=4,
    day=14,
    observance=sunday_to_monday,
)
SongkranFestival3 = Holiday(
    "Songkran Festival",
    month=4,
    day=15,
    observance=songkran_festival_last_day_observance,
)

LabourDay = european_labour_day(observance=weekend_to_monday)

CoronationDay2016AndBefore = Holiday(
    "Coronation Day For King #9",
    month=5,
    day=5,
    observance=weekend_to_monday,
    end_date="2017",
)
CoronationDay2019AndAfter = Holiday(
    "Coronation Day For King #10",
    month=5,
    day=4,
    observance=weekend_to_monday,
    start_date="2019",
)

HMQueensBirthday = Holiday(
    "Her Majesty The Queen's Birthday",
    month=6,
    day=3,
    observance=weekend_to_monday,
    start_date="2019",
)
HMKingsBirthday = Holiday(
    "His Majesty The King's Birthday",
    month=7,
    day=28,
    observance=weekend_to_monday,
    start_date="2017",
)
HMQueenMothersBirthday = Holiday(
    "Her Majesty The Queen Mother's Birthday",
    month=8,
    day=12,
    observance=weekend_to_monday,
)

# This holiday was historically used as a "catch up" day for the exchange, so
# it does not need to follow the usual observe-next-trading-day rule.
HalfYearHoliday = Holiday(
    "Half Year Holiday",
    month=7,
    day=1,
    start_date="2002",
    end_date="2017",
)

ThePassingOfKingBhumibol = Holiday(
    "The Passing of King Bhumibol",
    month=10,
    day=13,
    observance=weekend_to_monday,
    start_date="2017",
)

ChulalongkornDay = Holiday(
    "Chulalongkorn Day",
    month=10,
    day=23,
    observance=weekend_to_monday,
)

KingBhumibolsBirthday = Holiday(
    "King Bhumibol's Birthday",
    month=12,
    day=5,
    observance=weekend_to_monday,
)

ThailandConstitutionDay = Holiday(
    "Thailand Constitution Day",
    month=12,
    day=10,
    observance=weekend_to_monday,
)

NewYearsEve = new_years_eve(observance=new_years_eve_observance)

# Adhoc Holidays
# --------------

new_years_bridge_days = [
    pd.Timestamp("2002-12-30"),
    pd.Timestamp("2004-01-02"),
    pd.Timestamp("2009-01-02"),
    pd.Timestamp("2013-12-30"),
    pd.Timestamp("2015-01-02"),
]

asanha_bucha_bridge_days = [
    pd.Timestamp("2009-07-06"),
    pd.Timestamp("2016-07-18"),
]

queens_birthday_bridge_days = [
    pd.Timestamp("2010-08-13"),
    pd.Timestamp("2014-08-11"),
]

coronation_bridge_days = [
    pd.Timestamp("2015-05-04"),
    pd.Timestamp("2016-05-06"),
]

vesak_bridge_days = [
    pd.Timestamp("2011-05-16"),
]

misc_adhoc = [
    pd.Timestamp("2006-04-19"),  # Special Holiday
    pd.Timestamp("2006-06-12"),  # Special Holiday
    pd.Timestamp("2006-06-13"),  # Special Holiday
    pd.Timestamp("2006-09-20"),  # Exchange Holiday
    pd.Timestamp("2007-12-24"),  # Exchange Holiday
    pd.Timestamp("2010-05-20"),  # Closure Due to Security Concerns
    pd.Timestamp("2010-05-21"),  # Closure Due to Security Concerns
    pd.Timestamp("2012-04-09"),  # Bank Holiday
    pd.Timestamp("2017-10-26"),  # Cremation of King Bhumibol
]

# Lunar Holidays
# --------------

# Makha Bucha (also known as Magha Puja) is celebrated on the day of the Full
# Moon of Magha in the Buddhist calendar. This falls sometime between February
# and March.
makha_bucha = pd.to_datetime(
    [
        "1981-02-18",
        "1982-02-08",
        "1983-02-27",
        "1984-02-16",
        "1985-03-06",
        "1986-02-24",
        "1987-02-13",
        "1988-03-03",
        "1989-02-20",
        "1990-02-09",
        "1991-02-28",
        "1992-02-18",
        "1993-03-08",
        "1994-02-25",
        "1995-02-15",
        "1996-03-05",
        "1997-02-22",
        "1998-02-11",
        "1999-03-02",
        "2000-02-19",
        "2001-02-08",
        "2002-02-26",
        "2003-02-17",
        "2004-03-05",
        "2005-02-23",
        "2006-02-13",
        "2007-03-05",
        "2008-02-21",
        "2009-02-09",
        "2010-03-01",
        "2011-02-18",
        "2012-03-07",
        "2013-02-25",
        "2014-02-14",
        "2015-03-04",
        "2016-02-22",
        "2017-02-13",
        "2018-03-01",
        "2019-02-19",
        "2020-02-10",
    ]
)

# Vesak (also known as Buddha Day) is celebrated on the day of the Full Moon of
# Visakha in the Buddhist calendar. This typically falls in May.
vesak = pd.to_datetime(
    [
        "1981-05-18",
        "1982-05-07",
        "1983-05-26",
        "1984-05-15",
        "1985-06-02",
        "1986-05-23",
        "1987-05-13",
        "1988-05-31",
        "1989-05-20",
        "1990-05-09",
        "1991-05-28",
        "1992-05-16",
        "1993-06-04",
        "1994-05-24",
        "1995-05-14",
        "1996-06-01",
        "1997-05-22",
        "1998-05-11",
        "1999-05-30",
        "2000-05-18",
        "2001-05-07",
        "2002-05-27",
        "2003-05-15",
        "2004-06-02",
        "2005-05-23",
        "2006-05-12",
        "2007-05-31",
        "2008-05-19",
        "2009-05-08",
        "2010-05-28",
        "2011-05-17",
        "2012-06-04",
        "2013-05-24",
        "2014-05-13",
        "2015-06-01",
        "2016-05-20",
        "2017-05-10",
        "2018-05-29",
        "2019-05-20",
        "2020-05-06",
    ]
)

# Asanha Bucha (also known as Asalha Puja) is celebrated on the day of the Full
# Moon of Asadha in the Buddhist calendar. This typically falls in July.
asanha_bucha = pd.to_datetime(
    [
        "1981-07-17",
        "1982-07-06",
        "1983-07-24",
        "1984-07-12",
        "1985-07-31",
        "1986-07-21",
        "1987-07-10",
        "1988-07-28",
        "1989-07-18",
        "1990-07-07",
        "1991-07-26",
        "1992-07-14",
        "1993-08-02",
        "1994-07-22",
        "1995-07-12",
        "1996-07-30",
        "1997-07-19",
        "1998-07-09",
        "1999-07-28",
        "2000-07-16",
        "2001-07-05",
        "2002-07-25",
        "2003-07-14",
        "2004-08-02",
        "2005-07-22",
        "2006-07-11",
        "2007-07-30",
        "2008-07-17",
        "2009-07-07",
        "2010-07-26",
        "2011-07-15",
        "2012-08-02",
        "2013-07-22",
        "2014-07-11",
        "2015-07-30",
        "2016-07-19",
        "2017-07-10",
        "2018-07-27",
        "2019-07-16",
        "2020-07-06",
    ]
)
