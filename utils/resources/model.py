from __future__ import annotations
from pathlib import Path
from utils.resources.config import (
    ConfigNode,
    ConfigVisitor,
)
from utils.resources.errors import (
    ConfigFileNotFound,
    ConfigFileInvalid,
)
from utils.logging import logger
import json

class PropertiesConfigNode(ConfigNode):
    __slots__ = ("label", "properties")
    def __init__(self, label:str, model:str, data:dict) -> None:
        self.label = label
        self.model = model
        res = self.check_attribute(data, "properties", dict)
        self.properties = res.value if res.issuccess else {}
        
class CameraNode(PropertiesConfigNode):
    __slots__ = ("label", "model", "type", "properties")
    def __init__(self, label:str, model:str, data:dict) -> None:
        super().__init__(label, model, data)
        res = self.check_attribute(data, "type", str)
        self.type = res.value if res.issuccess else "default"

class MotorNode(PropertiesConfigNode):
    __slots__ = ("label", "model", "properties")
    def __init__(self, label:str, model:str, data:dict) -> None:
        super().__init__(label, model, data)

class MotorConfigNode(ConfigNode):
    __slots__ = ("label", "model", "type", "motors", "calibration")
    def __init__(self, label:str, model:str, data:dict) -> None:
        self.label = label
        self.model = model
        res = self.check_attribute(data, "type", str)
        self.type = res.value if res.issuccess else "default"
        res = self.check_attribute(data, "config", list)
        self.motors = self._build_motors(res.value) if res.issuccess else []
        res = self.check_attribute(data, "calibration", dict)
        self.calibration = self._build_calibration(res.value) if res.issuccess else {}

    def _build_motors(self, data:list) -> list[MotorNode]:
        motors = []
        if len(data) == 0: logger.warn(f"[Motor ({self.model}:{self.label})] No motors found")
        for motor_data in data:
            motors.append(MotorNode(motor_data["label"], self.model, motor_data))
        return motors

    def _build_calibration(self, data:dict) -> dict[str, tuple[float, ...]]:
        calibration = {}
        for label, content in data.items():
            f = tuple(content)
            if len(self.motors) != len(f):
                logger.warn(f"[Motor ({self.model}:{self.label})] Calibration data size mismatch")
                continue
            f = self._validate_calibration(f)
            if f is None:
                continue
            calibration[label] = f
        return calibration
    def _validate_calibration(self, value:tuple) -> tuple[float, ...] | None:
        f = []
        for v in value:
            if not isinstance(v, float):
                logger.warn(f"[Motor ({self.model}:{self.label})] Calibration data type mismatch")
                return None
            f.append(v)
        return tuple(f)
    
class UltrasonicNode(PropertiesConfigNode):
    __slots__ = ("label", "model", "type", "properties")
    def __init__(self, label:str, model:str, data:dict) -> None:
        super().__init__(label, model, data)
        res = self.check_attribute(data, "type", str)
        self.type = res.value if res.issuccess else "default"

class CompassNode(PropertiesConfigNode):
    __slots__ = ("label", "model", "type", "properties")
    def __init__(self, label:str, model:str, data:dict) -> None:
        super().__init__(label, model, data)
        res = self.check_attribute(data, "type", str)
        self.type = res.value if res.issuccess else "default"

class Model(ConfigNode):
    __slots__ = ("name", "l_components")
    def __init__(self, cfg:dict):
        res = self.check_attribute(cfg, "model", str)
        self.name = res.value if res.issuccess else "default"
        self.l_components:list[ConfigNode] = []
        self._build(cfg)

    def _build(self, cfg:dict) -> None:
        res = self.check_attribute(cfg, "components", dict)
        components = res.value if res.issuccess else {}
        self._read_component(components, "cameras")
        self._read_component(components, "motors")
        self._read_component(components, "ultrasonics")
        self._read_component(components, "compasses")

    def _read_component(self, data:dict, comp_type:str) -> None:
        res = self.check_attribute(data, comp_type, list)
        if not res.issuccess:
            return
        for comp in res.value:
            res = self.check_attribute(comp, "label", str)
            label = res.value if res.issuccess else f"unknown_{comp_type}"
            if comp_type == "cameras":
                self.l_components.append(CameraNode(label, self.name, comp))
            elif comp_type == "motors":
                self.l_components.append(MotorConfigNode(label, self.name, comp))
            elif comp_type == "ultrasonics":
                self.l_components.append(UltrasonicNode(label, self.name, comp))
            elif comp_type == "compasses":
                self.l_components.append(CompassNode(label, self.name, comp))

class ModelVisitor(ConfigVisitor):
    """Class with double dispatch that visits each ConfigNode"""
    def __init__(self) -> None:
        super().__init__()
        self.dispatch_table = {
            Model: self._visit_model,
            CameraNode: self._visit_camera,
            MotorConfigNode: self._visit_motor_config,
            MotorNode: self._visit_motor,
            UltrasonicNode: self._visit_ultrasonic,
            CompassNode: self._visit_compass
        }
    def _visit_model(self, node:Model) -> None:
        for component in node.l_components:
            component.accept(self)
    def _visit_camera(self, node:CameraNode) -> None:
        pass
    def _visit_motor_config(self, node:MotorConfigNode) -> None:
        pass
    def _visit_motor(self, node:MotorNode) -> None:
        pass
    def _visit_ultrasonic(self, node:UltrasonicNode) -> None:
        pass
    def _visit_compass(self, node: CompassNode) -> None:
        pass

def load_model(dir:Path, model:str) -> Model:
    """
    Load and validate the hardware config for the given robot model name.
    Args:
        **dir:** Config directory where the file will be read.
        **model:** Config filename without extension (e.g. 'alux3w').
    Returns:
        Parsed config dict.
    Raises:
        **ConfigFileNotFound**: If the config file is not found.
        **ConfigFileInvalid**: If the config file is invalid.
    """
    file_path = dir / f"{model}.json"
    if not file_path.exists():
        available = [f.stem for f in dir.glob("*.json")]
        raise ConfigFileNotFound(
            f"[{model}] Config file not found: '{file_path}'.\n"
            f"Available models: {available or ['(none)']}"
        )
    logger.msg(f"Reading model '{model}' from {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        try:
            cfg = json.load(f)
        except json.JSONDecodeError as exc:
            raise ConfigFileInvalid(
                f"[{model}] Failed to parse JSON config file at '{file_path}'.\n"
                f"Error: {exc}"
            ) from exc
    model_node = Model(cfg)
    return model_node
