from __future__ import annotations

from utils.components import ICamera
import numpy as np
import cv2

BACKEND = cv2.CAP_V4L2

class Camera(ICamera):
    def __init__(self, src:int, width:int, height:int, scale:float = 1.0):
        super().__init__(width, height)
        self.cap = cv2.VideoCapture(src, BACKEND)
        rw = int(width*scale)
        rh = int(height*scale)
        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, rw)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, rh)
    
    def cap_frame(self) -> np.ndarray:
        ret, frame = self.cap.read()
        if ret: return frame
        return None
    
    def cleanup(self) -> None:
        self.cap.release()