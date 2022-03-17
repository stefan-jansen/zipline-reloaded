#
# Copyright 2018 Quantopian, Inc.
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

from .calendar_utils import (
    clear_calendars,
    deregister_calendar,
    get_calendar,
    get_calendar_names,
    register_calendar,
    register_calendar_alias,
    register_calendar_type,
    resolve_alias,
    names_to_aliases,
    aliases_to_names,
)
from .exchange_calendar import ExchangeCalendar

__all__ = [
    "clear_calendars",
    "deregister_calendar",
    "get_calendar",
    "get_calendar_names",
    "register_calendar",
    "register_calendar_alias",
    "register_calendar_type",
    "resolve_alias",
    "names_to_aliases",
    "aliases_to_names",
    "ExchangeCalendar",
]

from ._version import get_versions

__version__ = get_versions()["version"]
del get_versions
