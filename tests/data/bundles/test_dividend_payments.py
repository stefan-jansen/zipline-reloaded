from io import BytesIO
from itertools import product
from zipfile import ZipFile

import numpy as np
import pandas as pd
import pytest
import responses
from parameterized import parameterized

import zipline.testing.fixtures as zf

from zipline import run_algorithm
from zipline.api import order, set_commission, set_slippage, symbol
from zipline.data.bundles import ingest, load, register, unregister
from zipline.data.bundles.csvdir import csvdir_equities
from zipline.data.bundles.quandl import format_metadata_url, quandl_bundle
from zipline.finance.commission import PerShare
from zipline.finance.slippage import FixedSlippage
from zipline.testing import patch_read_csv
from zipline.utils.calendar_utils import get_calendar


@pytest.mark.parametrize("bundle_type", ["csvdir", "quandl"])
@pytest.mark.parametrize("quantity", [1000, -1000])
def test_ingested_missing_pay_dates_settle_each_earned_dividend_once(
    tmp_path, bundle_type, quantity
):
    calendar = get_calendar("XNYS")
    sessions = calendar.sessions_in_range("2016-03-21", "2016-04-01")
    first_ex_date = pd.Timestamp("2016-03-23")
    second_ex_date = pd.Timestamp("2016-03-30")
    prices = np.where(sessions < first_ex_date, 10.0, 9.0)
    prices = np.where(sessions < second_ex_date, prices, 8.5)
    dividends = np.zeros(len(sessions))
    dividends[sessions == first_ex_date] = 1.0
    dividends[sessions == second_ex_date] = 0.5
    frame = pd.DataFrame(
        {field: prices for field in ("open", "high", "low", "close")},
        index=sessions,
    )
    frame["volume"] = 1000000
    frame["dividend"] = dividends
    frame["split"] = 1.0
    name = "cash-payment-" + bundle_type
    environ = {"ZIPLINE_ROOT": str(tmp_path / "zipline")}
    csvdir = tmp_path / "csv"
    (csvdir / "daily").mkdir(parents=True)
    frame.to_csv(csvdir / "daily" / "DIV.csv", index_label="date")

    if bundle_type == "csvdir":
        ingest_func = csvdir_equities(["daily"], str(csvdir))
    else:
        ingest_func = quandl_bundle
        environ["QUANDL_API_KEY"] = "test-placeholder"
        raw = frame.rename(columns={"dividend": "ex-dividend", "split": "split_ratio"})
        raw["ticker"] = "DIV"
        archive = BytesIO()
        with ZipFile(archive, "w") as zipped:
            zipped.writestr("prices.csv", raw.to_csv(index_label="date"))
        metadata = tmp_path / "metadata.csv"
        archive_url = "https://prices.example.invalid/archive.zip"
        pd.DataFrame({"file.link": [archive_url]}).to_csv(metadata, index=False)

    register(
        name,
        ingest_func,
        calendar_name="XNYS",
        start_session=sessions[0],
        end_session=sessions[-1],
    )
    try:
        if bundle_type == "quandl":
            with responses.RequestsMock() as transport:
                transport.add(responses.GET, archive_url, body=archive.getvalue())
                with patch_read_csv(
                    {format_metadata_url("test-placeholder"): metadata}
                ):
                    ingest(name, environ=environ, show_progress=False)
                assert len(transport.calls) == 1
        else:
            ingest(name, environ=environ, show_progress=False)

        bundle = load(name, environ=environ)
        asset = bundle.asset_finder.lookup_symbol("DIV", sessions[0])
        for ex_date, amount in [(first_ex_date, 1.0), (second_ex_date, 0.5)]:
            stored = bundle.adjustment_reader.get_dividends_with_ex_date(
                [asset], ex_date, bundle.asset_finder
            )
            assert len(stored) == 1
            assert stored[0].amount == amount
            assert pd.isnull(stored[0].pay_date)

        def initialize(context):
            context.ordered = False
            set_commission(us_equities=PerShare(cost=0, min_trade_cost=0))
            set_slippage(us_equities=FixedSlippage(0))

        def handle_data(context, data):
            if not context.ordered:
                order(symbol("DIV"), quantity)
                context.ordered = True

        # Reuse the already-ingested bundle for independent backtests.
        for _ in range(2):
            perf = run_algorithm(
                start=sessions[0],
                end=sessions[-1],
                initialize=initialize,
                handle_data=handle_data,
                capital_base=100000,
                bundle=name,
                environ=environ,
                default_extension=False,
                trading_calendar=calendar,
                benchmark_returns=pd.Series(0.0, index=sessions),
            )
            cash = perf.ending_cash.copy()
            cash.index = cash.index.normalize().tz_localize(None)
            expected = np.full(len(sessions), 100000 - quantity * 10.0)
            expected[0] = 100000
            expected[sessions >= first_ex_date] += quantity
            expected[sessions >= second_ex_date] += quantity * 0.5
            np.testing.assert_allclose(cash.to_numpy(), expected)
            np.testing.assert_allclose(perf.portfolio_value, 100000)
            fills = [txn for day in perf.transactions for txn in day]
            assert len(fills) == 1 and fills[0]["amount"] == quantity
    finally:
        unregister(name)


class TestDividendPaymentSessions(zf.WithMakeAlgo, zf.ZiplineTestCase):
    START_DATE = pd.Timestamp("2016-03-21")
    END_DATE = pd.Timestamp("2016-04-01")
    SIM_PARAMS_DATA_FREQUENCY = "daily"
    DATA_PORTAL_USE_MINUTE_DATA = False
    SIM_PARAMS_CAPITAL_BASE = 100000
    BENCHMARK_SID = None
    ASSET_FINDER_EQUITY_SIDS = (1, 2, 3, 4, 5)
    EX_DATE = pd.Timestamp("2016-03-23")
    PAY_DATES = [pd.NaT, "2016-03-25", "2016-03-26", "2016-03-24", "2016-04-04"]
    SETTLEMENT_DATES = [
        "2016-03-23",
        "2016-03-28",
        "2016-03-28",
        "2016-03-24",
        "2016-04-04",
    ]

    @classmethod
    def make_equity_daily_bar_data(cls, country_code, sids):
        frame = pd.DataFrame(
            {field: 10.0 for field in ("open", "high", "low", "close")},
            index=cls.equity_daily_bar_days,
        )
        frame["volume"] = 1000000
        return ((sid, frame) for sid in sids)

    @classmethod
    def make_dividends_data(cls):
        return pd.DataFrame(
            {
                "sid": cls.ASSET_FINDER_EQUITY_SIDS,
                "amount": 1.0,
                "ex_date": cls.EX_DATE,
                "record_date": cls.EX_DATE,
                "declared_date": cls.START_DATE,
                "pay_date": pd.to_datetime(cls.PAY_DATES),
            }
        )

    @classmethod
    def make_stock_dividends_data(cls):
        dividends = cls.make_dividends_data().drop(columns="amount")
        dividends["payment_sid"] = dividends.sid
        dividends["ratio"] = 0.1
        return dividends

    @parameterized.expand(product(range(1, 6), [100, -100]))
    def test_cash_and_stock_settle_once_on_calendar_session_without_early_credit(
        self, sid, quantity
    ):
        observed = []

        def initialize(context):
            set_commission(us_equities=PerShare(cost=0, min_trade_cost=0))
            set_slippage(us_equities=FixedSlippage(0))

        def handle_data(context, data):
            asset = self.asset_finder.retrieve_asset(sid)
            observed.append(
                (
                    context.portfolio.cash,
                    context.portfolio.positions[asset].amount,
                )
            )
            if len(observed) == 1:
                order(asset, quantity)

        self.run_algorithm(initialize=initialize, handle_data=handle_data)
        sessions = self.trading_calendar.sessions_in_range(
            self.START_DATE, self.END_DATE
        )
        assert not self.trading_calendar.is_session("2016-03-25")
        settlement = pd.Timestamp(self.SETTLEMENT_DATES[sid - 1])
        expected_cash = np.full(len(sessions), 100000 - quantity * 10.0)
        expected_quantity = np.full(len(sessions), quantity, dtype=float)
        expected_cash[0] = 100000
        expected_quantity[0] = 0
        expected_cash[sessions >= settlement] += quantity
        expected_quantity[sessions >= settlement] += quantity * 0.1
        np.testing.assert_allclose(np.asarray(observed)[:, 0], expected_cash)
        np.testing.assert_allclose(np.asarray(observed)[:, 1], expected_quantity)
