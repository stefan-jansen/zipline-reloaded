"""Tests for zipline.utils.memoize."""

from collections import defaultdict
import gc

import pytest

from zipline.utils.memoize import remember_last, weak_lru_cache


class TestRememberLast:
    def test_remember_last(self):
        # Store the count in a list so we can mutate it from inside `func`.
        call_count = [0]

        @remember_last
        def func(x):
            call_count[0] += 1
            return x

        assert (func(1), call_count[0]) == (1, 1)

        # Calling again with the same argument should just re-use the old
        # value, which means func shouldn't get called again.
        assert (func(1), call_count[0]) == (1, 1)
        assert (func(1), call_count[0]) == (1, 1)

        # Calling with a new value should increment the counter.
        assert (func(2), call_count[0]) == (2, 2)
        assert (func(2), call_count[0]) == (2, 2)

        # Calling the old value should still increment the counter.
        assert (func(1), call_count[0]) == (1, 3)
        assert (func(1), call_count[0]) == (1, 3)

    def test_remember_last_method(self):
        call_count = defaultdict(int)

        class clz:
            @remember_last
            def func(self, x):
                call_count[(self, x)] += 1
                return x

        inst1 = clz()
        assert (inst1.func(1), call_count) == (1, {(inst1, 1): 1})

        # Calling again with the same argument should just re-use the old
        # value, which means func shouldn't get called again.
        assert (inst1.func(1), call_count) == (1, {(inst1, 1): 1})

        # Calling with a new value should increment the counter.
        assert (inst1.func(2), call_count) == (2, {(inst1, 1): 1, (inst1, 2): 1})

        assert (inst1.func(2), call_count) == (2, {(inst1, 1): 1, (inst1, 2): 1})

        # Calling the old value should still increment the counter.
        assert (inst1.func(1), call_count) == (1, {(inst1, 1): 2, (inst1, 2): 1})

        assert (inst1.func(1), call_count) == (1, {(inst1, 1): 2, (inst1, 2): 1})

        inst2 = clz()
        assert (inst2.func(1), call_count) == (
            1,
            {(inst1, 1): 2, (inst1, 2): 1, (inst2, 1): 1},
        )

        assert (inst2.func(1), call_count) == (
            1,
            {(inst1, 1): 2, (inst1, 2): 1, (inst2, 1): 1},
        )

        assert (inst2.func(2), call_count) == (
            2,
            {(inst1, 1): 2, (inst1, 2): 1, (inst2, 1): 1, (inst2, 2): 1},
        )

        assert (inst2.func(2), call_count) == (
            2,
            {(inst1, 1): 2, (inst1, 2): 1, (inst2, 1): 1, (inst2, 2): 1},
        )

        assert (inst2.func(1), call_count) == (
            1,
            {(inst1, 1): 2, (inst1, 2): 1, (inst2, 1): 2, (inst2, 2): 1},
        )
        assert (inst2.func(1), call_count) == (
            1,
            {(inst1, 1): 2, (inst1, 2): 1, (inst2, 1): 2, (inst2, 2): 1},
        )

        # Remove the above references to the instances and ensure that
        # remember_last has not made its own.
        del inst1, inst2
        call_count.clear()
        while gc.collect():
            pass

        assert not [inst for inst in gc.get_objects() if type(inst) is clz]


@pytest.mark.parametrize("maxsize", [None, 2])
def test_cache_clear_recomputes_results_and_resets_counts(maxsize):
    class Item:
        value = 1

        @weak_lru_cache(maxsize)
        def cached(self, key):
            return self.value

    item = Item()
    cached = item.cached
    assert cached(1) == 1
    item.value = 2
    assert cached(1) == 1
    assert cached.cache_info().misses == 1
    cached.cache_clear()
    assert cached.cache_info().hits == cached.cache_info().misses == 0
    assert cached(1) == 2


@pytest.mark.parametrize("maxsize", [None, 2])
def test_cache_accepts_a_function_without_arguments(maxsize):
    calls = []

    class Item:
        @weak_lru_cache(maxsize)
        def cached(self):
            calls.append(None)
            return len(calls)

    item = Item()
    function = item.cached
    assert function() == function() == 1
    function.cache_clear()
    assert function() == 2
