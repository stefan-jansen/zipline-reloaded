# https://github.com/pandas-dev/pandas/blob/master/pandas/tseries/offsets.py
# https://github.com/pandas-dev/pandas/blob/master/pandas/_libs/tslibs/offsets.pyx

from datetime import datetime, timedelta

import toolz
import numpy as np
import pandas as pd

from pandas.tseries.offsets import CustomBusinessDay
from pandas._libs.tslibs.offsets import apply_wraps


class CompositeCustomBusinessDay(CustomBusinessDay):

    _prefix = "C"
    _attributes = tuple(
        [
            "n",
            "normalize",
            "weekmask",
            "holidays",
            "calendar",
            "offset",
            "business_days",
        ]
    )

    def __init__(
        self,
        n=1,
        normalize=False,
        weekmask="Mon Tue Wed Thu Fri",
        holidays=None,
        calendar=None,
        offset=timedelta(0),
        business_days=None,
    ):
        CustomBusinessDay.__init__(
            self, n, normalize, weekmask, holidays, calendar, offset
        )
        self.business_days = business_days

    def __setstate__(self, state):
        self.business_days = state.pop("business_days")
        CustomBusinessDay.__setstate__(self, state)

    @property
    def business_days(self):
        """
        Returns list of tuples of (start_date, end_date, custom_business_day)
        which overrides default behavior for the given interval, which starts
        from start_date to end_date, inclusive in both sides.
        """
        return tuple(self._business_days)

    @business_days.setter
    def business_days(self, business_days):
        self._business_days = []
        self._business_days_index = pd.IntervalIndex([], closed="both")
        self._business_days_all_index = pd.IntervalIndex([], closed="both")
        if business_days is not None:
            self._business_days = business_days
            business_days_intervals = []
            for start_date, end_date, _ in self._business_days:
                if start_date is None:
                    start_date = pd.Timestamp.min
                else:
                    start_date = pd.Timestamp(start_date)
                if end_date is None:
                    end_date = pd.Timestamp.max
                else:
                    end_date = pd.Timestamp(end_date)
                interval = pd.Interval(start_date, end_date, closed="both")
                business_days_intervals.append(interval)
            self._business_days_index = pd.IntervalIndex(
                business_days_intervals, closed="both"
            )
            business_days_all_intervals = []
            right = self._business_days_index[0]
            if pd.Timestamp.min < right.left:
                interval = pd.Interval(
                    pd.Timestamp.min, right.left - pd.Timedelta(1, unit="D")
                )
                business_days_all_intervals.append(interval)
            business_days_all_intervals.append(right)
            for left, right in toolz.sliding_window(
                2, toolz.concatv(self._business_days_index)
            ):
                if right.left - left.right > pd.Timestamp(1, unit="D"):
                    interval = pd.Interval(
                        left.right + pd.Timedelta(1, unit="D"),
                        right.left - pd.Timedelta(1, unit="D"),
                    )
                    business_days_all_intervals.append(interval)
                business_days_all_intervals.append(right)
            left = self._business_days_index[-1]
            if left.right < pd.Timestamp.max:
                interval = pd.Interval(
                    left.right + pd.Timedelta(1, unit="D"), pd.Timestamp.max
                )
                business_days_all_intervals.append(interval)
            self._business_days_all_index = pd.IntervalIndex(
                business_days_all_intervals, closed="both"
            )

    def _as_custom_business_day(self):
        return CustomBusinessDay(
            self.n,
            self.normalize,
            self.weekmask,
            self.holidays,
            self.calendar,
            self.offset,
        )

    def _custom_business_day_for(
        self, other, n=None, is_edge=False, with_interval=False
    ):
        loc = self._business_days_all_index.get_loc(other)
        if is_edge and n is not None:
            loc += np.sign(n)
        interval = self._business_days_all_index[loc]
        try:
            loc = self._business_days_index.get_loc(interval.left)
        except KeyError:
            bday = self._as_custom_business_day()
        else:
            bday = self._business_days[loc][-1]
        if n is not None:
            bday = bday.base * n
        if with_interval:
            return bday, interval
        else:
            return bday

    def _moved(self, from_date, to_date, bday):
        return np.busday_count(
            np.datetime64(from_date.date()),
            np.datetime64(to_date.date()),
            busdaycal=bday.calendar,
        )

    @apply_wraps
    def apply(self, other):
        if isinstance(other, datetime):
            moved = 0
            remaining = self.n - moved
            bday, interval = self._custom_business_day_for(
                other, remaining, with_interval=True
            )
            result = bday.apply(other)
            while not interval.left <= result <= interval.right:
                previous_other = other
                if result < interval.left:
                    other = interval.left
                elif result > interval.right:
                    other = interval.right
                else:
                    raise RuntimeError("Should not reach here")
                moved += self._moved(previous_other, other, bday)
                remaining = self.n - moved
                if remaining == 0:
                    break
                bday, interval = self._custom_business_day_for(
                    other, remaining, is_edge=True, with_interval=True
                )
                result = bday.apply(other)
            return result
        else:
            return super().apply(other)

    def is_on_offset(self, dt):
        if self.normalize and not _is_normalized(dt):
            return False
        day64 = _to_dt64D(dt)
        bday = self._custom_business_day_for(day64)
        return np.is_busday(day64, busdaycal=bday.calendar)


def _is_normalized(dt):
    if dt.hour != 0 or dt.minute != 0 or dt.second != 0 or dt.microsecond != 0:
        # Regardless of whether dt is datetime vs Timestamp
        return False
    if isinstance(dt, pd.Timestamp):
        return dt.nanosecond == 0
    return True


def _to_dt64D(dt):
    # Currently
    # > np.datetime64(dt.datetime(2013,5,1),dtype='datetime64[D]')
    # numpy.datetime64('2013-05-01T02:00:00.000000+0200')
    # Thus astype is needed to cast datetime to datetime64[D]
    if getattr(dt, "tzinfo", None) is not None:
        # Get the nanosecond timestamp,
        # equiv `Timestamp(dt).value` or `dt.timestamp() * 10**9`
        dt = pd.Timestamp(dt).value
        dt = np.int64(dt).astype("datetime64[ns]")
    else:
        dt = np.datetime64(dt)
    if dt.dtype.name != "datetime64[D]":
        dt = dt.astype("datetime64[D]")
    return dt


def _get_calendar(weekmask, holidays, calendar):
    """
    Generate busdaycalendar
    """
    if isinstance(calendar, np.busdaycalendar):
        if not holidays:
            holidays = tuple(calendar.holidays)
        elif not isinstance(holidays, tuple):
            holidays = tuple(holidays)
        else:
            # Trust that calendar.holidays and holidays are
            # consistent
            pass
        # Update weekmask if applicable (added)
        calendar = np.busdaycalendar(weekmask, holidays)
        return calendar, holidays

    if holidays is None:
        holidays = []
    # Handle non list holidays also (added)
    if isinstance(holidays, pd.DatetimeIndex):
        holidays = holidays.tolist()
    try:
        holidays = holidays + calendar.holidays().tolist()
    except AttributeError:
        pass
    holidays = [_to_dt64D(dt) for dt in holidays]
    holidays = tuple(sorted(holidays))

    kwargs = {"weekmask": weekmask}
    if holidays:
        kwargs["holidays"] = holidays

    busdaycalendar = np.busdaycalendar(**kwargs)
    return busdaycalendar, holidays


class MultipleWeekmaskCustomBusinessDay(CompositeCustomBusinessDay):

    _prefix = "C"
    _attributes = tuple(
        [
            "n",
            "normalize",
            "weekmask",
            "holidays",
            "calendar",
            "offset",
            "business_days",
            "weekmasks",
        ]
    )

    def __init__(
        self,
        n=1,
        normalize=False,
        weekmask="Mon Tue Wed Thu Fri",
        holidays=None,
        calendar=None,
        offset=timedelta(0),
        business_days=None,
        weekmasks=None,
    ):
        self._weekmasks = weekmasks
        if business_days is None and weekmasks is not None:
            calendars = [
                _get_calendar(weekmask=weekmask, holidays=holidays, calendar=calendar)
                for _start_date, _end_date, weekmask in weekmasks
            ]
            business_days = [
                (
                    start_date,
                    end_date,
                    CustomBusinessDay(
                        n, normalize, weekmask, holidays, calendar, offset
                    ),
                )
                for (start_date, end_date, weekmask), (calendar, holidays) in zip(
                    weekmasks, calendars
                )
            ]
        CompositeCustomBusinessDay.__init__(
            self, n, normalize, weekmask, holidays, calendar, offset, business_days
        )

    def __setstate__(self, state):
        self.weekmasks = state.pop("weekmasks")
        CompositeCustomBusinessDay.__setstate__(self, state)

    @property
    def weekmasks(self):
        return tuple(self._weekmasks)

    @weekmasks.setter
    def weekmasks(self, weekmasks):
        self._weekmasks = weekmasks
