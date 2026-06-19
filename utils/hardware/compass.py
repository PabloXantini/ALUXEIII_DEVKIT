import math

try:
    import smbus
except ImportError:
    from utils.mock import MockSMBus
    smbus = MockSMBus


# ── GY-87 Communication Bridge ───────────────────────────────────────────────

# MPU6050 I2C Address and Registers
MPU6050_ADDR = 0x68
PWR_MGMT_1   = 0x6B
INT_PIN_CFG  = 0x37
ACCEL_XOUT_H = 0x3B
GYRO_XOUT_H  = 0x43

# HMC5883L I2C Address and Registers (Magnetometer / Compass)
HMC5883L_ADDR = 0x1E
HMC_CONFIG_A  = 0x00
HMC_CONFIG_B  = 0x01
HMC_MODE      = 0x02
HMC_DATA_X_H  = 0x03


from utils.components import ICompass

class Compass(ICompass):
    """
    Communication bridge for the GY-87 multi-sensor module.
    Integrates MPU6050 (Accelerometer & Gyroscope) and enables bypass
    to talk to the HMC5883L (Magnetometer/Compass) chip.
    
    Author: PabloXantini (Placeholder as per guidelines)
    """

    def __init__(self, declination_angle=0.0, bus_id=1):
        # TODO: Placeholders for RPi customization by PabloXantini:
        # 1. Ensure I2C is enabled on Raspberry Pi: run 'sudo raspi-config' -> Interface Options -> I2C.
        # 2. Verify GY-87 is connected and check I2C addresses with: 'sudo i2cdetect -y 1'.
        # 3. Customize I2C bus number (default is 1) if using different RPi hardware.
        # 4. Calibration parameters for MPU6050 offset compensation can be adjusted here.
        self.bus_id = bus_id
        try:
            self.bus = smbus.SMBus(self.bus_id)
            self._init_mpu6050()
            self._init_hmc5883l()
        except Exception as e:
            # Fallback for systems without permission or real hardware
            print(f"[GY87Bridge] Warning: Failed to initialize real I2C bus {self.bus_id}: {e}")
            self.bus = None

    def set_rangle(self, rangle: float):
        """No-op on real hardware — rangle is read directly from IMU sensors."""
        pass

    def _init_mpu6050(self):
        """Wake up MPU6050 and enable I2C bypass mode to allow direct access to HMC5883L."""
        if self.bus is None:
            return
        try:
            # Wake up the MPU6050 (reset sleep mode)
            self.bus.write_byte_data(MPU6050_ADDR, PWR_MGMT_1, 0)
            
            # Enable I2C bypass on MPU6050 to expose HMC5883L directly on the main I2C bus
            self.bus.write_byte_data(MPU6050_ADDR, INT_PIN_CFG, 0x02)
        except Exception as e:
            print(f"[GY87Bridge] Error initializing MPU6050: {e}")

    def _init_hmc5883l(self):
        """Configure HMC5883L magnetometer for continuous measurements."""
        if self.bus is None:
            return
        try:
            # Configure Configuration Register A: 8-average, 15 Hz default, normal measurement
            self.bus.write_byte_data(HMC5883L_ADDR, HMC_CONFIG_A, 0x70)
            # Configure Configuration Register B: Gain = 1.3 Ga (default)
            self.bus.write_byte_data(HMC5883L_ADDR, HMC_CONFIG_B, 0x20)
            # Mode Register: Continuous-measurement mode
            self.bus.write_byte_data(HMC5883L_ADDR, HMC_MODE, 0x00)
        except Exception as e:
            print(f"[GY87Bridge] Error initializing HMC5883L: {e}")

    def _read_raw_word(self, addr, reg):
        """Read a 16-bit signed integer from I2C device registers."""
        if self.bus is None:
            return 0
        try:
            # GY-87 sensors output high byte first (MSB), then low byte (LSB)
            high = self.bus.read_byte_data(addr, reg)
            low = self.bus.read_byte_data(addr, reg + 1)
            val = (high << 8) | low
            if val >= 0x8000:
                val = -((65535 - val) + 1)
            return val
        except Exception:
            return 0

    def get_acceleration(self):
        """
        Gets the acceleration values for X, Y, Z axes.
        Returns:
            tuple: (accel_x, accel_y, accel_z) in g-forces (1g ≈ 9.81 m/s²).
        """
        # MPU6050 sensitivity scale factor for default ±2g range is 16384.0 LSB/g
        scale = 16384.0
        try:
            raw_x = self._read_raw_word(MPU6050_ADDR, ACCEL_XOUT_H)
            raw_y = self._read_raw_word(MPU6050_ADDR, ACCEL_XOUT_H + 2)
            raw_z = self._read_raw_word(MPU6050_ADDR, ACCEL_XOUT_H + 4)
            return raw_x / scale, raw_y / scale, raw_z / scale
        except Exception:
            return 0.0, 0.0, 0.0

    def get_gyro(self):
        """
        Gets the gyroscope rotation rate values for X, Y, Z axes.
        Returns:
            tuple: (gyro_x, gyro_y, gyro_z) in degrees per second (°/s).
        """
        # MPU6050 sensitivity scale factor for default ±250 °/s range is 131.0 LSB/(°/s)
        scale = 131.0
        try:
            raw_x = self._read_raw_word(MPU6050_ADDR, GYRO_XOUT_H)
            raw_y = self._read_raw_word(MPU6050_ADDR, GYRO_XOUT_H + 2)
            raw_z = self._read_raw_word(MPU6050_ADDR, GYRO_XOUT_H + 4)
            return raw_x / scale, raw_y / scale, raw_z / scale
        except Exception:
            return 0.0, 0.0, 0.0

    def get_magnetometer(self):
        """
        Gets raw magnetometer X, Y, Z readings from HMC5883L.
        Returns:
            tuple: (mag_x, mag_y, mag_z) in microteslas (uT) or raw units.
        """
        # HMC5883L data output registers are 0x03 through 0x08, in order X, Z, Y
        try:
            raw_x = self._read_raw_word(HMC5883L_ADDR, HMC_DATA_X_H)
            raw_z = self._read_raw_word(HMC5883L_ADDR, HMC_DATA_X_H + 2)
            raw_y = self._read_raw_word(HMC5883L_ADDR, HMC_DATA_X_H + 4)
            # Scale factor: default range of ±1.3 Ga corresponds to 1090 LSB/Gauss
            scale = 1090.0
            # 1 Gauss = 100 microteslas (uT)
            uT_factor = 100.0
            return (raw_x / scale) * uT_factor, (raw_y / scale) * uT_factor, (raw_z / scale) * uT_factor
        except Exception:
            return 0.0, 0.0, 0.0

    def get_angular_v(self):
        """
        Gets the angular velocity / rotation speed around the Z-axis (yaw rate 'w' / omega).
        Returns:
            float: Rotation speed around Z-axis in degrees per second.
        """
        # Gyroscope Z-axis measures the rotation rate around Z (yaw rate 'w' / omega)
        _, _, gz = self.get_gyro()
        return gz

    def get_heading(self):
        """
        Computes the current absolute heading (yaw/rotation relative to magnetic North).
        Returns:
            float: Heading angle in degrees [0, 360).
        """
        mx, my, _ = self.get_magnetometer()
        heading_rad = math.atan2(my, mx)
        
        # TODO: Placeholder for customizing RPi compass declination angle by PabloXantini:
        # Declination angle adjustment is required to convert Magnetic North to True North.
        # Find declination angle for your location (e.g. from http://www.magnetic-declination.com/).
        # Example: Declination = 0.08 radians
        declination_angle = 0.0
        heading_rad += declination_angle
        
        # Normalize to 0-360 degrees
        if heading_rad < 0:
            heading_rad += 2 * math.pi
        elif heading_rad > 2 * math.pi:
            heading_rad -= 2 * math.pi
            
        return math.degrees(heading_rad)
