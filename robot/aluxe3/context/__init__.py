import cv2
import time
import numpy as np
from utils.fsm import MContext
import utils.resources.model as robot_model
from ..cv import ColorSegmentator, CVDetector
from ..manifest import *

# CAMERA
CAMERA_W = 640
CAMERA_H = 480
SCALE_PERCENT  = 40
FLIP_FRAME     = True

# ROBOT BEHAVIOR PARAMETERS
CENTER_TOLERANCE = 40   # píxeles de tolerancia lateral
BALL_RADIUS_CLOSE_MIN = 18   # radio mínimo para considerar la pelota "cerca"

# BALL
#> ORANGE MASK
# LOWER_BALL = np.array([0, 20, 0], dtype=np.uint8)
# UPPER_BALL = np.array([27, 255, 255], dtype=np.uint8)
LOWER_BALL = np.array([0, 81, 82], dtype=np.uint8)
UPPER_BALL = np.array([20, 255, 255], dtype=np.uint8)
#> BALL PROXIMITY
BALL_AREA_MIN   = 50
BALL_AREA_MINT  = 1

# GOALS
#> GOAL PROXIMITY
GOAL_AREA_MIN = 80
#> BLUE MASK
# LOWER_GOAL1 = np.array([77, 123, 50], dtype=np.uint8)
# UPPER_GOAL1 = np.array([120, 255, 200], dtype=np.uint8)
LOWER_GOAL1 = np.array([0, 97, 195], dtype=np.uint8)
UPPER_GOAL1 = np.array([179, 255, 255], dtype=np.uint8)
#> YELLOW MASK
# LOWER_GOAL2 = np.array([28, 171, 139], dtype=np.uint8)
# UPPER_GOAL2 = np.array([41, 255, 255], dtype=np.uint8)
LOWER_GOAL2 = np.array([84, 75, 134], dtype=np.uint8)
UPPER_GOAL2 = np.array([122, 249, 220], dtype=np.uint8)

# CAMERA SOURCE
CAMERA_SOURCE  = 0
CAP_BACKEND    = cv2.CAP_V4L2

# Derived parameters
SCALE_NORM = SCALE_PERCENT / 100

class Environment:
    def __init__(self):
        self.frame_debug = None
        self.frame_width: int = 0
        self.frame_height: int = 0
        self.fps: float = 0.0
        self.last_time: float = time.time()
        self.estado_label: str = "Processing..."
        self.us_back_dist  = 0.0
        self.us_left_dist  = 0.0
        self.us_right_dist = 0.0
        self.heading       = 0.0

class Aluxe3Context(MContext):
    """
    Base context class. Handles FSM memory, Generic vision pipeline processing, 
    and debug rendering.
    """
    def __init__(self, debug: bool = False, name: str = 'robot', team_color: str = "blue"):
        super().__init__()
        self.model = robot_model.load_model(MODEL_DIR, ROBOT_MODEL)
        self.debug = debug
        self.name = name
        self.team_color = team_color.lower()
        self.team_color_rgb = (255, 0, 0) if self.team_color == "blue" else (0, 255, 255)
 
        # Diccionario central de percepción
        self.info = {
            'ball': {'detected': False, 'offset_x': None, 'radius': 0},
            'ally_goal': {'detected': False, 'offset_x': None, 'radius': 0},
            'enemy_goal': {'detected': False, 'offset_x': None, 'radius': 0}
        }

        self.env = Environment()
        self.actuators = None
        self.running = True
        
        # Configurar colores según equipo
        if self.team_color == "blue":
            ally_l, ally_u = LOWER_GOAL1, UPPER_GOAL1
            enemy_l, enemy_u = LOWER_GOAL2, UPPER_GOAL2
        else:
            ally_l, ally_u = LOWER_GOAL2, UPPER_GOAL2
            enemy_l, enemy_u = LOWER_GOAL1, UPPER_GOAL1
 
        # Inicializar Segmentadores
        ball_seg = ColorSegmentator(LOWER_BALL, UPPER_BALL, BALL_AREA_MINT)
        ally_seg = ColorSegmentator(ally_l, ally_u, GOAL_AREA_MIN)
        enemy_seg = ColorSegmentator(enemy_l, enemy_u, GOAL_AREA_MIN)
 
        # Orquestador
        self.vision = CVDetector(ball_seg, ally_seg, enemy_seg, center_tolerance=CENTER_TOLERANCE)

    @property
    def state_label(self):
        return self.env.estado_label
        
    @state_label.setter
    def state_label(self, value):
        self.env.estado_label = value

    def track_fps(self):
        current_time = time.time()
        dt = current_time - self.env.last_time
        dt = max(dt, 1e-6)
        self.env.fps = 1.0 / dt
        self.env.last_time = current_time
        return self.env.fps

    def get_debug_frame(self, window_name="POV:"):
        if self.debug and self.env.frame_debug is not None:
            frame = self.env.frame_debug.copy()
                
            cv2.putText(frame, f"Orientation: {self.env.heading}",
                        (10, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            cv2.putText(frame, f"{self.name} ({window_name})", (10, 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.team_color_rgb, 2)
            cv2.putText(frame, f"US (L/B/R): {self.env.us_left_dist:.1f} | {self.env.us_back_dist:.1f} | {self.env.us_right_dist:.1f}",
                        (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)
            cv2.putText(frame, f"E: {self.env.estado_label}",
                        (10, self.env.frame_height - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            cv2.putText(frame, f"FPS: {int(self.env.fps)}",
                        (10, self.env.frame_height - 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            return frame
        return None

    def show_debug(self, window_name="POV:"):
        frame = self.get_debug_frame(window_name)
        if frame is not None:
            cv2.imshow(f"{window_name} {self.name}", frame)

    def cleanup(self):
        self.running = False
        cv2.destroyAllWindows()