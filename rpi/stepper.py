import math
import time
import numpy as np

import pigpio

class Stepper:
    """Control stepper motor on Raspberry Pi."""

    DIRECTION_CCW = 0
    DIRECTION_CW = 1
    MICROSTEPS = 51200

    def __init__(self, pigpiod, ena_pin, dir_pin, step_pin, accel_max, velocity_max):
        self.pi = pigpiod

        # GPIO pin numbers (BCM)
        self.ena_pin = ena_pin
        self.dir_pin = dir_pin
        self.step_pin = step_pin

        self.accel_max = accel_max
        self.velocity_max = velocity_max

        # All in terms of steps
        self.position = 0
        self.velocity = 0.0
        self.velocity_setpoint = 1.0
        self.acceleration = 1.0
        self.dir = Stepper.DIRECTION_CW

        self.state = 0
        self.last_step_time = 0.0

        self.pi.set_mode(self.step_pin, pigpio.OUTPUT)
        self.pi.set_mode(self.dir_pin, pigpio.OUTPUT)
        self.pi.set_mode(self.ena_pin, pigpio.OUTPUT)
        self.pi.write(self.ena_pin, 0)  # Enable is active low.

    @property
    def accel_max_rad(self):
        return self._to_radians(self.accel_max)

    @property
    def velocity_max_rad(self):
        return self._to_radians(self.velocity_max)

    @property
    def position_rad(self):
        return self._to_radians(self.position)

    @property
    def velocity_rad(self):
        return self._to_radians(self.velocity)

    def run(self):
        """Polling function that runs at most one step per call, none if step distance has not been reached."""
        if self.state == 0:
            self.last_step_time = time.perf_counter()
            self.velocity = self.acceleration / 10.0
            self.state = 1

        curr_time = time.perf_counter()
        dt = curr_time - self.last_step_time
        distance = abs(self.velocity * dt)

        # Step is due
        if distance >= 1.0:

            if self.velocity > 0.0:
                self.dir = Stepper.DIRECTION_CW
                self.position += 1
            else:
                self.dir = Stepper.DIRECTION_CCW
                self.position -= 1

            self._step()
            self.last_step_time = curr_time
            self.velocity = (min if self.acceleration > 0.0 else max)(self.velocity + self.acceleration * dt, self.velocity_setpoint)

    def set_velocity_setpoint_rad(self, velocity):
        """Set velocity that motors will accelerate/deaccelerate to, in radians."""
        self.set_velocity_setpoint(self._to_steps(velocity))

    def set_velocity_setpoint(self, velocity):
        accel_sign = np.sign(velocity - self.velocity)
        self.acceleration = accel_sign * self.accel_max
        self.velocity_setpoint = max(min(velocity, self.velocity_max), -self.velocity_max)
        # self.velocity_setpoint = np.clip(velocity, -self.velocity_max, self.velocity_max) # why is this ~50us slower?

    def _step(self):
        """Performs a step with pulse of minimal width."""
        self.pi.write(self.dir_pin, self.dir)
        self.pi.gpio_trigger(self.step_pin, 20, 1)

    def _to_radians(self, steps):
        """Converts steps to radians based on step size of motor driver."""
        degrees = steps * 1.8 / Stepper.MICROSTEPS
        radians = degrees * math.pi / 180
        return radians

    def _to_steps(self, radians):
        """Converts radians to steps."""
        degrees = radians * 180 / math.pi
        steps = degrees * Stepper.MICROSTEPS / 1.8
        return steps

# TODO: drive faster! (switch modes?)
