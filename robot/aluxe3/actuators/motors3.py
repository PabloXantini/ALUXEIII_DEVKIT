from __future__ import annotations

try:
    import RPi.GPIO as GPIO
except ImportError:
    from utils.mock import MockGPIO
    GPIO = MockGPIO()

import math
from utils.actuators import IMotorController
from utils.config_loader import ROBOT_CONFIG, ConfigError
import utils.gpio as gpio

class MotorController3W(IMotorController):
    """Gestiona los tres motores omnidireccionales del robot vía GPIO/PWM."""

    def __init__(self, pins: dict | None = None, calib: dict | None = None) -> None:
        """
        pins: Diccionario con la configuración de pines para cada motor.
        calib: Diccionario con factores de calibración por tipo de movimiento.
        Ejemplo: {"fwd": (1.0, 0.85, 1.0)}
        """
        self.calib = {
            "fwd":    (1.0, 1.0, 1.0),
            "bwd":    (1.0, 1.0, 1.0),
            "left":   (1.0, 1.0, 1.0),
            "right":  (1.0, 1.0, 1.0),
            "turn_l": (1.0, 1.0, 1.0),
            "turn_r": (1.0, 1.0, 1.0)
        }
        if calib:
            self.calib.update(calib)

        if pins is None:
            pins = ROBOT_CONFIG["motors"]

        self._motor_configs = list(pins.values())
        self._validate_pins(self._motor_configs, 3)

        gpio.init()

        for motor in self._motor_configs:
            GPIO.setup(motor["in1"], GPIO.OUT)
            GPIO.setup(motor["in2"], GPIO.OUT)
            GPIO.setup(motor["en"],  GPIO.OUT)
            motor["pwm"] = GPIO.PWM(motor["en"], 1000)

        for motor in self._motor_configs:
            motor["pwm"].start(0)

    def _validate_pins(self, configs: list[dict], expected_count: int) -> None:
        """Validar que los pines estén configurados correctamente."""
        if len(configs) < expected_count:
            raise ConfigError(f"Expected at least {expected_count} motor configurations, got {len(configs)}")
        REQUIRED_KEYS = {"in1", "in2", "en"}
        for idx, m_cfg in enumerate(configs[:expected_count]):
            if not REQUIRED_KEYS.issubset(m_cfg.keys()):
                raise ConfigError(f"Motor configuration at index {idx} is missing keys: {m_cfg.keys()}")

    def _set_motor(self, motor: dict, speed: float) -> None:
        """Establecer la velocidad de un motor."""
        if speed >= 0:
            self._fwd(motor["in1"], motor["in2"], motor["pwm"], speed)
        else:
            self._bwd(motor["in1"], motor["in2"], motor["pwm"], abs(speed))

    def _fwd(self, in1: int, in2: int, pwm: GPIO.PWM, vel: float) -> None:
        GPIO.output(in1, GPIO.HIGH)
        GPIO.output(in2, GPIO.LOW)
        pwm.ChangeDutyCycle(vel)

    def _bwd(self, in1: int, in2: int, pwm: GPIO.PWM, vel: float) -> None:
        GPIO.output(in1, GPIO.LOW)
        GPIO.output(in2, GPIO.HIGH)
        pwm.ChangeDutyCycle(vel)

    def stop(self) -> None:
        for motor in self._motor_configs:
            GPIO.output(motor["in1"], GPIO.LOW)
            GPIO.output(motor["in2"], GPIO.LOW)
            motor["pwm"].ChangeDutyCycle(0)

    def go_from_angle(self, 
        angle: float, 
        vel: float = None, 
        default_max: float = None, 
        calib: dict | None = None) -> None:
        """
        Move in an arbitrary direction using 3-wheel omnidirectional kinematics.
        """
        if default_max is None:
            default_max = self.HIGH
        v = self.norm_vel(vel, default_max)
        rad = math.radians(angle)
        vx = v * math.cos(rad) # x component
        vy = v * math.sin(rad) # y component
        sqrt3_2 = 0.8660254
        
        # Standard 3-Omni wheel speed matrix (wheels at 60°, 180°, 300°)
        w1 = 0.5 * vx + sqrt3_2 * vy
        w2 = -vx
        w3 = 0.5 * vx - sqrt3_2 * vy

        if calib:
            w1 *= calib[0]
            w2 *= calib[1]
            w3 *= calib[2]

        self._set_motor(self._motor_configs[0], w1)
        self._set_motor(self._motor_configs[1], w2)
        self._set_motor(self._motor_configs[2], w3)

    def go_forward(self, vel: float = None) -> None:
        v = self.norm_vel(vel, self.HIGH)
        self._set_motor(self._motor_configs[0], -v)
        self._set_motor(self._motor_configs[1], v)

    def go_backward(self, vel: float = None) -> None:
        v = self.norm_vel(vel, self.HIGH)
        self._set_motor(self._motor_configs[0], v)
        self._set_motor(self._motor_configs[1], -v)

    def go_right(self, vel: float = None) -> None:
        self.go_from_angle(0, vel, default_max=self.MEDIUM, calib=self.calib['right'])

    def go_left(self, vel: float = None) -> None:
        self.go_from_angle(180, vel, default_max=self.MEDIUM, calib=self.calib['left'])

    def spin_right(self, vel: float = None) -> None:
        v = self.norm_vel(vel, self.MEDIUM)
        c = self.calib['turn_r']
        self._set_motor(self._motor_configs[0], v * c[0])
        self._set_motor(self._motor_configs[1], v * c[1])
        self._set_motor(self._motor_configs[2], v * c[2])

    def spin_left(self, vel: float = None) -> None:
        v = self.norm_vel(vel, self.MEDIUM)
        c = self.calib['turn_l']
        self._set_motor(self._motor_configs[0], -v * c[0])
        self._set_motor(self._motor_configs[1], -v * c[1])
        self._set_motor(self._motor_configs[2], -v * c[2])

    def spin_slow_right(self) -> None:
        self.spin_right(vel=self.MID_LOW)

    def spin_slow_left(self) -> None:
        self.spin_left(vel=self.MID_LOW)

    def cleanup(self) -> None:
        self.stop()
        for motor in self._motor_configs:
            motor["pwm"].stop()
        GPIO.cleanup()
