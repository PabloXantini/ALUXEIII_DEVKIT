try:
    import RPi.GPIO as GPIO
except ImportError:
    from utils.mock import MockGPIO
    GPIO = MockGPIO()

import math

# ── Pines ────────────────────────────────────────────────────────────────────
M1_IN1, M1_IN2, M1_EN = 17, 27, 18   # Motor 1 – derecha
M2_IN1, M2_IN2, M2_EN = 22, 23, 19   # Motor 2 – arriba
M3_IN1, M3_IN2, M3_EN = 5,  6,  12   # Motor 3 – izquierda
M4_IN1, M4_IN2, M4_EN = 16, 20, 13   # Motor 4 – abajo

from utils.actuators import IMotorController
import utils.gpio as gpio


class MotorController4W(IMotorController):
    """Gestiona los cuatro motores omnidireccionales del robot vía GPIO/PWM."""

    def __init__(self, calib=None):
        """
        calib: Diccionario con factores de calibración por tipo de movimiento.
        Ejemplo: {"fwd": (1.0, 0.95, 1.0, 0.95), "turn_r": (0.8, 1.0, 0.8, 1.0)}
        """
        self.calib = {
            "fwd":    (1.0, 1.0, 1.0, 1.0),
            "bwd":    (1.0, 1.0, 1.0, 1.0),
            "left":   (1.0, 1.0, 1.0, 1.0),
            "right":  (1.0, 1.0, 1.0, 1.0),
            "turn_l": (1.0, 1.0, 1.0, 1.0),
            "turn_r": (1.0, 1.0, 1.0, 1.0)
        }
        if calib:
            self.calib.update(calib)

        gpio.init()

        self._pins = [
            M1_IN1, M1_IN2, M1_EN,
            M2_IN1, M2_IN2, M2_EN,
            M3_IN1, M3_IN2, M3_EN,
            M4_IN1, M4_IN2, M4_EN,
        ]
        for pin in self._pins:
            GPIO.setup(pin, GPIO.OUT)

        self.pwm1 = GPIO.PWM(M1_EN, 1000)
        self.pwm2 = GPIO.PWM(M2_EN, 1000)
        self.pwm3 = GPIO.PWM(M3_EN, 1000)
        self.pwm4 = GPIO.PWM(M4_EN, 1000)
        
        self.pwm1.start(0)
        self.pwm2.start(0)
        self.pwm3.start(0)
        self.pwm4.start(0)

    # ── Primitivas ────────────────────────────────────────────────────────────
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
        for pin in [M1_IN1, M1_IN2, M2_IN1, M2_IN2,
                    M3_IN1, M3_IN2, M4_IN1, M4_IN2]:
            GPIO.output(pin, GPIO.LOW)
        for pwm in (self.pwm1, self.pwm2, self.pwm3, self.pwm4):
            pwm.ChangeDutyCycle(0)

    def go_from_angle(self, angle: float, vel: float = None):
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

        self._apply(M1_IN1, M1_IN2, self.pwm1, w1)
        self._apply(M2_IN1, M2_IN2, self.pwm2, w2)
        self._apply(M3_IN1, M3_IN2, self.pwm3, w3)
        self._apply(M4_IN1, M4_IN2, self.pwm4, w4)

    def go_forward(self, vel=None):
        v = self._norm_vel(vel, self.HIGH)
        c = self.calib["fwd"]
        self._bwd(M1_IN1, M1_IN2, self.pwm1, v * c[0])
        self._fwd(M2_IN1, M2_IN2, self.pwm2, v * c[1])
        self._bwd(M3_IN1, M3_IN2, self.pwm3, v * c[2])
        self._fwd(M4_IN1, M4_IN2, self.pwm4, v * c[3])

    def go_backward(self, vel=None):
        v = self._norm_vel(vel, self.HIGH)
        c = self.calib["bwd"]
        self._fwd(M1_IN1, M1_IN2, self.pwm1, v * c[0])
        self._bwd(M2_IN1, M2_IN2, self.pwm2, v * c[1])
        self._fwd(M3_IN1, M3_IN2, self.pwm3, v * c[2])
        self._bwd(M4_IN1, M4_IN2, self.pwm4, v * c[3])

    def go_right(self, vel=None):
        v = self._norm_vel(vel, self.MEDIUM)
        c = self.calib["right"]
        self._fwd(M1_IN1, M1_IN2, self.pwm1, v * c[0])
        self._fwd(M2_IN1, M2_IN2, self.pwm2, v * c[1])
        self._fwd(M3_IN1, M3_IN2, self.pwm3, v * c[2])
        self._fwd(M4_IN1, M4_IN2, self.pwm4, v * c[3])

    def go_left(self, vel=None):
        v = self._norm_vel(vel, self.MEDIUM)
        c = self.calib["left"]
        self._bwd(M1_IN1, M1_IN2, self.pwm1, v * c[0])
        self._bwd(M2_IN1, M2_IN2, self.pwm2, v * c[1])
        self._bwd(M3_IN1, M3_IN2, self.pwm3, v * c[2])
        self._bwd(M4_IN1, M4_IN2, self.pwm4, v * c[3])

    def spin_right(self, vel=None):
        v = self._norm_vel(vel, self.MEDIUM)
        c = self.calib["turn_r"]
        self._fwd(M1_IN1, M1_IN2, self.pwm1, v * c[0])
        self._fwd(M2_IN1, M2_IN2, self.pwm2, v * c[1])
        self._bwd(M3_IN1, M3_IN2, self.pwm3, v * c[2])
        self._bwd(M4_IN1, M4_IN2, self.pwm4, v * c[3])

    def spin_left(self, vel=None):
        v = self._norm_vel(vel, self.MEDIUM)
        c = self.calib["turn_l"]
        self._bwd(M1_IN1, M1_IN2, self.pwm1, v * c[0])
        self._bwd(M2_IN1, M2_IN2, self.pwm2, v * c[1])
        self._fwd(M3_IN1, M3_IN2, self.pwm3, v * c[2])
        self._fwd(M4_IN1, M4_IN2, self.pwm4, v * c[3])

    def spin_slow_right(self):
        self.spin_right(vel=self.MID_LOW)

    def spin_slow_left(self):
        self.spin_left(vel=self.MID_LOW)

    # ── Limpieza ──────────────────────────────────────────────────────────────

    def cleanup(self):
        self.stop()
        for pwm in (self.pwm1, self.pwm2, self.pwm3, self.pwm4):
            pwm.stop()
        GPIO.cleanup()
