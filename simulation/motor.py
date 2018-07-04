import numpy as np

from .coordinatemath import shortest_rad

class Motor:
    """Virtual motor object to simulate acceleration/inertia."""

    def __init__(self, velocity_max, accel_max):
        self.position = 0.0
        self.velocity = 0.0
        self.velocity_setpoint = 0.0
        self.accel_max    = accel_max
        self.velocity_max = velocity_max

    def get_stop_distance(self):
        return np.sign(self.velocity) * 0.5 * self.velocity**2 / self.accel_max

    def get_stop_position(self):
        return self.position + self.get_stop_distance()

    def recommend_accel(self, setpoint, nearest_angle=True):
        """Recommends an acceleration given desired position"""
        if nearest_angle:
            setpoint = self.to_nearest_angle(setpoint)
        diff = setpoint - self.get_stop_position()
        direction = np.sign(diff
            if diff != 0 else -self.velocity
            if self.position != setpoint else 0)
        return self.accel_max * direction

    def recommend_velocity(self, setpoint, nearest_angle=True):
        """Recommends a velocity given desired position"""
        return (np.sign(self.recommend_accel(setpoint, nearest_angle)) *
            self.velocity_max)

    def set_velocity_setpoint(self, velocity_setpoint):
        self.velocity_setpoint = velocity_setpoint

    def to_nearest_angle(self, angle):
        delta = shortest_rad(self.position, angle)
        return self.position + delta

    def update(self, dt):
        dv = np.clip(self.velocity_setpoint - self.velocity,
            -self.accel_max * dt,
             self.accel_max * dt)
        self.velocity = np.clip(self.velocity + dv,
            -self.velocity_max,
             self.velocity_max)
        self.position += dt * self.velocity

