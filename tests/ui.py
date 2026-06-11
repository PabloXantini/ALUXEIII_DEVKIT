from __future__ import annotations
from dataclasses import dataclass
import cv2
import numpy as np

# Color palette for HUD (matching hardware test aesthetics)
C_BG        = (23,  17,  14)       # Dark background (BGR: Dark Navy/Blue)
C_PANEL     = (34,  27,  22)       # Panel background (BGR)
C_BORDER    = (65,  50,  40)       # Border color (BGR)
C_ACCENT    = (255, 180, 80)       # Accent color (BGR: light blue/cyan)
C_GREEN     = (120, 220, 80)       # Green (BGR)
C_YELLOW    = (60,  210, 255)      # Yellow (BGR)
C_RED       = (80,  80,  255)      # Red (BGR)
C_GRAY      = (145, 130, 120)      # Gray (BGR)
C_WHITE     = (245, 235, 230)      # White (BGR)

@dataclass
class DataHUD:
    action: str
    speed_name: str
    speed_val: int
    last_cam_frame: np.ndarray

class RobotContextHUD:
    def __init__(self, context, sandbox: bool) -> None:
        self.context = context
        self.sandbox = sandbox
    def update(self, action, speed_name, speed_val, last_cam_frame) -> None:
        self.data = DataHUD(action, speed_name, speed_val, last_cam_frame)
    def draw(self) -> np.ndarray:
        """
        Renders the OpenCV HUD with current status, speed, telemetry, and camera preview.
    
        Author: PabloXantini
        """
        # Create an OpenCV frame for the HUD
        hud_w, hud_h = 600, 500
        hud = np.zeros((hud_h, hud_w, 3), dtype=np.uint8)
        hud[:] = C_BG

        # 1. Header Title
        mode_str = "Sandbox" if self.sandbox else "Hardware"
        cv2.putText(hud, f"ALUXE III - Actuator {mode_str} Test HUD", (20, 35),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, C_ACCENT, 2, cv2.LINE_AA)
        cv2.line(hud, (20, 50), (hud_w - 20, 50), C_BORDER, 1)

        # 2. Status Panel (Action, Speed, Heading)
        cv2.rectangle(hud, (20, 65), (hud_w - 20, 165), C_PANEL, -1)
        cv2.rectangle(hud, (20, 65), (hud_w - 20, 165), C_BORDER, 1)
    
        act_color = C_GREEN if self.data.action != "STOP" else C_GRAY
        cv2.putText(hud, f"Action : {self.data.action}", (35, 95),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, act_color, 1, cv2.LINE_AA)
        cv2.putText(hud, f"Speed  : {self.data.speed_name} ({self.data.speed_val}%)", (35, 125),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, C_YELLOW, 1, cv2.LINE_AA)
    
        heading = self.context.env.heading
        cv2.putText(hud, f"Heading: {heading:6.1f} deg", (320, 95),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, C_WHITE, 1, cv2.LINE_AA)

        # 3. Sensor Panel (Ultrasonic Distances)
        cv2.rectangle(hud, (20, 180), (hud_w - 20, 260), C_PANEL, -1)
        cv2.rectangle(hud, (20, 180), (hud_w - 20, 260), C_BORDER, 1)
        cv2.putText(hud, "Ultrasonic Distances", (35, 205),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, C_GRAY, 1, cv2.LINE_AA)

        def format_dist(v: float) -> str:
            return f"{v:5.1f} cm" if v >= 0 else "TIMEOUT"

        dist_l = self.context.env.us_left_dist
        dist_b = self.context.env.us_back_dist
        dist_r = self.context.env.us_right_dist

        cv2.putText(hud, f"LEFT: {format_dist(dist_l)}", (35, 235),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, C_WHITE, 1, cv2.LINE_AA)
        cv2.putText(hud, f"BACK: {format_dist(dist_b)}", (220, 235),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, C_WHITE, 1, cv2.LINE_AA)
        cv2.putText(hud, f"RIGHT: {format_dist(dist_r)}", (410, 235),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, C_WHITE, 1, cv2.LINE_AA)

        # 4. Embedded Camera Stream
        if self.data.last_cam_frame is not None:
            cam_h, cam_w = 160, 200
            resized = cv2.resize(self.data.last_cam_frame, (cam_w, cam_h))
            cv2.rectangle(hud, (35, 295), (35 + cam_w + 2, 295 + cam_h + 2), C_BORDER, 1)
            hud[296:296+cam_h, 36:36+cam_w] = resized
        cv2.putText(hud, "Camera Feed (POV)", (35, 285),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, C_GRAY, 1, cv2.LINE_AA)

        # 5. Instructions panel
        cv2.rectangle(hud, (260, 295), (hud_w - 20, 455), C_PANEL, -1)
        cv2.rectangle(hud, (260, 295), (hud_w - 20, 455), C_BORDER, 1)
        cv2.putText(hud, "Controls Info", (275, 320),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, C_GRAY, 1, cv2.LINE_AA)
        cv2.putText(hud, "WASD : Move", (275, 345),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, C_WHITE, 1, cv2.LINE_AA)
        cv2.putText(hud, "Q/E  : Spin Left/Right", (275, 370),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, C_WHITE, 1, cv2.LINE_AA)
        cv2.putText(hud, "SPACE: Stop", (275, 395),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, C_WHITE, 1, cv2.LINE_AA)
        cv2.putText(hud, "1-5  : Change Speed", (275, 420),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, C_WHITE, 1, cv2.LINE_AA)

        # 6. Exit text
        exit_msg = "Focus OpenCV HUD or Pygame. Press ESC to exit." if self.sandbox else "Focus OpenCV HUD. Press ESC to exit."
        cv2.putText(hud, exit_msg, (20, 485),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, C_GRAY, 1, cv2.LINE_AA)

        return hud
