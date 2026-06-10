"""
robot/aluxe3/manifest.py – Hardware configuration manifest.

Edit MOTOR_CONFIG to switch the active motor controller for both
the real hardware stack and the simulation sandbox simultaneously.
"""

# Active motor controller variant.
# Accepted values: "3W" (3-wheel omni) | "4W" (4-wheel omni)
MOTOR_CONFIG: str = "3W"
