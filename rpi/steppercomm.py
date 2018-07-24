from multiprocessing import Value

class StepperComm:
    def __init__(self, accel_max, velocity_max):
        self.position_s = Value('f', 0.0)
        self.velocity_s = Value('f', 0.0)
        self.velocity_setpoint_s = Value('f', 0.0)

        self.accel_max = accel_max
        self.velocity_max = velocity_max

    @property
    def position(self):
        return self.position_s.value

    @property
    def velocity(self):
        return self.velocity_s.value

    @property
    def velocity_setpoint(self):
        return self.velocity_setpoint_s.value

    def get_args(self):
        return self.position_s, self.velocity_s, self.velocity_setpoint_s

    def run(self):
        pass

    def set_velocity_setpoint(self, setpoint):
        self.velocity_setpoint_s.value = setpoint

    def update(self, dt):
        pass
