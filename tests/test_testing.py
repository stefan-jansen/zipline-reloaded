"""
Tests for our testing utilities.
"""

from unittest import TestCase

import pytest

from numpy import array, empty

from zipline._protocol import BarData
from zipline.finance.asset_restrictions import NoRestrictions
from zipline.finance.order import Order

from zipline.testing import (
    check_arrays,
    make_alternating_boolean_array,
    make_cascading_boolean_array,
    parameter_space,
)
from zipline.testing.fixtures import (  # Assuming this is where ZiplineTestCase and others are
    WithConstantEquityMinuteBarData,
    WithDataPortal,
    ZiplineTestCase,  # Add back ZiplineTestCase import
)
from zipline.testing.slippage import TestingSlippage
from zipline.testing.predicates import wildcard, instance_of
from zipline.utils.numpy_utils import bool_dtype

pytestmark = pytest.mark.xdist_group(name="module_group_test_testing")


class TestParameterSpace:
    @pytest.mark.parametrize("fail_fast", [False, True])
    def test_xy(self, fail_fast):
        invocations = []

        @parameter_space(__fail_fast=fail_fast, x=[1, 2], y=[3, 4])
        def record(self, x, y):
            invocations.append((x, y))

        record(TestCase())
        assert invocations == [(1, 3), (1, 4), (2, 3), (2, 4)]

    @pytest.mark.parametrize("fail_fast", [False, True])
    def test_yx(self, fail_fast):
        invocations = []

        @parameter_space(__fail_fast=fail_fast, x=[1, 2], y=[3, 4])
        def record(self, y, x):
            invocations.append((x, y))

        record(TestCase())
        assert invocations == [(1, 3), (2, 3), (1, 4), (2, 4)]

    @pytest.mark.parametrize("fail_fast", [False, True])
    def test_nothing(self, fail_fast):
        invocations = []

        @parameter_space(__fail_fast=fail_fast)
        def record(self):
            invocations.append("called")

        record(TestCase())
        assert invocations == ["called"]


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
