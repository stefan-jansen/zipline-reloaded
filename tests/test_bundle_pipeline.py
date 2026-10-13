import pandas as pd
import pytest

from zipline import run_algorithm
from zipline.api import attach_pipeline, pipeline_output
from zipline.assets.synthetic import make_simple_equity_info
from zipline.data import bundles
from zipline.pipeline import Pipeline
from zipline.pipeline.data import Column, DataSet, EquityPricing
from zipline.pipeline.domain import EquityCalendarDomain, US_EQUITIES
from zipline.pipeline.loaders.frame import DataFrameLoader
from zipline.utils.calendar_utils import get_calendar


class CustomData(DataSet):
    value = Column(float)
    domain = US_EQUITIES


@pytest.fixture
def run_pricing_bundle(tmp_path):
    name = "pricing-domain-regression"
    start, end = pd.Timestamp("2014-01-06"), pd.Timestamp("2014-01-10")
    country = "US"

    def ingest(
        environ,
        assets,
        minute,
        daily,
        adjustments,
        calendar,
        start_session,
        end_session,
        cache,
        show_progress,
        output_dir,
    ):
        assets.write(
            equities=make_simple_equity_info([1], start, end),
            exchanges=pd.DataFrame({"exchange": ["TEST"], "country_code": [country]}),
        )
        prices = pd.DataFrame(
            {field: 10.0 for field in ["open", "high", "low", "close"]},
            index=calendar.sessions_in_range(start, end),
        )
        prices["volume"] = 1000
        daily.write([(1, prices)])
        adjustments.write()

    bundles.register(name, ingest, start_session=start, end_session=end)

    def run(pipeline, country_code="US", **kwargs):
        nonlocal country
        country = country_code
        environ = {"ZIPLINE_ROOT": str(tmp_path)}
        bundles.ingest(name, environ=environ)
        values = []

        def initialize(context):
            attach_pipeline(pipeline, "prices")

        def before(context, data):
            values.extend(pipeline_output("prices").iloc[:, 0].tolist())

        run_algorithm(
            start=start + pd.Timedelta(days=1),
            end=end,
            initialize=initialize,
            before_trading_start=before,
            capital_base=10000,
            bundle=name,
            trading_calendar=get_calendar("XNYS"),
            environ=environ,
            default_extension=False,
            benchmark_returns=pd.Series(0.0, index=pd.date_range(start, end, freq="B")),
            **kwargs,
        )
        return values

    yield run
    bundles.unregister(name)


@pytest.mark.parametrize("country", ["US", "JP"])
def test_bundle_pricing_loads_for_its_asset_country(run_pricing_bundle, country):
    pipeline = Pipeline(
        {"close": EquityPricing.close.latest},
        domain=EquityCalendarDomain(country, "XNYS"),
    )
    assert run_pricing_bundle(pipeline, country) == [10.0] * 4


@pytest.mark.parametrize("loaders", [None, {}])
def test_missing_custom_loader_reports_column(run_pricing_bundle, loaders):
    with pytest.raises(ValueError, match="No PipelineLoader registered"):
        run_pricing_bundle(
            Pipeline({"value": CustomData.value.latest}), custom_loader=loaders
        )


def test_registered_custom_loader_still_supplies_values(run_pricing_bundle):
    values = pd.DataFrame(
        42.0, index=pd.date_range("2014-01-06", "2014-01-10", freq="B"), columns=[1]
    )
    loader = DataFrameLoader(CustomData.value, values)
    assert (
        run_pricing_bundle(
            Pipeline({"value": CustomData.value.latest}),
            custom_loader={CustomData.value: loader},
        )
        == [42.0] * 4
    )
