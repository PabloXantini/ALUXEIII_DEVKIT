import math

_WHEEL_ANGLES_DEG = [90.0, 210.0, 330.0]

class MockMotorController3W:
    """Implementación falsa del controlador de 3 motores omnidireccionales para el simulador."""

    # Velocidades simuladas que se aplicarán al robot
    FORWARD_SPEED = 2.0
    TURN_SPEED = 0.05
    SLOW_TURN_SPEED = 0.02
    # Velocidades por defecto (duty-cycle %)
    HIGH      = 4.0
    MID_HIGH  = 3.0
    MEDIUM    = 2.5
    MID_LOW   = 2.0
    LOW       = 1.5

    def __init__(self, calib=None):
        self.v_forward = 0.0
        self.v_lateral = 0.0
        self.v_turn = 0.0

    def _reset_speeds(self):
        self.v_forward = 0.0
        self.v_lateral = 0.0
        self.v_turn = 0.0

    def stop(self):
        self._reset_speeds()

    def go_from_angle(self, angle: float, vel=None):
        """Move in an arbitrary direction; simulation decomposes angle into vx/vy components."""
        v = vel or self.HIGH
        rad = math.radians(angle)
        self._reset_speeds()
        self.v_lateral = v * math.sin(rad)
        self.v_forward = v * math.cos(rad)

    def go_forward(self, vel=None):
        self.go_from_angle(0, vel)

    def go_backward(self, vel=None):
        self.go_from_angle(180, vel)

    def go_right(self, vel=None):
        # Native right direction at 60° for 3-wheel layout
        self.go_from_angle(60, vel or self.MEDIUM)

    def go_left(self, vel=None):
        # Native left direction at 300° for 3-wheel layout
        self.go_from_angle(300, vel or self.MEDIUM)

    def spin_right(self, vel=None):
        v = vel or self.MEDIUM / 40
        self._reset_speeds()
        self.v_turn = -v

    def spin_left(self, vel=None):
        v = vel or self.MEDIUM / 40
        self._reset_speeds()
        self.v_turn = v

    def spin_slow_right(self):
        self._reset_speeds()
        self.v_turn = -self.MID_LOW / 40

    def spin_slow_left(self):
        self._reset_speeds()
        self.v_turn = self.MID_LOW / 40

    def cleanup(self):
        self.stop()
