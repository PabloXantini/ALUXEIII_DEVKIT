from __future__ import annotations

class MockUltrasonicSensor:
    """
    Mock of the ultrasonic sensor for the simulation environment.
    Currently, this component does nothing and returns 0.0.
    
    [Future Implementation Suggestion]
    To implement realistic simulation for this sensor, this mock should be given 
    access to the `SimState` (or passed as an argument to `get_distance`). 
    You can use raycasting starting from the robot's coordinates in the 
    direction the sensor is facing. By checking for intersection with boundaries
    (walls) or other robots/obstacles, you can compute the Euclidean distance 
    and return it.
    """
    def __init__(self, trig_pin: int = 0, echo_pin: int = 0):
        self._trig_pin = trig_pin
        self._echo_pin = echo_pin

    def get_distance(self) -> float:
        """Returns a simulated distance placeholder."""
        return 0.0

    def cleanup(self) -> None:
        pass
