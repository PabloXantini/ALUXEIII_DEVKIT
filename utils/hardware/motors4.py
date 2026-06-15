from __future__ import annotations

import math
from utils.resources.model import MotorNode
from utils.actuators import Speed
from .motorh import MotorH, MotorHController

class MotorController4W(MotorHController):
    """Gestiona los cuatro motores omnidireccionales del robot vía GPIO/PWM."""

    def __init__(self, config:list[MotorNode] | None = None, calib:dict | None = None) -> None:
        super().__init__(config, calib)
        self.m1 = MotorH(config[0])
        self.m2 = MotorH(config[1])
        self.m3 = MotorH(config[2])
        self.m4 = MotorH(config[3])

    def stop(self) -> None:
        self.m1.stop()
        self.m2.stop()
        self.m3.stop()
        self.m4.stop()
        
    def go_from_angle(self, 
        angle: float, 
        vel: float = None,
        calib_name:str = "default") -> None:
        """
        Move in an arbitrary direction using 4-wheel omnidirectional kinematics.
        angle: heading in degrees (0=forward, 90=right, 180=backward, 270=left).
        """
        c = self.calib[calib_name]
        rad = math.radians(angle)
        vx = vel * math.sin(rad)   # x component
        vy = vel * math.cos(rad)   # y component
        sqrt2_2 = 0.70710678

        # Standard 4-Omni wheel speed matrix (wheels at 45°, 135°, 225°, 315°)
        # w_k = vx * cos(rad) + vy * sin(rad) + w * R
        w1 = sqrt2_2*(vx + vy)
        w2 = sqrt2_2*(-vx + vy)
        w3 = sqrt2_2*(-vx - vy)
        w4 = sqrt2_2*(vx - vy)

        self.m1.run(w1, c[0])
        self.m2.run(w2, c[1])
        self.m3.run(w3, c[2])
        self.m4.run(w4, c[3])

    def go_forward(self, vel: float = Speed.DEFAULT.value) -> None:
        c = self.calib.get("fwd", self.CALIBRATION_DEFAULT)
        self.m1.run(vel, c[0])
        self.m2.run(vel, c[1])
        self.m3.run(-vel, c[2])
        self.m4.run(-vel, c[3])

    def go_backward(self, vel: float = Speed.DEFAULT.value) -> None:
        c = self.calib.get("bwd", self.CALIBRATION_DEFAULT)
        self.m1.run(-vel, c[0])
        self.m2.run(-vel, c[1])
        self.m3.run(vel, c[2])
        self.m4.run(vel, c[3])

    def go_right(self, vel: float = Speed.DEFAULT.value) -> None:
        c = self.calib["right"]
        self.m1.run(vel, c[0])
        self.m2.run(-vel, c[1])
        self.m3.run(vel, c[2])
        self.m4.run(-vel, c[3])

    def go_left(self, vel: float = Speed.DEFAULT.value) -> None:
        c = self.calib["left"]
        self.m1.run(-vel, c[0])
        self.m2.run(vel, c[1])
        self.m3.run(-vel, c[2])
        self.m4.run(vel, c[3])

    def spin_left(self, vel: float = Speed.DEFAULT.value) -> None:
        c = self.calib["turn_l"]
        self.m1.run(vel, c[0])
        self.m2.run(vel, c[1])
        self.m3.run(vel, c[2])
        self.m4.run(vel, c[3])

    def spin_right(self, vel: float = Speed.DEFAULT.value) -> None:
        c = self.calib["turn_r"]
        self.m1.run(-vel, c[0])
        self.m2.run(-vel, c[1])
        self.m3.run(-vel, c[2])
        self.m4.run(-vel, c[3])
