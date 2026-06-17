"""
robot/aluxe3/manifest.py – Hardware configuration manifest for Aluxe3.

Declares which configs to use, resolves their paths, and exposes loaders
so runners never need to import resource utilities directly.

ROBOT_MODEL:str    – key for the hardware model JSON.
WORKSPACE_ENV:str  – key for the workspace/environment JSON.
"""
from __future__ import annotations
from pathlib import Path
from utils.resources.config import PROJECT_DIR
import utils.resources.model as model
import utils.resources.workspace as workspace

CONFIG_DIR:Path  = PROJECT_DIR / "robot" / "aluxe3" / "config"
MODEL_DIR:Path    = CONFIG_DIR / "models"
WORKSPACE_DIR:Path = CONFIG_DIR / "workspaces"

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
WORKSPACE_SIM_ENV:str = "sim"