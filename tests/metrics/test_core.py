from zipline.finance.metrics.core import _make_metrics_set_core
from zipline.testing.fixtures import ZiplineTestCase
from zipline.testing.predicates import assert_equal
from zipline.utils.compat import mappingproxy
import pytest


class MetricsSetCoreTestCase(ZiplineTestCase):
    def init_instance_fixtures(self):
        super(MetricsSetCoreTestCase, self).init_instance_fixtures()

        (
            self.metrics_sets,
            self.register,
            self.unregister,
            self.load,
        ) = _make_metrics_set_core()

        # make sure this starts empty
        assert_equal(self.metrics_sets, mappingproxy({}))

    def test_load_not_registered(self):
        msg = "no metrics set registered as 'ayy-lmao', options are: []"
        with pytest.raises(ValueError) as excinfo:
            self.load("ayy-lmao")
            assert excinfo.value == msg

        # register in reverse order to test the sorting of the options
        self.register("c", set)
        self.register("b", set)
        self.register("a", set)

        msg = "no metrics set registered as 'ayy-lmao', options are: " "['a', 'b', 'c']"
        with pytest.raises(ValueError) as excinfo:
            self.load("ayy-lmao")
            assert excinfo.value == msg

    def test_register_decorator(self):
        ayy_lmao_set = set()

        @self.register("ayy-lmao")
        def ayy_lmao():
            return ayy_lmao_set

        expected_metrics_sets = mappingproxy({"ayy-lmao": ayy_lmao})
        assert self.metrics_sets == expected_metrics_sets
        assert self.load("ayy-lmao") is ayy_lmao_set

        msg = "metrics set 'ayy-lmao' is already registered"
        with pytest.raises(ValueError) as excinfo:

            @self.register("ayy-lmao")
            def other():  # pragma: no cover
                raise AssertionError("dead")
            
            assert excinfo.value.args[0] == msg

        # ensure that the failed registration didn't break the previously
        # registered set
        assert self.metrics_sets == expected_metrics_sets
        assert self.load("ayy-lmao") is ayy_lmao_set

        self.unregister("ayy-lmao")
        assert self.metrics_sets == mappingproxy({})

        msg = "no metrics set registered as 'ayy-lmao', options are: []"
        with pytest.raises(ValueError) as excinfo:
            self.load("ayy-lmao")
            assert excinfo.value == msg

        msg = "metrics set 'ayy-lmao' was not already registered"
        with pytest.raises(ValueError) as excinfo:
            self.unregister("ayy-lmao")
            assert excinfo.value == msg

    def test_register_non_decorator(self):
        ayy_lmao_set = set()

        def ayy_lmao():
            return ayy_lmao_set

        self.register("ayy-lmao", ayy_lmao)

        expected_metrics_sets = mappingproxy({"ayy-lmao": ayy_lmao})
        assert self.metrics_sets == expected_metrics_sets
        assert self.load("ayy-lmao") is ayy_lmao_set

        def other():  # pragma: no cover
            raise AssertionError("dead")

        msg = "metrics set 'ayy-lmao' is already registered"
        with pytest.raises(ValueError) as excinfo:
            self.register("ayy-lmao", other)
            assert excinfo.value == msg

        # ensure that the failed registration didn't break the previously
        # registered set
        assert self.metrics_sets == expected_metrics_sets
        assert self.load("ayy-lmao") is ayy_lmao_set

        self.unregister("ayy-lmao")
        assert_equal(self.metrics_sets, mappingproxy({}))

        msg = "no metrics set registered as 'ayy-lmao', options are: []"
        with pytest.raises(ValueError) as excinfo:
            self.load("ayy-lmao")
            assert excinfo.value == msg

        msg = "metrics set 'ayy-lmao' was not already registered"
        with pytest.raises(ValueError, match=msg):
            self.unregister("ayy-lmao")
            assert excinfo.value == msg
