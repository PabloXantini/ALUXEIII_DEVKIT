from utils.resources.workspace import Workspace
import cv2
import time
import numpy as np
from utils.fsm import MContext
from utils.resources.model import Model
from ..cv import (
    ThresholdSegmentator,
    CVDetector,
)
from ..manifest import *

SCALE_PERCENT = 40
SCALE_NORM = SCALE_PERCENT / 100
FLIP_FRAME = True

# CONSTANT ROBOT BEHAVIOR PARAMETERS
CENTER_TOLERANCE = 40   # píxeles de tolerancia lateral
BALL_RADIUS_CLOSE_MIN = 18   # radio mínimo para considerar la pelota "cerca"

class Environment:
    def __init__(self, workspace:Workspace):
        self.frame_debug = None
        self.frame_width: int = 0
        self.frame_height: int = 0
        self.fps: float = 0.0
        self.last_time: float = time.time()
        self.st_label: str = "Processing..."
        self.us_back_dist  = 0.0
        self.us_left_dist  = 0.0
        self.us_right_dist = 0.0
        self.heading       = 0.0

class Aluxe3Context(MContext):
    """
    Base context class. Handles FSM memory, Generic vision pipeline processing, 
    and debug rendering.
    """
    def __init__(self, model:Model, workspace:Workspace, debug: bool = False, name: str = 'robot', team: str = "blue"):
        super().__init__()
        self.model = model
        self.workspace = workspace
        self.debug = debug
        self.name = name
        self.team = team.lower()
        self.running = True
        self.actuators = None
        self.cameras = None
        self.env = Environment(workspace)
        self.info = {
            'ball': {'detected': False, 'offset_x': None, 'radius': 0},
            'ally_goal': {'detected': False, 'offset_x': None, 'radius': 0},
            'enemy_goal': {'detected': False, 'offset_x': None, 'radius': 0}
        }
        color = (255, 255, 255)

        if self.team == "blue":
            color = (255, 0, 0)
            ally_seg_mask = self.workspace.masks["blue"]
            enemy_seg_mask = self.workspace.masks["yellow"]
        elif self.team == "yellow":
            color = (0, 255, 255)
            ally_seg_mask = self.workspace.masks["yellow"]
            enemy_seg_mask = self.workspace.masks["blue"]
        self.color = color
        
        # Inicializar Segmentadores
        ball_seg = ThresholdSegmentator(self.workspace.masks["ball"], 1)
        ally_seg = ThresholdSegmentator(ally_seg_mask, 80)
        enemy_seg = ThresholdSegmentator(enemy_seg_mask, 80)
 
        # Orquestador
        self.vision = CVDetector(center_tolerance=CENTER_TOLERANCE)
        self.vision.add_segmentator(ball_seg, "ball")
        self.vision.add_segmentator(ally_seg, "ally_goal")
        self.vision.add_segmentator(enemy_seg, "enemy_goal")

    @property
    def state_label(self):
        return self.env.st_label
        
    @state_label.setter
    def state_label(self, value):
        self.env.st_label = value

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
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.color, 2)
            cv2.putText(frame, f"US (L/B/R): {self.env.us_left_dist:.1f} | {self.env.us_back_dist:.1f} | {self.env.us_right_dist:.1f}",
                        (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)
            cv2.putText(frame, f"E: {self.env.st_label}",
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

    def process_frame(self, frame: np.ndarray):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        self.info, self.env.frame_debug = self.vision.detect(frame, hsv, self.debug)

    def cleanup(self):
        self.running = False
        cv2.destroyAllWindows()