import numpy as np

# VirtualMotor... inherits from Motor?
class Motor:
    def __init__(self):
        self.position = 0.0
        self.velocity = 0.0
        self.velocity_setpoint = 0.0
        self.accel_max = 1.0
        self.velocity_max = 0.5

    def set_velocity_setpoint(self, velocity_setpoint):
        self.velocity_setpoint = velocity_setpoint

    def update(self, dt):
        dv = np.clip(self.velocity_setpoint - self.velocity,
            -self.accel_max * dt,
             self.accel_max * dt)
        self.velocity = np.clip(self.velocity + dv,
            -self.velocity_max, self.velocity_max)
        self.position += dt * self.velocity

