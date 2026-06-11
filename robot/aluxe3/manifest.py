"""
robot/aluxe3/manifest.py – Hardware configuration manifest.

Set ROBOT_MODEL to the name of the desired config file (without .json)
located in robot/aluxe3/config/. The loader will raise a ConfigError at
startup if the file is missing or contains invalid fields.

Available models:
  - "alux3w"  →  3-wheel omnidirectional robot
  - "alux4w"  →  4-wheel omnidirectional robot
Available environments:
  - "salon" →  tests environment
  - "cup"   →  cup environment
"""

ROBOT_MODEL: str = "alux3w"
ENV_SETUP: str = "salon"
