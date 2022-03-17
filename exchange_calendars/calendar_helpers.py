from __future__ import annotations
import typing
import datetime

import numpy as np
import pandas as pd

from exchange_calendars import errors

if typing.TYPE_CHECKING:
    from exchange_calendars import ExchangeCalendar

NANOSECONDS_PER_MINUTE = int(6e10)

NP_NAT = pd.NaT.value

# Use Date type where input does not need to represent an actual session
# and will be parsed by parse_date
Date = typing.Union[pd.Timestamp, str, int, float, datetime.datetime]
# Use Session type where input should represent an actual session and will
# be parsed by parse_session
Session = Date
# Use Minute type where input does not need to represent an actual trading
# minute and will be parsed by parse_timestamp
Minute = typing.Union[pd.Timestamp, str, int, float, datetime.datetime]


def next_divider_idx(dividers: np.ndarray, minute_val: int) -> int:

    divider_idx = np.searchsorted(dividers, minute_val, side="right")
    target = dividers[divider_idx]

    if minute_val == target:
        # if dt is exactly on the divider, go to the next value
        return divider_idx + 1
    else:
        return divider_idx


def previous_divider_idx(dividers: np.ndarray, minute_val: int) -> int:

    divider_idx = np.searchsorted(dividers, minute_val)

    if divider_idx == 0:
        raise ValueError("Cannot go earlier in calendar!")

    return divider_idx - 1


def compute_all_minutes(
    opens_in_ns: np.ndarray,
    break_starts_in_ns: np.ndarray,
    break_ends_in_ns: np.ndarray,
    closes_in_ns: np.ndarray,
) -> np.ndarray:
    """
    Given arrays of opens and closes (in nanoseconds) and optionally
    break_starts and break ends, return an array of each minute between the
    opens and closes.

    NOTE: Add an extra minute to ending boundaries (break_start and close)
    so we include the last bar (arange doesn't include its stop).
    """
    pieces = []
    for open_time, break_start_time, break_end_time, close_time in zip(
        opens_in_ns, break_starts_in_ns, break_ends_in_ns, closes_in_ns
    ):
        if break_start_time != NP_NAT:
            pieces.append(
                np.arange(
                    open_time,
                    break_start_time + NANOSECONDS_PER_MINUTE,
                    NANOSECONDS_PER_MINUTE,
                )
            )
            pieces.append(
                np.arange(
                    break_end_time,
                    close_time + NANOSECONDS_PER_MINUTE,
                    NANOSECONDS_PER_MINUTE,
                )
            )
        else:
            pieces.append(
                np.arange(
                    open_time,
                    close_time + NANOSECONDS_PER_MINUTE,
                    NANOSECONDS_PER_MINUTE,
                )
            )
    out = np.concatenate(pieces).view("datetime64[ns]")
    return out


def parse_timestamp(
    timestamp: Date | Minute,
    param_name: str,
    utc: bool = True,
    raise_oob: bool = False,
    calendar: ExchangeCalendar | None = None,
) -> pd.Timestamp:
    """Parse input intended to represent either a date or a minute.

    Parameters
    ----------
    timestamp
        Input to be parsed as either a Date or a Minute. Must be valid
        input to pd.Timestamp.

    param_name
        Name of a parameter that was to receive a Date or Minute.

    utc : default: True
        True - convert / set timezone to "UTC".
        False - leave any timezone unchanged. Note, if timezone of
        `timestamp` is "UTC" then will remain as "UTC".

    raise_oob : default: False
        True to raise MinuteOutOfBounds if `timestamp` is earlier than the
        first trading minute or later than the last trading minute of
        `calendar`. Only use when `timestamp` represents a Minute (as
        opposed to a Date). If True then `calendar` must be passed.

    calendar
        ExchangeCalendar against which to evaluate out-of-bounds timestamps.
        Only requried if `raise_oob` True.

    Raises
    ------
    TypeError
        If `timestamp` is not of type [pd.Timestamp | str | int | float |
            datetime.datetime].

    ValueError
        If `timestamp` is not an acceptable single-argument input to
        pd.Timestamp.

    exchange_calendars.errors.MinuteOutOfBounds
        If `raise_oob` True and `timestamp` parses to a valid timestamp
        although timestamp is either before `calendar`'s first trading
        minute or after `calendar`'s last trading minute.
    """
    try:
        ts = pd.Timestamp(timestamp)
    except Exception as e:
        msg = (
            f"Parameter `{param_name}` receieved as '{timestamp}' although a Date or"
            f" Minute must be passed as a pd.Timestamp or a valid single-argument"
            f" input to pd.Timestamp."
        )
        if isinstance(e, TypeError):
            raise TypeError(msg) from e
        else:
            raise ValueError(msg) from e

    if utc:
        ts = ts.tz_localize("UTC") if ts.tz is None else ts.tz_convert("UTC")

    ts = ts.floor("T")

    if raise_oob:
        if calendar is None:
            raise ValueError("`calendar` must be passed if `raise_oob` is True.")
        if ts < calendar.first_trading_minute or ts > calendar.last_trading_minute:
            raise errors.MinuteOutOfBounds(calendar, ts, param_name)

    return ts


def parse_date(
    date: Date,
    param_name: str,
    raise_oob: bool = False,
    calendar: ExchangeCalendar | None = None,
) -> pd.Timestamp:
    """Parse input intended to represent a date.

     Parameters
     ----------
     date
         Input to be parsed as date. Must be valid input to pd.Timestamp
         and have a time component of 00:00.

     param_name
         Name of a parameter that was to receive a date.

    raise_oob : default: False
        True to raise DateOutOfBounds if `date` is earlier than the
        first session or later than the last session of `calendar`. NB if
        True then `calendar` must be passed.

    calendar
        ExchangeCalendar against which to evalute out-of-bounds dates.
        Only requried if `raise_oob` True.

    Returns
     -------
     pd.Timestamp
         pd.Timestamp (UTC with time component of 00:00).

     Raises
     ------
     Errors as `parse_timestamp` and additionally:

     ValueError
         If `date` time component is not 00:00.

         If `date` is timezone aware and timezone is not UTC.

    exchange_calendars.errors.DateOutOfBounds
        If `raise_oob` True and `date` parses to a valid timestamp although
        timestamp is before `calendar`'s first session or after
        `calendar`'s last session.
    """
    ts = parse_timestamp(date, param_name, utc=False)

    if not (ts.tz is None or ts.tz.zone == "UTC"):
        raise ValueError(
            f"Parameter `{param_name}` parsed as '{ts}' although a Date must be"
            f" timezone naive or have timezone as 'UTC'."
        )

    if not ts == ts.normalize():
        raise ValueError(
            f"Parameter `{param_name}` parsed as '{ts}' although a Date must have"
            f" a time component of 00:00."
        )

    if ts.tz is None:
        ts = ts.tz_localize("UTC")

    if raise_oob:
        if calendar is None:
            raise ValueError("`calendar` must be passed if `raise_oob` is True.")
        if ts < calendar.first_session or ts > calendar.last_session:
            raise errors.DateOutOfBounds(calendar, ts, param_name)

    return ts


def parse_session(
    calendar: ExchangeCalendar, session: Session, param_name: str
) -> pd.Timestamp:
    """Parse input intended to represent a session label.

    Parameters
    ----------
    calendar
        Calendar against which to evaluate `session`.

    session
        Input to be parsed as session. Must be valid input to pd.Timestamp,
        have a time component of 00:00 and represent a session of
        `calendar`.

    param_name
        Name of a parameter that was to receive a session label.

    Returns
    -------
    pd.Timestamp
        pd.Timestamp (UTC with time component of 00:00) that represents a
        real session of `calendar`.

    Raises
    ------
    Errors as `parse_date` and additionally:

    exchange_calendars.errors.NotSessionError
        If `session` parses to a valid date although date does not
        represent a session of `calendar`.
    """
    ts = parse_date(session, param_name)
    # don't check via is_session to allow for more specific error message if
    # `session` is out-of-bounds
    if ts not in calendar.schedule.index:
        raise errors.NotSessionError(calendar, ts, param_name)
    return ts
