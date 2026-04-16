import RPi.GPIO as GPIO


# ── Pines ────────────────────────────────────────────────────────────────────
M1_IN1, M1_IN2, M1_EN = 17, 27, 18   # Motor 1 – derecha
M2_IN1, M2_IN2, M2_EN = 22, 23, 19   # Motor 2 – arriba
M3_IN1, M3_IN2, M3_EN = 5,  6,  12   # Motor 3 – izquierda
M4_IN1, M4_IN2, M4_EN = 16, 20, 13   # Motor 4 – abajo

class MotorController:
    """Gestiona los cuatro motores del robot vía GPIO/PWM."""

    # Velocidades por defecto (duty-cycle %)
    DEFAULT_VEL  = 80
    TURN_VEL     = 50
    SLOW_TURN    = 30
    FORWARD_SLOW = 60

    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

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

        for pwm in (self.pwm1, self.pwm2, self.pwm3, self.pwm4):
            pwm.start(0)

    # ── Primitivas ────────────────────────────────────────────────────────────

    def _fwd(self, in1, in2, pwm, vel):
        GPIO.output(in1, GPIO.HIGH)
        GPIO.output(in2, GPIO.LOW)
        pwm.ChangeDutyCycle(max(0, min(100, vel)))

    def _bwd(self, in1, in2, pwm, vel):
        GPIO.output(in1, GPIO.LOW)
        GPIO.output(in2, GPIO.HIGH)
        pwm.ChangeDutyCycle(max(0, min(100, vel)))

    # ── Movimientos compuestos ────────────────────────────────────────────────

    def stop(self):
        for pin in [M1_IN1, M1_IN2, M2_IN1, M2_IN2,
                    M3_IN1, M3_IN2, M4_IN1, M4_IN2]:
            GPIO.output(pin, GPIO.LOW)
        for pwm in (self.pwm1, self.pwm2, self.pwm3, self.pwm4):
            pwm.ChangeDutyCycle(0)

    def adelante_lento(self):
        v = self.FORWARD_SLOW
        self._fwd(M1_IN1, M1_IN2, self.pwm1, v)
        self._fwd(M2_IN1, M2_IN2, self.pwm2, v)
        self._fwd(M3_IN1, M3_IN2, self.pwm3, v)
        self._fwd(M4_IN1, M4_IN2, self.pwm4, v)

    def girar_derecha(self, vel=None):
        v = vel or self.TURN_VEL
        self._fwd(M1_IN1, M1_IN2, self.pwm1, v)
        self._fwd(M2_IN1, M2_IN2, self.pwm2, v)
        self._bwd(M3_IN1, M3_IN2, self.pwm3, v)
        self._bwd(M4_IN1, M4_IN2, self.pwm4, v)

    def girar_izquierda(self, vel=None):
        v = vel or self.TURN_VEL
        self._bwd(M1_IN1, M1_IN2, self.pwm1, v)
        self._bwd(M2_IN1, M2_IN2, self.pwm2, v)
        self._fwd(M3_IN1, M3_IN2, self.pwm3, v)
        self._fwd(M4_IN1, M4_IN2, self.pwm4, v)

    def girar_lento_derecha(self):
        self.girar_derecha(vel=self.SLOW_TURN)

    def girar_lento_izquierda(self):
        self.girar_izquierda(vel=self.SLOW_TURN)

    # ── Limpieza ──────────────────────────────────────────────────────────────

    def cleanup(self):
        self.stop()
        for pwm in (self.pwm1, self.pwm2, self.pwm3, self.pwm4):
            pwm.stop()
        GPIO.cleanup()