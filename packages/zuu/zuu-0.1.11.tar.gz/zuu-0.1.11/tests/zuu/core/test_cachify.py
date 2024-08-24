import pytest
import time
from zuu.core.cachify import cachify, timed_cachify, lru_cachify


class TestCachify:
    def test_cachify_basic(self):
        call_count = 0

        @cachify
        def expensive_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        assert expensive_function(5) == 10
        assert expensive_function(5) == 10
        assert call_count == 1

    def test_cachify_different_args(self):
        @cachify
        def add(a, b):
            return a + b

        assert add(2, 3) == 5
        assert add(3, 4) == 7
        assert add(2, 3) == 5


class TestTimedCachify:
    def test_timed_cachify_expiration(self):
        call_count = 0

        @timed_cachify(1)
        def timed_function():
            nonlocal call_count
            call_count += 1
            return time.time()

        first_call = timed_function()
        time.sleep(0.5)
        second_call = timed_function()
        assert first_call == second_call
        assert call_count == 1

        time.sleep(0.6)
        third_call = timed_function()
        assert third_call != second_call
        assert call_count == 2

    def test_timed_cachify_different_expirations(self):
        @timed_cachify(0.5)
        def short_lived():
            return time.time()

        @timed_cachify(2)
        def long_lived():
            return time.time()

        short_first = short_lived()
        long_first = long_lived()

        time.sleep(1)

        assert short_lived() != short_first
        assert long_lived() == long_first


class TestLRUCachify:
    def test_lru_cachify_maxsize(self):
        call_count = 0

        @lru_cachify(maxsize=2)
        def lru_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        lru_function(1)
        lru_function(2)
        lru_function(3)
        lru_function(1)

        assert call_count == 4

    def test_lru_cachify_unlimited(self):
        call_count = 0

        @lru_cachify(maxsize=None)
        def unlimited_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        for i in range(1000):
            unlimited_function(i)

        assert call_count == 1000

        for i in range(1000):
            unlimited_function(i)

        assert call_count == 1000
