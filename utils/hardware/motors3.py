from __future__ import annotations

import math
from utils.resources.model import MotorNode
from utils.components import Speed
from .motorh import MotorH, OmniMotorHController

class OmniMotorHController3W(OmniMotorHController):
    """Gestiona los tres motores omnidireccionales del robot vía GPIO/PWM."""
    MOTOR_COUNT = 3
    CALIBRATION_DEFAULT = (1.0, 1.0, 1.0)
    def __init__(self, config:list[MotorNode], calib:dict = {}) -> None:
        super().__init__(config, calib)
        self.radius = 0.18 # m
        self.m1 = MotorH(config[0])
        self.m2 = MotorH(config[1])
        self.m3 = MotorH(config[2])

    def stop(self) -> None:
        self.m1.stop()
        self.m2.stop()
        self.m3.stop()

    def go_from_angle(self, 
        angle:float,
        vel:float = Speed.DEFAULT.value,
        w:float = 0.0,
        calib:tuple[float, float, float] = (1.0, 1.0, 1.0)) -> None:
        """
        Move in an arbitrary direction using 3-wheel omnidirectional kinematics.
        """
        if self.active_control:
            vel = self.active_control.calculate(setpoint=angle)
        rad = math.radians(angle)
        vx = vel * math.cos(rad) # x component
        vy = vel * math.sin(rad) # y component
        vw = w * self.radius
        sqrt3_2 = 0.8660254

        # Standard 3-Omni wheel speed matrix (wheels at 60°, 180°, 300°)
        # w_k = vx * cos(rad) + vy * sin(rad) + vw
        # Where vw = w * R (w = angular velocity, R = radius of the wheel base)
        
        w1 = sqrt3_2 * vx + 0.5 * vy + vw
        w2 = vy + vw
        w3 = -sqrt3_2 * vx - 0.5 * vy + vw

        self.m1.run(w1, calib[0])
        self.m2.run(w2, calib[1])
        self.m3.run(w3, calib[2])

    def go_forward(self, vel: float = Speed.DEFAULT.value) -> None:
        c = self.calib.get("fwd", self.CALIBRATION_DEFAULT)
        self.m1.run(vel, c[0])
        self.m2.last_vel = 0.0
        self.m3.run(-vel, c[2])

    def go_backward(self, vel: float = Speed.DEFAULT.value) -> None:
        c = self.calib.get("bwd", self.CALIBRATION_DEFAULT)
        self.m1.run(-vel, c[0])
        self.m2.last_vel = 0.0
        self.m3.run(vel, c[2])

    def go_left(self, vel: float = Speed.DEFAULT.value) -> None:
        c = self.calib.get("left", self.CALIBRATION_DEFAULT)
        self.go_from_angle(angle=90, vel=vel, calib=c)

    def go_right(self, vel: float = Speed.DEFAULT.value) -> None:
        c = self.calib.get("right", self.CALIBRATION_DEFAULT)
        self.go_from_angle(angle=270, vel=vel, calib=c)

    def spin_left(self, vel: float = Speed.DEFAULT.value) -> None:
        c = self.calib.get("turn_l", self.CALIBRATION_DEFAULT)
        self.m1.run(vel, c[0])
        self.m2.run(vel, c[1])
        self.m3.run(vel, c[2])

    def spin_right(self, vel: float = Speed.DEFAULT.value) -> None:
        c = self.calib.get("turn_r", self.CALIBRATION_DEFAULT)
        self.m1.run(-vel, c[0])  
        self.m2.run(-vel, c[1])
        self.m3.run(-vel, c[2])

    def get_speeds(self) -> str:
        return f"""
        error: {self.active_control.last_e:.2f}
        w1: {self.m1.last_vel:.2f}
        w2: {self.m2.last_vel:.2f}
        w3: {self.m3.last_vel:.2f}"""
