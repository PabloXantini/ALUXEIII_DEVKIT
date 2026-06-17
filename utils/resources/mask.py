from __future__ import annotations
from pathlib import Path
from utils.resources.errors import Result
from utils.resources.config import (
    ConfigVisitor,
    ConfigNode,
)
from utils.resources.errors import (
    ConfigFileNotFound,
    ConfigFileInvalid,
)
from utils.logging import logger
import json

class Mask(ConfigNode):
    __slots__ = ("label", "lower_bound", "upper_bound", "properties")
    def __init__(self, data:dict):
        res = self.check_attribute(data, "mask", str)
        self.label = res.value if res.issuccess else f"unknown_mask"
        res = self.check_attribute(data, "lower_bound", list)
        self.lower_bound = self._build_bound(res.value) if res.issuccess else (0, 0, 0)
        res = self.check_attribute(data, "upper_bound", list)
        self.upper_bound = self._build_bound(res.value) if res.issuccess else (255, 255, 255)
        self.properties = data.get("properties", {})

    def _build_bound(self, bound:list) -> tuple[int, int, int] | None:
        if len(bound) != 3:
            logger.warn(f"[{self.label}] Bound size mismatch")
            return None
        for i in range(3):
            if not isinstance(bound[i], int):
                logger.warn(f"[{self.label}] Bound type mismatch")
                return None
        return (bound[0], bound[1], bound[2])

class MaskVisitor(ConfigVisitor):
    def __init__(self) -> None:
        super().__init__()
        self.dispatch_table = {
            Mask: self._visit_mask
        }
    def _visit_mask(self, node:Mask) -> None:
        pass
        
def load_mask(dir:Path, file:str) -> Mask:
    """
    Load and validate the mask config for the given mask name.
    Args:
        **dir:** Mask directory where the file will be read.
        **mask:** Mask name.
        **workspace:** Workspace name.
    Returns:
        **Mask:** Mask configuration.
    Raises:
        **ConfigFileNotFound:** If the config file is not found.
        **ConfigFileInvalid:** If the config file is invalid.
    """
    file_path = dir / f"{file}.json"
    available = [f.stem for f in dir.glob("*.json")]
    if not file_path.exists():
        res = Result.fail(
            ConfigFileNotFound(
                f"[{file}] Config file not found: '{file_path}'.\n"
                f"Available masks: {available or ['(none)']}"
            )
        )
        logger.error(res.error)
        return None
    logger.msg(f"Reading mask '{file}' from {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        try:
            cfg = json.load(f)
        except json.JSONDecodeError as exc:
            raise ConfigFileInvalid(
                f"[{file}] Failed to parse JSON config file at '{file_path}'.\n"
                f"Error: {exc}"
            ) from exc
    mask_node = Mask(cfg)
    return mask_node
    
