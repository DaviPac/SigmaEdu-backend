from typing import Generic, TypeVar

T = TypeVar("T")


class Result(Generic[T]):
    def __init__(self, value: T | None, error: str | None):
        self._value = value
        self._error = error

    @classmethod
    def ok(cls, value: T | None = None) -> "Result[T]":
        return cls(value=value, error=None)

    @classmethod
    def fail(cls, error: str) -> "Result[T]":
        return cls(value=None, error=error)

    @property
    def is_success(self) -> bool:
        return self._error is None

    @property
    def value(self) -> T | None:
        return self._value

    @property
    def error(self) -> str | None:
        return self._error
