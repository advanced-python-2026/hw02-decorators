"""Тесты для вариантных декораторов (задание 2.1).

Каждый тестовый класс пропускается, если декоратор не входит в вариант студента.
"""

import logging
import time
import warnings
from typing import Callable

import pytest

from hw02.decorators import curry, deprecated, memoize, retry, throttle, trace


# ============================================================
# Хелпер для пропуска тестов по варианту
# ============================================================


def _skip_unless_variant(decorator_names: tuple[str, str], name: str) -> None:
    if name not in decorator_names:
        pytest.skip(f"Декоратор @{name} не входит в вариант студента")


# ============================================================
# @curry — варианты 0, 4
# ============================================================


class TestCurry:
    """Тесты для @curry."""

    @pytest.fixture(autouse=True)
    def _check_variant(self, decorator_names: tuple[str, str]) -> None:
        _skip_unless_variant(decorator_names, "curry")

    def test_full_application(self) -> None:
        @curry
        def add(a: int, b: int, c: int) -> int:
            return a + b + c

        assert add(1, 2, 3) == 6

    def test_single_arg_chain(self) -> None:
        @curry
        def add(a: int, b: int, c: int) -> int:
            return a + b + c

        assert add(1)(2)(3) == 6

    def test_partial_two_then_one(self) -> None:
        @curry
        def add(a: int, b: int, c: int) -> int:
            return a + b + c

        assert add(1, 2)(3) == 6

    def test_partial_one_then_two(self) -> None:
        @curry
        def add(a: int, b: int, c: int) -> int:
            return a + b + c

        assert add(1)(2, 3) == 6

    def test_preserves_result(self) -> None:
        @curry
        def multiply(a: int, b: int) -> int:
            return a * b

        double = multiply(2)
        assert double(5) == 10
        assert double(3) == 6

    def test_single_arg_function(self) -> None:
        @curry
        def identity(x: int) -> int:
            return x

        assert identity(42) == 42

    def test_preserves_name(self) -> None:
        @curry
        def my_func(a: int, b: int) -> int:
            return a + b

        assert my_func.__name__ == "my_func"


# ============================================================
# @memoize — варианты 0, 3
# ============================================================


class TestMemoize:
    """Тесты для @memoize."""

    @pytest.fixture(autouse=True)
    def _check_variant(self, decorator_names: tuple[str, str]) -> None:
        _skip_unless_variant(decorator_names, "memoize")

    def test_caches_result(self) -> None:
        call_count = 0

        @memoize()
        def square(x: int) -> int:
            nonlocal call_count
            call_count += 1
            return x * x

        assert square(4) == 16
        assert square(4) == 16
        assert call_count == 1

    def test_different_args_different_cache(self) -> None:
        call_count = 0

        @memoize()
        def double(x: int) -> int:
            nonlocal call_count
            call_count += 1
            return x * 2

        assert double(1) == 2
        assert double(2) == 4
        assert call_count == 2

    def test_ttl_expiration(self) -> None:
        call_count = 0

        @memoize(ttl=0.2)
        def func(x: int) -> int:
            nonlocal call_count
            call_count += 1
            return x

        assert func(1) == 1
        assert call_count == 1

        time.sleep(0.3)

        assert func(1) == 1
        assert call_count == 2  # кеш истёк

    def test_ttl_not_expired(self) -> None:
        call_count = 0

        @memoize(ttl=5.0)
        def func(x: int) -> int:
            nonlocal call_count
            call_count += 1
            return x

        func(1)
        func(1)
        assert call_count == 1

    def test_no_ttl_caches_forever(self) -> None:
        call_count = 0

        @memoize()
        def func(x: int) -> int:
            nonlocal call_count
            call_count += 1
            return x

        for _ in range(100):
            func(42)
        assert call_count == 1

    def test_preserves_name(self) -> None:
        @memoize()
        def my_func(x: int) -> int:
            return x

        assert my_func.__name__ == "my_func"

    def test_keyword_args_cached(self) -> None:
        call_count = 0

        @memoize()
        def func(a: int, b: int = 0) -> int:
            nonlocal call_count
            call_count += 1
            return a + b

        func(1, b=2)
        func(1, b=2)
        assert call_count == 1


# ============================================================
# @retry — варианты 1, 3
# ============================================================


class TestRetry:
    """Тесты для @retry."""

    @pytest.fixture(autouse=True)
    def _check_variant(self, decorator_names: tuple[str, str]) -> None:
        _skip_unless_variant(decorator_names, "retry")

    def test_succeeds_first_try(self) -> None:
        @retry(max_retries=3, exceptions=(ValueError,), backoff=0.01)
        def ok() -> str:
            return "ok"

        assert ok() == "ok"

    def test_retries_then_succeeds(self) -> None:
        attempts = 0

        @retry(max_retries=3, exceptions=(ValueError,), backoff=0.01)
        def flaky() -> str:
            nonlocal attempts
            attempts += 1
            if attempts < 3:
                raise ValueError("not yet")
            return "done"

        assert flaky() == "done"
        assert attempts == 3

    def test_exhausts_retries_raises(self) -> None:
        @retry(max_retries=2, exceptions=(ValueError,), backoff=0.01)
        def always_fail() -> None:
            raise ValueError("fail")

        with pytest.raises(ValueError, match="fail"):
            always_fail()

    def test_does_not_retry_other_exceptions(self) -> None:
        attempts = 0

        @retry(max_retries=5, exceptions=(ValueError,), backoff=0.01)
        def wrong_error() -> None:
            nonlocal attempts
            attempts += 1
            raise TypeError("wrong")

        with pytest.raises(TypeError):
            wrong_error()
        assert attempts == 1

    def test_exponential_backoff(self) -> None:
        timestamps: list[float] = []

        @retry(max_retries=3, exceptions=(RuntimeError,), backoff=0.05)
        def timed_fail() -> None:
            timestamps.append(time.monotonic())
            raise RuntimeError("fail")

        with pytest.raises(RuntimeError):
            timed_fail()

        assert len(timestamps) == 4  # 1 initial + 3 retries
        # Проверяем экспоненциальный рост задержек
        delays = [timestamps[i + 1] - timestamps[i] for i in range(len(timestamps) - 1)]
        # Каждая следующая задержка должна быть примерно вдвое больше
        for i in range(1, len(delays)):
            assert delays[i] >= delays[i - 1] * 1.5  # допуск на неточность таймера

    def test_preserves_name(self) -> None:
        @retry(max_retries=1, exceptions=(Exception,), backoff=0.01)
        def my_func() -> None:
            pass

        assert my_func.__name__ == "my_func"

    def test_retry_multiple_exception_types(self) -> None:
        attempts = 0

        @retry(max_retries=3, exceptions=(ValueError, OSError), backoff=0.01)
        def multi_error() -> str:
            nonlocal attempts
            attempts += 1
            if attempts == 1:
                raise ValueError("v")
            if attempts == 2:
                raise OSError("o")
            return "ok"

        assert multi_error() == "ok"
        assert attempts == 3


# ============================================================
# @deprecated — варианты 2, 5
# ============================================================


class TestDeprecated:
    """Тесты для @deprecated."""

    @pytest.fixture(autouse=True)
    def _check_variant(self, decorator_names: tuple[str, str]) -> None:
        _skip_unless_variant(decorator_names, "deprecated")

    def test_issues_warning(self) -> None:
        @deprecated(message="use new_func")
        def old_func() -> str:
            return "result"

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            old_func()
            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)

    def test_warning_contains_message(self) -> None:
        @deprecated(message="use new_func instead")
        def old_func() -> str:
            return "result"

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            old_func()
            assert "use new_func instead" in str(w[0].message)

    def test_function_still_works(self) -> None:
        @deprecated(message="old")
        def compute(x: int) -> int:
            return x * 2

        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            assert compute(5) == 10

    def test_empty_message(self) -> None:
        @deprecated(message="")
        def func() -> None:
            pass

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            func()
            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)

    def test_preserves_name(self) -> None:
        @deprecated(message="old")
        def my_func() -> None:
            pass

        assert my_func.__name__ == "my_func"

    def test_preserves_doc(self) -> None:
        @deprecated(message="old")
        def my_func() -> None:
            """My docstring."""

        assert my_func.__doc__ == "My docstring."

    def test_warning_each_call(self) -> None:
        @deprecated(message="old")
        def func() -> int:
            return 1

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            func()
            func()
            assert len(w) == 2

    def test_removal_version_in_warning(self) -> None:
        @deprecated(message="use new_func", removal_version="2.0")
        def old_func() -> str:
            return "result"

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            old_func()
            assert len(w) == 1
            warning_text = str(w[0].message)
            assert "2.0" in warning_text

    def test_removal_version_none_no_crash(self) -> None:
        @deprecated(message="old", removal_version=None)
        def func() -> str:
            return "ok"

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            assert func() == "ok"
            assert len(w) == 1


# ============================================================
# @trace — варианты 1, 4
# ============================================================


class TestTrace:
    """Тесты для @trace."""

    @pytest.fixture(autouse=True)
    def _check_variant(self, decorator_names: tuple[str, str]) -> None:
        _skip_unless_variant(decorator_names, "trace")

    def test_logs_function_name(self, caplog: pytest.LogCaptureFixture) -> None:
        @trace(logger_name="test_trace")
        def greet(name: str) -> str:
            return f"Hello, {name}"

        with caplog.at_level(logging.DEBUG, logger="test_trace"):
            greet("Alice")

        assert "greet" in caplog.text

    def test_logs_arguments(self, caplog: pytest.LogCaptureFixture) -> None:
        @trace(logger_name="test_trace")
        def add(a: int, b: int) -> int:
            return a + b

        with caplog.at_level(logging.DEBUG, logger="test_trace"):
            add(3, 4)

        assert "3" in caplog.text
        assert "4" in caplog.text

    def test_logs_result(self, caplog: pytest.LogCaptureFixture) -> None:
        @trace(logger_name="test_trace")
        def double(x: int) -> int:
            return x * 2

        with caplog.at_level(logging.DEBUG, logger="test_trace"):
            result = double(5)

        assert result == 10
        assert "10" in caplog.text

    def test_logs_execution_time(self, caplog: pytest.LogCaptureFixture) -> None:
        @trace(logger_name="test_trace")
        def slow() -> str:
            time.sleep(0.05)
            return "done"

        with caplog.at_level(logging.DEBUG, logger="test_trace"):
            slow()

        # Должно содержать что-то про время (секунды, ms, time и т.п.)
        log_lower = caplog.text.lower()
        assert any(word in log_lower for word in ("time", "duration", "elapsed", "sec", "ms"))

    def test_function_still_works(self, caplog: pytest.LogCaptureFixture) -> None:
        @trace(logger_name="test_trace")
        def multiply(a: int, b: int) -> int:
            return a * b

        with caplog.at_level(logging.DEBUG, logger="test_trace"):
            assert multiply(3, 7) == 21

    def test_preserves_name(self) -> None:
        @trace(logger_name="test_trace")
        def my_func() -> None:
            pass

        assert my_func.__name__ == "my_func"

    def test_uses_specified_logger(self, caplog: pytest.LogCaptureFixture) -> None:
        @trace(logger_name="custom_logger")
        def func() -> int:
            return 42

        with caplog.at_level(logging.DEBUG, logger="custom_logger"):
            func()

        assert any(r.name == "custom_logger" for r in caplog.records)


# ============================================================
# @throttle — варианты 2, 5
# ============================================================


class TestThrottle:
    """Тесты для @throttle."""

    @pytest.fixture(autouse=True)
    def _check_variant(self, decorator_names: tuple[str, str]) -> None:
        _skip_unless_variant(decorator_names, "throttle")

    def test_first_call_immediate(self) -> None:
        @throttle(rate=1.0)
        def func() -> str:
            return "ok"

        start = time.monotonic()
        result = func()
        elapsed = time.monotonic() - start

        assert result == "ok"
        assert elapsed < 0.1

    def test_second_call_delayed(self) -> None:
        @throttle(rate=0.2)
        def func() -> str:
            return "ok"

        func()
        start = time.monotonic()
        func()
        elapsed = time.monotonic() - start

        assert elapsed >= 0.15  # допуск

    def test_respects_rate(self) -> None:
        timestamps: list[float] = []

        @throttle(rate=0.1)
        def func() -> None:
            timestamps.append(time.monotonic())

        for _ in range(3):
            func()

        for i in range(1, len(timestamps)):
            assert timestamps[i] - timestamps[i - 1] >= 0.08  # допуск

    def test_function_returns_correct_value(self) -> None:
        @throttle(rate=0.05)
        def double(x: int) -> int:
            return x * 2

        assert double(5) == 10
        assert double(3) == 6

    def test_preserves_name(self) -> None:
        @throttle(rate=0.1)
        def my_func() -> None:
            pass

        assert my_func.__name__ == "my_func"

    def test_no_delay_after_rate_elapsed(self) -> None:
        @throttle(rate=0.1)
        def func() -> str:
            return "ok"

        func()
        time.sleep(0.15)

        start = time.monotonic()
        func()
        elapsed = time.monotonic() - start

        assert elapsed < 0.05  # не должно быть задержки


# ============================================================
# Composability — стекирование декораторов
# ============================================================


class TestComposability:
    """Test that decorators work correctly when stacked."""

    def _get_decorator(self, name: str) -> Callable:
        """Return a ready-to-apply decorator by name (calling factories with defaults)."""
        import hw02.decorators as mod

        raw = getattr(mod, name)
        # Factories need to be called with params; curry is applied directly
        factories = {
            "memoize": lambda: raw(),
            "retry": lambda: raw(max_retries=2, exceptions=(Exception,), backoff=0.01),
            "deprecated": lambda: raw(message="test"),
            "trace": lambda: raw(logger_name="test_compose"),
            "throttle": lambda: raw(rate=0.01),
            "curry": lambda: raw,  # not a factory
        }
        return factories[name]()

    def test_validate_types_with_variant_decorators(
        self, variant: int, decorator_names: tuple[str, str]
    ) -> None:
        """Stack @validate_types with both variant decorators."""
        from hw02.decorators import validate_types

        dec1 = self._get_decorator(decorator_names[0])
        dec2 = self._get_decorator(decorator_names[1])

        # curry requires special handling: it changes call signature
        if "curry" in decorator_names:
            # For curry variants, just stack the non-curry decorator with validate_types
            other = decorator_names[1] if decorator_names[0] == "curry" else decorator_names[0]
            dec = self._get_decorator(other)

            @dec
            @validate_types
            def add(a: int, b: int) -> int:
                return a + b

            assert add(2, 3) == 5
        else:
            @dec1
            @dec2
            @validate_types
            def add(a: int, b: int) -> int:
                return a + b

            with warnings.catch_warnings(record=True):
                warnings.simplefilter("always")
                assert add(2, 3) == 5

    def test_validate_types_catches_error_through_stack(
        self, variant: int, decorator_names: tuple[str, str]
    ) -> None:
        """Ensure validate_types still raises TypeError when stacked."""
        from hw02.decorators import validate_types

        # Skip for curry variants — curry changes how args are passed
        if "curry" in decorator_names:
            pytest.skip("curry changes call semantics; tested separately")

        dec1 = self._get_decorator(decorator_names[0])
        dec2 = self._get_decorator(decorator_names[1])

        @dec1
        @dec2
        @validate_types
        def add(a: int, b: int) -> int:
            return a + b

        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            with pytest.raises(TypeError):
                add(1, "two")  # type: ignore[arg-type]

    def test_stacked_decorators_preserve_name(
        self, variant: int, decorator_names: tuple[str, str]
    ) -> None:
        """All stacked decorators should preserve __name__ via functools.wraps."""
        from hw02.decorators import validate_types

        # Skip curry — it returns a wrapper with its own __name__ handling
        if "curry" in decorator_names:
            pytest.skip("curry has special __name__ handling")

        dec1 = self._get_decorator(decorator_names[0])
        dec2 = self._get_decorator(decorator_names[1])

        @dec1
        @dec2
        @validate_types
        def my_stacked_func(a: int, b: int) -> int:
            return a + b

        assert my_stacked_func.__name__ == "my_stacked_func"
