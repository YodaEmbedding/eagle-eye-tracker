import pigpio

from stepper import Stepper

pi = pigpio.pi()
if not pi.connected:
    exit()

try:
    # look into negative velocity bug?
    #   stepper.set_velocity_setpoint(-1000)
    #   stepper.set_acceleration(500)
    stepper = Stepper(pi, 22, 27, 17, 2000, 5000)
    stepper.set_velocity_setpoint(4000)
    state = 0
    #stepper2 = Stepper(pi, 13, 19, 26)
    #stepper2.set_velocity_setpoint(4000)

    while True:
        if state == 0 and stepper.velocity == 4000:
            stepper.set_velocity_setpoint(-4000)
            state = 1
        if state == 1 and stepper.velocity == -4000:
            stepper.set_velocity_setpoint(4000)
            state = 2
        if state == 2 and stepper.velocity == 4000:
            stepper.set_velocity_setpoint(-4000)
            state = 3
        if state == 3 and stepper.velocity == -4000:
            stepper.set_velocity_setpoint(4000)
            state = 4
        stepper.run()
        #stepper2.run()

except KeyboardInterrupt:
    print("\nExiting...")
     # TODO: Switch ENA back to high

finally:
    pi.write(22, 1)
    print("done")
