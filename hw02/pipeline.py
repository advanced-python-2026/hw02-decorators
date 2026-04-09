"""Функциональный пайплайн для ДЗ 2.

Задание 2.2:
- pipe(*fns) — применяет функции слева направо
- compose(*fns) — применяет функции справа налево
- filter_by(**kwargs) — фильтрация по атрибутам/ключам
- sort_by(key) — сортировка по ключу
- take(n) — первые N элементов
"""

from __future__ import annotations

from typing import Any, Callable


def pipe(*fns: Callable[..., Any]) -> Callable[..., Any]:
    """Применяет функции слева направо.

    Пример::

        pipe(str.upper, str.strip)("  hello  ")  # "HELLO"
        pipe(add_one, double)(5)  # double(add_one(5)) = 12
    """
    # TODO: реализовать
    raise NotImplementedError("pipe не реализован")


def compose(*fns: Callable[..., Any]) -> Callable[..., Any]:
    """Применяет функции справа налево.

    Пример::

        compose(double, add_one)(5)  # double(add_one(5)) = 12
    """
    # TODO: реализовать
    raise NotImplementedError("compose не реализован")


def filter_by(**kwargs: Any) -> Callable[[list[Any]], list[Any]]:
    """Возвращает функцию, фильтрующую список словарей/объектов по указанным полям.

    Пример::

        users = [{"name": "Alice", "active": True}, {"name": "Bob", "active": False}]
        filter_by(active=True)(users)  # [{"name": "Alice", "active": True}]
    """
    # TODO: реализовать
    raise NotImplementedError("filter_by не реализован")


def sort_by(key: str, *, reverse: bool = False) -> Callable[[list[Any]], list[Any]]:
    """Возвращает функцию, сортирующую список словарей/объектов по указанному ключу.

    Пример::

        sort_by("name")(users)  # отсортировано по name
    """
    # TODO: реализовать
    raise NotImplementedError("sort_by не реализован")


def take(n: int) -> Callable[[list[Any]], list[Any]]:
    """Возвращает функцию, берущую первые n элементов.

    Пример::

        take(2)([1, 2, 3, 4])  # [1, 2]
    """
    # TODO: реализовать
    raise NotImplementedError("take не реализован")
