import threading
import cv2
import time
from robot.aluxe3.context import *
from robot.aluxe3.actuators import HardwareActuatorController

class RobotContext(Aluxe3Context):
    """
    Contexto específico para el hardware del robot.
    Inicia la cámara física y los hilos para sensores reales.
    """
    def __init__(self, debug: bool = False, name: str = 'robot', team_color: str = "blue"):
        super().__init__(debug=debug, name=name, team_color=team_color)
        self.actuators = HardwareActuatorController(self.model)
        
        self._last_frame = None
        self.cap = self._initialize_camera()
        
        # Start daemon threads for physical camera and sensors
        self.camera_thread = threading.Thread(target=self._camera_process, daemon=True)
        self.sensor_thread = threading.Thread(target=self._sensor_process, daemon=True)
        self.camera_thread.start()
        self.sensor_thread.start()

    def _camera_process(self):
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                self._last_frame = frame
            else:
                time.sleep(0.01)

    def _sensor_process(self):
        while self.running:
            self.env.us_back_dist = self.actuators.us_back.get_distance()
            self.env.us_left_dist = self.actuators.us_left.get_distance()
            self.env.us_right_dist = self.actuators.us_right.get_distance()
            self.env.heading = self.actuators.psensor.get_heading()
            time.sleep(0.05)

    def _initialize_camera(self):
        cap = cv2.VideoCapture(CAMERA_SOURCE, CAP_BACKEND)
        cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
        r_w = int(CAMERA_W * SCALE_NORM)
        r_h = int(CAMERA_H * SCALE_NORM)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, r_w)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, r_h)
        return cap
        
    def compute(self):
        """Captura y procesa un frame."""
        if self._last_frame is None:
            return False            
        frame = self._last_frame.copy()
        
        # track FPS
        self.track_fps()
        w = frame.shape[1]
        h = frame.shape[0]
        
        if FLIP_FRAME:
            frame = cv2.flip(frame, -1)
 
        self.env.frame_width  = w
        self.env.frame_height = h
        
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        self.info, self.env.frame_debug = self.vision.detect(frame, hsv, self.debug)
        
        return True

    def cleanup(self):
        super().cleanup()
        self.actuators.cleanup()
        self.cap.release()
        self.camera_thread.join()
        self.sensor_thread.join()