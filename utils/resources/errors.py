from __future__ import annotations
from typing import Generic, TypeVar

T = TypeVar("T")
E = TypeVar("E")

# Error Handling
class Result(Generic[T, E]):
    def __init__(self, issuccess:bool, value:T, error:E) -> None:
        self._value = value
        self._error = error
        self._issuccess = issuccess
    @property
    def value(self) -> T:
        if not self._issuccess:
            raise ValueError("Cannot access value of failed result")
        return self._value
    @property
    def error(self) -> E:
        if self._issuccess:
            raise ValueError("Cannot access error of successful result")
        return self._error
    @property
    def issuccess(self) -> bool:
        return self._issuccess
    @staticmethod
    def success(value:T) -> Result[T, E]:
        return Result(True, value, None)
    @staticmethod
    def fail(error:E) -> Result[T, E]:
        return Result(False, None, error)

class ConfigError(Exception):
    """
    Raised when there is an error loading the configuration file.
    """
    pass

class ConfigFileNotFound(ConfigError):
    """
    Raised when the configuration file is not found.
    """
    pass

class ConfigFileInvalid(ConfigError):
    """
    Raised when the configuration file is invalid.
    """
    pass
class ConfigMissingAttribute(ConfigError):
    """
    Raised when an atribute or key from configuration is missing
    """
    pass
class ConfigMismatchAttribute(ConfigError):
    """
    Raised when an atribute or key from configuration mismatchs
    """
    pass
class ConfigTypeMismatch(ConfigError):
    """
    Raised when an atribute or key from configuration mismatchs in type
    """
    pass
