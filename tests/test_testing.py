"""
Tests for our testing utilities.
"""

from itertools import product
import pytest  # Add pytest back
import os

# import logging # No longer needed if logger is removed
# import sys # No longer used

from numpy import array, empty

from zipline._protocol import BarData
from zipline.finance.asset_restrictions import NoRestrictions
from zipline.finance.order import Order

from zipline.testing import (
    check_arrays,
    make_alternating_boolean_array,
    make_cascading_boolean_array,
    # parameter_space, # This was commented out, so it's unused
)
from zipline.testing.fixtures import (  # Assuming this is where ZiplineTestCase and others are
    WithConstantEquityMinuteBarData,
    WithDataPortal,
    ZiplineTestCase,  # Add back ZiplineTestCase import
)
from zipline.testing.slippage import TestingSlippage
from zipline.testing.predicates import wildcard, instance_of
from zipline.utils.numpy_utils import bool_dtype

ON_GHA = os.getenv("GITHUB_ACTIONS") == "true"

# Group all tests in this module to run on the same worker
pytestmark = pytest.mark.xdist_group(name="module_group_test_testing")

# Configure a logger for this module
# logger = logging.getLogger(__name__) # Removed as it's no longer used


@pytest.fixture(scope="class")
def invocations_state(request):
    request.cls.xy_invocations = []
    request.cls.yx_invocations = []
    yield

    actual_xy_invocations = sorted(request.cls.xy_invocations)
    actual_yx_invocations = sorted(request.cls.yx_invocations)

    expected_xy = sorted(
        list(product(request.cls.x_args_vals, request.cls.y_args_vals))
    )
    expected_yx = sorted(
        list(product(request.cls.y_args_vals, request.cls.x_args_vals))
    )

    worker = os.environ.get("PYTEST_XDIST_WORKER", "main")

    assert (
        actual_xy_invocations == expected_xy
    ), f"[{worker}] XY invocations do not match. Expected: {expected_xy}, Got: {actual_xy_invocations}"
    assert (
        actual_yx_invocations == expected_yx
    ), f"[{worker}] YX invocations do not match. Expected: {expected_yx}, Got: {actual_yx_invocations}"


@pytest.mark.usefixtures("invocations_state")
@pytest.mark.xfail(
    ON_GHA,
    reason="Unresolved issues on GHA",
)
class TestParameterSpace:
    """Test class for parametrized tests using a shared state via fixture."""

    x_args_vals = [1, 2]
    y_args_vals = [3, 4]

    @pytest.mark.parametrize("x", x_args_vals)
    @pytest.mark.parametrize("y", y_args_vals)
    def test_xy(self, x, y):
        """Test xy parameter combinations."""
        self.__class__.xy_invocations.append((x, y))

    @pytest.mark.parametrize("y", y_args_vals)
    @pytest.mark.parametrize("x", x_args_vals)
    def test_yx(self, y, x):
        """Test yx parameter combinations."""
        self.__class__.yx_invocations.append((y, x))

    @pytest.mark.xfail(
        ON_GHA,
        reason="Unresolved issues on GHA",
    )
    def test_nothing(self):
        """A simple test that does nothing but ensures fixture setup/teardown works."""
        pass


class TestMakeBooleanArray:
    def test_make_alternating_boolean_array(self):
        check_arrays(
            make_alternating_boolean_array((3, 3)),
            array([[True, False, True], [False, True, False], [True, False, True]]),
        )
        check_arrays(
            make_alternating_boolean_array((3, 3), first_value=False),
            array([[False, True, False], [True, False, True], [False, True, False]]),
        )
        check_arrays(
            make_alternating_boolean_array((1, 3)),
            array([[True, False, True]]),
        )
        check_arrays(
            make_alternating_boolean_array((3, 1)),
            array([[True], [False], [True]]),
        )
        check_arrays(
            make_alternating_boolean_array((3, 0)),
            empty((3, 0), dtype=bool_dtype),
        )

    def test_make_cascading_boolean_array(self):
        check_arrays(
            make_cascading_boolean_array((3, 3)),
            array([[True, True, False], [True, False, False], [False, False, False]]),
        )
        check_arrays(
            make_cascading_boolean_array((3, 3), first_value=False),
            array([[False, False, True], [False, True, True], [True, True, True]]),
        )
        check_arrays(
            make_cascading_boolean_array((1, 3)),
            array([[True, True, False]]),
        )
        check_arrays(
            make_cascading_boolean_array((3, 1)),
            array([[False], [False], [False]]),
        )
        check_arrays(
            make_cascading_boolean_array((3, 0)),
            empty((3, 0), dtype=bool_dtype),
        )


class TestTestingSlippage(
    WithConstantEquityMinuteBarData,
    WithDataPortal,
    ZiplineTestCase,  # Add ZiplineTestCase back as a base class
):
    ASSET_FINDER_EQUITY_SYMBOLS = ("A",)
    ASSET_FINDER_EQUITY_SIDS = (1,)

    @classmethod
    def init_class_fixtures(cls):
        super(TestTestingSlippage, cls).init_class_fixtures()
        cls.asset = cls.asset_finder.retrieve_asset(1)
        cls.minute = cls.trading_calendar.session_first_minute(cls.START_DATE)

    def init_instance_fixtures(self):
        super(TestTestingSlippage, self).init_instance_fixtures()
        self.bar_data = BarData(
            self.data_portal,
            lambda: self.minute,
            "minute",
            self.trading_calendar,
            NoRestrictions(),
        )

    def make_order(self, amount):
        return Order(
            self.minute,
            self.asset,
            amount,
        )

    def test_constant_filled_per_tick(self):
        filled_per_tick = 1
        model = TestingSlippage(filled_per_tick)
        order = self.make_order(100)

        price, volume = model.process_order(self.bar_data, order)

        assert price == self.EQUITY_MINUTE_CONSTANT_CLOSE
        assert volume == filled_per_tick

    def test_fill_all(self):
        filled_per_tick = TestingSlippage.ALL
        order_amount = 100

        model = TestingSlippage(filled_per_tick)
        order = self.make_order(order_amount)

        price, volume = model.process_order(self.bar_data, order)

        assert price == self.EQUITY_MINUTE_CONSTANT_CLOSE
        assert volume == order_amount


class TestPredicates:
    def test_wildcard(self):
        for obj in 1, object(), "foo", {}:
            assert obj == wildcard
            assert [obj] == [wildcard]
            assert {"foo": wildcard} == {"foo": wildcard}

    def test_instance_of(self):
        assert 1 == instance_of(int)
        assert 1 != instance_of(str)
        assert 1 == instance_of((str, int))
        assert "foo" == instance_of((str, int))

    def test_instance_of_exact(self):
        class Foo:
            pass

        class Bar(Foo):
            pass

        assert Bar() == instance_of(Foo)
        assert Bar() != instance_of(Foo, exact=True)
