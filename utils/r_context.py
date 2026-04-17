import cv2
import numpy as np
from fsm import MContext
from utils.r_actuators import MotorController
 
 
# ── Parámetros de visión ──────────────────────────────────────────────────────
 
CAMERA_SOURCE  = 0
CAP_BACKEND    = cv2.CAP_V4L2
SCALE_PERCENT  = 0.50
FLIP_FRAME     = True

# BALL
# Rango HSV de la pelota (naranja/rojo)
LOWER_BALL = np.array([0, 120, 0], dtype=np.uint8)
UPPER_BALL = np.array([20, 255, 255], dtype=np.uint8)
BALL_AREA_MIN   = 50

# GOALS
# Rango HSV de la portería (azul)
LOWER_GOAL1 = np.array([90, 50, 50], dtype=np.uint8)
UPPER_GOAL1 = np.array([130, 255, 255], dtype=np.uint8)
# Rango HSV de la portería (amarillo)
LOWER_GOAL2 = np.array([20, 100, 100], dtype=np.uint8)
UPPER_GOAL2 = np.array([30, 255, 255], dtype=np.uint8)
GOAL_AREA_MIN = 80

# KERNELS
KERNEL5 = np.ones((5, 5), np.uint8)
KERNEL3 = np.ones((3, 3), np.uint8)

# ── Parámetros de comportamiento ──────────────────────────────────────────────

FRANJA_CENTRAL = 40   # píxeles de tolerancia lateral
RADIO_OBJETIVO = 30   # radio mínimo para considerar la pelota "cerca"
 
 
class RobotContext(MContext):
    """
    Contexto compartido entre todos los estados.
    Captura el frame, detecta la pelota, las porterías y expone los datos
    (offset_x, radius, etc.) + acceso a los motores.
    """
 
    def __init__(self, debug: bool = False, team_color: str = "blue"):
        super().__init__()
        self.debug = debug
        self.team_color = team_color.lower()
        self.motors = MotorController()
        self.cap    = cv2.VideoCapture(CAMERA_SOURCE, CAP_BACKEND)
 
        # Datos de percepción (actualizados en compute)
        self.ball_detected: bool  = False
        self.offset_x: int | None = None
        self.radius: int          = 0
        
        # Detección de porterías
        self.ally_goal_detected: bool  = False
        self.ally_goal_offset_x: int | None = None
        self.ally_goal_radius: int = 0
        
        self.enemy_goal_detected: bool  = False
        self.enemy_goal_offset_x: int | None = None
        self.enemy_goal_radius: int = 0

        self.frame_debug          = None
        self.frame_width: int     = 0
        self.frame_height: int    = 0
 
        # Estado legible para overlay
        self.estado_label: str    = "Iniciando..."
        
        # Configurar colores de portería según el equipo
        if self.team_color == "blue":
            self.ally_goal_lower = LOWER_GOAL1
            self.ally_goal_upper = UPPER_GOAL1
            self.enemy_goal_lower = LOWER_GOAL2
            self.enemy_goal_upper = UPPER_GOAL2
        else: # yellow
            self.ally_goal_lower = LOWER_GOAL2
            self.ally_goal_upper = UPPER_GOAL2
            self.enemy_goal_lower = LOWER_GOAL1
            self.enemy_goal_upper = UPPER_GOAL1
 
    # ── Implementación MContext ───────────────────────────────────────────────
 
    def compute(self):
        """Captura y procesa un frame. Llámalo al inicio de cada ciclo."""
        ret, frame = self.cap.read()
        if not ret:
            return False
 
        if FLIP_FRAME:
            frame = cv2.flip(frame, 0)
 
        w = int(frame.shape[1] * SCALE_PERCENT)
        h = int(frame.shape[0] * SCALE_PERCENT)
        frame = cv2.resize(frame, (w, h), interpolation=cv2.INTER_AREA)
 
        self.frame_width  = w
        self.frame_height = h
        
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        self._detect_objects(frame, hsv)
        return True
 
    # ── Detección ─────────────────────────────────────────────────────────────
 
    def _detect_color(self, hsv, lower, upper, min_area):
        """Método unificado para detectar un color específico usando HSV."""
        mask = cv2.inRange(hsv, lower, upper)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, KERNEL5, iterations=2)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN,  KERNEL5, iterations=1)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        detected = False
        offset_x = None
        radius = 0
        best_contour = None
        
        if contours:
            c = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(c)
            if area > min_area:
                detected = True
                M = cv2.moments(c)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    offset_x = cx - (self.frame_width // 2)
                    (_, _), rf = cv2.minEnclosingCircle(c)
                    radius = int(rf)
                    best_contour = c
                    
        return detected, offset_x, radius, best_contour

    def _detect_objects(self, frame, hsv):
        debug = frame.copy() if self.debug else None
        
        # 1. Detección de la pelota (Naranja/Rojo)
        self.ball_detected, self.offset_x, self.radius, ball_contour = \
            self._detect_color(hsv, LOWER_BALL, UPPER_BALL, BALL_AREA_MIN)
            
        # 2. Detección de Portería Aliada
        self.ally_goal_detected, self.ally_goal_offset_x, self.ally_goal_radius, ally_contour = \
            self._detect_color(hsv, self.ally_goal_lower, self.ally_goal_upper, GOAL_AREA_MIN)
            
        # 3. Detección de Portería Enemiga
        self.enemy_goal_detected, self.enemy_goal_offset_x, self.enemy_goal_radius, enemy_contour = \
            self._detect_color(hsv, self.enemy_goal_lower, self.enemy_goal_upper, GOAL_AREA_MIN)
        
        if self.debug:
            img_cx = self.frame_width // 2
            # Dibujar la pelota
            if self.ball_detected and ball_contour is not None:
                cv2.drawContours(debug, [ball_contour], -1, (255, 0, 0), 2)
                cx = img_cx + self.offset_x
                cv2.circle(debug, (cx, self.frame_height // 2), 5, (0, 255, 0), -1)
                
            # Dibujar portería aliada (verde para diferenciar en debug)
            if self.ally_goal_detected and ally_contour is not None:
                cv2.drawContours(debug, [ally_contour], -1, (0, 255, 0), 2)
                cx = img_cx + self.ally_goal_offset_x
                cv2.putText(debug, "ALLY GOAL", (cx - 30, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                
            # Dibujar portería enemiga (rojo para diferenciar en debug)
            if self.enemy_goal_detected and enemy_contour is not None:
                cv2.drawContours(debug, [enemy_contour], -1, (0, 0, 255), 2)
                cx = img_cx + self.enemy_goal_offset_x
                cv2.putText(debug, "ENEMY GOAL", (cx - 40, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
 
        if self.debug:
            img_cx = self.frame_width // 2
            # Franja central de referencia
            lx = img_cx - FRANJA_CENTRAL
            rx = img_cx + FRANJA_CENTRAL
            cv2.line(debug, (lx, 0), (lx, frame.shape[0]), (255, 255, 255), 1)
            cv2.line(debug, (rx, 0), (rx, frame.shape[0]), (255, 255, 255), 1)
 
        self.frame_debug = debug

    

    # ── Debug visual ──────────────────────────────────────────────────────────
 
    def show_debug(self, window_name="Robot Vision"):
        if self.debug and self.frame_debug is not None:
            cv2.putText(self.frame_debug, self.estado_label,
                        (10, self.frame_height - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            cv2.imshow(window_name, self.frame_debug)
 
    # ── Limpieza ──────────────────────────────────────────────────────────────
 
    def cleanup(self):
        self.motors.cleanup()
        self.cap.release()
        cv2.destroyAllWindows()