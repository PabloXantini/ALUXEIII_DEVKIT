from __future__ import annotations
from pathlib import Path
from utils.resources.config import (
    ConfigNode,
    ConfigVisitor,
    ConfigMissingAttribute,
    ConfigMismatchAttribute,
    ConfigFileInvalid,
    ConfigFileNotFound
)
from utils.logging import logger
import json

class MotorNode(ConfigNode):
    __slots__ = ("label", "model", "raw_data", "properties")
    def __init__(self, label:str, model:str, data:dict) -> None:
        self.label = label
        self.model = model
        self.raw_data = data
        self.properties = data.get("properties", {})

class MotorConfigNode(ConfigNode):
    __slots__ = ("label", "model", "raw_data", "type", "motors", "calibration")
    def __init__(self, label:str, model:str, data:dict) -> None:
        self.label = label
        self.model = model
        self.raw_data = data
        self.type = data.get("type", "default")
        self.motors = self._build_motors(data.get("config", []))
        self.calibration = self._build_calibration(data.get("calibration", {}))
        
    def _build_motors(self, data:list) -> list[MotorNode]:
        motors = []
        if not data:
            logger.warn(f"Motors has not been specified ({self.model}:{self.label})")
            return motors
        for motor_data in data:
            motors.append(MotorNode(motor_data["label"], self.model, motor_data))
        return motors

    def _build_calibration(self, data:dict) -> dict[str, tuple[float, ...]]:
        if not data:
            return {}
        calibration = {}
        for label, content in data.items():
            f_content = tuple(content)
            if len(f_content) != len(self.motors):
                raise ConfigMismatchAttribute(
                    f"[Model ({self.model}): {self.label}] Calibration Attributes do not match with the specified number of motors"
                )
            calibration[label] = f_content
        return calibration
            
class UltrasonicNode(ConfigNode):
    __slots__ = ("label", "model", "raw_data", "type", "properties")
    def __init__(self, label:str, model:str, data:dict) -> None:
        self.label = label
        self.model = model
        self.raw_data = data
        self.type = data.get("type", "default")
        self.properties = data.get("properties", {})

class CompassNode(ConfigNode):
    __slots__ = ("label", "model", "raw_data", "type", "properties")
    def __init__(self, label:str, model:str, data:dict) -> None:
        self.label = label
        self.model = model
        self.raw_data = data
        self.type = data.get("type", "default")
        self.properties = data.get("properties", {})

class ModelNode(ConfigNode):
    __slots__ = ("name", "l_components")
    def __init__(self, name:str, cfg:dict):
        self.name = name
        self.l_components:list[ConfigNode] = []
        self._build(cfg)

    def _build(self, cfg:dict) -> None:
        components = cfg.get("components", {})
        self._read_component(components, "motors")
        self._read_component(components, "ultrasonics")
        self._read_component(components, "compasses")

    def _read_component(self, data:dict, comp_type:str) -> None:
        comp_data = data.get(comp_type, [])
        for comp in comp_data:
            data = dict(comp)
            label = data.get("label", f"unknown_{comp_type}")
            if comp_type == "motors":
                self.l_components.append(MotorConfigNode(label, self.name, data))
            elif comp_type == "ultrasonics":
                self.l_components.append(UltrasonicNode(label, self.name, data))
            elif comp_type == "compasses":
                self.l_components.append(CompassNode(label, self.name, data))

class ModelVisitor(ConfigVisitor):
    """Class with double dispatch that visits each ConfigNode"""
    def __init__(self) -> None:
        super().__init__()
        self.dispatch_table = {
            ModelNode: self._visit_model,
            MotorConfigNode: self._visit_motor_config,
            MotorNode: self._visit_motor,
            UltrasonicNode: self._visit_ultrasonic,
            CompassNode: self._visit_compass
        }
    def _visit_model(self, node:ModelNode) -> None:
        if not node.name:
            raise ConfigMissingAttribute("[Model] Model name is required")
        for component in node.l_components:
            component.accept(self)
    def _visit_motor_config(self, node:MotorConfigNode) -> None:
        pass
    def _visit_motor(self, node:MotorNode) -> None:
        pass
    def _visit_ultrasonic(self, node:UltrasonicNode) -> None:
        pass
    def _visit_compass(self, node: CompassNode) -> None:
        pass

class ConfigModelValidator(ModelVisitor):
    """Validates the configuration of each component."""
    def __init__(self):
        super().__init__()    
    def _visit_motor_config(self, node:MotorConfigNode) -> None:
        if ("type" not in node.raw_data) or ("config" not in node.raw_data):
            raise ConfigMissingAttribute(
                f"[Model ({node.model}): {node.label}] Missing required attributes in motors config"
            )            
    def _visit_ultrasonic(self, node:UltrasonicNode) -> None:
        if ("type" not in node.raw_data) or ("properties" not in node.raw_data):
            raise ConfigMissingAttribute(
                f"[Model ({node.model}): {node.label}] Missing required attributes in ultrasonic config"
            )
    def _visit_compass(self, node:CompassNode) -> None:
        if ("type" not in node.raw_data) or ("properties" not in node.raw_data):
            raise ConfigMissingAttribute(
                f"[Model ({node.model}): {node.label}] Missing required attributes in compass config"
            )
def load_model(dir:Path, model:str) -> ModelNode:
    """
    Load and validate the hardware config for the given robot model name.
    Args:
        **dir:** Config directory where the file will be read.
        **model:** Config filename without extension (e.g. 'alux3w').
    Returns:
        Parsed config dict.
    Raises:
        **ConfigError**: If the file does not exist or fails validation.
    """
    file_path = dir / f"{model}.json"
    if not file_path.exists():
        available = [f.stem for f in dir.glob("*.json")]
        raise ConfigFileNotFound(
            f"[{model}] Config file not found: '{file_path}'.\n"
            f"Available models: {available or ['(none)']}"
        )
    with open(file_path, "r", encoding="utf-8") as f:
        try:
            cfg = json.load(f)
        except json.JSONDecodeError as exc:
            raise ConfigFileInvalid(
                f"[{model}] Config file is not valid JSON: {exc}"
            ) from exc
    model_node = ModelNode(model, cfg)
    validator = ConfigModelValidator()
    model_node.accept(validator)
    return model_node
