"""
robot/aluxe3/manifest.py – Hardware configuration manifest.

The variables below define the default config files for the robot model and workspace.
Changing them allows for easy configuration of different robot models and workspaces.

ROBOT_MODEL:str
WORKSPACE_ENV:str
"""
from utils.resources.config import PROJECT_DIR

CONFIG_DIR = PROJECT_DIR / "robot" / "aluxe3" / "config"
MODEL_DIR = CONFIG_DIR / "models"
WORKSPACE_DIR = CONFIG_DIR / "workspaces"
"""
The robot model in use.

Available models:
  - "alux3w1"  →  1st robot 3-wheel omnidirectional
  - "alux3w2"  →  2nd robot 3-wheel omnidirectional
  - "alux4w1"  →  1st robot 4-wheel omnidirectional
"""
ROBOT_MODEL:str = "alux3w1"
"""
The robot workspace envoriment to execute for competition and tests.

Available environments:
  - "salon" →  tests environment
  - "cup"   →  cup environment
"""
WORKSPACE_ENV:str = "salon"
