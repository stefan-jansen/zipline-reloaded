# https://github.com/pandas-dev/pandas/blob/master/pandas/tseries/holiday.py

import warnings

from pandas.tseries.holiday import (
    Holiday as PandasHoliday,
    AbstractHolidayCalendar as PandasAbstractHolidayCalendar,
)
from pandas.tseries.offsets import BaseOffset
from pandas import (
    DatetimeIndex,
    Series,
    Timestamp,
)
from pandas.errors import PerformanceWarning

from .offsets import _is_normalized


class Holiday(PandasHoliday):
    """
    This extension allows to have both offset and observance while the original
    Holiday does not. The order of application is offset => observance.
    """

    def __init__(
        self,
        name,
        year=None,
        month=None,
        day=None,
        offset=None,
        observance=None,
        start_date=None,
        end_date=None,
        days_of_week=None,
        tz=None,
    ):
        super().__init__(
            name,
            year,
            month,
            day,
            None,
            None,
            start_date,
            end_date,
            days_of_week,
        )
        self.offset = offset
        self.observance = observance
        self.tz = tz
        if self.start_date is not None:
            if self.tz is None and self.start_date.tz is not None:
                self.tz = start_date.tz
            if self.start_date.tz is None and self.tz is not None:
                self.start_date = self.start_date.tz_localize(self.tz)
            assert self.tz == self.start_date.tz
        if self.end_date is not None:
            if self.tz is None and self.end_date.tz is not None:
                self.tz = start_date.tz
            if self.end_date.tz is None and self.tz is not None:
                self.end_date = self.end_date.tz_localize(self.tz)
            assert self.tz == self.end_date.tz
        if self.start_date is not None and self.end_date is not None:
            self.start_date.tz == self.end_date.tz

    def __repr__(self) -> str:
        info = ""
        if self.year is not None:
            info += f"year={self.year}, "
        info += f"month={self.month}, day={self.day}"

        if self.offset is not None:
            info += f", offset={self.offset}"

        if self.observance is not None:
            info += f", observance={self.observance}"

        repr = f"{self.__class__.__name__}: {self.name} ({info})"
        return repr

    def dates(self, start_date, end_date, return_name=False):
        start_date = Timestamp(start_date)
        end_date = Timestamp(end_date)
        assert start_date.tz == self.tz
        assert _is_normalized(start_date)
        assert end_date.tz == self.tz
        assert _is_normalized(end_date)
        return super().dates(start_date, end_date, return_name=return_name)

    def _apply_offset(self, dates):
        if self.offset is not None:
            if not isinstance(self.offset, list):
                offsets = [self.offset]
            else:
                offsets = self.offset
            for offset in offsets:
                # If we are adding a non-vectorized value
                # ignore the PerformanceWarnings:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", PerformanceWarning)
                    dates += offset
        return dates

    def _apply_observance(self, dates):
        if self.observance is not None:
            if not isinstance(self.observance, list):
                observances = [self.observance]
            else:
                observances = self.observance
            for observance in observances:
                if isinstance(observance, BaseOffset):
                    offset = observance

                    def f(d):
                        return d + offset

                    observance = f
                dates = dates.map(observance)
        return dates

    def _apply_rule(self, dates, apply_offset=True, apply_observance=True):
        if apply_offset:
            dates = self._apply_offset(dates)
        if apply_observance:
            dates = self._apply_observance(dates)
        return dates


def combine(pre_holidays):
    combined = Series(index=DatetimeIndex([]), dtype=object)
    for holidays in pre_holidays:
        combined = combined.combine_first(holidays)
    return combined


class AbstractHolidayCalendar(PandasAbstractHolidayCalendar):
    """
    This extension allows to have overlaps between calculated holidays while
    the original AbstractHolidayCalendar does not.
    """

    def holidays(self, start=None, end=None, return_name=False):
        """
        Returns a curve with holidays between start_date and end_date
        Parameters
        ----------
        start : starting date, datetime-like, optional
        end : ending date, datetime-like, optional
        return_name : bool, optional
            If True, return a series that has dates and holiday names.
            False will only return a DatetimeIndex of dates.
        Returns
        -------
            DatetimeIndex of holidays
        """
        if self.rules is None:
            raise Exception(
                f"Holiday Calendar {self.name} does not have any rules specified"
            )

        if start is None:
            start = AbstractHolidayCalendar.start_date

        if end is None:
            end = AbstractHolidayCalendar.end_date

        start = Timestamp(start)
        end = Timestamp(end)

        # If we don't have a cache or the dates are outside the prior cache, we
        # get them again
        if self._cache is None or start < self._cache[0] or end > self._cache[1]:
            pre_holidays = [
                rule.dates(start, end, return_name=True) for rule in self.rules
            ]
            if pre_holidays:
                # This line's behavior is changed to use custom combine()
                # function instead of the original concat() function
                holidays = combine(pre_holidays)
            else:
                holidays = Series(index=DatetimeIndex([]), dtype=object)

            self._cache = (start, end, holidays.sort_index())

        holidays = self._cache[2]
        holidays = holidays[start:end]

        if return_name:
            return holidays
        else:
            return holidays.index
