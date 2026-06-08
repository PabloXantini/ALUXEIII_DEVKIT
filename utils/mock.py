from __future__ import annotations

class MockGPIO:
    """Mock for RPi.GPIO to allow execution on non-embedded systems (Windows/Mac)."""
    BCM = 'BCM'
    OUT = 'OUT'
    IN = 'IN'
    HIGH = 1
    LOW = 0

    @staticmethod
    def setmode(mode):
        pass

    @staticmethod
    def setwarnings(flag):
        pass

    @staticmethod
    def setup(pin, mode):
        pass

    @staticmethod
    def output(pin, state):
        pass

    @staticmethod
    def input(pin):
        return 0

    @staticmethod
    def cleanup():
        pass

    class PWM:
        def __init__(self, pin, freq):
            pass
        def start(self, dc):
            pass
        def ChangeDutyCycle(self, dc):
            pass
        def stop(self):
            pass

class MockSMBus:
    """Mock for smbus to allow execution on non-embedded systems."""
    def __init__(self, bus=1):
        pass

    @staticmethod
    def SMBus(bus):
        return MockSMBus(bus)

    def write_byte_data(self, addr, cmd, val):
        pass

    def read_byte_data(self, addr, cmd):
        return 0

    def read_i2c_block_data(self, addr, cmd, length):
        return [0] * length
