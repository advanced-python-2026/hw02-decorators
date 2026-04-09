"""Декораторы для ДЗ 2.

Задание 2.1:
- validate_types — обязательный для всех
- Два дополнительных декоратора определяются вариантом студента

Все декораторы должны:
- Быть параметризованными (фабрика)
- Использовать functools.wraps
- Быть композируемыми (stackable)
- Иметь type hints
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, TypeVar

F = TypeVar("F", bound=Callable[..., Any])


# ============================================================
# validate_types — обязательный для всех вариантов
# ============================================================


def validate_types(func: F) -> F:
    """Декоратор, проверяющий типы аргументов и возвращаемого значения по аннотациям.

    Если аргумент или возвращаемое значение не соответствует аннотации,
    выбрасывает TypeError с понятным сообщением.
    Параметры без аннотаций не проверяются.

    Пример::

        @validate_types
        def add(a: int, b: int) -> int:
            return a + b

        add(1, 2)       # OK -> 3
        add(1, "two")   # TypeError
    """
    # TODO: реализовать декоратор
    raise NotImplementedError("validate_types не реализован")


# ============================================================
# Вариант 0, 4: curry
# ============================================================


def curry(func: F) -> F:
    """Декоратор каррирования.

    Позволяет вызывать функцию с частичным применением аргументов::

        @curry
        def add(a: int, b: int, c: int) -> int:
            return a + b + c

        add(1)(2)(3)     # 6
        add(1, 2)(3)     # 6
        add(1)(2, 3)     # 6
    """
    # TODO: реализовать декоратор
    raise NotImplementedError("curry не реализован")


# ============================================================
# Вариант 0, 3: memoize
# ============================================================


def memoize(*, ttl: float | None = None) -> Callable[[F], F]:
    """Декоратор кеширования результатов.

    Args:
        ttl: Время жизни кеша в секундах. None — бессрочно.

    Пример::

        @memoize(ttl=60)
        def expensive(n: int) -> int:
            return n ** 2
    """

    # TODO: реализовать декоратор
    def decorator(func: F) -> F:
        raise NotImplementedError("memoize не реализован")

    return decorator


# ============================================================
# Вариант 1, 3: retry
# ============================================================


def retry(
    *,
    max_retries: int = 3,
    exceptions: tuple[type[Exception], ...] = (Exception,),
    backoff: float = 1.0,
) -> Callable[[F], F]:
    """Декоратор повторных попыток при исключении.

    Args:
        max_retries: Максимальное количество повторных попыток.
        exceptions: Кортеж классов исключений, при которых повторять.
        backoff: Базовая задержка (экспоненциальная: backoff * 2^attempt).

    Пример::

        @retry(max_retries=3, exceptions=(ConnectionError,), backoff=0.1)
        def fetch(url: str) -> str:
            ...
    """

    # TODO: реализовать декоратор
    def decorator(func: F) -> F:
        raise NotImplementedError("retry не реализован")

    return decorator


# ============================================================
# Вариант 2, 5: deprecated
# ============================================================


def deprecated(*, message: str = "", removal_version: str | None = None) -> Callable[[F], F]:
    """Декоратор, помечающий функцию как устаревшую.

    При вызове выдаёт DeprecationWarning с указанным сообщением.

    Args:
        message: Текст предупреждения.
        removal_version: Версия, в которой функция будет удалена (добавляется в предупреждение).

    Пример::

        @deprecated(message="Используйте new_func вместо old_func", removal_version="2.0")
        def old_func() -> None:
            ...
    """

    # TODO: реализовать декоратор
    def decorator(func: F) -> F:
        raise NotImplementedError("deprecated не реализован")

    return decorator


# ============================================================
# Вариант 1, 4: trace
# ============================================================


def trace(*, logger_name: str = __name__) -> Callable[[F], F]:
    """Декоратор трассировки вызовов через модуль logging.

    Логирует имя функции, аргументы, результат и время выполнения.

    Args:
        logger_name: Имя логгера.

    Пример::

        @trace(logger_name="myapp")
        def compute(x: int) -> int:
            return x * 2
    """

    # TODO: реализовать декоратор
    def decorator(func: F) -> F:
        raise NotImplementedError("trace не реализован")

    return decorator


# ============================================================
# Вариант 2, 5: throttle
# ============================================================


def throttle(*, rate: float) -> Callable[[F], F]:
    """Декоратор ограничения частоты вызовов.

    Если функция вызывается чаще чем раз в `rate` секунд,
    блокирует (sleep) до истечения интервала.

    Args:
        rate: Минимальный интервал между вызовами в секундах.

    Пример::

        @throttle(rate=1.0)
        def api_call() -> dict:
            ...
    """

    # TODO: реализовать декоратор
    def decorator(func: F) -> F:
        raise NotImplementedError("throttle не реализован")

    return decorator
