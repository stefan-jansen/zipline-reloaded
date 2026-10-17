import pandas as pd
import sqlalchemy as sa

from zipline.assets import AssetDBWriter, AssetFinder


def test_write_direct_can_roundtrip_futures(tmp_path):
    engine = sa.create_engine("sqlite:///" + str(tmp_path / "assets.sqlite"))
    AssetDBWriter(engine).write_direct(
        futures=pd.DataFrame(
            {
                "symbol": ["ESH20"],
                "root_symbol": ["ES"],
                "exchange": ["CME"],
                "notice_date": [pd.Timestamp("2020-03-01").value],
                "auto_close_date": [pd.Timestamp("2020-02-28").value],
                "expiration_date": [pd.Timestamp("2020-03-15").value],
            },
            index=[1],
        ),
        exchanges=pd.DataFrame({"exchange": ["CME"], "country_code": ["US"]}),
    )
    finder = AssetFinder(engine)
    try:
        assert finder.retrieve_asset(1).symbol == "ESH20"
    finally:
        finder.close()
        engine.dispose()
