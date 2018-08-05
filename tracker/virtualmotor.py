import numpy as np

class VirtualMotor:
    """Virtual motor object to simulate acceleration/inertia."""

    def __init__(self, accel_max, velocity_max):
        self.accel_max = accel_max
        self.velocity_max = velocity_max

        self.position = 0.0
        self.velocity = 0.0
        self.velocity_setpoint = 0.0

    def set_velocity_setpoint(self, velocity_setpoint):
        self.velocity_setpoint = velocity_setpoint

    def update(self, dt):
        dv = np.clip(self.velocity_setpoint - self.velocity,
            -self.accel_max * dt,
             self.accel_max * dt)
        self.velocity = np.clip(self.velocity + dv,
            -self.velocity_max,
             self.velocity_max)
        self.position += dt * self.velocity
