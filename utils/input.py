from __future__ import annotations
import cv2

class InputManager:
    def __init__(self, sandbox: bool, debug: bool):
        self.sandbox = sandbox
        self.debug = debug
        if sandbox and debug:
            import pygame
            self.pygame = pygame

    @staticmethod
    def poll(wait_ms: int = 1) -> int:
        """Returns the raw ASCII keycode from the last OpenCV window event (255 if none)."""
        return cv2.waitKey(wait_ms) & 0xFF

    @staticmethod
    def key_polled(key_code: int, wait_ms: int = 1) -> bool:
        """Returns True if the given ASCII keycode was pressed in the last OpenCV window poll."""
        return InputManager.poll(wait_ms) == key_code

    def key_pressed(self, key_code: int) -> bool:
        """Returns True if the key is currently held in Pygame (only when sandbox+debug)."""
        if self.debug and hasattr(self, 'pygame'):
            return bool(self.pygame.key.get_pressed()[key_code])
        return False

def init(sandbox: bool, debug: bool) -> InputManager:
    return InputManager(sandbox, debug)