"""Тесты для @validate_types — обязательный декоратор для всех вариантов."""

import pytest

from hw02.decorators import validate_types


class TestValidateTypesBasic:
    """Базовая проверка типов аргументов."""

    def test_correct_types_pass(self) -> None:
        @validate_types
        def add(a: int, b: int) -> int:
            return a + b

        assert add(1, 2) == 3

    def test_wrong_arg_type_raises(self) -> None:
        @validate_types
        def add(a: int, b: int) -> int:
            return a + b

        with pytest.raises(TypeError):
            add(1, "two")

    def test_wrong_first_arg_type(self) -> None:
        @validate_types
        def greet(name: str) -> str:
            return f"Hello, {name}"

        with pytest.raises(TypeError):
            greet(123)

    def test_multiple_wrong_args(self) -> None:
        @validate_types
        def func(a: int, b: str, c: float) -> str:
            return f"{a}{b}{c}"

        with pytest.raises(TypeError):
            func("not_int", "ok", 1.0)

    def test_keyword_arguments(self) -> None:
        @validate_types
        def func(a: int, b: str = "default") -> str:
            return f"{a}-{b}"

        assert func(1, b="hello") == "1-hello"

    def test_wrong_keyword_arg_type(self) -> None:
        @validate_types
        def func(a: int, b: str = "default") -> str:
            return f"{a}-{b}"

        with pytest.raises(TypeError):
            func(1, b=42)


class TestValidateTypesReturn:
    """Проверка типа возвращаемого значения."""

    def test_correct_return_type(self) -> None:
        @validate_types
        def double(x: int) -> int:
            return x * 2

        assert double(5) == 10

    def test_wrong_return_type_raises(self) -> None:
        @validate_types
        def bad_return(x: int) -> int:
            return str(x)  # type: ignore[return-value]

        with pytest.raises(TypeError):
            bad_return(5)

    def test_none_return_type(self) -> None:
        @validate_types
        def void_func(x: int) -> None:
            _ = x

        assert void_func(1) is None

    def test_wrong_none_return(self) -> None:
        @validate_types
        def should_return_none(x: int) -> None:
            return x  # type: ignore[return-value]

        with pytest.raises(TypeError):
            should_return_none(5)

    def test_return_float(self) -> None:
        @validate_types
        def to_float(x: int) -> float:
            return float(x)

        assert to_float(3) == 3.0


class TestValidateTypesVariousTypes:
    """Проверка с различными типами: int, str, float, list, dict."""

    def test_str_type(self) -> None:
        @validate_types
        def upper(s: str) -> str:
            return s.upper()

        assert upper("hello") == "HELLO"

    def test_float_type(self) -> None:
        @validate_types
        def half(x: float) -> float:
            return x / 2

        assert half(4.0) == 2.0

    def test_list_type(self) -> None:
        @validate_types
        def length(items: list) -> int:
            return len(items)

        assert length([1, 2, 3]) == 3

    def test_wrong_list_type(self) -> None:
        @validate_types
        def length(items: list) -> int:
            return len(items)

        with pytest.raises(TypeError):
            length("not a list")

    def test_dict_type(self) -> None:
        @validate_types
        def keys(d: dict) -> list:
            return list(d.keys())

        assert keys({"a": 1}) == ["a"]

    def test_wrong_dict_type(self) -> None:
        @validate_types
        def keys(d: dict) -> list:
            return list(d.keys())

        with pytest.raises(TypeError):
            keys([1, 2])


class TestValidateTypesNoAnnotations:
    """Без аннотаций декоратор не проверяет ничего (no-op)."""

    def test_no_annotations_passes(self) -> None:
        @validate_types
        def add(a, b):  # noqa: ANN001, ANN201
            return a + b

        assert add(1, 2) == 3
        assert add("a", "b") == "ab"

    def test_partial_annotations(self) -> None:
        @validate_types
        def func(a: int, b):  # noqa: ANN001, ANN201
            return str(a) + str(b)

        assert func(1, 2) == "12"
        # b has no annotation — anything goes
        assert func(1, "x") == "1x"

    def test_only_return_annotation(self) -> None:
        @validate_types
        def func(a, b) -> int:  # noqa: ANN001
            return a + b

        assert func(1, 2) == 3

    def test_wrong_return_with_partial_annotations(self) -> None:
        @validate_types
        def func(a, b) -> int:  # noqa: ANN001
            return str(a)  # type: ignore[return-value]

        with pytest.raises(TypeError):
            func(1, 2)


class TestValidateTypesPreservesMetadata:
    """Декоратор сохраняет __name__ и __doc__."""

    def test_preserves_name(self) -> None:
        @validate_types
        def my_function(x: int) -> int:
            return x

        assert my_function.__name__ == "my_function"

    def test_preserves_doc(self) -> None:
        @validate_types
        def documented(x: int) -> int:
            """This is documentation."""
            return x

        assert documented.__doc__ == "This is documentation."

    def test_preserves_wrapped(self) -> None:
        @validate_types
        def original(x: int) -> int:
            return x

        assert hasattr(original, "__wrapped__")

    def test_preserves_module(self) -> None:
        @validate_types
        def func(x: int) -> int:
            return x

        assert func.__module__ == __name__

    def test_preserves_qualname(self) -> None:
        @validate_types
        def func(x: int) -> int:
            return x

        assert "func" in func.__qualname__
