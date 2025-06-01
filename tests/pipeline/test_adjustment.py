"""Tests for zipline.lib.adjustment"""

import pytest

from zipline.lib import adjustment as adj
from zipline.utils.numpy_utils import make_datetime64ns


class TestAdjustment:
    """Tests for adjustment objects and functions."""

    @pytest.mark.parametrize(  # type: ignore
        ("name", "adj_type"),
        [
            ("add", adj.ADD),
            ("multiply", adj.MULTIPLY),
            ("overwrite", adj.OVERWRITE),
        ],
    )
    def test_make_float_adjustment(
        self, name: str, adj_type: adj.AdjustmentKind
    ) -> None:
        """Test creating float adjustments."""
        expected_types = {
            "add": adj.Float64Add,
            "multiply": adj.Float64Multiply,
            "overwrite": adj.Float64Overwrite,
        }
        result = adj.make_adjustment_from_indices(
            1,
            2,
            3,
            4,
            adjustment_kind=adj_type,
            value=0.5,
        )
        expected = expected_types[name](
            first_row=1,
            last_row=2,
            first_col=3,
            last_col=4,
            value=0.5,
        )
        assert result == expected

    def test_make_int_adjustment(self) -> None:
        """Test creating integer adjustments."""
        result = adj.make_adjustment_from_indices(
            1,
            2,
            3,
            4,
            adjustment_kind=adj.OVERWRITE,
            value=1,
        )
        expected = adj.Int64Overwrite(
            first_row=1,
            last_row=2,
            first_col=3,
            last_col=4,
            value=1,
        )
        assert result == expected

    def test_make_datetime_adjustment(self) -> None:
        """Test creating datetime adjustments."""
        overwrite_dt = make_datetime64ns(0)
        result = adj.make_adjustment_from_indices(
            1,
            2,
            3,
            4,
            adjustment_kind=adj.OVERWRITE,
            value=overwrite_dt,
        )
        expected = adj.Datetime64Overwrite(
            first_row=1,
            last_row=2,
            first_col=3,
            last_col=4,
            value=overwrite_dt,
        )
        assert result == expected

    @pytest.mark.parametrize(  # type: ignore
        "value",
        [
            "some text",
            b"some text",
            None,
        ],
    )
    def test_make_object_adjustment(self, value: int) -> None:
        """Test creating object adjustments."""
        result = adj.make_adjustment_from_indices(
            1,
            2,
            3,
            4,
            adjustment_kind=adj.OVERWRITE,
            value=value,
        )

        expected = adj.ObjectOverwrite(
            first_row=1,
            last_row=2,
            first_col=3,
            last_col=4,
            value=value,
        )
        assert result == expected

    def test_unsupported_type(self) -> None:
        """Test that unsupported types raise TypeError."""

        class SomeClass:
            pass

        expected_msg = (
            f"Don't know how to make overwrite adjustments "
            f"for values of type {SomeClass!r}."
        )
        with pytest.raises(TypeError, match=expected_msg):
            adj.make_adjustment_from_indices(
                1,
                2,
                3,
                4,
                adjustment_kind=adj.OVERWRITE,
                value=SomeClass(),
            )
