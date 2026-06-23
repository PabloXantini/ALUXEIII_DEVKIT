from __future__ import annotations

import cv2
from robot.aluxe3.context import *
from robot.aluxe3.context import Aluxe3Context
from robot.aluxe3.actuators import (
    SimCameraController,
    SimActuatorController
)
from utils.sim.virtual_camera import VirtualCamera
from sandbox.sim_cache import SimState

class SimContext(Aluxe3Context):
    """
    Contexto simulado simplificado.
    Actúa únicamente como puente (MVC) entre el Robot físico simulado en 'game.py' y 
    los estados mentales del FSM (fsm.py).
    """
    def __init__(self, model:Model, workspace:Workspace, debug:bool = True, name:str = 'robot', team:str = "blue"):
        super().__init__(model=model, workspace=workspace, debug=debug, name=name ,team=team)
        self.actuators = SimActuatorController(self.model)
        self.cameras = SimCameraController(self.model)
        
        # Enlace a la entidad cinemática
        self.robot = None
        
        self._cam_main:VirtualCamera = self.cameras.front_cam
        self._cam_main.set_light_level(
            ambient=0.4,
            diffuse=0.8,
            x=320, y=240, z=500 # Luz cenital simulada
        )
        self._cam_main.set_fisheye_params(k=-1.4, zoom=1.7)
        self._cam_main.set_motion_blur(strength=0.3, samples=3)

    def link_robot(self, robot_entity):
        self.robot = robot_entity

    def compute(self, state=None):
        if not self.robot or not state or not state.ball: return False        
        self.track_fps()

        # Sync simulated states to the environment (for HUD/FSM)
        self.env.heading       = self.actuators.psensor.get_heading() + self.env.orientation_offset
        self.env.us_left_dist  = self.actuators.us_left.get_distance()
        self.env.us_back_dist  = self.actuators.us_back.get_distance()
        self.env.us_right_dist = self.actuators.us_right.get_distance()

        # Exclude itself from robots to draw
        other_robots = [r for r in state.robots if r is not self.robot]
        
        # Build filtered state preserving all elements in the cache
        filtered_state = SimState(ball=state.ball, robots=other_robots, goals=state.goals, pitch=state.pitch)
        
        # Delegate rendering to VirtualCamera passing the state cache
        frame = self._cam_main.cap_frame(observer=self.robot, state=filtered_state)

        # Evaluate vision on the resulting image (with injected distortion)
        self.env.frame_width  = frame.shape[1]
        self.env.frame_height = frame.shape[0]
        self.process_frame(frame)
        
        return True

    def _get_window_name(self):
        window_name = "Robot"
        if self.robot:
            if self.robot.color == (0, 0, 255):
                window_name = "Blue"
            elif self.robot.color == (255, 255, 0):
                window_name = "Yellow"
        return window_name

    def get_debug_frame(self):
        return super().get_debug_frame(window_name=self._get_window_name())

    def show_debug(self):
        super().show_debug(window_name=self._get_window_name())

    def cleanup(self):
        super().cleanup()
