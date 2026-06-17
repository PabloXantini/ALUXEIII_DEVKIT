class PIDController:
    def __init__(self, Kp:float, Ki:float, Kd:float) -> None:
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.last_e = 0
        self.acc_e = 0

    def calculate(self, setpoint:float, measured:float) -> float:
        error = setpoint - measured # < - Proportional
        self.acc_e += error         # < - Integral
        self.last_e = error         # < - Derivative
        return self.Kp * error + self.Ki * self.acc_e + self.Kd * self.last_e