from pytz import UTC
import pandas as pd

PANDAS_VERSION = pd.__version__

try:
    from exchange_calendars import ExchangeCalendar as TradingCalendar
    from exchange_calendars.calendar_utils import (
        ExchangeCalendarDispatcher,
        _default_calendar_factories,
        _default_calendar_aliases,
    )
    from exchange_calendars.errors import InvalidCalendarName
    from exchange_calendars.utils.memoize import lazyval
    from exchange_calendars.utils.pandas_utils import days_at_time  # noqa: reexport

    def _fabricate(self, name: str, **kwargs):
        """Fabricate calendar with `name` and `**kwargs`."""
        try:
            factory = self._calendar_factories[name]
        except KeyError as e:
            raise InvalidCalendarName(calendar_name=name) from e
        if name in ["us_futures", "CMES", "XNYS"]:
            # exchange_calendars has a different default start data
            # that we need to overwrite in order to pass the legacy tests
            setattr(factory, "default_start", pd.Timestamp("1990-01-01", tz=UTC))
            # kwargs["start"] = pd.Timestamp("1990-01-01", tz="UTC")
        # Zipline had default open time of t+1min
        if name not in ["us_futures", "24/7", "24/5", "CMES"]:
            factory.open_times = [
                (d, t.replace(minute=t.minute + 1)) for d, t in factory.open_times
            ]
        calendar = factory(**kwargs)
        self._factory_output_cache[name] = (calendar, kwargs)
        return calendar

    # Yay! Monkey patching
    ExchangeCalendarDispatcher._fabricate = _fabricate

    global_calendar_dispatcher = ExchangeCalendarDispatcher(
        calendars={},
        calendar_factories=_default_calendar_factories,
        aliases=_default_calendar_aliases,
    )
    get_calendar = global_calendar_dispatcher.get_calendar

    get_calendar_names = global_calendar_dispatcher.get_calendar_names
    clear_calendars = global_calendar_dispatcher.clear_calendars
    deregister_calendar = global_calendar_dispatcher.deregister_calendar
    register_calendar = global_calendar_dispatcher.register_calendar
    register_calendar_type = global_calendar_dispatcher.register_calendar_type
    register_calendar_alias = global_calendar_dispatcher.register_calendar_alias
    resolve_alias = global_calendar_dispatcher.resolve_alias
    aliases_to_names = global_calendar_dispatcher.aliases_to_names
    names_to_aliases = global_calendar_dispatcher.names_to_aliases

except ImportError:
    if PANDAS_VERSION > "1.2.5":
        raise ImportError("For pandas >= 1.3 YOU MUST INSTALL exchange-calendars")
    else:
        from trading_calendars import (
            register_calendar,
            TradingCalendar,
            get_calendar,
            register_calendar_alias,
        )
        from trading_calendars.calendar_utils import global_calendar_dispatcher
        from trading_calendars.utils.memoize import lazyval
        from trading_calendars.utils.pandas_utils import days_at_time  # noqa: reexport
