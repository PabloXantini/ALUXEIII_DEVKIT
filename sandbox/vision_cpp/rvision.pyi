from enum import Enum
from typing import List
import numpy as np

class RenderType(Enum):
    CIRCLE: int
    RECT: int
    MESH: int
    CYLINDER: int

class Vec3:
    x: float
    y: float
    z: float
    def __init__(self, x: float, y: float, z: float) -> None: ...

class Vec4:
    r: float
    g: float
    b: float
    a: float
    def __init__(self, r: float, g: float, b: float, a: float) -> None: ...

class Vertex:
    x: float
    y: float
    z: float
    nx: float
    ny: float
    nz: float
    def __init__(self, x: float = 0, y: float = 0, z: float = 0, nx: float = 0, ny: float = 0, nz: float = 1) -> None: ...

class RenderObject:
    type: RenderType
    vertices: List[Vertex]
    position: Vec3
    size: Vec3
    color: Vec4
    def __init__(self) -> None: ...

class CameraState:
    x: float
    y: float
    z: float
    yaw: float
    pitch: float
    roll: float
    focal_length: float
    cx: int
    cy: int
    width: int
    height: int
    near_plane: float
    far_plane: float
    use_fisheye: bool
    use_motion_blur: bool
    def __init__(self) -> None: ...

class LightState:
    ambient: float
    diffuse: float
    position: Vec3
    def __init__(self) -> None: ...

class Renderer:
    def __init__(self, width: int, height: int) -> None: ...
    def initialize(self) -> bool: ...
    def render(self, camera: CameraState, objects: List[RenderObject]) -> None: ...
    def set_light(self, light: LightState) -> None: ...
    def set_fisheye(self, k: float = -0.4, zoom: float = 1.0) -> None: ...
    def set_motion_blur(self, strength: float = 0.5, samples: int = 3) -> None: ...
    def get_frame(self) -> np.ndarray: ...
