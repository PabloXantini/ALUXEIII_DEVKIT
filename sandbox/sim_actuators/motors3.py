import math

_WHEEL_ANGLES_DEG = [90.0, 210.0, 330.0]

from utils.actuators import IMotorController

class MockMotorController3W(IMotorController):
    """Implementación falsa del controlador de 3 motores omnidireccionales para el simulador."""

    # Escala para convertir las constantes de motor (ej: 80) a velocidad de simulador (ej: 4.0)
    SIM_SCALE = 0.05
    # Escala extra para la rotación (para mantener la consistencia con el divisor /40 previo)
    SIM_TURN_SCALE = 0.05 / 40.0

    def __init__(self, calib=None):
        self.v_forward = 0.0
        self.v_lateral = 0.0
        self.v_turn = 0.0

    def _norm_vel(self, vel, max_val, min_val=0.0):
        v_base = super()._norm_vel(vel, max_val, min_val)
        return v_base * self.SIM_SCALE

    def _reset_speeds(self):
        self.v_forward = 0.0
        self.v_lateral = 0.0
        self.v_turn = 0.0

    def stop(self):
        self._reset_speeds()

    def go_from_angle(self, angle: float, vel=None):
        """Move in an arbitrary direction; simulation decomposes angle into vx/vy components."""
        v = self._norm_vel(vel, self.HIGH)
        rad = math.radians(angle)
        self._reset_speeds()
        self.v_lateral = v * math.sin(rad)
        self.v_forward = v * math.cos(rad)

    def go_forward(self, vel=None):
        v = self._norm_vel(vel, self.HIGH)
        self._reset_speeds()
        self.v_forward = v

    def go_backward(self, vel=None):
        v = self._norm_vel(vel, self.HIGH)
        self._reset_speeds()
        self.v_forward = -v

    def go_right(self, vel=None):
        self.go_from_angle(0, vel or self.MEDIUM)

    def go_left(self, vel=None):
        # Native left direction at 300° for 3-wheel layout
        self.go_from_angle(180, vel or self.MEDIUM)

    def spin_right(self, vel=None):
        v_base = super()._norm_vel(vel, self.MEDIUM)
        v = v_base * self.SIM_TURN_SCALE
        self._reset_speeds()
        self.v_turn = v

    def spin_left(self, vel=None):
        v_base = super()._norm_vel(vel, self.MEDIUM)
        v = v_base * self.SIM_TURN_SCALE
        self._reset_speeds()
        self.v_turn = -v

    def spin_slow_right(self):
        self._reset_speeds()
        v_base = super()._norm_vel(None, self.MID_LOW)
        self.v_turn = - (v_base * self.SIM_TURN_SCALE)

    def spin_slow_left(self):
        self._reset_speeds()
        v_base = super()._norm_vel(None, self.MID_LOW)
        self.v_turn = v_base * self.SIM_TURN_SCALE

    def cleanup(self):
        self.stop()
