import numpy as np

class Motor:
    """Virtual motor object to simulate acceleration/inertia."""

    VEL_MAX = 2.0

    def __init__(self):
        self.position = 0.0
        self.velocity = 0.0
        self.velocity_setpoint = 0.0
        self.accel_max = 1.5
        self.velocity_max = Motor.VEL_MAX

    def get_stop_distance(self):
        return np.sign(self.velocity) * 0.5 * self.velocity**2 / self.accel_max

    def get_stop_position(self):
        return self.position + self.get_stop_distance()

    def recommend_accel(self, setpoint):
        """Recommends an acceleration given desired position"""
        diff = setpoint - self.get_stop_position()
        direction = np.sign(diff
            if diff != 0 else -self.velocity
            if self.position != setpoint else 0)
        return self.accel_max * direction

        # if diff != 0:
        #     return self.accel_max * np.sign(diff)
        # if self.position != setpoint:
        #     return self.accel_max * np.sign(-self.velocity)
        # return 0
        #
        # sign = (np.sign(diff)
        #     if diff != 0 else np.sign(-self.velocity)
        #     if self.position != setpoint else 0)
        # return sign * self.accel_max

    def recommend_velocity(self, setpoint):
        """Recommends a velocity given desired position"""
        return np.sign(self.recommend_accel(setpoint)) * self.velocity_max

        # if symmetric, we can do this easier...
        #
        # v_p = sqrt(2*a*(x_l + v_0**2/(2*a)))
        #     = sqrt(2*a*x_r)
        #
        # x = x_l + x_r
        #   = (v_p**2 - v_0**2 + v_p**2) / (2*a)
        #   = (v_p**2 / a) - (v_0**2 / (2*a))
        #
        # if v_0 = 0,
        # x = v_p**2 / a
        # v_p = sqrt(a*x)
        #
        # if v_0 =/= 0,
        # x = (v_p**2 / a) - (v_0**2 / (2*a))
        # v_p = sqrt(a*x + v_0**2 / 2)
        #
        # dx = setpoint - self.position
        # v_p = np.sqrt(self.accel_max * dx + self.velocity**2 / 2)

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

