import numpy as np
import pandas as pd
import sqlalchemy as sa
from zipline.assets import AssetDBWriter, AssetFinder
from zipline.assets.synthetic import make_simple_equity_info
from zipline.pipeline import Pipeline, SimplePipelineEngine
from zipline.pipeline.data import USEquityPricing
from zipline.pipeline.domain import US_EQUITIES
from zipline.pipeline.loaders.frame import DataFrameLoader
from zipline.pipeline.term import AssetExists


def test_shared_pipeline_terms_produce_expected_output(tmp_path):
    db = sa.create_engine("sqlite:///" + str(tmp_path / "assets.sqlite"))
    start, end = pd.Timestamp("2020-01-02"), pd.Timestamp("2020-02-03")
    AssetDBWriter(db).write(
        equities=make_simple_equity_info([1, 2], start, end),
        exchanges=pd.DataFrame({"exchange": ["TEST"], "country_code": ["US"]}),
    )
    finder = AssetFinder(db)
    try:
        dates = US_EQUITIES.calendar.sessions_in_range(start, end)
        frame = pd.DataFrame(
            np.tile([1.0, 2.0], (len(dates), 1)), index=dates, columns=[1, 2]
        )
        loader = DataFrameLoader(USEquityPricing.close, frame)
        engine = SimplePipelineEngine(lambda column: loader, finder)
        out = USEquityPricing.close.latest
        for _ in range(8):
            out = (out > 1.5).if_else(out, out / 2)
        result = engine.run_pipeline(Pipeline({"out": out}), dates[1], dates[-1])
        np.testing.assert_allclose(
            result["out"].values.reshape(-1, 2),
            np.tile([1 / 256, 2], (len(dates) - 1, 1)),
        )
    finally:
        finder.close()
        db.dispose()


def test_execution_plan_can_increase_requested_history():
    dates = US_EQUITIES.calendar.sessions_in_range("2020-01-02", "2020-02-03")
    term = USEquityPricing.close.latest
    plan = Pipeline({"close": term}).to_execution_plan(
        US_EQUITIES, AssetExists(), dates[10], dates[-1]
    )
    plan.set_extra_rows(term, dates, dates[10], dates[-1], min_extra_rows=3)
    assert plan.extra_rows[term] >= 3


def test_mutated_factor_cycle_is_rejected_during_planning():
    import pytest
    from zipline.pipeline.factors import CustomFactor
    from zipline.pipeline.graph import CyclicDependency, TermGraph

    class RecursiveFactor(CustomFactor):
        inputs = ()
        window_length = 1

        def compute(self, today, assets, out):
            out[:] = 1

    factor = RecursiveFactor()
    factor.inputs = (factor,)
    with pytest.raises(CyclicDependency):
        TermGraph({"recursive": factor})
