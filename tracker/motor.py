import numpy as np

from .coordinatemath import shortest_rad
from .history import History

class Motor:
    """Provides interface with virtual or physical motor and other useful functionality"""

    def __init__(self, motor, direction=1, bound_min=-np.inf, bound_max=np.inf):
        self.motor = motor
        self.bound_min = bound_min
        self.bound_max = bound_max
        self.direction = direction

        self.position_history = History(5.0)

    @property
    def position(self):
        return self.direction * self.motor.position

    @property
    def velocity(self):
        return self.direction * self.motor.velocity

    @property
    def accel_max(self):
        return self.motor.accel_max

    @property
    def velocity_max(self):
        return self.motor.velocity_max

    def get_stop_distance(self):
        return np.sign(self.velocity) * 0.5 * self.velocity**2 / self.accel_max

    def get_stop_position(self):
        return self.position + self.get_stop_distance()

    def recommend_accel(self, setpoint, nearest_angle=True):
        """Recommends an acceleration given desired position"""
        if nearest_angle:
            setpoint = self.to_nearest_angle(setpoint)
        setpoint = self._constrain_bounds(setpoint)
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
        self.motor.set_velocity_setpoint(self.direction * velocity_setpoint)

    def to_nearest_angle(self, angle):
        delta = shortest_rad(self.position, angle)
        return self.position + delta

    def update(self, dt):
        self.motor.update(dt)
        self.position_history.append(self.position, dt)

    def _constrain_bounds(self, setpoint):
        return np.clip(setpoint, self.bound_min, self.bound_max)
