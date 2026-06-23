from __future__ import annotations
from pathlib import Path
from utils.resources.mask import Mask
from utils.resources.config import (
    ConfigNode,
    ConfigVisitor,
)
from utils.resources.errors import (
    ConfigFileNotFound,
    ConfigFileInvalid,
)
from utils.logging import logger
import utils.resources.mask as mask
import json

class Workspace(ConfigNode):
    __slots__ = ("dir", "name", "mask_dir", "masks", "o_offset")
    def __init__(self, dir:str, cfg:dict, config_dir:Path = None):
        if config_dir is None:
            config_dir = dir
        self.dir = dir
        res = self.check_attribute(cfg, "workspace", str)
        self.name = res.value if res.issuccess else "unknown"
        res = self.check_attribute(cfg, "properties", dict)
        properties = res.value if res.issuccess else {}
        self._build_properties(properties, config_dir)

    def _build_properties(self, properties:dict, config_dir:Path) -> None:
        """Build properties from properties dictionary"""
        res = self.check_attribute(properties, "mask_dir", str)
        self.mask_dir:Path = config_dir / res.value if res.issuccess else ""
        res = self.check_attribute(properties, "masks", list)
        masks = res.value if res.issuccess else []
        self.masks = self._build_masks(masks, self.mask_dir)
        res = self.check_attribute(properties, "orientation", float)
        self.o_offset = res.value if res.issuccess else 0.0
        
    def _build_masks(self, masks:list, masks_dir:Path) -> dict[str, Mask]:
        masks_dict = {}
        final_dir = self.dir / masks_dir
        for mask_name in masks:
            new_mask = mask.load_mask(final_dir, mask_name)
            masks_dict[new_mask.label] = new_mask
        return masks_dict

class WorkspaceVisitor(ConfigVisitor):
    """Class with double dispatch that visits each ConfigNode"""
    def __init__(self) -> None:
        super().__init__()
        self.dispatch_table = {
            Workspace: self._visit_workspace,
            Mask: self._visit_mask
        }
    def _visit_workspace(self, node:Workspace) -> None:
        for mask in node.masks:
            mask.accept(self)
    def _visit_mask(self, node:Mask) -> None:
        pass

def load_workspace(dir:Path, workspace:str, config_dir:Path = None) -> Workspace:
    """
    Load and validate the hardware config for the given robot model name.
    Args:
        **dir:** Config directory where the file will be read.
        **workspace:** Robot workspace name.
    Returns:
        **WorkspaceNode:** Workspace configuration.
    Raises:
        **ConfigFileNotFound:** If the config file is not found.
        **ConfigFileInvalid:** If the config file is invalid.
    """
    file_path = dir / f"{workspace}.json"
    available = [f.stem for f in dir.glob("*.json")]
    if not file_path.exists():
        raise ConfigFileNotFound(
            f"[{workspace}] Config file not found: '{file_path}'.\n"
            f"Available workspaces: {available or ['(none)']}"
        )
    logger.msg(f"Reading workspace '{workspace}' from {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        try:
            cfg = json.load(f)
        except json.JSONDecodeError as exc:
            raise ConfigFileInvalid(
                f"[{workspace}] Failed to parse JSON config file at '{file_path}'.\n"
                f"Error: {exc}"
            ) from exc
    workspace_node = Workspace(dir, cfg, config_dir)
    return workspace_node



