"""
tests/test_actuators.py – Manual hardware test for physical actuators.

Uses RobotContext directly (sensors and camera threads are started automatically).
No FSM is run — motors are driven by keyboard input only.

Usage (from project root on the Pi):
    python alux.py --test
    python tests/test_actuators.py
"""
from __future__ import annotations

import os
import sys
import time
import queue
import threading
import tty
import termios

DIVIDER = "─" * 50

def _section(title: str) -> None:
    print(f"\n{DIVIDER}")
    print(f"  {title}")
    print(DIVIDER)

def _ok(msg: str) -> None:
    print(f"  [OK] {msg}")

def _info(msg: str) -> None:
    print(f"  [..] {msg}")


# ─────────────────────────────────────────────────────────────────
# Keyboard input thread — reads raw chars into a queue
# ─────────────────────────────────────────────────────────────────

class _KeyboardThread:
    """
    Reads single keystrokes in raw mode from stdin in a daemon thread.
    Characters are pushed into a thread-safe queue.
    """

    def __init__(self):
        self._queue  = queue.Queue()
        self._stop   = threading.Event()
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._fd     = sys.stdin.fileno()
        self._old    = termios.tcgetattr(self._fd)

    def start(self) -> None:
        tty.setraw(self._fd)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        termios.tcsetattr(self._fd, termios.TCSADRAIN, self._old)

    def get(self) -> str | None:
        """Return the next queued char, or None if empty."""
        try:
            return self._queue.get_nowait()
        except queue.Empty:
            return None

    def _loop(self) -> None:
        while not self._stop.is_set():
            try:
                ch = os.read(self._fd, 1).decode("utf-8", errors="ignore")
                self._queue.put(ch.lower())
            except Exception:
                break


# ─────────────────────────────────────────────────────────────────
# Status display (in-place update via ANSI)
# ─────────────────────────────────────────────────────────────────

_BINDINGS_HELP = """
  ┌─────────────────────────────────────────┐
  │          KEYBOARD REMOTE CONTROL        │
  │                                         │
  │           W  – Forward                  │
  │           S  – Backward                 │
  │           A  – Strafe Left              │
  │           D  – Strafe Right             │
  │           Q  – Spin Left                │
  │           E  – Spin Right               │
  │        SPACE  – Stop                    │
  │     1/2/3/4  – Speed: LOW/MED/HIGH/MAX  │
  │           X  – Exit                     │
  └─────────────────────────────────────────┘
"""

_SPEED_LEVELS = {
    "1": ("LOW",    20),
    "2": ("MEDIUM", 40),
    "3": ("HIGH",   60),
    "4": ("MAX",    80),
}

_STATUS_LINES = 6


def _fmt_dist(d: float) -> str:
    return f"{d:5.1f} cm" if d >= 0 else " TIMEOUT"


def _print_status_placeholder() -> None:
    for _ in range(_STATUS_LINES):
        print()


def _render_status(action: str, env, speed_name: str, speed_val: int) -> None:
    sys.stdout.write(f"\033[{_STATUS_LINES}A\033[J")  # move up + clear below
    sys.stdout.write(
        f"  Action  : {action:<16}  Speed: {speed_name} ({speed_val}%)\n"
        f"  Heading : {env.heading:6.1f}°\n"
        f"  US Left : {_fmt_dist(env.us_left_dist)}\n"
        f"  US Back : {_fmt_dist(env.us_back_dist)}\n"
        f"  US Right: {_fmt_dist(env.us_right_dist)}\n"
        f"  [W/S/A/D/Q/E=move  SPACE=stop  1-4=speed  X=exit]\n"
    )
    sys.stdout.flush()


# ─────────────────────────────────────────────────────────────────
# Remote control main loop
# ─────────────────────────────────────────────────────────────────

def run_remote(ctx) -> None:
    _section("KEYBOARD REMOTE CONTROL")
    print(_BINDINGS_HELP)

    motors      = ctx.actuators.motors
    speed_name  = "HIGH"
    speed_val   = 60
    current_act = "STOP"

    bindings = {
        "w": ("FORWARD",      lambda v: motors.go_forward(v)),
        "s": ("BACKWARD",     lambda v: motors.go_backward(v)),
        "a": ("STRAFE LEFT",  lambda v: motors.go_left(v)),
        "d": ("STRAFE RIGHT", lambda v: motors.go_right(v)),
        "q": ("SPIN LEFT",    lambda v: motors.spin_left(v)),
        "e": ("SPIN RIGHT",   lambda v: motors.spin_right(v)),
        " ": ("STOP",         lambda _: motors.stop()),
    }

    _print_status_placeholder()

    kb = _KeyboardThread()
    kb.start()

    try:
        while True:
            # ── Process all pending key events ──────────────────
            while True:
                ch = kb.get()
                if ch is None:
                    break

                if ch == "x":
                    motors.stop()
                    return

                if ch in _SPEED_LEVELS:
                    speed_name, speed_val = _SPEED_LEVELS[ch]
                elif ch in bindings:
                    current_act, fn = bindings[ch]
                    fn(speed_val)

            # ── Tick: update context + refresh display ───────────
            ctx.compute()
            _render_status(current_act, ctx.env, speed_name, speed_val)
            time.sleep(0.05)

    finally:
        kb.stop()
        print()
        _ok("Remote control exited.")


# ─────────────────────────────────────────────────────────────────
# Menu + entry point
# ─────────────────────────────────────────────────────────────────

_MENU = """
  1) Keyboard remote control (WASD + QE)
  q) Quit
"""


def run() -> None:
    from robot.aluxe3.context import RobotContext

    _info("Initializing robot context (sensors + camera threads start now)…")
    ctx = RobotContext()

    print("\n========================================")
    print("  FUT_ALUX – Manual Actuator Test Suite")
    print("========================================")

    try:
        while True:
            print(_MENU)
            choice = input("  Select > ").strip().lower()

            if choice == "q":
                break
            elif choice == "1":
                try:
                    run_remote(ctx)
                except KeyboardInterrupt:
                    ctx.actuators.motors.stop()
                    print("\n  [!] Interrupted.")
            else:
                print("  [!] Invalid option.")
    except KeyboardInterrupt:
        pass
    finally:
        ctx.cleanup()
        print("  Done.")


if __name__ == "__main__":
    run()
