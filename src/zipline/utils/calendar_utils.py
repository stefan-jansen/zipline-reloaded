from pytz import UTC
import pandas as pd
from functools import partial

from trading_calendars import (
    register_calendar,
    TradingCalendar,
    get_calendar,
    register_calendar_alias,
)
from trading_calendars.calendar_utils import global_calendar_dispatcher
from trading_calendars.utils.memoize import lazyval
from trading_calendars.utils.pandas_utils import days_at_time  # noqa: reexport

# from exchange_calendars.calendar_utils import (
#     ExchangeCalendarDispatcher,
#     _default_calendar_factories,
#     _default_calendar_aliases,
# )


# for k, v in _default_calendar_factories.items():
#     if k in ["us_futures", "CMES", "XNYS"]:
#         # TODO: I don't really like setting attribute like this
#         setattr(v, "default_start", pd.Timestamp("1990-01-01", tz=UTC))
#     if k not in ["us_futures", "24/7", "24/5", "CMES"]:
#         v.open_times = [(d, t.replace(minute=t.minute + 1)) for d, t in v.open_times]
#         _default_calendar_factories[k] = v


# global_calendar_dispatcher = ExchangeCalendarDispatcher(
#     calendars={},
#     calendar_factories=_default_calendar_factories,
#     aliases=_default_calendar_aliases,
# )

# # exchange_calendars has a different default start data that we need to overwrite
# get_calendar = global_calendar_dispatcher.get_calendar

# get_calendar_names = global_calendar_dispatcher.get_calendar_names
# clear_calendars = global_calendar_dispatcher.clear_calendars
# deregister_calendar = global_calendar_dispatcher.deregister_calendar
# register_calendar = global_calendar_dispatcher.register_calendar
# register_calendar_type = global_calendar_dispatcher.register_calendar_type
# register_calendar_alias = global_calendar_dispatcher.register_calendar_alias
# resolve_alias = global_calendar_dispatcher.resolve_alias
# aliases_to_names = global_calendar_dispatcher.aliases_to_names
# names_to_aliases = global_calendar_dispatcher.names_to_aliases
