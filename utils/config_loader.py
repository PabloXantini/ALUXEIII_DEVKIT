"""
utils/config_loader.py – JSON hardware config loader.

Reads a robot model config file from robot/aluxe3/config/<model>.json and
validates the required sections. Raises descriptive errors on missing fields
or missing files so misconfigured deployments fail fast and clearly.

Usage:
    from utils.config_loader import ROBOT_CONFIG
"""

from __future__ import annotations

import json
from pathlib import Path

# Config files live in robot/aluxe3/config/ relative to the project root
_PROJECT_ROOT = Path(__file__).parent.parent
_CONFIG_DIR   = _PROJECT_ROOT / "robot" / "aluxe3" / "config"

# Required top-level sections and their mandatory keys
_REQUIRED_SECTIONS: dict[str, list[str]] = {
    "motors":     [],          # Keys validated per motor_config type by actuators
    "ultrasonic": ["back", "left", "right"],
    "compass":    ["bus_id"],
}

_REQUIRED_US_KEYS = ("trig", "echo")


class ConfigError(Exception):
    """Raised when the robot config file is invalid or incomplete."""


def _validate(cfg: dict, model: str) -> None:
    """Validate that all required keys are present in the loaded config dict."""
    for section, keys in _REQUIRED_SECTIONS.items():
        if section not in cfg:
            raise ConfigError(
                f"[{model}] Missing required section '{section}' in config."
            )
        for key in keys:
            if key not in cfg[section]:
                raise ConfigError(
                    f"[{model}] Missing key '{key}' inside section '{section}'."
                )

    # Validate each ultrasonic sensor entry has trig and echo
    for position, pins in cfg["ultrasonic"].items():
        for field in _REQUIRED_US_KEYS:
            if field not in pins:
                raise ConfigError(
                    f"[{model}] Ultrasonic '{position}' missing field '{field}'."
                )


def load_config(model: str) -> dict:
    """
    Load and validate the hardware config for the given robot model name.

    Args:
        model: Config filename without extension (e.g. 'alux3w').

    Returns:
        Parsed config dict.

    Raises:
        ConfigError: If the file does not exist or fails validation.
    """
    config_path = _CONFIG_DIR / f"{model}.json"

    if not config_path.exists():
        available = [p.stem for p in _CONFIG_DIR.glob("*.json")]
        raise ConfigError(
            f"Config file not found: '{config_path}'.\n"
            f"Available models: {available or ['(none)']}"
        )

    with open(config_path, "r", encoding="utf-8") as f:
        try:
            cfg = json.load(f)
        except json.JSONDecodeError as exc:
            raise ConfigError(
                f"[{model}] Config file is not valid JSON: {exc}"
            ) from exc

    _validate(cfg, model)
    return cfg


# ── Active robot config ───────────────────────────────────────────────────────
# Loaded once at import time from the model declared in manifest.py.
# Import this constant instead of calling load_config() directly.
from robot.aluxe3.manifest import ROBOT_MODEL   # noqa: E402
ROBOT_CONFIG: dict = load_config(ROBOT_MODEL)
