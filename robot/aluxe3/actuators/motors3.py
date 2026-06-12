try:
    import RPi.GPIO as GPIO
except ImportError:
    from utils.mock import MockGPIO
    GPIO = MockGPIO()

import math
from utils.actuators import IMotorController
import utils.gpio as gpio

# =======================================================
# PINES DE LOS MOTORES (Usando distribución M1, M3, M4)
# =======================================================
M1_IN1, M1_IN2, M1_EN = 17, 27, 18   # Delantera izquierda
M3_IN1, M3_IN2, M3_EN = 5,  6,  12   # Delantera derecha
M4_IN1, M4_IN2, M4_EN = 16, 20, 13   # Trasera

# Wheel angles for a standard 120° spaced 3-wheel omni configuration
_WHEEL_ANGLES_DEG = [0.0, 60.0, 120.0]



class MotorController3W(IMotorController):
    """Gestiona los tres motores omnidireccionales del robot vía GPIO/PWM."""

    def __init__(self, calib=None):
        """
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

        gpio.init()

        self._pins = [
            M1_IN1, M1_IN2, M1_EN,
            M3_IN1, M3_IN2, M3_EN,
            M4_IN1, M4_IN2, M4_EN,
        ]
        for pin in self._pins:
            GPIO.setup(pin, GPIO.OUT)

        self.pwm1 = GPIO.PWM(M1_EN, 1000)
        self.pwm2 = GPIO.PWM(M3_EN, 1000)
        self.pwm3 = GPIO.PWM(M4_EN, 1000)

        self.pwm1.start(0)
        self.pwm2.start(0)
        self.pwm3.start(0)

    def _fwd(self, in1, in2, pwm, vel):
        GPIO.output(in1, GPIO.HIGH)
        GPIO.output(in2, GPIO.LOW)
        pwm.ChangeDutyCycle(vel)

    def _bwd(self, in1, in2, pwm, vel):
        GPIO.output(in1, GPIO.LOW)
        GPIO.output(in2, GPIO.HIGH)
        pwm.ChangeDutyCycle(vel)
        
    def _apply(self, in1, in2, pwm, w):
        speed = abs(w)
        if w >= 0:
            self._fwd(in1, in2, pwm, speed)
        else:
            self._bwd(in1, in2, pwm, speed)

    # ── Movimientos compuestos ────────────────────────────────────────────────

    def stop(self):
        for pin in [M1_IN1, M1_IN2, M3_IN1, M3_IN2, M4_IN1, M4_IN2]:
            GPIO.output(pin, GPIO.LOW)
        for pwm in (self.pwm1, self.pwm2, self.pwm3):
            pwm.ChangeDutyCycle(0)

    def go_from_angle(self, angle: float, vel: float = None, default_max: float = None):
        """
        Move in an arbitrary direction using 3-wheel omnidirectional kinematics.
        """
        if default_max is None:
            default_max = self.HIGH
        v = self._norm_vel(vel, default_max)
        rad = math.radians(angle)
        vx = v * math.cos(rad) # x component
        vy = v * math.sin(rad) # y component
        sqrt3_2 = 0.8660254
        
        # Standard 3-Omni wheel speed matrix (wheels at 60°, 180°, 300°)
        w1 = 0.5 * vx + sqrt3_2 * vy
        w2 = -vx
        w3 = 0.5 * vx - sqrt3_2 * vy

        self._apply(M1_IN1, M1_IN2, self.pwm1, w1)
        self._apply(M3_IN1, M3_IN2, self.pwm2, w2)
        self._apply(M4_IN1, M4_IN2, self.pwm3, w3)

    def go_forward(self, vel=None):
        # self.go_from_angle(0, vel)
        v = self._norm_vel(vel, self.HIGH)
        self._bwd(M1_IN1, M1_IN2, self.pwm1, v)
        self._fwd(M3_IN1, M3_IN2, self.pwm2, v)
        # self._fwd(M4_IN1, M4_IN2, self.pwm3, v)

    def go_backward(self, vel=None):
        # self.go_from_angle(180, vel)
        v = self._norm_vel(vel, self.HIGH)
        self._fwd(M1_IN1, M1_IN2, self.pwm1, v)
        self._bwd(M3_IN1, M3_IN2, self.pwm2, v)
        # self._bwd(M4_IN1, M4_IN2, self.pwm3, v)

    def go_right(self, vel=None):
        # Native right direction at 60° for 3-wheel layout
        self.go_from_angle(0, vel, default_max=self.MEDIUM)

    def go_left(self, vel=None):
        # Native left direction at 300° for 3-wheel layout
        self.go_from_angle(180, vel, default_max=self.MEDIUM)

    def spin_right(self, vel=None):
        v = self._norm_vel(vel, self.MEDIUM)
        c = self.calib["turn_r"]
        self._bwd(M1_IN1, M1_IN2, self.pwm1, v * c[0])
        self._bwd(M3_IN1, M3_IN2, self.pwm2, v * c[1])
        self._bwd(M4_IN1, M4_IN2, self.pwm3, v * c[2])

    def spin_left(self, vel=None):
        v = self._norm_vel(vel, self.MEDIUM)
        c = self.calib["turn_l"]
        self._fwd(M1_IN1, M1_IN2, self.pwm1, v * c[0])
        self._fwd(M3_IN1, M3_IN2, self.pwm2, v * c[1])
        self._fwd(M4_IN1, M4_IN2, self.pwm3, v * c[2])

    def spin_slow_right(self):
        self.spin_right(vel=self.MID_LOW)

    def spin_slow_left(self):
        self.spin_left(vel=self.MID_LOW)

    def cleanup(self):
        self.stop()
        for pwm in (self.pwm1, self.pwm2, self.pwm3):
            pwm.stop()
        GPIO.cleanup()
