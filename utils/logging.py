"""
utils/logging.py – Canonical robot logger.

Usage:
    from utils.logging import logger
    logger.msg("System ready")
    logger.warn("Low battery")
    logger.error("Sensor read failed")
    logger.fatal("Unrecoverable state")   # raises RuntimeError
"""

from __future__ import annotations

import time

class RobotLogger:
    """Structured canonical logger: msg / warn / error / fatal."""

    _TAGS = {
        "MSG":   ">",
        "WARN":  "!",
        "ERROR": "X",
        "FATAL": "✗",
    }

    def msg(self, text: str) -> None:
        self._emit("MSG", text)

    def warn(self, text: str) -> None:
        self._emit("WARN", text)

    def error(self, text: str) -> None:
        self._emit("ERROR", text)

    def fatal(self, text: str) -> None:
        """Emit a fatal-level log entry and raise RuntimeError."""
        self._emit("FATAL", text)
        raise RuntimeError(f"[FATAL] {text}")

    def _emit(self, level: str, text: str) -> None:
        ts  = time.strftime("%H:%M:%S")
        tag = self._TAGS[level]
        print(f"  [{ts}][{tag}] {text}", flush=True)

# Module-level singleton — import and use directly.
logger = RobotLogger()
