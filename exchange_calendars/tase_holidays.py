from datetime import date, datetime

import pandas as pd
from pandas._libs.tslibs.conversion import localize_pydatetime
from pandas.tseries.holiday import Day, Holiday
from pandas.tseries.offsets import Easter
from pyluach import dates, hebrewcal

try:
    from pandas._libs.tslibs.offsets import apply_wraps
except ImportError:
    from pandas.tseries.offsets import apply_wraps

# Auxiliary functions to get Hebrew dates for holidays observed by TASE for a
# given Hebrew calendar year. These are just the raw dates with no adjustments
# applied.
#
# Note: pyluach uses the biblical month numbering scheme where the year is
# incremented when moving from the month of Elul (6) to Tishrei (7). See also
# https://en.wikipedia.org/wiki/Hebrew_calendar.


def _purim(year):
    """
    Return the Hebrew date for Purim in the given Hebrew year.
    """
    # Purim is observed in Adar (12), or Adar II (13) if in a leap year.
    return dates.HebrewDate(year.year, 13 if year.leap else 12, 14)


def _passover(year):
    """
    Return the Hebrew date for the first day of Passover in the given Hebrew
    year.
    """
    return dates.HebrewDate(year.year, 1, 15)


def _memorial_day(year):
    """
    Return the Hebrew date for Memorial Day in the given Hebrew year.

    Note: Independence Day is always celebrated the following day.
    """
    return dates.HebrewDate(year.year, 2, 4)


def _pentecost(year):
    """
    Return the Hebrew date for Pentecost in the given Hebrew year.
    """
    return dates.HebrewDate(year.year, 3, 6)


def _fast_day(year):
    """
    Return the Hebrew date for Tisha B'Av in the given Hebrew year.
    """
    return dates.HebrewDate(year.year, 5, 9)


def _new_year(year):
    """
    Return the Hebrew date for the first day of a new year in the given Hebrew
    year.
    """
    return dates.HebrewDate(year.year, 7, 1)


def _yom_kippur(year):
    """
    Return the Hebrew date for Yom Kippur in the given Hebrew year.
    """
    return dates.HebrewDate(year.year, 7, 10)


def _sukkoth(year):
    """
    Return the Hebrew date for Sukkoth in the given Hebrew year.
    """
    return dates.HebrewDate(year.year, 7, 15)


def _simchat_torah(year):
    """
    Return the Hebrew date for Simchat Torah in the given Hebrew year.
    """
    return dates.HebrewDate(year.year, 7, 22)


def _hebrew_year(year):
    """
    Return the Hebrew calendar year that corresponds to 1st January of the
    given Gregorian calendar year.

    1st January of any Gregorian calendar year, say x, always falls into the
    month of Tevet (10) or Shevat (11) of some Hebrew year f(x). Also, we have
    f(x+1) = f(x) + 1, so that any year in the Gregorian calendar always
    overlaps with two consecutive years in the Hebrew calendar and vice versa.
    """
    return hebrewcal.Year(dates.GregorianDate(year, 1, 1).to_heb().year)


# Auxilliary functions to calculate Gregorian dates for holidays observed by
# TASE for a given Gregorian calendar year. Adjustments are also applied.


def purim(year):
    """
    Return the Gregorian date for Purim in the given Gregorian calendar year.
    """
    return _purim(_hebrew_year(year)).to_greg()


def passover(year):
    """
    Return the Gregorian date for the first day of Passover in the given
    Gregorian calendar year.
    """
    return _passover(_hebrew_year(year)).to_greg()


def memorial_day(year):
    """
    Return the Gregorian date for Memorial Day in the given Gregorian calendar
    year.
    """

    # Regular Memorial Day date.
    d = _memorial_day(_hebrew_year(year)).to_greg()

    # Reschedule to avoid Sabbath desecration, maybe.
    if d.weekday() == 5:
        # Falls on a Thursday, so Independency Day falls on the Friday.
        # Moved down by one day.
        return d - 1
    elif d.weekday() == 6:
        # Falls on a Friday, so Independence Day falls on the Saturday.
        # Moved down by two days.
        return d - 2
    elif d.weekday() == 7:
        # Falls on a Saturday, therefore moved up by one day.
        return d + 1
    else:
        return d


def pentecost(year):
    """
    Return the Gregorian date for Pentecost in the given Gregorian calendar
    year.
    """
    return _pentecost(_hebrew_year(year)).to_greg()


def fast_day(year):
    """
    Return the Gregorian date for Tisha B'Av in the given Gregorian calendar
    year.
    """
    d = _fast_day(_hebrew_year(year)).to_greg()

    # Reschedule if it falls on Sabbath (Saturday), maybe.
    if d.weekday() == 7:
        # Falls on a Saturday, therefore moved up by one day.
        return d + 1
    else:
        return d


def new_year(year):
    """
    Return the Gregorian date for the first day of a new year in the given
    Gregorian calendar year.
    """
    return _new_year(_hebrew_year(year + 1)).to_greg()


def yom_kippur(year):
    """
    Return the Gregorian date for Yom Kippur in the given Gregorian calendar
    year.
    """
    return _yom_kippur(_hebrew_year(year + 1)).to_greg()


def sukkoth(year):
    """
    Return the Gregorian date for Sukkoth in the given Gregorian calendar year.
    """
    return _sukkoth(_hebrew_year(year + 1)).to_greg()


def simchat_torah(year):
    """
    Return the Gregorian date for Simchat Torah in the given Gregorian calendar
    year.
    """
    return _simchat_torah(_hebrew_year(year + 1)).to_greg()


def _is_normalized(dt):
    if dt.hour != 0 or dt.minute != 0 or dt.second != 0 or dt.microsecond != 0:
        # Regardless of whether dt is datetime vs Timestamp
        return False
    if isinstance(dt, pd.Timestamp):
        return dt.nanosecond == 0
    return True


class _HolidayOffset(Easter):
    """
    Auxiliary class for DateOffset instances for the different holidays.
    """

    @property
    def holiday(self):
        """
        Return the Gregorian date for the holiday in a given Gregorian calendar
        year.
        """
        pass

    @apply_wraps
    def apply(self, other):
        current = self.holiday(other.year).to_pydate()
        current = datetime(current.year, current.month, current.day)
        current = localize_pydatetime(current, other.tzinfo)

        n = self.n
        if n >= 0 and other < current:
            n -= 1
        elif n < 0 and other > current:
            n += 1
        # TODO: Why does this handle the 0 case the opposite of others?

        # NOTE: self.holiday a dates.GregorianDate so we have to convert to
        # type of other
        new = self.holiday(other.year + n).to_pydate()
        new = datetime(
            new.year,
            new.month,
            new.day,
            other.hour,
            other.minute,
            other.second,
            other.microsecond,
        )
        return new

    def is_on_offset(self, dt):
        if self.normalize and not _is_normalized(dt):
            return False
        return date(dt.year, dt.month, dt.day) == self.holiday(dt.year).to_pydate()


# DateOffset subclasses for holidays observed by TASE.


class _Purim(_HolidayOffset):
    @property
    def holiday(self):
        return purim


class _Passover(_HolidayOffset):
    @property
    def holiday(self):
        return passover


class _MemorialDay(_HolidayOffset):
    @property
    def holiday(self):
        return memorial_day


class _Pentecost(_HolidayOffset):
    @property
    def holiday(self):
        return pentecost


class _FastDay(_HolidayOffset):
    @property
    def holiday(self):
        return fast_day


class _NewYear(_HolidayOffset):
    @property
    def holiday(self):
        return new_year


class _YomKippur(_HolidayOffset):
    @property
    def holiday(self):
        return yom_kippur


class _Sukkoth(_HolidayOffset):
    @property
    def holiday(self):
        return sukkoth


class _SimchatTorah(_HolidayOffset):
    @property
    def holiday(self):
        return simchat_torah


# Holiday instances for holidays observed by TASE.
Purim = Holiday("Purim", month=1, day=1, offset=[_Purim()])
PassoverEve = Holiday("Passover Eve", month=1, day=1, offset=[_Passover(), Day(-1)])
Passover = Holiday("Passover", month=1, day=1, offset=[_Passover()])
Passover2Eve = Holiday("Passover II Eve", month=1, day=1, offset=[_Passover(), Day(5)])
Passover2 = Holiday("Passover II", month=1, day=1, offset=[_Passover(), Day(6)])
PentecostEve = Holiday("Pentecost Eve", month=1, day=1, offset=[_Pentecost(), Day(-1)])
Pentecost = Holiday("Pentecost", month=1, day=1, offset=[_Pentecost()])
FastDay = Holiday("Tisha B'Av", month=1, day=1, offset=[_FastDay()])
MemorialDay = Holiday("Memorial Day", month=1, day=1, offset=[_MemorialDay()])
IndependenceDay = Holiday(
    "Independence Day", month=1, day=1, offset=[_MemorialDay(), Day(1)]
)
NewYearsEve = Holiday("New Year's Eve", month=1, day=1, offset=[_NewYear(), Day(-1)])
NewYear = Holiday("New Year", month=1, day=1, offset=[_NewYear()])
NewYear2 = Holiday("New Year II", month=1, day=1, offset=[_NewYear(), Day(1)])
YomKippurEve = Holiday("Yom Kippur Eve", month=1, day=1, offset=[_YomKippur(), Day(-1)])
YomKippur = Holiday("Yom Kippur", month=1, day=1, offset=[_YomKippur()])
SukkothEve = Holiday("Sukkoth Eve", month=1, day=1, offset=[_Sukkoth(), Day(-1)])
Sukkoth = Holiday("Sukkoth", month=1, day=1, offset=[_Sukkoth()])
SimchatTorahEve = Holiday(
    "Simchat Torah Eve", month=1, day=1, offset=[_SimchatTorah(), Day(-1)]
)
SimchatTorah = Holiday("Simchat Torah", month=1, day=1, offset=[_SimchatTorah()])

# Passover interim days are the days between beginning and end of passover. Any otherwise regular business day in that
# period becomes an early close day.
PassoverInterimDay1 = Holiday("Passover Interim Day", month=1, day=1, offset=[_Passover(), Day(1)], days_of_week=(0, 1, 2, 3, 6))
PassoverInterimDay2 = Holiday("Passover Interim Day", month=1, day=1, offset=[_Passover(), Day(2)], days_of_week=(0, 1, 2, 3, 6))
PassoverInterimDay3 = Holiday("Passover Interim Day", month=1, day=1, offset=[_Passover(), Day(3)], days_of_week=(0, 1, 2, 3, 6))
PassoverInterimDay4 = Holiday("Passover Interim Day", month=1, day=1, offset=[_Passover(), Day(4)], days_of_week=(0, 1, 2, 3, 6))
