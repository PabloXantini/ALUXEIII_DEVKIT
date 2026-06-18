from __future__ import annotations
from utils.components import Speed
from utils.input import Key, InputManager

class KeyboardListener:
    """
    Keyboard listener for the actuator test suite.
    Uses InputManager to track key state continuously.

    Author: PabloXantini
    """
    _SPEED_KEYS = {
        Key.K_1: ("LOW",      Speed.LOW.value),
        Key.K_2: ("MID_LOW",  Speed.MID_LOW.value),
        Key.K_3: ("MEDIUM",   Speed.MEDIUM.value),
        Key.K_4: ("MID_HIGH", Speed.MID_HIGH.value),
        Key.K_5: ("HIGH",     Speed.HIGH.value),
    }

    _MOVE_KEYS = {
        Key.W: "FORWARD",
        Key.S: "BACKWARD",
        Key.A: "LEFT",
        Key.D: "RIGHT",
        Key.Z: "SPIN LEFT",
        Key.X: "SPIN RIGHT",
    }

    def __init__(self, input_manager: InputManager):
        self.input_manager = input_manager
        self.running = True
        self.speed_name = "MEDIUM"
        self.speed_val = Speed.MEDIUM.value
        self.active_action = "STOP"

    def poll_inputs(self) -> None:
        """
        Updates active action and speed from the current held key state.
        """
        # Service window events and snapshot input state
        self.input_manager.poll()

        # Check exit keys
        if (self.input_manager.is_key_pressed(Key.ESC) 
        or self.input_manager.is_key_pressed(Key.Q)):
            self.running = False
            return

        # Speed selection (last wins, instantaneous)
        for key, (name, val) in self._SPEED_KEYS.items():
            if self.input_manager.is_key_pressed(key):
                self.speed_name = name
                self.speed_val = val

        # Movement (continuous held check)
        action = "STOP"
        if self.input_manager.is_key_held(Key.SPACE):
            action = "STOP"
        else:
            for key, act in self._MOVE_KEYS.items():
                if self.input_manager.is_key_held(key):
                    action = act
                    break

        self.active_action = action

    def stop(self) -> None:
        pass
