"""
robot/aluxe3/manifest.py – Hardware configuration manifest.

Set ROBOT_MODEL to the name of the desired config file (without .json)
located in robot/aluxe3/config/. The loader will raise a ConfigError at
startup if the file is missing or contains invalid fields.

Available environments:
  - "salon" →  tests environment
  - "cup"   →  cup environment
"""
from utils.resources.config import PROJECT_DIR

CONFIG_DIR = PROJECT_DIR / "robot" / "aluxe3" / "config"
MODEL_DIR = CONFIG_DIR / "models"
ENV_DIR = CONFIG_DIR / "envs"
"""
The robot model in use.

Available models:
  - "alux3w"  →  3-wheel omnidirectional robot
  - "alux4w"  →  4-wheel omnidirectional robot
"""
ROBOT_MODEL:str = "alux3w"
"""
The robot workspace envoriment to execute for competition and tests.

Available environments:
  - "salon" →  tests environment
  - "cup"   →  cup environment
"""
WORKSPACE_ENV:str = "salon"
