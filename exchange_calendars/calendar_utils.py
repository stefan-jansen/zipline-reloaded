from __future__ import annotations

from .calendar_helpers import parse_date
from .always_open import AlwaysOpenCalendar
from .errors import CalendarNameCollision, CyclicCalendarAlias, InvalidCalendarName
from .exchange_calendar import ExchangeCalendar
from .exchange_calendar_aixk import AIXKExchangeCalendar
from .exchange_calendar_asex import ASEXExchangeCalendar
from .exchange_calendar_bvmf import BVMFExchangeCalendar
from .exchange_calendar_cmes import CMESExchangeCalendar
from .exchange_calendar_iepa import IEPAExchangeCalendar
from .exchange_calendar_xams import XAMSExchangeCalendar
from .exchange_calendar_xasx import XASXExchangeCalendar
from .exchange_calendar_xbkk import XBKKExchangeCalendar
from .exchange_calendar_xbog import XBOGExchangeCalendar
from .exchange_calendar_xbom import XBOMExchangeCalendar
from .exchange_calendar_xbru import XBRUExchangeCalendar
from .exchange_calendar_xbse import XBSEExchangeCalendar
from .exchange_calendar_xbud import XBUDExchangeCalendar
from .exchange_calendar_xbue import XBUEExchangeCalendar
from .exchange_calendar_xcbf import XCBFExchangeCalendar
from .exchange_calendar_xcse import XCSEExchangeCalendar
from .exchange_calendar_xdub import XDUBExchangeCalendar
from .exchange_calendar_xetr import XETRExchangeCalendar
from .exchange_calendar_xfra import XFRAExchangeCalendar
from .exchange_calendar_xhel import XHELExchangeCalendar
from .exchange_calendar_xhkg import XHKGExchangeCalendar
from .exchange_calendar_xice import XICEExchangeCalendar
from .exchange_calendar_xidx import XIDXExchangeCalendar
from .exchange_calendar_xist import XISTExchangeCalendar
from .exchange_calendar_xjse import XJSEExchangeCalendar
from .exchange_calendar_xkar import XKARExchangeCalendar
from .exchange_calendar_xkls import XKLSExchangeCalendar
from .exchange_calendar_xkrx import XKRXExchangeCalendar
from .exchange_calendar_xlim import XLIMExchangeCalendar
from .exchange_calendar_xlis import XLISExchangeCalendar
from .exchange_calendar_xlon import XLONExchangeCalendar
from .exchange_calendar_xmad import XMADExchangeCalendar
from .exchange_calendar_xmex import XMEXExchangeCalendar
from .exchange_calendar_xmil import XMILExchangeCalendar
from .exchange_calendar_xmos import XMOSExchangeCalendar
from .exchange_calendar_xnys import XNYSExchangeCalendar
from .exchange_calendar_xnze import XNZEExchangeCalendar
from .exchange_calendar_xosl import XOSLExchangeCalendar
from .exchange_calendar_xpar import XPARExchangeCalendar
from .exchange_calendar_xphs import XPHSExchangeCalendar
from .exchange_calendar_xpra import XPRAExchangeCalendar
from .exchange_calendar_xses import XSESExchangeCalendar
from .exchange_calendar_xsgo import XSGOExchangeCalendar
from .exchange_calendar_xshg import XSHGExchangeCalendar
from .exchange_calendar_xsto import XSTOExchangeCalendar
from .exchange_calendar_xswx import XSWXExchangeCalendar
from .exchange_calendar_xtae import XTAEExchangeCalendar
from .exchange_calendar_xtai import XTAIExchangeCalendar
from .exchange_calendar_xtks import XTKSExchangeCalendar
from .exchange_calendar_xtse import XTSEExchangeCalendar
from .exchange_calendar_xwar import XWARExchangeCalendar
from .exchange_calendar_xwbo import XWBOExchangeCalendar
from .us_futures_calendar import QuantopianUSFuturesCalendar
from .weekday_calendar import WeekdayCalendar

_default_calendar_factories = {
    # Exchange calendars.
    "AIXK": AIXKExchangeCalendar,
    "ASEX": ASEXExchangeCalendar,
    "BVMF": BVMFExchangeCalendar,
    "CMES": CMESExchangeCalendar,
    "IEPA": IEPAExchangeCalendar,
    "XAMS": XAMSExchangeCalendar,
    "XASX": XASXExchangeCalendar,
    "XBKK": XBKKExchangeCalendar,
    "XBOG": XBOGExchangeCalendar,
    "XBOM": XBOMExchangeCalendar,
    "XBRU": XBRUExchangeCalendar,
    "XBSE": XBSEExchangeCalendar,
    "XBUD": XBUDExchangeCalendar,
    "XBUE": XBUEExchangeCalendar,
    "XCBF": XCBFExchangeCalendar,
    "XCSE": XCSEExchangeCalendar,
    "XDUB": XDUBExchangeCalendar,
    "XFRA": XFRAExchangeCalendar,
    "XETR": XETRExchangeCalendar,
    "XHEL": XHELExchangeCalendar,
    "XHKG": XHKGExchangeCalendar,
    "XICE": XICEExchangeCalendar,
    "XIDX": XIDXExchangeCalendar,
    "XIST": XISTExchangeCalendar,
    "XJSE": XJSEExchangeCalendar,
    "XKAR": XKARExchangeCalendar,
    "XKLS": XKLSExchangeCalendar,
    "XKRX": XKRXExchangeCalendar,
    "XLIM": XLIMExchangeCalendar,
    "XLIS": XLISExchangeCalendar,
    "XLON": XLONExchangeCalendar,
    "XMAD": XMADExchangeCalendar,
    "XMEX": XMEXExchangeCalendar,
    "XMIL": XMILExchangeCalendar,
    "XMOS": XMOSExchangeCalendar,
    "XNYS": XNYSExchangeCalendar,
    "XNZE": XNZEExchangeCalendar,
    "XOSL": XOSLExchangeCalendar,
    "XPAR": XPARExchangeCalendar,
    "XPHS": XPHSExchangeCalendar,
    "XPRA": XPRAExchangeCalendar,
    "XSES": XSESExchangeCalendar,
    "XSGO": XSGOExchangeCalendar,
    "XSHG": XSHGExchangeCalendar,
    "XSTO": XSTOExchangeCalendar,
    "XSWX": XSWXExchangeCalendar,
    "XTAE": XTAEExchangeCalendar,
    "XTAI": XTAIExchangeCalendar,
    "XTKS": XTKSExchangeCalendar,
    "XTSE": XTSEExchangeCalendar,
    "XWAR": XWARExchangeCalendar,
    "XWBO": XWBOExchangeCalendar,
    # Miscellaneous calendars.
    "us_futures": QuantopianUSFuturesCalendar,
    "24/7": AlwaysOpenCalendar,
    "CRYPTO": AlwaysOpenCalendar,
    "24/5": WeekdayCalendar,
}
_default_calendar_aliases = {
    "NYSE": "XNYS",
    "NASDAQ": "XNYS",
    "BATS": "XNYS",
    "FWB": "XFRA",
    "LSE": "XLON",
    "TSX": "XTSE",
    "BMF": "BVMF",
    "CME": "CMES",
    "CBOT": "CMES",
    "COMEX": "CMES",
    "NYMEX": "CMES",
    "ICE": "IEPA",
    "ICEUS": "IEPA",
    "NYFE": "IEPA",
    "CFE": "XCBF",
    "JKT": "XIDX",
    "SIX": "XSWX",
    "JPX": "XTKS",
    "ASX": "XASX",
    "HKEX": "XHKG",
    "OSE": "XOSL",
    "BSE": "XBOM",
    "SSE": "XSHG",
    "TASE": "XTAE",
    "BVB": "XBSE",
}

default_calendar_names = sorted(_default_calendar_factories.keys())


class ExchangeCalendarDispatcher(object):
    """
    A class for dispatching and caching exchange calendars.

    Methods of a global instance of this class can be accessed directly
    from exchange_calendars, for example `exchange_calendars.get_calendar`.

    Parameters
    ----------
    calendars : dict[str -> ExchangeCalendar]
        Initial set of calendars.
    calendar_factories : dict[str -> function]
        Factories for lazy calendar creation.
    aliases : dict[str -> str]
        Calendar name aliases.
    """

    def __init__(self, calendars, calendar_factories, aliases):
        self._calendars = calendars
        self._calendar_factories = dict(calendar_factories)
        self._aliases = dict(aliases)
        # key: factory name, value: (calendar, dict of calendar kwargs)
        self._factory_output_cache: dict(str, tuple(ExchangeCalendar, dict)) = {}

    def _fabricate(self, name: str, **kwargs) -> ExchangeCalendar:
        """Fabricate calendar with `name` and `**kwargs`."""
        try:
            factory = self._calendar_factories[name]
        except KeyError as e:
            raise InvalidCalendarName(calendar_name=name) from e
        calendar = factory(**kwargs)
        self._factory_output_cache[name] = (calendar, kwargs)
        return calendar

    def _get_cached_factory_output(
        self, name: str, **kwargs
    ) -> ExchangeCalendar | None:
        """Get calendar from factory output cache.

        Return None if `name` not in cache or `name` in cache although
        calendar got with kwargs other than `**kwargs`.
        """
        calendar, calendar_kwargs = self._factory_output_cache.get(name, (None, None))
        if calendar is not None and calendar_kwargs == kwargs:
            return calendar
        else:
            return None

    def get_calendar(self, name: str, **kwargs) -> ExchangeCalendar:
        """Get exchange calendar with a given name.

        Parameters
        ----------
        name
            Name of the ExchangeCalendar to get, for example 'XNYS'.

        **kwargs
            Kwargs to be passed to calendar factory. `**kwargs` can only be
            passed if `name` is registered as a calendar factory (either by
            having been included to `calendar_factories` passed to the
            dispatcher's constructor or having been subsequently registered
            via the `register_calendar_type` method).

        Returns
        -------
        ExchangeCalendar
            Requested calendar.

        Raises
        ------
        InvalidCalendarName
            If `name` does not represent a registered calendar.

        ValueError
            If `**kwargs` are received although `name` is a registered
            calendar (as opposed to a calendar factory).

            If `start` or `end` are included to `**kwargs` although do not
            parse as a date that could represent a session.
        """
        # will raise InvalidCalendarName if name not valid
        name = self.resolve_alias(name)

        if name in self._calendars:
            if kwargs:
                raise ValueError(
                    f"Receieved constructor arguments `start` and/or `end`"
                    f" although calendar {name} is registered as a specific"
                    f" instance of class {self._calendars[name].__class__},"
                    f" not as a calendar factory."
                )
            else:
                return self._calendars[name]

        if kwargs.get("start"):
            kwargs["start"] = parse_date(kwargs["start"], "start")
        else:
            kwargs["start"] = None
        if kwargs.get("end"):
            kwargs["end"] = parse_date(kwargs["end"], "end")
        else:
            kwargs["end"] = None

        cached = self._get_cached_factory_output(name, **kwargs)
        return cached if cached is not None else self._fabricate(name, **kwargs)

    def get_calendar_names(
        self, include_aliases: bool = True, sort: bool = True
    ) -> list[str]:
        """Return all canoncial calendar names and, optionally, aliases.

        Parameters
        ----------
        include_aliases : default: True
            True to include calendar aliases.
            False to return only canonical calendar names.

        sort : default: True
            Return calendar names sorted alphabetically.

        Returns
        -------
        list of str
            List of canonical calendar names and, optionally, aliases.

        See Also
        --------
        names_to_aliases : Mapping of cononcial names to aliases.
        aliases_to_names : Mapping of aliases to canoncial names.
        resolve_alias : Resolve single alias to a canonical name.
        """
        keys = set(self._calendar_factories.keys()).union(set(self._calendars.keys()))
        if include_aliases:
            keys = keys.union(set(self._aliases.keys()))
        names = list(keys)
        if sort:
            names.sort()
        return names

    def has_calendar(self, name):
        """
        Do we have (or have the ability to make) a calendar with ``name``?
        """
        return (
            name in self._calendars
            or name in self._calendar_factories
            or name in self._aliases
        )

    def register_calendar(self, name, calendar, force=False):
        """
        Registers a calendar for retrieval by the get_calendar method.

        Parameters
        ----------
        name: str
            The key with which to register this calendar.
        calendar: ExchangeCalendar
            The calendar to be registered for retrieval.
        force : bool, optional
            If True, old calendars will be overwritten on a name collision.
            If False, name collisions will raise an exception.
            Default is False.

        Raises
        ------
        CalendarNameCollision
            If a calendar is already registered with the given calendar's name.
        """
        if force:
            self.deregister_calendar(name)

        if self.has_calendar(name):
            raise CalendarNameCollision(calendar_name=name)

        self._calendars[name] = calendar

    def register_calendar_type(self, name, calendar_type, force=False):
        """
        Registers a calendar by type.

        This is useful for registering a new calendar to be lazily instantiated
        at some future point in time.

        Parameters
        ----------
        name: str
            The key with which to register this calendar.
        calendar_type: type
            The type of the calendar to register.
        force : bool, optional
            If True, old calendars will be overwritten on a name collision.
            If False, name collisions will raise an exception.
            Default is False.

        Raises
        ------
        CalendarNameCollision
            If a calendar is already registered with the given calendar's name.
        """
        if force:
            self.deregister_calendar(name)

        if self.has_calendar(name):
            raise CalendarNameCollision(calendar_name=name)

        self._calendar_factories[name] = calendar_type

    def register_calendar_alias(self, alias, real_name, force=False):
        """
        Register an alias for a calendar.

        This is useful when multiple exchanges should share a calendar, or when
        there are multiple ways to refer to the same exchange.

        After calling ``register_alias('alias', 'real_name')``, subsequent
        calls to ``get_calendar('alias')`` will return the same result as
        ``get_calendar('real_name')``.

        Parameters
        ----------
        alias : str
            The name to be used to refer to a calendar.
        real_name : str
            The canonical name of the registered calendar.
        force : bool, optional
            If True, old calendars will be overwritten on a name collision.
            If False, name collisions will raise an exception.
            Default is False.
        """
        if force:
            self.deregister_calendar(alias)

        if self.has_calendar(alias):
            raise CalendarNameCollision(calendar_name=alias)

        self._aliases[alias] = real_name

        # Ensure that the new alias doesn't create a cycle, and back it out if
        # we did.
        try:
            self.resolve_alias(alias)
        except CyclicCalendarAlias:
            del self._aliases[alias]
            raise

    def resolve_alias(self, name: str):
        """Resolve an alias to cononcial name of corresponding calendar.

        A cononical name will resolve to itself.

        Parameters
        ----------
        name :
            Alias or canoncial name corresponding to a calendar.

        Returns
        -------
        canonical_name : str
            Canonical name of calendar that would be created for `name`.

        Raises
        ------
        InvalidCalendarName
            If `name` is not an alias or canonical name of any registered
            calendar.

        See Also
        --------
        aliases_to_names : Mapping of aliases to canoncial names.
        names_to_aliases : Mapping of cononcial names to aliases.
        """
        if name not in self.get_calendar_names(include_aliases=True, sort=False):
            raise InvalidCalendarName(calendar_name=name)

        seen = []

        while name in self._aliases:
            seen.append(name)
            name = self._aliases[name]

            # This is O(N ** 2), but if there's an alias chain longer than 2,
            # something strange has happened.
            if name in seen:
                seen.append(name)
                raise CyclicCalendarAlias(cycle=" -> ".join(repr(k) for k in seen))

        return name

    def aliases_to_names(self) -> dict[str, str]:
        """Return dictionary mapping aliases to canonical names.

        Returns
        -------
        dict of {str, str}
            Dictionary mapping aliases to canoncial name of corresponding
            calendar.

        See Also
        --------
        resolve_alias : Resolve single alias to a canonical name.
        names_to_aliases : Mapping of cononcial names to aliases.
        """
        return {alias: self.resolve_alias(alias) for alias in self._aliases}

    def names_to_aliases(self) -> dict[str, list[str]]:
        """Return mapping of canonical calendar names to associated aliases.

        Returns
        -------
        dict of {str, list of str}
            Dictionary mapping canonical calendar names to any associated
            aliases.

        See Also
        --------
        aliases_to_names : Mapping of aliases to canoncial names.
        """
        names = self.get_calendar_names(include_aliases=False)
        dic = {name: [] for name in names}
        for alias, name in self.aliases_to_names().items():
            dic[name].append(alias)
        return dic

    def deregister_calendar(self, name):
        """
        If a calendar is registered with the given name, it is de-registered.

        Parameters
        ----------
        name : str
            The name of the calendar to be deregistered.
        """
        self._calendars.pop(name, None)
        self._calendar_factories.pop(name, None)
        self._aliases.pop(name, None)

    def clear_calendars(self):
        """
        Deregisters all current registered calendars
        """
        self._calendars.clear()
        self._calendar_factories.clear()
        self._aliases.clear()


# We maintain a global calendar dispatcher so that users can just do
# `register_calendar('my_calendar', calendar) and then use `get_calendar`
# without having to thread around a dispatcher.
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
