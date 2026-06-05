import math

class MockCompass:
    """
    Simulated/Mock communication bridge for the GY-87 multi-sensor module.
    Reads orientation directly from the simulator's robot angle (rangle),
    which is set each frame by the physics engine.
    
    Author: PabloXantini
    """

    def __init__(self, bus_id=1):
        self.bus_id = bus_id
        # Heading in radians, updated each frame by SimContext or physics engine
        self._rangle: float = 0.0

    def set_rangle(self, rangle: float):
        """Update the current robot orientation angle (radians) from the simulator."""
        self._rangle = rangle

    def get_acceleration(self):
        """
        Simulates acceleration values for X, Y, Z axes.
        Returns:
            tuple: (accel_x, accel_y, accel_z) in g-forces (1g ≈ 9.81 m/s²).
        """
        # Static gravity-dominant reading (no drift in sim)
        return 0.0, 0.0, 1.0

    def get_gyro(self):
        """
        Simulates gyroscope rotation rate values for X, Y, Z axes.
        Returns:
            tuple: (gyro_x, gyro_y, gyro_z) in degrees per second (°/s).
        """
        return 0.0, 0.0, 0.0

    def get_rotation_w(self):
        """
        Returns rotation rate around the Z-axis (yaw rate 'w' / omega).
        Returns:
            float: Rotation speed around Z-axis in degrees per second.
        """
        _, _, gz = self.get_gyro()
        return gz

    def get_magnetometer(self):
        """
        Computes synthetic magnetometer readings based on the robot's rangle.
        Returns:
            tuple: (mag_x, mag_y, mag_z) in microteslas (uT).
        """
        # Simulate a magnetic north vector projected by the robot's current orientation
        mx = math.cos(self._rangle)
        my = math.sin(self._rangle)
        return mx, my, 0.0

    def get_heading(self) -> float:
        """
        Returns the robot's current absolute heading derived from its simulator angle.
        Returns:
            float: Heading angle in degrees [0, 360).
        """
        mx, my, _ = self.get_magnetometer()
        heading_rad = math.atan2(my, mx)

        # Normalize to 0-360 degrees
        if heading_rad < 0:
            heading_rad += 2 * math.pi

        return math.degrees(heading_rad)


# Abstract name matching the real bridge
Compass = MockCompass
