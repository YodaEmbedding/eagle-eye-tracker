# Credits to Mike McCauley's AccelStepper library, which is based off of the article below.
# https://www.embedded.com/design/mcus-processors-and-socs/4006438/Generate-stepper-motor-speed-profiles-in-real-time
import time
import math
import pigpio


class Stepper:

    DIRECTION_CCW = 0
    DIRECTION_CW = 1

    def __init__(self, pigpiod, ena_pin, dir_pin, step_pin):
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

        # Variables named after those used in article.
        self.n = 0  # step counter. Positive is accelerating, negative is deaccelerating.
        self.c_0 = 0.0  # initial timer comparison value in microseconds
        self.c_n = 0.0  # timer value for the nth step
        self.c_min = 1.0  # timer value at max velocity

        self.pi.set_mode(self.step_pin, pigpio.OUTPUT)
        self.pi.set_mode(self.dir_pin, pigpio.OUTPUT)
        self.pi.set_mode(self.ena_pin, pigpio.OUTPUT)
        self.pi.write(self.ena_pin, 0)  # Enable is active low.

    # Polling function that runs at most one step per call, none if step interval has not been reached.
    def run(self):
        if self._run_velocity():
            self._compute_new_velocity()
        return self.velocity != 0.0

    def set_velocity_setpoint(self, velocity):
        # TODO: lock = acquire_lock()

        if self.velocity_setpoint == velocity:
            return
        # TODO: Deaccelerate before changing direction
        if velocity < 0.0:
            self.velocity_setpoint = -velocity
            self.dir = Stepper.DIRECTION_CCW
        else:
            self.velocity_setpoint = velocity
            self.dir = Stepper.DIRECTION_CW

        self.c_min = 1000000.0 / self.velocity_setpoint
        if (self.velocity_setpoint < self.velocity and self.n > 0) or \
                (self.velocity_setpoint > self.velocity and self.n < 0):
            self.n = -self.n
            self._compute_new_velocity()
        # lock.release()

    def set_acceleration(self, acceleration):
        if self.acceleration == acceleration:
            return
        self.n = self.n * (self.acceleration / acceleration)  # Equation 17
        self.c_0 = 0.676 * math.sqrt(2.0 / acceleration) * 1000000.0  # Equation 15
        self.acceleration = acceleration
        self._compute_new_velocity()

    def _run_velocity(self):
        if self.step_interval == 0.0:
            return False

        curr_time = time.perf_counter() * 1000000.0
        # Step is due.
        if curr_time - self.last_step_time >= self.step_interval:
            if self.dir == Stepper.DIRECTION_CW:
                self.curr_pos += 1
            else:
                self.curr_pos -= 1

            self._step()
            self.last_step_time = curr_time
            return True
        else:
            return False

    # Computes new velocity after each step, or changes to velocity setpoint, acceleration
    def _compute_new_velocity(self):
        # First step
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

    # Performs a step with pulse of minimal width.
    def _step(self):
        self.pi.write(self.dir_pin, self.dir)
        self.pi.gpio_trigger(self.step_pin, 20, 1)


pi = pigpio.pi()
if not pi.connected:
    exit()
try:
    # TODO: Drive two motors simulataneously.
    # Also look into negative velocity bug?
    #   stepper.set_velocity_setpoint(-1000)
    #   stepper.set_acceleration(500)
    stepper = Stepper(pi, 16, 20, 21)
    stepper.set_velocity_setpoint(4000)
    stepper.set_acceleration(500)
    state = 0

    while True:
        if state == 0 and stepper.velocity > 3000:
            print (" down ")
            stepper.set_velocity_setpoint(1000)
            state = 1
        if state == 1 and stepper.velocity == 1000:
            print (" up ")
            stepper.set_velocity_setpoint(2000)
            state = 2
        if state == 2 and stepper.velocity == 2000:
            print(" ccw ")
            stepper.set_velocity_setpoint(-1000)
            state = 3
        if state == 3 and stepper.velocity == 1000:
            print(" cw ")
            stepper.set_velocity_setpoint(4000)
            state = 4
        stepper.run()

except KeyboardInterrupt:
    print("\nExiting...")
    pi.stop() # TODO: Switch ENA back to high
