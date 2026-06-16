from __future__ import annotations
from pathlib import Path
from utils.resources import workspace
from utils.resources.config import (
    ConfigVisitor,
    ConfigNode,
    ConfigFileNotFound,
    ConfigFileInvalid,
)
from utils.logging import logger
import json

class MaskNode(ConfigNode):
    __slots__ = ("label", "workspace", "lower_bound", "upper_bound")
    def __init__(self, workspace:str, data:dict):
        res = self.check_attribute(data, "mask", str)
        self.label = res.value if res.issuccess else f"unknown_mask"
        self.workspace = workspace
        res = self.check_attribute(data, "lower_bound", tuple)
        self.lower_bound = res.value if res.issuccess else (0, 0, 0)
        res = self.check_attribute(data, "upper_bound", tuple)
        self.upper_bound = res.value if res.issuccess else (255, 255, 255)

class MaskVisitor(ConfigVisitor):
    def __init__(self) -> None:
        super().__init__()
        self.dispatch_table = {
            MaskNode: self._visit_mask
        }
    def _visit_mask(self, node:MaskNode) -> None:
        pass
        
def load_mask(dir:Path, file:str, workspace:str = "none") -> MaskNode:
    """
    Load and validate the mask config for the given mask name.
    Args:
        **dir:** Mask directory where the file will be read.
        **mask:** Mask name.
        **workspace:** Workspace name.
    Returns:
        **MaskNode:** Mask configuration.
    Raises:
        **ConfigFileNotFound:** If the config file is not found.
        **ConfigFileInvalid:** If the config file is invalid.
    """
    file_path = dir / f"{file}.json"
    available = [f.stem for f in dir.glob("*.json")]
    if not file_path.exists():
        raise ConfigFileNotFound(
            f"[{file}] Config file not found: '{file_path}'.\n"
            f"Available masks: {available or ['(none)']}"
        )
    logger.msg(f"Reading mask {file} config from {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        try:
            cfg = json.load(f)
        except json.JSONDecodeError as exc:
            raise ConfigFileInvalid(
                f"[{file}] Failed to parse JSON config file at '{file_path}'.\n"
                f"Error: {exc}"
            ) from exc
    mask_node = MaskNode(workspace, cfg)
    return mask_node
    
