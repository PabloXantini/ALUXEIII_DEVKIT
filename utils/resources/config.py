"""
utils/resources/config.py – Configuration file utilities.
"""
from __future__ import annotations
from pathlib import Path
from utils.logging import logger
from utils.resources.errors import (
    Result, 
    ConfigError, 
    ConfigMissingAttribute, 
    ConfigTypeMismatch
)

PROJECT_DIR = Path(__file__).parent.parent.parent

class ConfigNode:
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

class ConfigVisitor:
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
