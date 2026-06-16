"""
utils/resources/config.py – Configuration file utilities.
"""
from __future__ import annotations
from typing import Generic, TypeVar
from pathlib import Path
from abc import ABC, abstractmethod
from utils.logging import logger

PROJECT_DIR = Path(__file__).parent.parent.parent

class ConfigNode(ABC):
    __slots__ = ()
    def accept(self, visitor: ConfigVisitor):
        visitor.visit(self)
    def check_attribute(self, data:dict, attribute:str, type:type) -> Result[bool, ConfigError]:
        if attribute not in data:
            msg = f"Missing '{attribute}' attribute"
            res = Result.fail(ConfigMissingAttribute(msg))
            logger.warn(res.error.args[0])
            return res
        if not isinstance(data[attribute], type):
            msg = f"'{attribute}' must be a {type.__name__}"
            res = Result.fail(ConfigTypeMismatch(msg))
            logger.warn(res.error.args[0])
            return res
        return Result.success(data[attribute])

class ConfigVisitor(ABC):
    def __init__(self) -> None:
        self.dispatch_table = {}

    def visit(self, node: ConfigNode) -> None:
        if node is None:
            return
        handler = self.dispatch_table.get(type(node))
        if handler is not None:
            handler(node)
        else:
            self.visit_default(node)

    def visit_default(self, node: ConfigNode) -> None:
        pass

class ConfigAttributeNode(ConfigNode):
    __slots__ = ("label", "model", "raw_data")
    def __init__(self, label: str, model: str, raw_data: dict) -> None:
        self.label = label
        self.model = model
        self.raw_data = raw_data

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
