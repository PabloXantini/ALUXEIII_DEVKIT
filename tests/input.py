from __future__ import annotations
import threading
from utils.actuators import IMotorController
import utils.input as inputs

try:
    from pynput import keyboard as pynput_kb
except ImportError:
    pynput_kb = None


class KeyboardListener:
    """
    Threaded keyboard listener for the actuator test suite.
    Uses pynput to track key state continuously in a background daemon thread,
    eliminating OS key-repeat delays. cv2.waitKey(1) is still called each frame
    to keep the OpenCV window responsive.

    Author: PabloXantini
    """
    _SPEED_KEYS = {
        '1': ("LOW",      IMotorController.LOW),
        '2': ("MID_LOW",  IMotorController.MID_LOW),
        '3': ("MEDIUM",   IMotorController.MEDIUM),
        '4': ("MID_HIGH", IMotorController.MID_HIGH),
        '5': ("HIGH",     IMotorController.HIGH),
    }

    _MOVE_KEYS = {
        'w': "FORWARD",
        's': "BACKWARD",
        'a': "LEFT",
        'd': "RIGHT",
        'z': "SPIN LEFT",
        'x': "SPIN RIGHT",
    }

    def __init__(self, sandbox: bool = False):
        self.sandbox = sandbox
        self.running = True
        self.speed_name = "MEDIUM"
        self.speed_val = IMotorController.MEDIUM
        self.active_action = "STOP"

        self._held: set[str] = set()
        self._lock = threading.Lock()
        self._start_listener()

    def _start_listener(self) -> None:
        if pynput_kb is None:
            return
        self._kb_listener = pynput_kb.Listener(
            on_press=self._on_press,
            on_release=self._on_release,
            daemon=True
        )
        self._kb_listener.start()

    def _on_press(self, key) -> None:
        char = self._key_to_char(key)
        if char:
            with self._lock:
                self._held.add(char)

    def _on_release(self, key) -> None:
        char = self._key_to_char(key)
        if char:
            with self._lock:
                self._held.discard(char)

    @staticmethod
    def _key_to_char(key) -> str | None:
        try:
            return key.char
        except AttributeError:
            # Special keys (space, esc, etc.)
            if key == pynput_kb.Key.space:
                return ' '
            if key == pynput_kb.Key.esc:
                return '\x1b'
        return None

    def _is_held(self, char: str) -> bool:
        with self._lock:
            return char in self._held

    def poll_inputs(self) -> None:
        """
        Updates active action and speed from the current held key state.
        Also calls cv2.waitKey(1) to keep the OpenCV window responsive.
        """
        # Service OpenCV window events (must run on main thread)
        inputs.InputManager.poll()

        # Check exit keys
        if self._is_held('\x1b') or self._is_held('q'):
            self.running = False
            return

        # Speed selection (last wins)
        for char, (name, val) in self._SPEED_KEYS.items():
            if self._is_held(char):
                self.speed_name = name
                self.speed_val = val

        # Movement (space = STOP, movement keys override)
        action = "STOP"
        if self._is_held(' '):
            action = "STOP"
        else:
            for char, act in self._MOVE_KEYS.items():
                if self._is_held(char):
                    action = act
                    break

        self.active_action = action

    def stop(self) -> None:
        """Stop the background listener thread."""
        if hasattr(self, '_kb_listener'):
            self._kb_listener.stop()
