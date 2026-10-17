import pytest
import numpy as np
import pandas as pd
from os.path import (
    dirname,
    join,
    realpath,
)

from zipline.utils.calendar_utils import get_calendar

from zipline.data.bundles import ingest, load, bundles
from zipline.utils.functional import apply
from zipline.testing.github_actions import skip_on

TEST_RESOURCE_PATH = join(
    dirname(dirname(dirname(realpath(__file__)))),
    "resources",  # zipline_repo/tests
)


class TestCSVDIRBundle:
    symbols = "AAPL", "IBM", "KO", "MSFT"
    asset_start = pd.Timestamp("2012-01-03")
    asset_end = pd.Timestamp("2014-12-31")
    bundle = bundles["csvdir"]
    calendar = get_calendar(bundle.calendar_name)
    start_date = calendar.first_session
    end_date = calendar.last_session
    api_key = "ayylmao"
    columns = "open", "high", "low", "close", "volume"

    def _expected_data(self, asset_finder):
        sids = {
            symbol: asset_finder.lookup_symbol(
                symbol,
                self.asset_start,
            ).sid
            for symbol in self.symbols
        }

        def per_symbol(symbol):
            df = pd.read_csv(
                join(
                    TEST_RESOURCE_PATH,
                    "csvdir_samples",
                    "csvdir",
                    "daily",
                    symbol + ".csv.gz",
                ),
                parse_dates=["date"],
                index_col="date",
                usecols=[
                    "open",
                    "high",
                    "low",
                    "close",
                    "volume",
                    "date",
                    "dividend",
                    "split",
                ],
                na_values=["NA"],
            )
            df["sid"] = sids[symbol]
            return df

        all_ = (
            pd.concat(map(per_symbol, self.symbols))
            .set_index("sid", append=True)
            .unstack()
        )

        # fancy list comprehension with statements
        @list
        @apply
        def pricing():
            for column in self.columns:
                vs = all_[column].values
                if column == "volume":
                    vs = np.nan_to_num(vs)
                yield vs

        adjustments = [
            [
                5572,
                5576,
                5595,
                5634,
                5639,
                5659,
                5698,
                5699,
                5701,
                5702,
                5722,
                5760,
                5764,
                5774,
                5821,
                5822,
                5829,
                5845,
                5884,
                5885,
                5888,
                5908,
                5947,
                5948,
                5951,
                5972,
                6011,
                6020,
                6026,
                6073,
                6080,
                6096,
                6135,
                6136,
                6139,
                6157,
                6160,
                6198,
                6199,
                6207,
                6223,
                6263,
                6271,
                6277,
            ],
            [
                5572,
                5576,
                5595,
                5634,
                5639,
                5659,
                5698,
                5699,
                5701,
                5702,
                5722,
                5760,
                5764,
                5774,
                5821,
                5822,
                5829,
                5845,
                5884,
                5885,
                5888,
                5908,
                5947,
                5948,
                5951,
                5972,
                6011,
                6020,
                6026,
                6073,
                6080,
                6096,
                6135,
                6136,
                6139,
                6157,
                6160,
                6198,
                6199,
                6207,
                6223,
                6263,
                6271,
                6277,
            ],
            [
                5572,
                5576,
                5595,
                5634,
                5639,
                5659,
                5698,
                5699,
                5701,
                5702,
                5722,
                5760,
                5764,
                5774,
                5821,
                5822,
                5829,
                5845,
                5884,
                5885,
                5888,
                5908,
                5947,
                5948,
                5951,
                5972,
                6011,
                6020,
                6026,
                6073,
                6080,
                6096,
                6135,
                6136,
                6139,
                6157,
                6160,
                6198,
                6199,
                6207,
                6223,
                6263,
                6271,
                6277,
            ],
            [
                5572,
                5576,
                5595,
                5634,
                5639,
                5659,
                5698,
                5699,
                5701,
                5702,
                5722,
                5760,
                5764,
                5774,
                5821,
                5822,
                5829,
                5845,
                5884,
                5885,
                5888,
                5908,
                5947,
                5948,
                5951,
                5972,
                6011,
                6020,
                6026,
                6073,
                6080,
                6096,
                6135,
                6136,
                6139,
                6157,
                6160,
                6198,
                6199,
                6207,
                6223,
                6263,
                6271,
                6277,
            ],
            [5701, 6157],
        ]

        return pricing, adjustments

    @skip_on(PermissionError)
    def test_bundle(self):
        environ = {
            "CSVDIR": join(
                TEST_RESOURCE_PATH,
                "csvdir_samples",
                "csvdir",
            ),
        }

        ingest("csvdir", environ=environ)
        bundle = load("csvdir", environ=environ)
        sids = 0, 1, 2, 3
        assert set(bundle.asset_finder.sids) == set(sids)

        for equity in bundle.asset_finder.retrieve_all(sids):
            assert equity.start_date == self.asset_start, equity
            assert equity.end_date == self.asset_end, equity

        sessions = self.calendar.sessions
        actual = bundle.equity_daily_bar_reader.load_raw_arrays(
            self.columns,
            sessions[sessions.get_indexer([self.asset_start], "bfill")[0]],
            sessions[sessions.get_indexer([self.asset_end], "ffill")[0]],
            sids,
        )

        expected_pricing, expected_adjustments = self._expected_data(
            bundle.asset_finder,
        )
        np.testing.assert_array_almost_equal(actual, expected_pricing, decimal=2)

        adjs_for_cols = bundle.adjustment_reader.load_pricing_adjustments(
            self.columns,
            sessions,
            pd.Index(sids),
        )
        assert [sorted(adj.keys()) for adj in adjs_for_cols] == expected_adjustments


@pytest.mark.parametrize(
    "symbols, n_events",
    [
        # Columns present everywhere but no split or dividend events at all. This is the
        # case where the empty per-symbol frames used to turn the result into object dtype.
        (("AAA",), 0),
        (("AAA", "BBB"), 1),
        (("BBB", "AAA"), 1),
    ],
)
def test_pricing_iter_keeps_dtypes_when_a_file_has_no_splits_or_dividends(
    tmp_path, symbols, n_events
):
    # AAA has split and dividend columns but no events, BBB has one of each.
    from zipline.data.bundles.csvdir import _empty_divs_splits, _pricing_iter

    header = "date,open,high,low,close,volume,dividend,split\n"
    (tmp_path / "AAA.csv").write_text(
        header + "2020-01-02,1,1,1,1,100,0.0,1.0\n2020-01-03,1,1,1,1,100,0.0,1.0\n"
    )
    (tmp_path / "BBB.csv").write_text(
        header + "2020-01-02,1,1,1,1,100,0.0,1.0\n2020-01-03,1,1,1,1,100,0.5,2.0\n"
    )
    metadata = pd.DataFrame(
        np.empty(
            len(symbols),
            dtype=[
                ("start_date", "datetime64[ns]"),
                ("end_date", "datetime64[ns]"),
                ("auto_close_date", "datetime64[ns]"),
                ("symbol", "object"),
            ],
        )
    )
    divs_splits = _empty_divs_splits()

    list(_pricing_iter(str(tmp_path), list(symbols), metadata, divs_splits, False))

    splits, divs = divs_splits["splits"], divs_splits["divs"]
    assert splits["effective_date"].dtype == "datetime64[ns]"
    assert splits["ratio"].dtype == "float64"
    for column in ("ex_date", "record_date", "declared_date", "pay_date"):
        assert divs[column].dtype == "datetime64[ns]"
    assert divs["amount"].dtype == "float64"
    assert len(splits) == n_events
    assert len(divs) == n_events
