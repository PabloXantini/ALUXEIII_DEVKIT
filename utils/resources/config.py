"""
utils/resources/config.py – Configuration file utilities.
"""
from __future__ import annotations
from pathlib import Path
from abc import ABC, abstractmethod

PROJECT_DIR = Path(__file__).parent.parent.parent

class ConfigNode(ABC):
    __slots__ = ()
    def accept(self, visitor: ConfigVisitor):
        visitor.visit(self)

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

# Error Handling
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