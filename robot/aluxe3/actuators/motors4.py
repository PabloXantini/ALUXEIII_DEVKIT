from __future__ import annotations

try:
    import RPi.GPIO as GPIO
except ImportError:
    from utils.mock import MockGPIO
    GPIO = MockGPIO()

import math
from utils.actuators import IMotorController
from utils.config_loader import ROBOT_CONFIG
import utils.gpio as gpio


class MotorController4W(IMotorController):
    """Gestiona los cuatro motores omnidireccionales del robot vía GPIO/PWM."""

    def __init__(self, pins: dict | None = None, calib: dict | None = None) -> None:
        """
        pins: Diccionario con la configuración de pines para cada motor.
        calib: Diccionario con factores de calibración por tipo de movimiento.
        Ejemplo: {"fwd": (1.0, 0.95, 1.0, 0.95), "turn_r": (0.8, 1.0, 0.8, 1.0)}
        """
        super().__init__()
        self.calib = {
            "fwd":    (1.0, 1.0, 1.0, 1.0),
            "bwd":    (1.0, 1.0, 1.0, 1.0),
            "left":   (1.0, 1.0, 1.0, 1.0),
            "right":  (1.0, 1.0, 1.0, 1.0),
            "turn_l": (1.0, 1.0, 1.0, 1.0),
            "turn_r": (1.0, 1.0, 1.0, 1.0)
        }
        if pins is None:
            pins = ROBOT_CONFIG["motors"]

        self._motor_configs = list(pins.values())
        self._validate_pins(self._motor_configs, 4)

        gpio.init()

        for motor in self._motor_configs:
            GPIO.setup(motor["in1"], GPIO.OUT)
            GPIO.setup(motor["in2"], GPIO.OUT)
            GPIO.setup(motor["en"],  GPIO.OUT)
            motor["pwm"] = GPIO.PWM(motor["en"], 1000)
            motor["c"] = motor.get("c", 1.0)

        for motor in self._motor_configs:
            motor["pwm"].start(0)

    def _validate_pins(self, configs: list[dict], expected_count: int) -> None:
        """Validar que los pines estén configurados correctamente."""
        if len(configs) < expected_count:
            from utils.config_loader import ConfigError
            raise ConfigError(f"Expected at least {expected_count} motor configurations, got {len(configs)}")
        REQUIRED_KEYS = {"in1", "in2", "en"}
        for idx, m_cfg in enumerate(configs[:expected_count]):
            if not REQUIRED_KEYS.issubset(m_cfg.keys()):
                from utils.config_loader import ConfigError
                raise ConfigError(f"Motor configuration at index {idx} is missing keys: {m_cfg.keys()}")

    # ── Primitivas ────────────────────────────────────────────────────────────
    def _set_motor(self, motor: dict, speed: float) -> None:
        """Establecer la velocidad de un motor."""
        val = speed * motor["c"]
        if val >= 0:
            self._fwd(motor["in1"], motor["in2"], motor["pwm"], val)
        else:
            self._bwd(motor["in1"], motor["in2"], motor["pwm"], abs(val))

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

    def go_from_angle(self, angle: float, vel: float = None) -> None:
        """
        Move in an arbitrary direction using 4-wheel omnidirectional kinematics.
        angle: heading in degrees (0=forward, 90=right, 180=backward, 270=left).
        """
        v = self._norm_vel(vel, self.HIGH)
        rad = math.radians(angle)
        vx = v * math.sin(rad)   # x component
        vy = v * math.cos(rad)   # y component

        # Standard 4-Omni wheel speed matrix (wheels at 45°, 135°, 225°, 315°)
        w1 = vy - vx
        w2 = vy + vx
        w3 = vy - vx
        w4 = vy + vx

        self._set_motor(self._motor_configs[0], w1)
        self._set_motor(self._motor_configs[1], w2)
        self._set_motor(self._motor_configs[2], w3)
        self._set_motor(self._motor_configs[3], w4)

    def go_forward(self, vel: float = None) -> None:
        v = self._norm_vel(vel, self.HIGH)
        c = self.calib["fwd"]
        self._set_motor(self._motor_configs[0], -v * c[0])
        self._set_motor(self._motor_configs[1], v * c[1])
        self._set_motor(self._motor_configs[2], -v * c[2])
        self._set_motor(self._motor_configs[3], v * c[3])

    def go_backward(self, vel: float = None) -> None:
        v = self._norm_vel(vel, self.HIGH)
        c = self.calib["bwd"]
        self._set_motor(self._motor_configs[0], v * c[0])
        self._set_motor(self._motor_configs[1], -v * c[1])
        self._set_motor(self._motor_configs[2], v * c[2])
        self._set_motor(self._motor_configs[3], -v * c[3])

    def go_right(self, vel: float = None) -> None:
        v = self._norm_vel(vel, self.MEDIUM)
        c = self.calib["right"]
        self._set_motor(self._motor_configs[0], v * c[0])
        self._set_motor(self._motor_configs[1], v * c[1])
        self._set_motor(self._motor_configs[2], v * c[2])
        self._set_motor(self._motor_configs[3], v * c[3])

    def go_left(self, vel: float = None) -> None:
        v = self._norm_vel(vel, self.MEDIUM)
        c = self.calib["left"]
        self._set_motor(self._motor_configs[0], -v * c[0])
        self._set_motor(self._motor_configs[1], -v * c[1])
        self._set_motor(self._motor_configs[2], -v * c[2])
        self._set_motor(self._motor_configs[3], -v * c[3])

    def spin_right(self, vel: float = None) -> None:
        v = self._norm_vel(vel, self.MEDIUM)
        c = self.calib["turn_r"]
        self._set_motor(self._motor_configs[0], v * c[0])
        self._set_motor(self._motor_configs[1], v * c[1])
        self._set_motor(self._motor_configs[2], -v * c[2])
        self._set_motor(self._motor_configs[3], -v * c[3])

    def spin_left(self, vel: float = None) -> None:
        v = self._norm_vel(vel, self.MEDIUM)
        c = self.calib["turn_l"]
        self._set_motor(self._motor_configs[0], -v * c[0])
        self._set_motor(self._motor_configs[1], -v * c[1])
        self._set_motor(self._motor_configs[2], v * c[2])
        self._set_motor(self._motor_configs[3], v * c[3])

    def spin_slow_right(self) -> None:
        self.spin_right(vel=self.MID_LOW)

    def spin_slow_left(self) -> None:
        self.spin_left(vel=self.MID_LOW)

    # ── Limpieza ──────────────────────────────────────────────────────────────

    def cleanup(self) -> None:
        self.stop()
        for motor in self._motor_configs:
            motor["pwm"].stop()
        GPIO.cleanup()
