"""Тесты для функционального пайплайна (задание 2.2)."""

import pytest

from hw02.pipeline import compose, filter_by, pipe, sort_by, take


# ============================================================
# pipe
# ============================================================


class TestPipe:
    """Тесты для pipe — применяет функции слева направо."""

    def test_single_function(self) -> None:
        result = pipe(str.upper)("hello")
        assert result == "HELLO"

    def test_two_functions_left_to_right(self) -> None:
        def add_one(x: int) -> int:
            return x + 1

        def double(x: int) -> int:
            return x * 2

        # pipe(add_one, double)(5) => double(add_one(5)) = double(6) = 12
        assert pipe(add_one, double)(5) == 12

    def test_three_functions(self) -> None:
        def add_one(x: int) -> int:
            return x + 1

        def double(x: int) -> int:
            return x * 2

        def to_str(x: int) -> str:
            return str(x)

        assert pipe(add_one, double, to_str)(5) == "12"

    def test_identity_with_no_transform(self) -> None:
        def identity(x: int) -> int:
            return x

        assert pipe(identity)(42) == 42

    def test_string_transformations(self) -> None:
        def strip(s: str) -> str:
            return s.strip()

        def upper(s: str) -> str:
            return s.upper()

        assert pipe(strip, upper)("  hello  ") == "HELLO"

    def test_pipe_returns_callable(self) -> None:
        fn = pipe(str.upper)
        assert callable(fn)


# ============================================================
# compose
# ============================================================


class TestCompose:
    """Тесты для compose — применяет функции справа налево."""

    def test_single_function(self) -> None:
        assert compose(str.upper)("hello") == "HELLO"

    def test_two_functions_right_to_left(self) -> None:
        def add_one(x: int) -> int:
            return x + 1

        def double(x: int) -> int:
            return x * 2

        # compose(double, add_one)(5) => double(add_one(5)) = 12
        assert compose(double, add_one)(5) == 12

    def test_three_functions(self) -> None:
        def add_one(x: int) -> int:
            return x + 1

        def double(x: int) -> int:
            return x * 2

        def to_str(x: int) -> str:
            return str(x)

        # compose(to_str, double, add_one)(5) => to_str(double(add_one(5))) = "12"
        assert compose(to_str, double, add_one)(5) == "12"

    def test_compose_returns_callable(self) -> None:
        fn = compose(str.upper)
        assert callable(fn)

    def test_compose_vs_pipe_equivalence(self) -> None:
        def add_one(x: int) -> int:
            return x + 1

        def double(x: int) -> int:
            return x * 2

        # pipe(f, g)(x) == compose(g, f)(x)
        assert pipe(add_one, double)(10) == compose(double, add_one)(10)

    def test_compose_vs_pipe_equivalence_multiple(self) -> None:
        def inc(x: int) -> int:
            return x + 1

        def dbl(x: int) -> int:
            return x * 2

        def neg(x: int) -> int:
            return -x

        assert pipe(inc, dbl, neg)(3) == compose(neg, dbl, inc)(3)


# ============================================================
# filter_by
# ============================================================


class TestFilterBy:
    """Тесты для filter_by — фильтрация по ключам словаря."""

    def test_single_filter(self) -> None:
        data = [
            {"name": "Alice", "active": True},
            {"name": "Bob", "active": False},
            {"name": "Charlie", "active": True},
        ]
        result = filter_by(active=True)(data)
        assert len(result) == 2
        assert all(item["active"] for item in result)

    def test_multiple_filters(self) -> None:
        data = [
            {"name": "Alice", "age": 30, "active": True},
            {"name": "Bob", "age": 25, "active": True},
            {"name": "Charlie", "age": 30, "active": False},
        ]
        result = filter_by(age=30, active=True)(data)
        assert len(result) == 1
        assert result[0]["name"] == "Alice"

    def test_no_match(self) -> None:
        data = [{"x": 1}, {"x": 2}]
        result = filter_by(x=3)(data)
        assert result == []

    def test_all_match(self) -> None:
        data = [{"x": 1}, {"x": 1}]
        result = filter_by(x=1)(data)
        assert len(result) == 2

    def test_empty_input(self) -> None:
        result = filter_by(x=1)([])
        assert result == []

    def test_returns_callable(self) -> None:
        fn = filter_by(active=True)
        assert callable(fn)


# ============================================================
# sort_by
# ============================================================


class TestSortBy:
    """Тесты для sort_by — сортировка по ключу."""

    def test_sort_ascending(self) -> None:
        data = [{"name": "Charlie"}, {"name": "Alice"}, {"name": "Bob"}]
        result = sort_by("name")(data)
        assert [item["name"] for item in result] == ["Alice", "Bob", "Charlie"]

    def test_sort_numeric(self) -> None:
        data = [{"age": 30}, {"age": 20}, {"age": 25}]
        result = sort_by("age")(data)
        assert [item["age"] for item in result] == [20, 25, 30]

    def test_sort_reverse(self) -> None:
        data = [{"val": 1}, {"val": 3}, {"val": 2}]
        result = sort_by("val", reverse=True)(data)
        assert [item["val"] for item in result] == [3, 2, 1]

    def test_stable_sort(self) -> None:
        data = [
            {"name": "B", "order": 1},
            {"name": "A", "order": 2},
            {"name": "B", "order": 3},
        ]
        result = sort_by("name")(data)
        b_items = [item for item in result if item["name"] == "B"]
        assert b_items[0]["order"] == 1
        assert b_items[1]["order"] == 3

    def test_returns_callable(self) -> None:
        fn = sort_by("name")
        assert callable(fn)

    def test_empty_list(self) -> None:
        result = sort_by("x")([])
        assert result == []


# ============================================================
# take
# ============================================================


class TestTake:
    """Тесты для take — первые N элементов."""

    def test_take_from_list(self) -> None:
        assert take(2)([1, 2, 3, 4]) == [1, 2]

    def test_take_zero(self) -> None:
        assert take(0)([1, 2, 3]) == []

    def test_take_more_than_available(self) -> None:
        assert take(10)([1, 2]) == [1, 2]

    def test_take_from_empty(self) -> None:
        assert take(5)([]) == []

    def test_take_all(self) -> None:
        assert take(3)([1, 2, 3]) == [1, 2, 3]

    def test_returns_callable(self) -> None:
        fn = take(3)
        assert callable(fn)


# ============================================================
# Композиция (composability)
# ============================================================


class TestPipelineComposition:
    """Тесты на композируемость функций пайплайна."""

    def test_filter_then_sort(self) -> None:
        data = [
            {"name": "Charlie", "active": True},
            {"name": "Alice", "active": True},
            {"name": "Bob", "active": False},
        ]
        pipeline = pipe(filter_by(active=True), sort_by("name"))
        result = pipeline(data)
        assert [item["name"] for item in result] == ["Alice", "Charlie"]

    def test_filter_sort_take(self) -> None:
        data = [
            {"name": "D", "score": 80},
            {"name": "A", "score": 95},
            {"name": "C", "score": 70},
            {"name": "B", "score": 90},
        ]
        pipeline = pipe(
            sort_by("score", reverse=True),
            take(2),
        )
        result = pipeline(data)
        assert len(result) == 2
        assert result[0]["score"] == 95
        assert result[1]["score"] == 90

    def test_full_pipeline(self) -> None:
        students = [
            {"name": "Alice", "grade": 90, "passed": True},
            {"name": "Bob", "grade": 60, "passed": False},
            {"name": "Charlie", "grade": 85, "passed": True},
            {"name": "Diana", "grade": 95, "passed": True},
            {"name": "Eve", "grade": 75, "passed": True},
        ]
        top_passing = pipe(
            filter_by(passed=True),
            sort_by("grade", reverse=True),
            take(3),
        )
        result = top_passing(students)
        assert len(result) == 3
        assert result[0]["name"] == "Diana"
        assert result[1]["name"] == "Alice"
        assert result[2]["name"] == "Charlie"

    def test_compose_with_pipeline_functions(self) -> None:
        data = [
            {"name": "Z", "active": True},
            {"name": "A", "active": True},
            {"name": "M", "active": False},
        ]
        # compose applies right to left: first filter, then sort
        pipeline = compose(sort_by("name"), filter_by(active=True))
        result = pipeline(data)
        assert [item["name"] for item in result] == ["A", "Z"]

    def test_pipe_compose_equivalence_with_pipeline(self) -> None:
        data = [{"v": 3}, {"v": 1}, {"v": 2}]
        pipe_result = pipe(sort_by("v"), take(2))(data)
        compose_result = compose(take(2), sort_by("v"))(data)
        assert pipe_result == compose_result
