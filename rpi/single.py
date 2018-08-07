from time import perf_counter

import pigpio

from stepper import Stepper

pi = pigpio.pi()
if not pi.connected:
    exit()

try:
    # look into negative velocity bug?
    #   stepper.set_velocity_setpoint(-1000)
    #   stepper.set_acceleration(500)
    stepper = Stepper(pi, 16, 20, 21, 2000, 5000)
    state = 0
    #stepper2 = Stepper(pi, 13, 19, 26)
    #stepper2.set_velocity_setpoint(4000)

    pairs = [
        (1000, 1), 
        (0, 5)]

    prev_time = perf_counter()

    while True:
        v, t = pairs[state % len(pairs)]
        stepper.set_velocity_setpoint(v)

        curr_time = perf_counter()
        if curr_time - prev_time >= t:
            state += 1
            prev_time = curr_time

        stepper.run()

except KeyboardInterrupt:
    print("\nExiting...")
     # TODO: Switch ENA back to high

finally:
    pi.write(16, 1)
    print("done")
