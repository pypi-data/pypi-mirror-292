from collections.abc import Callable
from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")
U = TypeVar("U")


class Result(BaseModel, Generic[T]):
    """
    Represents the result of an operation, encapsulating success or failure.
    This class is a generic model that allows specifying the type of the value it holds.
    Attributes:
        is_successful (bool): Indicates whether the operation was successful.
        value (T | None): The value returned by the operation if it was successful.
        error (Exception | None): The error object if the operation failed.
    """

    is_successful: bool
    value: T | None
    error: Exception | None

    class Config:
        arbitrary_types_allowed = True

    def get_safe_value(self) -> T:
        """
        :return: the value if the operation was successful, otherwise raises the error.
        """
        if self.is_successful and self.value is not None:
            return self.value
        error_message = "Can't retrieve the value because the result is not successful."
        raise RuntimeError(error_message)

    def get_safe_error(self) -> Exception:
        """
        :return: the error if the operation failed, otherwise raises a RuntimeError.
        """
        if not self.is_successful and self.error is not None:
            return self.error
        error_message = "Can't retrieve the error because the result is successful."
        raise RuntimeError(error_message)

    def map(self, func: Callable[[T], U]) -> "Result[U]":
        """
        Maps the value of the result using the given function.
        """
        if self.is_successful:
            return Result.success(func(self.get_safe_value()))
        return Result.failure(self.get_safe_error())

    @staticmethod
    def success(value: T) -> "Result[T]":
        """
        Creates a new instance of Result representing a successful operation with the given value.
        """
        return Result(is_successful=True, value=value, error=None)

    @staticmethod
    def failure(error: Exception | str) -> "Result[T]":
        """
        Creates a new instance of Result representing a failed operation with the given error.
        """
        return Result(
            is_successful=False, error=error if isinstance(error, Exception) else RuntimeError(error), value=None
        )