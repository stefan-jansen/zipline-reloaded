from itertools import product

import numpy as np
import pandas as pd
import pytest
from parameterized import parameterized

import zipline.api as api
import zipline.testing.fixtures as zf
from zipline.data.bar_reader import NoDataOnDate
from zipline.data.data_portal import DataPortal
from zipline.data.session_bars import SessionBarReader
from zipline.errors import BadOrderParameters
from zipline.finance.commission import PerTrade
from zipline.finance.slippage import FixedSlippage


class FloatSessionReader(SessionBarReader):
    """DataFrame feed retaining signed prices through the session-reader API."""

    def __init__(self, calendar, frames):
        self._calendar = calendar
        self.frames = frames
        self._sessions = next(iter(frames.values())).index

    trading_calendar = property(lambda self: self._calendar)
    sessions = property(lambda self: self._sessions)
    first_trading_day = property(lambda self: self.sessions[0])
    last_available_dt = property(lambda self: self.sessions[-1])

    def get_value(self, sid, dt, field):
        try:
            return self.frames[int(sid)].loc[dt, field]
        except KeyError as exc:
            raise NoDataOnDate(dt) from exc

    def get_last_traded_dt(self, asset, dt):
        frame = self.frames[int(asset)].loc[:dt]
        return frame.loc[frame.volume > 0, "close"].last_valid_index()

    def load_raw_arrays(self, columns, start_date, end_date, assets):
        return [
            np.column_stack(
                [
                    self.frames[int(sid)].loc[start_date:end_date, field].to_numpy()
                    for sid in assets
                ]
            )
            for field in columns
        ]


class TestValueOrderPrices(zf.WithMakeAlgo, zf.ZiplineTestCase):
    START_DATE = pd.Timestamp("2016-01-06")
    END_DATE = pd.Timestamp("2016-01-08")
    SIM_PARAMS_DATA_FREQUENCY = "daily"
    SIM_PARAMS_CAPITAL_BASE = 100000
    DATA_PORTAL_USE_MINUTE_DATA = False
    BENCHMARK_SID = None
    ASSET_FINDER_EQUITY_SIDS = (2,)

    @classmethod
    def make_futures_info(cls):
        return pd.DataFrame.from_dict(
            {
                1: {
                    "symbol": "CLG16",
                    "root_symbol": "CL",
                    "start_date": cls.START_DATE,
                    "end_date": cls.END_DATE,
                    "notice_date": pd.Timestamp("2016-01-20"),
                    "expiration_date": pd.Timestamp("2016-02-19"),
                    "auto_close_date": pd.Timestamp("2016-01-18"),
                    "exchange": "TEST",
                    "multiplier": 1000,
                },
            },
            orient="index",
        )

    def portal_for_prices(self, prices):
        sessions = self.trading_calendar.sessions_in_range(
            self.START_DATE, self.END_DATE
        )
        frame = pd.DataFrame(
            {field: prices for field in ("open", "high", "low", "close")},
            index=sessions,
        )
        frame["volume"] = 1000
        reader = FloatSessionReader(self.trading_calendar, {1: frame, 2: frame})
        return DataPortal(
            self.asset_finder,
            self.trading_calendar,
            first_trading_day=sessions[0],
            last_available_session=sessions[-1],
            equity_daily_reader=reader,
            future_daily_reader=reader,
        )

    @parameterized.expand(
        product(
            [
                "order_value",
                "order_percent",
                "order_target_value",
                "order_target_percent",
            ],
            [0.0, -37.63],
            [1, 2],
            [1, -1],
        )
    )
    def test_nonpositive_price_cannot_silently_drop_or_reverse_value_orders(
        self,
        method,
        price,
        sid,
        direction,
    ):
        calls = []

        def handle_data(context, data):
            asset = api.sid(sid)
            assert data.current(asset, "price") == price
            value = direction * (0.5 if "percent" in method else 50000)
            with pytest.raises(BadOrderParameters, match="strictly positive price"):
                getattr(api, method)(asset, value)
            assert api.get_open_orders(asset) == []
            calls.append(api.get_datetime())

        self.run_algorithm(
            handle_data=handle_data, data_portal=self.portal_for_prices([price] * 3)
        )
        assert len(calls) == 3

    @parameterized.expand(
        product(
            [
                "order_value",
                "order_percent",
                "order_target_value",
                "order_target_percent",
            ],
            [1, 2],
            [1, -1],
        )
    )
    def test_positive_price_preserves_direction_and_futures_multiplier(
        self, method, sid, direction
    ):
        amounts = []

        def handle_data(context, data):
            if amounts:
                return
            asset = api.sid(sid)
            value = direction * (0.5 if "percent" in method else 50000)
            order_id = getattr(api, method)(asset, value)
            amounts.append(api.get_order(order_id).amount)

        self.run_algorithm(
            handle_data=handle_data, data_portal=self.portal_for_prices([18.27] * 3)
        )
        assert amounts == [direction * (2 if sid == 1 else 2736)]

    @parameterized.expand(product(["order", "order_target"], [1, -1]))
    def test_explicit_contract_orders_fill_at_negative_prices_and_mark_to_market(
        self, method, direction
    ):
        ordered = []

        def initialize(context):
            api.set_commission(us_futures=PerTrade(0))
            api.set_slippage(us_futures=FixedSlippage(0))

        def handle_data(context, data):
            if not ordered:
                ordered.append(getattr(api, method)(api.sid(1), direction * 2))

        results = self.run_algorithm(
            initialize=initialize,
            handle_data=handle_data,
            data_portal=self.portal_for_prices([-37.63, -37.63, -36.63]),
        )
        transactions = [txn for day in results.transactions for txn in day]
        assert len(transactions) == 1
        assert transactions[0]["amount"] == direction * 2
        assert transactions[0]["price"] == -37.63
        np.testing.assert_allclose(
            results.iloc[-1].portfolio_value, 100000 + direction * 2000
        )

    @parameterized.expand(
        product(["order_target_value", "order_target_percent"], [0.0, -37.63])
    )
    def test_invalid_value_target_does_not_liquidate_existing_contracts(
        self, method, price
    ):
        calls = []

        def initialize(context):
            api.set_commission(us_futures=PerTrade(0))
            api.set_slippage(us_futures=FixedSlippage(0))

        def handle_data(context, data):
            asset = api.sid(1)
            if not calls:
                api.order(asset, 2)
            else:
                assert context.portfolio.positions[asset].amount == 2
                with pytest.raises(BadOrderParameters, match="strictly positive price"):
                    getattr(api, method)(asset, 0)
                assert api.get_open_orders(asset) == []
            calls.append(api.get_datetime())

        results = self.run_algorithm(
            initialize=initialize,
            handle_data=handle_data,
            data_portal=self.portal_for_prices([18.27, price, price]),
        )
        assert len(calls) == 3
        transactions = [txn for day in results.transactions for txn in day]
        assert [txn["amount"] for txn in transactions] == [2]
        assert results.iloc[-1].positions[0]["amount"] == 2

    @parameterized.expand([0.0, -37.63])
    def test_explicit_zero_contract_target_can_liquidate_at_nonpositive_price(
        self, price
    ):
        calls = []

        def initialize(context):
            api.set_commission(us_futures=PerTrade(0))
            api.set_slippage(us_futures=FixedSlippage(0))

        def handle_data(context, data):
            asset = api.sid(1)
            if not calls:
                api.order(asset, 2)
            elif len(calls) == 1:
                assert context.portfolio.positions[asset].amount == 2
                api.order_target(asset, 0)
            else:
                assert asset not in context.portfolio.positions
            calls.append(api.get_datetime())

        results = self.run_algorithm(
            initialize=initialize,
            handle_data=handle_data,
            data_portal=self.portal_for_prices([18.27, price, price]),
        )
        transactions = [txn for day in results.transactions for txn in day]
        assert [txn["amount"] for txn in transactions] == [2, -2]
        assert all(txn["price"] == price for txn in transactions)
        assert results.iloc[-1].positions == []
