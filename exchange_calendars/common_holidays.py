import pandas as pd
from dateutil.easter import EASTER_ORTHODOX, easter
from pandas.tseries.holiday import FR, DateOffset, Easter, Holiday
from pandas.tseries.offsets import Day

from .exchange_calendar import MONDAY, TUESDAY


def new_years_day(start_date=None, end_date=None, observance=None, days_of_week=None):
    return Holiday(
        "New Year's Day",
        month=1,
        day=1,
        start_date=start_date,
        end_date=end_date,
        observance=observance,
        days_of_week=days_of_week,
    )


def new_years_eve(
    start_date=None,
    end_date=None,
    observance=None,
    days_of_week=None,
    offset=None,
):
    return Holiday(
        "New Year's Eve",
        month=12,
        day=31,
        start_date=start_date,
        end_date=end_date,
        offset=offset,
        observance=observance,
        days_of_week=days_of_week,
    )


def epiphany(
    start_date=None,
    end_date=None,
    observance=None,
    days_of_week=None,
    offset=None,
):
    return Holiday(
        "Epiphany",
        month=1,
        day=6,
        start_date=start_date,
        end_date=end_date,
        offset=offset,
        observance=observance,
        days_of_week=days_of_week,
    )


def anzac_day(start_date=None, end_date=None, observance=None, days_of_week=None):
    return Holiday(
        "Anzac Day",
        month=4,
        day=25,
        start_date=start_date,
        end_date=end_date,
        observance=observance,
        days_of_week=days_of_week,
    )


def european_labour_day(
    start_date=None, end_date=None, observance=None, days_of_week=None
):
    return Holiday(
        "Labour Day",
        month=5,
        day=1,
        start_date=start_date,
        end_date=end_date,
        observance=observance,
        days_of_week=days_of_week,
    )


# Holy Wednesday, Maundy Thursday, Ascension Day, Whit Monday, and Corpus
# Christi do not take observance as a parameter because they depend on a
# particular offset, and offset and observance cannot both be passed to a
# Holiday.
def holy_wednesday(start_date=None, end_date=None, days_of_week=None):
    return Holiday(
        "Holy Wednesday",
        month=1,
        day=1,
        offset=[Easter(), -Day(4)],
        start_date=start_date,
        end_date=end_date,
        days_of_week=days_of_week,
    )


def maundy_thursday(start_date=None, end_date=None, days_of_week=None):
    return Holiday(
        "Maundy Thursday",
        month=1,
        day=1,
        offset=[Easter(), -Day(3)],
        start_date=start_date,
        end_date=end_date,
        days_of_week=days_of_week,
    )


def ascension_day(start_date=None, end_date=None):
    return Holiday(
        "Ascension Day",
        month=1,
        day=1,
        offset=[Easter(), Day(39)],
        start_date=start_date,
        end_date=end_date,
    )


def whit_monday(start_date=None, end_date=None):
    return Holiday(
        "Whit Monday",
        month=1,
        day=1,
        offset=[Easter(), Day(50)],
        start_date=start_date,
        end_date=end_date,
    )


def corpus_christi(start_date=None, end_date=None):
    return Holiday(
        "Corpus Christi",
        month=1,
        day=1,
        offset=[Easter(), Day(60)],
        start_date=start_date,
        end_date=end_date,
    )


def midsummer_eve(start_date=None, end_date=None):
    return Holiday(
        "Midsummer Eve",
        month=6,
        day=19,
        offset=DateOffset(weekday=FR(1)),
        start_date=start_date,
        end_date=end_date,
    )


def saint_peter_and_saint_paul_day(
    start_date=None, end_date=None, observance=None, days_of_week=None
):
    return Holiday(
        "Saint Peter and Saint Paul Day",
        month=6,
        day=29,
        start_date=start_date,
        end_date=end_date,
        observance=observance,
        days_of_week=days_of_week,
    )


def assumption_day(start_date=None, end_date=None, observance=None, days_of_week=None):
    return Holiday(
        "Assumption Day",
        month=8,
        day=15,
        start_date=start_date,
        end_date=end_date,
        observance=observance,
        days_of_week=days_of_week,
    )


def all_saints_day(start_date=None, end_date=None, observance=None, days_of_week=None):
    return Holiday(
        "All Saints Day",
        month=11,
        day=1,
        start_date=start_date,
        end_date=end_date,
        observance=observance,
        days_of_week=days_of_week,
    )


def immaculate_conception(
    start_date=None, end_date=None, observance=None, days_of_week=None
):
    return Holiday(
        "Immaculate Conception",
        month=12,
        day=8,
        start_date=start_date,
        end_date=end_date,
        observance=observance,
        days_of_week=days_of_week,
    )


def christmas_eve(start_date=None, end_date=None, observance=None, days_of_week=None):
    return Holiday(
        "Christmas Eve",
        month=12,
        day=24,
        start_date=start_date,
        end_date=end_date,
        observance=observance,
        days_of_week=days_of_week,
    )


def christmas(start_date=None, end_date=None, observance=None, days_of_week=None):
    return Holiday(
        "Christmas",
        month=12,
        day=25,
        start_date=start_date,
        end_date=end_date,
        observance=observance,
        days_of_week=days_of_week,
    )


def weekend_christmas(start_date=None, end_date=None, observance=None):
    """
    If christmas day is Saturday Monday 27th is a holiday
    If christmas day is sunday the Tuesday 27th is a holiday
    """
    return Holiday(
        "Weekend Christmas",
        month=12,
        day=27,
        days_of_week=(MONDAY, TUESDAY),
        start_date=start_date,
        end_date=end_date,
        observance=observance,
    )


def boxing_day(start_date=None, end_date=None, observance=None, days_of_week=None):
    return Holiday(
        "Boxing Day",
        month=12,
        day=26,
        start_date=start_date,
        end_date=end_date,
        observance=observance,
        days_of_week=days_of_week,
    )


def weekend_boxing_day(start_date=None, end_date=None, observance=None):
    """
    If boxing day is saturday then Monday 28th is a holiday
    If boxing day is sunday then Tuesday 28th is a holiday
    """
    return Holiday(
        "Weekend Boxing Day",
        month=12,
        day=28,
        days_of_week=(MONDAY, TUESDAY),
        start_date=start_date,
        end_date=end_date,
        observance=observance,
    )


# These dates were initially calculated using the ummalqura Python
# package (https://pypi.org/project/ummalqura/), and then tweaked
# to fit Turkey's observance of Eid al-Fitr.  Other countries that
# observe Eid al-Fitr might use slightly different dates
eid_al_fitr_first_day = pd.to_datetime(
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
        "2007-10-12",
        "2008-09-30",
        "2009-09-20",
        "2010-09-09",
        "2011-08-30",
        "2012-08-19",
        "2013-08-08",
        "2014-07-28",
        "2015-07-17",
        "2016-07-05",
        "2017-06-25",
        "2018-06-15",
        "2019-06-04",
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

# These dates were initially calculated using the ummalqura Python
# package (https://pypi.org/project/ummalqura/), and then tweaked
# to fit Turkey's observance of Eid al-Adha.  Other countries that
# observe Eid al-Adha might use slightly different dates
eid_al_adha_first_day = pd.to_datetime(
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
        "2002-02-22",
        "2003-02-10",
        "2004-02-01",
        "2005-01-20",
        "2006-01-09",
        "2006-12-31",
        "2007-12-20",
        "2008-12-08",
        "2009-11-27",
        "2010-11-16",
        "2011-11-06",
        "2012-10-25",
        "2013-10-15",
        "2014-10-04",
        "2015-09-24",
        "2016-09-12",
        "2017-09-01",
        "2018-08-21",
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


def orthodox_easter(start_date="1980", end_date="2022"):
    """
    This function gives a DatetimeIndex of Orthodox Easter dates from start_date to end_date
    """
    return pd.to_datetime(
        [
            easter(year, method=EASTER_ORTHODOX)
            for year in range(int(start_date), int(end_date))
        ]
    )
