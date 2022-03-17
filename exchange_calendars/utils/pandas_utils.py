import numpy as np
import pandas as pd
from pytz import UTC


def days_at_time(days, t, tz, day_offset=0):
    """
    Create an index of days at time ``t``, interpreted in timezone ``tz``.

    The returned index is localized to UTC.

    Parameters
    ----------
    days : DatetimeIndex
        An index of dates (represented as midnight).
    t : datetime.time
        The time to apply as an offset to each day in ``days``.
    tz : pytz.timezone
        The timezone to use to interpret ``t``.
    day_offset : int
        The number of days we want to offset @days by

    Examples
    --------
    In the example below, the times switch from 13:45 to 12:45 UTC because
    March 13th is the daylight savings transition for UAmerica/New_York. All
    the times are still 8:45 when interpreted in America/New_York.

    >>> import pandas as pd; import datetime; import pprint
    >>> dts = pd.date_range('2016-03-12', '2016-03-14')
    >>> dts_845 = days_at_time(dts, datetime.time(8, 45), 'America/New_York')
    >>> pprint.pprint([str(dt) for dt in dts_845])
    ['2016-03-12 13:45:00+00:00',
     '2016-03-13 12:45:00+00:00',
     '2016-03-14 12:45:00+00:00']
    """
    if t is None:
        return pd.DatetimeIndex([None for _ in days]).tz_localize(UTC)

    days = pd.DatetimeIndex(days).tz_localize(None)

    if len(days) == 0:
        return days.tz_localize(UTC)

    # Offset days without tz to avoid timezone issues.
    delta = pd.Timedelta(
        days=day_offset,
        hours=t.hour,
        minutes=t.minute,
        seconds=t.second,
    )
    return (days + delta).tz_localize(tz).tz_convert(UTC)


def vectorized_sunday_to_monday(dtix):
    """A vectorized implementation of
    :func:`pandas.tseries.holiday.sunday_to_monday`.

    Parameters
    ----------
    dtix : pd.DatetimeIndex
        The index to shift sundays to mondays.

    Returns
    -------
    sundays_as_mondays : pd.DatetimeIndex
        ``dtix`` with all sundays moved to the next monday.
    """
    values = dtix.values.copy()
    values[dtix.weekday == 6] += np.timedelta64(1, "D")
    return pd.DatetimeIndex(values)
