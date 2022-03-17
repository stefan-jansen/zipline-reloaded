from __future__ import annotations
from abc import abstractproperty

import numpy as np
import pandas as pd
from pytz import UTC

from .exchange_calendar import ExchangeCalendar


class PrecomputedExchangeCalendar(ExchangeCalendar):
    """
    Used to model an exchange calendar whose holidays inlcude holidays that
    are precomputed and hardcoded.
    """

    @abstractproperty
    def precomputed_holidays(self) -> pd.DatetimeIndex | list[pd.Timestamp]:
        raise NotImplementedError()

    @property
    def adhoc_holidays(self) -> pd.DatetimeIndex | list[pd.Timestamp]:
        return self.precomputed_holidays

    @property
    def _earliest_precomputed_year(self) -> int:
        return np.min(self.precomputed_holidays).year

    @property
    def _latest_precomputed_year(self) -> int:
        return np.max(self.precomputed_holidays).year

    @property
    def bound_start(self) -> pd.Timestamp:
        return pd.Timestamp(f"{self._earliest_precomputed_year}-01-01", tz=UTC)

    @property
    def bound_end(self) -> pd.Timestamp:
        return pd.Timestamp(f"{self._latest_precomputed_year}-12-31", tz=UTC)

    def _bound_start_error_msg(self, start: pd.Timestamp) -> str:
        return (
            f"The {self.name} holidays are only recorded back to the year"
            f" {self._earliest_precomputed_year}, cannot instantiate the"
            f" {self.name} calendar from {start}."
        )

    def _bound_end_error_msg(self, end: pd.Timestamp) -> str:
        return (
            f"The {self.name} holidays are only recorded to the year"
            f" {self._latest_precomputed_year}, cannot instantiate the"
            f" {self.name} calendar through to {end}."
        )
