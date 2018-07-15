# Credits to Mike McCauley's AccelStepper library, which is based off of the article below.
# https://www.embedded.com/design/mcus-processors-and-socs/4006438/Generate-stepper-motor-speed-profiles-in-real-time
import time
import math
import pigpio

class Stepper:
    DIRECTION_CCW = 0
    DIRECTION_CW = 1
    SWITCHDIR_SPEED = 100.0
    MICROSTEPS = 51200
    # def set_velocity_setpoint(self):
    #     accel_sign = np.sign(self.velocity_setpoint - self.velocity)
    #     self.acceleration = accel_sign * self.accel_max
    # JK NVM    cap accel depending on velocity

    # def basic_run(self):
    #     dt = time since last step
    #     step_interval = abs(self.velocity * dt)
    #     if step_interval >= 1:
    #         self._step()
    #         self.curr_pos += ???
    #         self.velocity = np.clip(self.velocity + self.acceleration * dt,
    #             -self.velocity_max,
    #              self.velocity_max)

    def __init__(self, pigpiod, ena_pin, dir_pin, step_pin, accel_max, velocity_max):
        self.pi = pigpiod

        # GPIO pin numbers (BCM)
        self.ena_pin = ena_pin
        self.dir_pin = dir_pin
        self.step_pin = step_pin

        # All in terms of steps
        self.curr_pos = 0
        self.velocity = 0.0
        self.velocity_setpoint = 1.0
        self.acceleration = 1.0

        self.step_interval = 0.0  # delay between steps
        self.last_step_time = 0.0
        self.dir = Stepper.DIRECTION_CW
        self.dir_flag = Stepper.DIRECTION_CW

        # Variables named after those used in article.
        self.n = 0  # step counter. Positive is accelerating, negative is deaccelerating.
        self.c_0 = 0.0  # initial timer comparison value in microseconds
        self.c_n = 0.0  # timer value for the nth step
        self.c_min = 1.0  # timer value at max velocity

        self.pi.set_mode(self.step_pin, pigpio.OUTPUT)
        self.pi.set_mode(self.dir_pin, pigpio.OUTPUT)
        self.pi.set_mode(self.ena_pin, pigpio.OUTPUT)
        self.pi.write(self.ena_pin, 0)  # Enable is active low.

        self.accel_max = accel_max
        self.set_acceleration(self.accel_max)
        self.velocity_max = velocity_max

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
        """Polling function that runs at most one step per call, none if step interval has not been reached."""
        if self._run_velocity():
            self._compute_new_velocity()

    def set_velocity_setpoint_rad(self, setpoint):
        self.set_velocity_setpoint(self._to_steps(setpoint))

    def set_velocity_setpoint(self, velocity):
        self.velocity_setpoint = 0.001 if velocity == 0 else abs(velocity)
        self.dir_flag = Stepper.DIRECTION_CCW if velocity < 0.0 else Stepper.DIRECTION_CW

        if (self.dir_flag != self.dir):
            print("deaccelerate to switchdir speed")
            self.c_min = 1000000.0 / Stepper.SWITCHDIR_SPEED
            self.n = -self.n
        else:
            self.c_min = 1000000.0 / self.velocity_setpoint

        if ((self.velocity_setpoint < self.velocity and self.n > 0) or
            (self.velocity_setpoint > self.velocity and self.n < 0)):
            self.n = -self.n

        self._compute_new_velocity()

    def set_acceleration(self, acceleration):
        if self.acceleration == acceleration:
            return
        self.n = self.n * (self.acceleration / acceleration)  # Equation 17
        self.c_0 = 0.676 * math.sqrt(2.0 / acceleration) * 1000000.0  # Equation 15
        self.acceleration = acceleration
        self._compute_new_velocity()

    def _run_velocity(self):
        """Update position and step if on time.

        Returns:
            True if successfully stepped"""

        if self.step_interval == 0.0:
            return False

        curr_time = time.perf_counter() * 1000000.0
        if curr_time - self.last_step_time < self.step_interval:
            return False

        # Step is due
        if self.dir == Stepper.DIRECTION_CW:
            self.curr_pos += 1
        else:
            self.curr_pos -= 1

        self._step()
        self.last_step_time = curr_time

        return True

    def _compute_new_velocity(self):
        """Determine next step_interval and update velocity.

        Typically called after each step, or changes to velocity setpoint, acceleration.
        """

        # First step
        if self.dir_flag != self.dir and self.velocity <= Stepper.SWITCHDIR_SPEED:
            print("switch dir and accelerate")
            self.dir = self.dir_flag
            self.n = abs(self.n)
            self.c_min = 1000000.0 / self.velocity_setpoint

        if self.n == 0 and self.velocity != self.velocity_setpoint:
            self.c_n = self.c_0
        else:
            self.c_n = self.c_n - ((2.0 * self.c_n) / ((4.0 * self.n) + 1))  # Equation 13

            if self.n > 0:
                self.c_n = max(self.c_n, self.c_min)
            else:
                self.c_n = min(self.c_n, self.c_min)

        self.n += 1
        self.step_interval = self.c_n
        self.velocity = 1000000.0 / self.c_n

        # print("velocity: " + str(self.velocity))
        # print("Acceleration: " + str(self.acceleration))
        # print("c_n: " + str(self.c_n))
        # print("c_0: " + str(self.c_0))
        # print("c_min " + str(self.c_min))
        # print("n: " + str(self.n))
        # print("Step Interval: " + str(self.step_interval))
        # print("Current Position: " + str(self.curr_pos))
        # print("-------------------------------")

    def _step(self):
        """Performs a step with pulse of minimal width."""
        self.pi.write(self.dir_pin, self.dir)
        self.pi.gpio_trigger(self.step_pin, 20, 1)

    def _to_radians(self, steps):
        degrees = steps * 1.8 / MICROSTEPS
        radians = degrees * math.pi / 180
        return radians

    def _to_steps(self, radians):
        degrees = radians * 180 / math.pi
        steps = degrees * MICROSTEPS / 1.8
        return steps

# TODO: reverse direction, drive faster! (switch modes?), to_rad, to_step
