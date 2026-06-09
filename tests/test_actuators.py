"""
tests/test_actuators.py – Manual hardware test for physical actuators.

Uses RobotContext directly (sensors and camera threads start automatically).
No FSM is run — motors are driven by pygame keyboard events.
Canonical logs are printed to the terminal.

Usage (from project root on the Pi):
    python alux.py --test
    python tests/test_actuators.py
"""
from __future__ import annotations

import os
import sys
import time

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"
import pygame

# ─────────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────────

WIN_W, WIN_H = 560, 540

# Color palette
C_BG        = (14,  17,  23)
C_PANEL     = (22,  27,  34)
C_BORDER    = (40,  50,  65)
C_ACCENT    = (80, 180, 255)
C_GREEN     = (80, 220, 120)
C_YELLOW    = (255, 210,  60)
C_RED       = (255,  80,  80)
C_GRAY      = (120, 130, 145)
C_WHITE     = (230, 235, 245)
C_KEY_BG    = (35,  45,  60)
C_KEY_ACT   = (50, 140, 220)

_SPEED_LEVELS = {
    pygame.K_1: ("LOW",    20),
    pygame.K_2: ("MEDIUM", 40),
    pygame.K_3: ("HIGH",   60),
    pygame.K_4: ("MAX",    80),
}

_MOVE_KEYS = {
    pygame.K_w:     "FORWARD",
    pygame.K_s:     "BACKWARD",
    pygame.K_a:     "STRAFE LEFT",
    pygame.K_d:     "STRAFE RIGHT",
    pygame.K_q:     "SPIN LEFT",
    pygame.K_e:     "SPIN RIGHT",
    pygame.K_SPACE: "STOP",
}


# ─────────────────────────────────────────────────────────────────
# Terminal logger
# ─────────────────────────────────────────────────────────────────

def _log(msg: str) -> None:
    ts = time.strftime("%H:%M:%S")
    print(f"  [{ts}] {msg}", flush=True)


# ─────────────────────────────────────────────────────────────────
# Pygame UI renderer
# ─────────────────────────────────────────────────────────────────

class RemoteUI:
    def __init__(self, screen: pygame.Surface):
        self._screen = screen
        self._font_lg  = pygame.font.SysFont("monospace", 22, bold=True)
        self._font_md  = pygame.font.SysFont("monospace", 17)
        self._font_sm  = pygame.font.SysFont("monospace", 14)

    def _panel(self, rect: tuple, color=C_PANEL, border=C_BORDER) -> None:
        r = pygame.Rect(rect)
        pygame.draw.rect(self._screen, color, r, border_radius=8)
        pygame.draw.rect(self._screen, border, r, width=1, border_radius=8)

    def _text(self, txt: str, x: int, y: int, font=None, color=C_WHITE) -> None:
        f = font or self._font_md
        surf = f.render(txt, True, color)
        self._screen.blit(surf, (x, y))

    def _key_tile(self, label: str, x: int, y: int, active: bool = False, w: int = 50, h: int = 36) -> None:
        bg = C_KEY_ACT if active else C_KEY_BG
        r  = pygame.Rect(x, y, w, h)
        pygame.draw.rect(self._screen, bg, r, border_radius=6)
        pygame.draw.rect(self._screen, C_BORDER, r, width=1, border_radius=6)
        surf = self._font_sm.render(label, True, C_WHITE)
        self._screen.blit(surf, surf.get_rect(center=r.center))

    def draw(self, action: str, speed_name: str, speed_val: int, env) -> None:
        s = self._screen
        s.fill(C_BG)

        # ── Title ──────────────────────────────────────────────
        self._text("ALUXE III  –  Actuator Remote Control",
                   14, 14, self._font_lg, C_ACCENT)
        pygame.draw.line(s, C_BORDER, (14, 44), (WIN_W - 14, 44))

        # ── Status panel ───────────────────────────────────────
        self._panel((14, 54, WIN_W - 28, 100))
        act_color = C_GREEN if action != "STOP" else C_GRAY
        self._text(f"Action : {action}", 26, 66, color=act_color)
        self._text(f"Speed  : {speed_name}  ({speed_val}%)", 26, 90, color=C_YELLOW)
        self._text(f"Heading: {env.heading:6.1f}°", 300, 66, color=C_WHITE)

        # ── Sensor panel ───────────────────────────────────────
        self._panel((14, 166, WIN_W - 28, 80))
        self._text("Ultrasonic distances", 26, 174, self._font_sm, C_GRAY)

        def _d(v: float) -> str:
            return f"{v:5.1f} cm" if v >= 0 else "TIMEOUT"

        self._text(f"LEFT   {_d(env.us_left_dist)}", 26,  194, color=C_WHITE)
        self._text(f"BACK   {_d(env.us_back_dist)}", 210, 194, color=C_WHITE)
        self._text(f"RIGHT  {_d(env.us_right_dist)}", 390, 194, color=C_WHITE)

        # ── Key map ────────────────────────────────────────────
        self._panel((14, 260, WIN_W - 28, 220))
        self._text("Controls", 26, 268, self._font_sm, C_GRAY)

        pressed = pygame.key.get_pressed()

        # WASD + QE grid
        cx = 80   # center column x
        self._key_tile("Q", cx - 66, 292, pressed[pygame.K_q])
        self._key_tile("W", cx,      292, pressed[pygame.K_w])
        self._key_tile("E", cx + 66, 292, pressed[pygame.K_e])
        self._key_tile("A", cx - 66, 338, pressed[pygame.K_a])
        self._key_tile("S", cx,      338, pressed[pygame.K_s])
        self._key_tile("D", cx + 66, 338, pressed[pygame.K_d])
        self._key_tile("SPACE", cx - 33, 384, pressed[pygame.K_SPACE], w=116)

        # Labels
        self._text("Spin L",   cx - 80, 336, self._font_sm, C_GRAY)
        self._text("Spin R",   cx + 84, 336, self._font_sm, C_GRAY)
        self._text("Fwd / Back / Strafe", cx - 66, 430, self._font_sm, C_GRAY)

        # Speed keys
        self._text("Speed:", 320, 292, self._font_sm, C_GRAY)
        for i, (lbl, val) in enumerate([("1=LOW", 20), ("2=MED", 40),
                                         ("3=HIGH", 60), ("4=MAX", 80)]):
            active = (speed_val == val)
            self._key_tile(lbl, 320 + i * 56, 312, active, w=52)

        # ── Footer ─────────────────────────────────────────────
        pygame.draw.line(s, C_BORDER, (14, WIN_H - 36), (WIN_W - 14, WIN_H - 36))
        self._text("ESC / close window to exit", 14, WIN_H - 26, self._font_sm, C_GRAY)

        # ── Sensor mini label under status (160px gap) ─────────
        self._panel((14, 158, WIN_W - 28, 10), color=C_BG, border=C_BG)


# ─────────────────────────────────────────────────────────────────
# Remote control loop
# ─────────────────────────────────────────────────────────────────

def run_remote(ctx) -> None:
    pygame.init()
    screen = pygame.display.set_mode((WIN_W, WIN_H))
    pygame.display.set_caption("FUT_ALUX – Actuator Remote Control")
    clock  = pygame.time.Clock()
    ui     = RemoteUI(screen)

    motors      = ctx.actuators.motors
    speed_name  = "HIGH"
    speed_val   = 60
    current_act = "STOP"

    dispatch = {
        pygame.K_w:     lambda v: motors.go_forward(v),
        pygame.K_s:     lambda v: motors.go_backward(v),
        pygame.K_a:     lambda v: motors.go_left(v),
        pygame.K_d:     lambda v: motors.go_right(v),
        pygame.K_q:     lambda v: motors.spin_left(v),
        pygame.K_e:     lambda v: motors.spin_right(v),
        pygame.K_SPACE: lambda _: motors.stop(),
    }

    _log("Remote control started.")

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                elif event.key in _SPEED_LEVELS:
                    speed_name, speed_val = _SPEED_LEVELS[event.key]
                    _log(f"Speed → {speed_name} ({speed_val}%)")

                elif event.key in _MOVE_KEYS:
                    current_act = _MOVE_KEYS[event.key]
                    dispatch[event.key](speed_val)
                    _log(f"Motor → {current_act}  @{speed_val}%")

            elif event.type == pygame.KEYUP:
                if event.key in _MOVE_KEYS and event.key != pygame.K_SPACE:
                    motors.stop()
                    current_act = "STOP"
                    _log("Motor → STOP")

        ctx.compute()
        ui.draw(current_act, speed_name, speed_val, ctx.env)
        pygame.display.flip()
        clock.tick(30)

    motors.stop()
    pygame.quit()
    _log("Remote control exited.")

def run() -> None:
    from robot.aluxe3.context import RobotContext

    _log("Initializing robot context…")
    ctx = RobotContext()

    try:
        run_remote(ctx)
    except KeyboardInterrupt:
        ctx.actuators.motors.stop()
    finally:
        ctx.cleanup()
        _log("Done.")


if __name__ == "__main__":
    run()
