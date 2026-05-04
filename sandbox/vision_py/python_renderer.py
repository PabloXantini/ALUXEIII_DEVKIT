import numpy as np
import cv2
import math

class OpenCVRenderer:
    def __init__(self, width, height, focal_length):
        self.width = width
        self.height = height
        self.focal_length = focal_length
        self.cx = width // 2
        self.cy = height // 2

    def render(self, observer, state, camera_params, fisheye_maps=None):
        frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        # Fondo (Pasto/Cielo)
        frame[self.height//2:, :] = (50, 100, 30)
        frame[:self.height//2, :] = (30, 30, 30)
        
        # Aquí iría la lógica antigua de OpenCV si se desea conservar al 100%
        # Por ahora es un fallback simple
        cv2.putText(frame, "FALLBACK: OpenCV", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        # Aplicar fisheye si se proporcionaron mapas
        if fisheye_maps is not None:
            map_x, map_y = fisheye_maps
            frame = cv2.remap(frame, map_x, map_y, cv2.INTER_LINEAR)

        return frame
