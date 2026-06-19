import math
from utils.components import OmniWheelMotorController, Speed

class SimMotorController(OmniWheelMotorController):
    # Escala para convertir las constantes de motor (ej: 80) a velocidad de simulador (ej: 4.0)
    SIM_SCALE = 0.05

    def __init__(self):
        super().__init__()
        self.v_x = 0.0
        self.v_y = 0.0
        self.v_turn = 0.0
        #Temporally stored values
        self._last_vx = 0.0
        self._last_vy = 0.0
        self._last_v_turn = 0.0

    def capture_speed(self):
        self._last_vx = self.v_x
        self._last_vy = self.v_y
        self._last_v_turn = self.v_turn

    def norm_vel(self, vel=Speed.DEFAULT.value, minv=0.0, maxv=90.0):
        v_base = max(minv, min(maxv, float(vel))) / maxv
        v = minv + v_base * (maxv - minv)
        return v * self.SIM_SCALE

    def reset_speeds(self):
        self.v_x = 0.0
        self.v_y = 0.0
        self.v_turn = 0.0

    def go_from_angle(self, angle: float, vel=Speed.DEFAULT.value, w: float = 0.0):
        """Move in an arbitrary direction; simulation decomposes angle into vx/vy components."""
        v = self.norm_vel(vel)
        rad = math.radians(angle)
        self.v_x = v * math.cos(rad)
        self.v_y = v * math.sin(rad)
        self.v_turn = w

    def go_forward(self, vel=Speed.DEFAULT.value):
        v = self.norm_vel(vel)
        self.v_y = 0.0
        self.v_x = v

    def go_backward(self, vel=Speed.DEFAULT.value):
        v = self.norm_vel(vel)
        self.v_y = 0.0
        self.v_x = -v

    def spin_left(self, vel=Speed.DEFAULT.value):
        v = self.norm_vel(vel)
        self.v_x = 0.0
        self.v_y = 0.0
        self.v_turn = v / 40
        
    def spin_right(self, vel=Speed.DEFAULT.value):
        v = self.norm_vel(vel)
        self.v_x = 0.0
        self.v_y = 0.0
        self.v_turn = - v / 40

    def stop(self):
        self.reset_speeds()        
    
    def get_speeds(self) -> str:
        return f"""
        v_x: {self.v_x:.2f}
        v_y: {self.v_y:.2f}
        v_turn: {self.v_turn:.2f}"""