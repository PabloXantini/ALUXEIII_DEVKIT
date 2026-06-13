from __future__ import annotations
import cv2
import threading
from enum import Enum, auto

class Key(Enum):
    W = auto()
    S = auto()
    A = auto()
    D = auto()
    Z = auto()
    X = auto()
    Q = auto()
    E = auto()
    R = auto()
    SPACE = auto()
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()
    ESC = auto()
    ENTER = auto()
    K_1 = auto()
    K_2 = auto()
    K_3 = auto()
    K_4 = auto()
    K_5 = auto()

class InputManager:
    def __init__(self, sandbox: bool, debug: bool):
        self.sandbox = sandbox
        self.debug = debug
        
        self._held: set[Key] = set()
        self._previous_held: set[Key] = set()
        
        if sandbox:
            import pygame
            self.pygame = pygame
            self._pygame_key_map = {
                Key.W: pygame.K_w,
                Key.S: pygame.K_s,
                Key.A: pygame.K_a,
                Key.D: pygame.K_d,
                Key.Z: pygame.K_z,
                Key.X: pygame.K_x,
                Key.Q: pygame.K_q,
                Key.E: pygame.K_e,
                Key.R: pygame.K_r,
                Key.UP: pygame.K_UP,
                Key.DOWN: pygame.K_DOWN,
                Key.LEFT: pygame.K_LEFT,
                Key.RIGHT: pygame.K_RIGHT,
                Key.SPACE: pygame.K_SPACE,
                Key.ESC: pygame.K_ESCAPE,
                Key.ENTER: pygame.K_RETURN,
                Key.K_1: pygame.K_1,
                Key.K_2: pygame.K_2,
                Key.K_3: pygame.K_3,
                Key.K_4: pygame.K_4,
                Key.K_5: pygame.K_5,
            }
        else:
            self._lock = threading.Lock()
            self._pynput_key_map = {
                'w': Key.W,
                's': Key.S,
                'a': Key.A,
                'd': Key.D,
                'z': Key.Z,
                'x': Key.X,
                'q': Key.Q,
                'e': Key.E,
                'r': Key.R,
                '' : Key.UP,
                '' : Key.DOWN,
                '' : Key.LEFT,
                '' : Key.RIGHT,
                ' ': Key.SPACE,
                '\x1b': Key.ESC,
                '\r': Key.ENTER,
                '\n': Key.ENTER,
                '1': Key.K_1,
                '2': Key.K_2,
                '3': Key.K_3,
                '4': Key.K_4,
                '5': Key.K_5,
            }
            self._start_pynput()

    def _start_pynput(self):
        try:
            from pynput import keyboard as pynput_kb
        except ImportError:
            return
        
        def on_press(key):
            char = self._key_to_char(key, pynput_kb)
            if char in self._pynput_key_map:
                with self._lock:
                    self._held.add(self._pynput_key_map[char])
        
        def on_release(key):
            char = self._key_to_char(key, pynput_kb)
            if char in self._pynput_key_map:
                with self._lock:
                    self._held.discard(self._pynput_key_map[char])

        self._kb_listener = pynput_kb.Listener(
            on_press=on_press,
            on_release=on_release,
            daemon=True
        )
        self._kb_listener.start()

    def _key_to_char(self, key, kb) -> str | None:
        try:
            return key.char
        except AttributeError:
            if key == kb.Key.space: return ' '
            if key == kb.Key.esc: return '\x1b'
            if key == kb.Key.enter: return '\n'
        return None

    def poll(self, wait_ms: int = 1) -> None:
        """Services OpenCV events and snapshots the keyboard state for instantaneous checks."""
        # OpenCV window responsiveness
        cv2.waitKey(wait_ms)
        
        if self.sandbox:
            self._previous_held = set(self._held)
            self.pygame.event.pump()
            keys = self.pygame.key.get_pressed()
            self._held.clear()
            for key_enum, py_key in self._pygame_key_map.items():
                if keys[py_key]:
                    self._held.add(key_enum)
        else:
            with self._lock:
                self._previous_held = set(self._held)

    def is_key_held(self, key: Key) -> bool:
        """Returns True if the key is currently held down."""
        if not self.sandbox:
            with self._lock:
                return key in self._held
        return key in self._held

    def is_key_pressed(self, key: Key) -> bool:
        """Returns True only on the frame the key was initially pressed."""
        if not self.sandbox:
            with self._lock:
                return key in self._held and key not in self._previous_held
        return key in self._held and key not in self._previous_held

    def is_key_released(self, key: Key) -> bool:
        """Returns True only on the frame the key was released."""
        if not self.sandbox:
            with self._lock:
                return key not in self._held and key in self._previous_held
        return key not in self._held and key in self._previous_held

def init(sandbox: bool, debug: bool) -> InputManager:
    return InputManager(sandbox, debug)