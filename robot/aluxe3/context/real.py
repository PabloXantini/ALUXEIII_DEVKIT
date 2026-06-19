import threading
import cv2
import time
from robot.aluxe3.context import *
from robot.aluxe3.actuators import (
    HardwareActuatorController, 
    HardwareCameraController
)

class RobotContext(Aluxe3Context):
    """
    Contexto específico para el hardware del robot.
    Inicia la cámara física y los hilos para sensores reales.
    """
    def __init__(self, model:Model, workspace:Workspace, debug:bool = False, name:str = 'robot', team:str = "blue"):
        super().__init__(model=model, workspace=workspace, debug=debug, name=name, team=team)
        self.actuators = HardwareActuatorController(self.model)
        self.cameras = HardwareCameraController(self.model)
        self._last_frame = None
        
        # Start daemon threads for physical camera and sensors
        self.camera_thread = threading.Thread(target=self._camera_process, daemon=True)
        self.sensor_thread = threading.Thread(target=self._sensor_process, daemon=True)
        self.camera_thread.start()
        self.sensor_thread.start()

    def _camera_process(self):
        while self.running:
            frame = self.cameras.front_cam.cap_frame()
            if frame is not None:
                self._last_frame = frame
            time.sleep(0.01)
    def _sensor_process(self):
        while self.running:
            self.env.us_back_dist = self.actuators.us_back.get_distance()
            self.env.us_left_dist = self.actuators.us_left.get_distance()
            self.env.us_right_dist = self.actuators.us_right.get_distance()
            self.env.heading = self.actuators.psensor.get_heading()
            time.sleep(0.05)

    def compute(self):
        """Captura y procesa un frame."""
        if self._last_frame is None: return False
        frame = self._last_frame.copy()
        self.track_fps()
        if FLIP_FRAME: frame = cv2.flip(frame, -1)
        self.env.frame_width  = frame.shape[1]
        self.env.frame_height = frame.shape[0]
        self.process_frame(frame)
        return True

    def cleanup(self):
        super().cleanup()
        self.actuators.cleanup()
        self.cameras.cleanup()
        self.camera_thread.join()
        self.sensor_thread.join()