"""Tests for the zipline.pipeline.data.DataSet and related functionality.
"""
from textwrap import dedent

from zipline.pipeline.data.dataset import Column, DataSet
from zipline.testing import chrange, ZiplineTestCase
import pytest
import re
from contextlib import ExitStack


class SomeDataSet(DataSet):
    a = Column(dtype=float)
    b = Column(dtype=object)
    c = Column(dtype=int, missing_value=-1)

    exists_but_not_a_column = "foo"


# A DataSet with lots of columns.
class LargeDataSet(DataSet):
    locals().update({name: Column(dtype=float) for name in chrange("a", "z")})


class GetColumnTestCase(ZiplineTestCase):
    def test_get_column_success(self):
        a = SomeDataSet.a
        b = SomeDataSet.b
        c = SomeDataSet.c

        # Run multiple times to validate caching of descriptor return values.
        for _ in range(3):
            assert SomeDataSet.get_column("a") is a
            assert SomeDataSet.get_column("b") is b
            assert SomeDataSet.get_column("c") is c

    def test_get_column_failure(self):
        expected = dedent(
            """\
            SomeDataSet has no column 'arglebargle':

            Possible choices are:
              - a
              - b
              - c"""
        )
        with pytest.raises(AttributeError, match=re.escape(expected)):
            SomeDataSet.get_column("arglebargle")

    def test_get_column_failure_but_attribute_exists(self):
        attr = "exists_but_not_a_column"
        assert hasattr(SomeDataSet, attr)

        expected = dedent(
            """\
            SomeDataSet has no column 'exists_but_not_a_column':

            Possible choices are:
              - a
              - b
              - c"""
        )
        with pytest.raises(AttributeError, match=re.escape(expected)):
            SomeDataSet.get_column(attr)

    def test_get_column_failure_truncate_error_message(self):
        expected = dedent(
            """\
            LargeDataSet has no column 'arglebargle':

            Possible choices are:
              - a
              - b
              - c
              - d
              - e
              - f
              - g
              - h
              - i
              - ...
              - z"""
        )
        with pytest.raises(AttributeError, match=re.escape(expected)):
            LargeDataSet.get_column("arglebargle")


class ReprTestCase(ZiplineTestCase):
    def test_dataset_repr(self):
        assert repr(SomeDataSet) == "<DataSet: 'SomeDataSet', domain=GENERIC>"

@pytest.fixture(scope="class")
def setup_and_teardown(request):
    # Hold a set of all the "static" attributes on the class. These are
    # things that are not populated after the class was created like
    # methods or other class level attributes.
    _static_class_attributes = set(vars(request.cls))
    _class_teardown_stack = ExitStack()
    yield
    stack = _class_teardown_stack
    for name in set(vars(request.cls)) - _static_class_attributes:
        # Remove all of the attributes that were added after the class was
        # constructed. This cleans up any large test data that is class
        # scoped while still allowing subclasses to access class level
        # attributes.
        delattr(request.cls, name)
    stack.close()

@pytest.mark.usefixtures("setup_and_teardown")
class TestRepr:
    def test_dataset_repr(self):
        assert repr(SomeDataSet) == "<DataSet: 'SomeDataSet', domain=GENERIC>"