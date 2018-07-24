from multiprocessing import Process
import pigpio
import time
from random import randint

from stepper import Stepper
from steppercomm import StepperComm

pi = pigpio.pi()
if not pi.connected:
    exit()

steppers = [
    Stepper(pi, 16, 20, 21, 1000, 4000),
    Stepper(pi, 13, 19, 26, 1000, 4000)]

def run_motor_func(stepper):
    def run_motor(position, velocity, velocity_setpoint):
        while True:
            stepper.run()
            position.value = stepper.position
            velocity.value = stepper.velocity
            stepper.set_velocity_setpoint(velocity_setpoint.value)
    return run_motor

if __name__ == '__main__':
    try:
        stepper_comms = [StepperComm(s.accel_max_rad, s.velocity_max_rad) for s in steppers]

        processes = [Process(target=run_motor_func(s), args=sc.get_args())
            for s, sc in zip(steppers, stepper_comms)]

        for p in processes:
            p.start()

        while True:
            for x in stepper_comms:
                print(x.position)
                #print(x.velocity)
                x.set_velocity_setpoint(randint(-4000, 4000))

            time.sleep(10)

    except KeyboardInterrupt:
        print("Exiting...")
        pi.stop()
