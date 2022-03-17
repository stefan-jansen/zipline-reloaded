#
# Copyright 2015 Quantopian, Inc.
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
from __future__ import annotations
import typing
import pandas as pd

from exchange_calendars.utils.memoize import lazyval

if typing.TYPE_CHECKING:
    from exchange_calendars import ExchangeCalendar


class CalendarError(Exception):
    msg = None

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    @lazyval
    def message(self):
        return str(self)

    def __str__(self):
        msg = self.msg.format(**self.kwargs)
        return msg

    __unicode__ = __str__
    __repr__ = __str__


class InvalidCalendarName(CalendarError):
    """
    Raised when a calendar with an invalid name is requested.
    """

    msg = "The requested ExchangeCalendar, {calendar_name}, does not exist."


class CalendarNameCollision(CalendarError):
    """
    Raised when the static calendar registry already has a calendar with a
    given name.
    """

    msg = "A calendar with the name {calendar_name} is already registered."


class CyclicCalendarAlias(CalendarError):
    """
    Raised when calendar aliases form a cycle.
    """

    msg = "Cycle in calendar aliases: [{cycle}]"


class ScheduleFunctionWithoutCalendar(CalendarError):
    """
    Raised when schedule_function is called but there is not a calendar to be
    used in the construction of an event rule.
    """

    # TODO update message when new TradingSchedules are built
    msg = (
        "To use schedule_function, the TradingAlgorithm must be running on an "
        "ExchangeTradingSchedule, rather than {schedule}."
    )


class ScheduleFunctionInvalidCalendar(CalendarError):
    """
    Raised when schedule_function is called with an invalid calendar argument.
    """

    msg = (
        "Invalid calendar '{given_calendar}' passed to schedule_function. "
        "Allowed options are {allowed_calendars}."
    )


class NotSessionError(ValueError):
    """Input does not represent a valid session.

    Raised if parameter expecting a session label receives input that
    parses correctly (UTC midnight) although is not a session.

    Parameters
    ----------
    calendar
        Calendar for which `ts` assumed as a session.

    ts
        Timestamp assumed as a session.

    param_name
        Name of a parameter that was to receive a session label.
    """

    def __init__(self, calendar: ExchangeCalendar, ts: pd.Timestamp, param_name: str):
        self.calendar = calendar
        self.ts = ts
        self.param_name = param_name

    def __str__(self) -> str:
        msg = (
            f"Parameter `{self.param_name}` takes a session label"
            f" although received input that parsed to '{self.ts}' which"
        )

        if self.ts < self.calendar.first_session:
            msg += (
                " is earlier than the first session of calendar"
                f" '{self.calendar.name}' ('{self.calendar.first_session}')."
            )
        elif self.ts > self.calendar.last_session:
            msg += (
                " is later than the last session of calendar"
                f" '{self.calendar.name}' ('{self.calendar.last_session}')."
            )
        else:
            msg += f" is not a session of calendar '{self.calendar.name}'."
        return msg


class DateOutOfBounds(ValueError):
    """A date required to be within sessions' bounds is not.

    Parameters
    ----------
    calendar
        Calendar for which `date` required to be within sessions'
        bounds.

    date
        Date required to be within `calendar`'s sessions' bounds.

    param_name
        Name of a parameter receiving date.
    """

    def __init__(self, calendar: ExchangeCalendar, date: pd.Timestamp, param_name: str):
        self.calendar = calendar
        self.date = date
        self.param_name = param_name

    def __str__(self) -> str:
        msg = f"Parameter `{self.param_name}` receieved as '{self.date}' although"
        if self.date < self.calendar.first_session:
            msg += (
                " cannot be earlier than the first session of calendar"
                f" '{self.calendar.name}' ('{self.calendar.first_session}')."
            )
        elif self.date > self.calendar.last_session:
            msg += (
                " cannot be later than the last session of calendar"
                f" '{self.calendar.name}' ('{self.calendar.last_session}')."
            )
        else:
            assert (
                self.date < self.calendar.first_session
                or self.date > self.calendar.last_session
            )
        return msg


class MinuteOutOfBounds(ValueError):
    """A minute required to be within bounds of trading minutes is not.

    Parameters
    ----------
    calendar
        Calendar for which `minute` required to be within bounds of
        trading minutes.

    minute
        Minute required to be within bounds of `calendar`'s trading
        minutes.

    param_name
        Name of a parameter receiving `minute`.
    """

    def __init__(
        self, calendar: ExchangeCalendar, minute: pd.Timestamp, param_name: str
    ):
        self.calendar = calendar
        self.minute = minute
        self.param_name = param_name

    def __str__(self) -> str:
        msg = f"Parameter `{self.param_name}` receieved as '{self.minute}' although"
        if self.minute < self.calendar.first_trading_minute:
            msg += (
                " cannot be earlier than the first trading minute of calendar"
                f" '{self.calendar.name}' ('{self.calendar.first_trading_minute}')."
            )
        elif self.minute > self.calendar.last_trading_minute:
            msg += (
                " cannot be later than the last trading minute of calendar"
                f" '{self.calendar.name}' ('{self.calendar.last_trading_minute}')."
            )
        else:
            assert (
                self.minute < self.calendar.first_trading_minute
                or self.minute > self.calendar.last_trading_minute
            )
        return msg
