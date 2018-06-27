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

        self.curr_pos = 0  # in steps
        self.target_pos = 0
        self.speed = 0.0  # in steps per sec
        self.speed_setpoint = 1.0
        self.acceleration = 1.0
        self.step_interval = 0.0  # delay between steps
        self.last_step_time = 0.0
        self.dir = Stepper.DIRECTION_CW

        # Variables named after those used in article.
        self.n = 0  # step counter. Positive is accelerating, negative is deaccelerating.
        self.c_0 = 0.0  # initial timer comparison value in microseconds
        self.c_n = 0.0  # timer value for the nth step
        self.c_min = 1.0  # timer value at max speed

        self.pi.set_mode(self.step_pin, pigpio.OUTPUT)
        self.pi.set_mode(self.dir_pin, pigpio.OUTPUT)
        self.pi.set_mode(self.ena_pin, pigpio.OUTPUT)
        self.pi.write(self.ena_pin, 0)  # Enable is active low.

    # Sets the target absolute position in steps.
    def move_to(self, absolute):
        if self.target_pos != absolute:
            self.target_pos = absolute
            self._compute_new_speed()

    def get_current_position(self):
        return self.curr_pos

    # Polling function that runs at most one step per call, none if step interval has not been reached.
    def run(self):
        if self.run_speed():
            self._compute_new_speed()
        return self.speed != 0.0 or self.get_distance_to_go() != 0

    def run_speed(self):
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

    def get_distance_to_go(self):
        return self.target_pos - self.curr_pos

    def set_speed_setpoint(self, speed):
        if self.speed_setpoint != speed:
            self.speed_setpoint = speed
            self.c_min = 1000000.0 / speed
            if self.n > 0:
                self.n = int((speed * speed) / (2.0 * self.acceleration))
                self._compute_new_speed()

    def set_acceleration(self, acceleration):
        if self.acceleration != acceleration:
            self.n = self.n * (self.acceleration / acceleration)  # Equation 17
            self.c_0 = 0.676 * math.sqrt(2.0 / acceleration) * 1000000.0  # Equation 15
            self.acceleration = acceleration
            self._compute_new_speed()

    # Computes new speed after each step, or changes to speed setpoint, acceleration, target position
    def _compute_new_speed(self):
        distance_to = self.get_distance_to_go()
        steps_to_stop = int((self.speed * self.speed) / (2.0 * self.acceleration))

        # Target reached, stop.
        if distance_to == 0 and steps_to_stop <= 1:
            self.step_interval = 0
            self.speed = 0.0
            self.n = 0
            return

        # Currently anticlockwise from target; go clockwise.
        if distance_to > 0:
            if self.n > 0:
                if steps_to_stop >= distance_to or self.dir == Stepper.DIRECTION_CCW:
                    self.n = -steps_to_stop
            elif self.n < 0:
                if steps_to_stop < distance_to and self.dir == Stepper.DIRECTION_CW:
                    self.n = -self.n

        # Currently clockwise from target; go anticlockwise.
        elif distance_to < 0:
            if self.n > 0:
                if steps_to_stop >= -distance_to or self.dir == Stepper.DIRECTION_CW:
                    self.n = -steps_to_stop
            elif self.n < 0:
                if steps_to_stop < -distance_to and self.dir == Stepper.DIRECTION_CCW:
                    self.n = -self.n

        # First step
        if self.n == 0:
            self.c_n = self.c_0
            self.dir = Stepper.DIRECTION_CW if distance_to > 0 else Stepper.DIRECTION_CCW
        else:
            self.c_n = self.c_n - ((2.0 * self.c_n) / ((4.0 * self.n) + 1))  # Equation 13
            self.c_n = max(self.c_n, self.c_min)

        self.n += 1
        self.step_interval = self.c_n
        self.speed = 1000000.0 / self.c_n

        # print("Speed: " + str(self.speed))
        # print("Acceleration: " + str(self.acceleration))
        # print("c_n: " + str(self.c_n))
        # print("c_0: " + str(self.c_0))
        # print("n: " + str(self.n))
        # print("Step Interval: " + str(self.step_interval))
        # print("Target Position: " + str(self.target_pos))
        # print("Current Position: " + str(self.curr_pos))
        # print("Distance To: " + str(distance_to))
        # print("Steps To Stop: " + str(steps_to_stop))
        # print("-------------------------------")

    # Performs a step with pulse of minimal width.
    def _step(self):
        self.pi.write(self.dir_pin, self.dir)
        self.pi.gpio_trigger(self.step_pin, 10, 1)


pi = pigpio.pi()
if not pi.connected:
    exit()
try:
    stepper = Stepper(pi, 16, 20, 21)
    stepper.set_speed_setpoint(5000)
    stepper.set_acceleration(500)
    stepper.move_to(25000)
    while True:
        if stepper.get_distance_to_go() == 0:
            stepper.move_to(-stepper.get_current_position())

        stepper.run()

except KeyboardInterrupt:
    print("\nExiting...")
    pi.stop()
