import cv2
import time
import numpy as np
import threading
from utils.fsm import MContext
from .actuators import ActuatorController
from .cv import CVDetector, ColorSegmentator

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
LOWER_BALL = np.array([0, 20, 0], dtype=np.uint8)
UPPER_BALL = np.array([27, 255, 255], dtype=np.uint8)
#> BALL PROXIMITY
BALL_AREA_MIN   = 50
BALL_AREA_MINT  = 1

# GOALS
#> GOAL PROXIMITY
GOAL_AREA_MIN = 80
#> BLUE MASK
LOWER_GOAL1 = np.array([77, 123, 50], dtype=np.uint8)
UPPER_GOAL1 = np.array([120, 255, 200], dtype=np.uint8)
#> YELLOW MASK
LOWER_GOAL2 = np.array([28, 171, 139], dtype=np.uint8)
UPPER_GOAL2 = np.array([41, 255, 255], dtype=np.uint8)

# CAMERA SOURCE
CAMERA_SOURCE  = 0
CAP_BACKEND    = cv2.CAP_V4L2

# Derived parameters
SCALE_NORM = SCALE_PERCENT / 100

class RobotContext(MContext):
    """
    Contexto compartido entre todos los estados.
    Almacena el estado de percepción en self.info y expone motores y sensores unificados.
    """
 
    def __init__(self, debug: bool = False, name: str = 'robot', team_color: str = "blue", init_hardware: bool = True):
        super().__init__()
        self.debug = debug
        self.name = name
        self.team_color = team_color.lower()
        self.team_color_rgb = (255, 0, 0) if self.team_color == "blue" else (0, 255, 255)
        self.actuators = ActuatorController()

        if init_hardware:
            self.cap = self._initialize_camera()
        else:
            self.cap = None
 
        # Diccionario central de percepción
        self.info = {
            'ball': {'detected': False, 'offset_x': None, 'radius': 0},
            'ally_goal': {'detected': False, 'offset_x': None, 'radius': 0},
            'enemy_goal': {'detected': False, 'offset_x': None, 'radius': 0}
        }

        self.frame_debug          = None
        self.frame_width: int     = 0
        self.frame_height: int    = 0
        self.fps: float           = 0.0
        self._last_time: float    = time.time()
 
        # Estado legible para overlay
        self.estado_label: str    = "Iniciando..."
        
        # Ultrasonic distances (read from actuators facade)
        self.us_back_dist = 0.0
        self.us_left_dist = 0.0
        self.us_right_dist = 0.0
        
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
        self.vision = CVDetector(ball_seg, ally_seg, enemy_seg, franja_central=CENTER_TOLERANCE)
        
        # Threading state variables
        self._running = True
        self._latest_frame = None
        
        if init_hardware:
            # Start daemon threads for camera and sensors
            self.camera_thread = threading.Thread(target=self._camera_thread_loop, daemon=True)
            self.sensor_thread = threading.Thread(target=self._sensor_thread_loop, daemon=True)
            self.camera_thread.start()
            self.sensor_thread.start()

    def _camera_thread_loop(self):
        while self._running:
            ret, frame = self.cap.read()
            if ret:
                self._latest_frame = frame
            else:
                time.sleep(0.01)

    def _sensor_thread_loop(self):
        while self._running:
            self.us_back_dist = self.actuators.us_back.get_distance()
            self.us_left_dist = self.actuators.us_left.get_distance()
            self.us_right_dist = self.actuators.us_right.get_distance()
            time.sleep(0.05)  # Add a small delay to avoid excessive CPU usage if sensor reads fail fast

    def _initialize_camera(self):
        cap = cv2.VideoCapture(CAMERA_SOURCE, CAP_BACKEND)
        cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
        r_w = int(CAMERA_W * SCALE_NORM)
        r_h = int(CAMERA_H * SCALE_NORM)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, r_w)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, r_h)
        return cap

    def track_fps(self):
        current_time = time.time()
        dt = current_time - self._last_time
        dt = max(dt, 1e-6)
        self.fps = 1.0 / dt
        self._last_time = current_time
        return self.fps
 
    def compute(self):
        """Captura y procesa un frame."""
        if self._latest_frame is None:
            # Wait for the first frame
            return True
            
        frame = self._latest_frame.copy()
        
        # track FPS
        self.track_fps()

        w = frame.shape[1]
        h = frame.shape[0]

        if FLIP_FRAME:
            frame = cv2.flip(frame, 0)
 
        self.frame_width  = w
        self.frame_height = h
        
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        self.info, self.frame_debug = self.vision.detect(frame, hsv, self.debug)
        
        return True
 
    # ── Debug visual ──────────────────────────────────────────────────────────
 
    def get_debug_frame(self, window_name="POV:"):
        if self.debug and self.frame_debug is not None:
            frame = self.frame_debug.copy()
            # Combina el nombre de la ventana y el estado para mostrar en el mosaico/ventana
            cv2.putText(frame, f"{self.name} ({window_name})", (10, 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.team_color_rgb, 2)
            cv2.putText(frame, f"Orientation: {self.actuators.psensor.get_heading()}",
                        (10, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            cv2.putText(frame, f"US (L/B/R): {self.us_left_dist:.1f} | {self.us_back_dist:.1f} | {self.us_right_dist:.1f}",
                        (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)
            cv2.putText(frame, f"E: {self.estado_label}",
                        (10, self.frame_height - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            cv2.putText(frame, f"FPS: {int(self.fps)}",
                        (10, self.frame_height - 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            return frame
        return None

    def show_debug(self, window_name="POV:"):
        frame = self.get_debug_frame(window_name)
        if frame is not None:
            cv2.imshow(f"{window_name} {self.name}", frame)
 
    # ── Limpieza ──────────────────────────────────────────────────────────────
 
    def cleanup(self):
        self._running = False
        self.actuators.cleanup()
        self.cap.release()
        cv2.destroyAllWindows()