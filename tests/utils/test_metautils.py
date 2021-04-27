from zipline.testing.fixtures import ZiplineTestCase
from zipline.testing.predicates import (
    assert_is_subclass,
)
from zipline.utils.metautils import compose_types, with_metaclasses


class C:
    @staticmethod
    def f():
        return "C.f"

    def delegate(self):
        return "C.delegate", super(C, self).delegate()


class D:
    @staticmethod
    def f():
        return "D.f"

    @staticmethod
    def g():
        return "D.g"

    def delegate(self):
        return "D.delegate"


class TestComposeTypes:
    def test_identity(self):
        assert (
            compose_types(C) is C
        ), "compose_types of a single class should be identity"

    def test_compose(self):
        composed = compose_types(C, D)

        assert_is_subclass(composed, C)
        assert_is_subclass(composed, D)

    def test_compose_mro(self):
        composed = compose_types(C, D)

        assert composed.f() == C.f()
        assert composed.g() == D.g()

        assert composed().delegate() == ("C.delegate", "D.delegate")


class M(type):
    def __new__(mcls, name, bases, dict_):
        dict_["M"] = True
        return super(M, mcls).__new__(mcls, name, bases, dict_)


class N(type):
    def __new__(mcls, name, bases, dict_):
        dict_["N"] = True
        return super(N, mcls).__new__(mcls, name, bases, dict_)


class TestWithMetaclasses:
    def test_with_metaclasses_no_subclasses(self):
        class E(with_metaclasses((M, N))):
            pass

        assert E.M
        assert E.N

        assert isinstance(E, M)
        assert isinstance(E, N)

    def test_with_metaclasses_with_subclasses(self):
        class E(with_metaclasses((M, N), C, D)):
            pass

        assert E.M
        assert E.N

        assert isinstance(E, M)
        assert isinstance(E, N)
        assert_is_subclass(E, C)
        assert_is_subclass(E, D)
