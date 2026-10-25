import pandas as pd
import pytest
from exchange_calendars import get_calendar as ec_get_calendar

from zipline.utils.calendar_utils import get_calendar


@pytest.mark.parametrize("name", ["XNYS", "NYSE", "CMES", "us_futures", "XLON"])
def test_keyword_name_matches_positional(name):
    positional = get_calendar(name)
    keyword = get_calendar(name=name)
    assert keyword.name == positional.name
    assert keyword.side == positional.side == "right"
    pd.testing.assert_index_equal(keyword.sessions, positional.sessions)


@pytest.mark.parametrize("name", ["XNYS", "NYSE", "CMES", "us_futures", "XLON"])
def test_end_is_forwarded(name):
    end = "2020-01-31"
    start = "1990-01-01" if name != "XLON" else None
    expected = ec_get_calendar(name, start=start, end=end, side="right")
    actual = get_calendar(name, end=end)
    assert actual.last_session == expected.last_session == pd.Timestamp(end)
    pd.testing.assert_index_equal(actual.sessions, expected.sessions)


@pytest.mark.parametrize("name", ["XNYS", "CMES", "XLON"])
def test_explicit_bounds_work_positionally_and_by_keyword(name):
    start, end = "2020-01-02", "2020-01-31"
    expected = ec_get_calendar(name, start=start, end=end, side="right")
    positional = get_calendar(name, start, end)
    keyword = get_calendar(name=name, start=start, end=end)
    pd.testing.assert_index_equal(positional.sessions, expected.sessions)
    pd.testing.assert_index_equal(keyword.sessions, expected.sessions)


def test_explicit_start_before_1990_is_honoured():
    start, end = "1985-01-02", "1985-01-31"
    expected = ec_get_calendar("XNYS", start=start, end=end, side="right")
    positional = get_calendar("XNYS", start, end)
    keyword = get_calendar("XNYS", start=start, end=end)
    assert positional.first_session == pd.Timestamp(start)
    pd.testing.assert_index_equal(positional.sessions, expected.sessions)
    pd.testing.assert_index_equal(keyword.sessions, expected.sessions)


@pytest.mark.parametrize("name", ["XNYS", "NYSE", "CMES", "us_futures"])
def test_legacy_defaults_stay_unchanged(name):
    expected = ec_get_calendar(name, start="1990-01-01", side="right")
    actual = get_calendar(name)
    assert actual.side == "right"
    pd.testing.assert_index_equal(actual.sessions, expected.sessions)


def test_side_right_is_accepted():
    assert get_calendar("XNYS", side="right").side == "right"


@pytest.mark.parametrize("side", ["left", "both", "neither"])
def test_conflicting_side_is_rejected(side):
    with pytest.raises(TypeError, match="right-sided"):
        get_calendar("XNYS", side=side)


@pytest.mark.parametrize(
    "args, kwargs",
    [
        ((), {}),
        (("XNYS",), {"name": "XNYS"}),
        (("XNYS",), {"typo": True}),
    ],
)
def test_signature_rejects_invalid_arguments(args, kwargs):
    with pytest.raises(TypeError):
        get_calendar(*args, **kwargs)
