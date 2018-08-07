import math
import time
import numpy as np

import pigpio

class Stepper:
    """Control stepper motor on Raspberry Pi."""

    DIRECTION_CCW = 0
    DIRECTION_CW = 1
    STEPS_PER_REV = 51200.0

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

        self._is_initialized = False
        self.last_step_time = 0.0
        self.last_run_time = 0.0

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

        curr_time = time.perf_counter()
        dt_run = curr_time - self.last_run_time
        self.last_run_time = curr_time

        if not self._is_initialized:
            self._is_initialized = True
            return

        self.velocity = (min if self.acceleration > 0.0 else max)(
            self.velocity + self.acceleration * dt_run,
            self.velocity_setpoint)
        self.dir = (Stepper.DIRECTION_CW if self.velocity > 0.0 else
            Stepper.DIRECTION_CCW)

        dt_step = curr_time - self.last_step_time
        distance = abs(self.velocity * dt_step)

        # Step distance not reached
        if distance < 1.0:
            return

        self._step()
        self.position += 1 if self.velocity > 0.0 else -1
        self.last_step_time = curr_time

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
        self.pi.gpio_trigger(self.step_pin, 50, 1)

    def _to_radians(self, steps):
        """Converts steps to radians based on step size of motor driver."""
        radians = steps * 2 * math.pi / Stepper.STEPS_PER_REV
        return radians

    def _to_steps(self, radians):
        """Converts radians to steps."""
        steps = radians * Stepper.STEPS_PER_REV / (2 * math.pi)
        return steps

    def enable_off(self):
        self.pi.write(self.ena_pin, 1)

# TODO: drive faster! (switch modes?)
