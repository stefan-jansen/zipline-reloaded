import pandas as pd
import sqlalchemy as sa
import pytest

from zipline.assets import AssetDBWriter, AssetFinder
from zipline.assets.synthetic import make_simple_equity_info
from zipline.errors import SameSymbolUsedAcrossCountries


def test_ambiguous_symbol_reports_each_country(tmp_path):
    engine = sa.create_engine("sqlite:///" + str(tmp_path / "assets.sqlite"))
    eq = make_simple_equity_info(
        [1, 2],
        pd.Timestamp("2014-01-01"),
        pd.Timestamp("2014-12-31"),
        symbols=["A", "A"],
    )
    eq["exchange"] = ["NYSE", "TSE"]
    AssetDBWriter(engine).write(
        equities=eq,
        exchanges=pd.DataFrame(
            {"exchange": ["NYSE", "TSE"], "country_code": ["US", "JP"]}
        ),
    )
    finder = AssetFinder(engine)
    try:
        with pytest.raises(SameSymbolUsedAcrossCountries) as error:
            finder.lookup_symbol("A", None)
        assert "US" in str(error.value)
        assert "JP" in str(error.value)
    finally:
        finder.close()
        engine.dispose()
