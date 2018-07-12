from multiprocessing import Process, Pipe, Queue
import pigpio
import time

from stepper import Stepper
from steppercomm import StepperComm

pi = pigpio.pi()
if not pi.connected:
    exit()

steppers = [
    Stepper(pi, 16, 20, 21),
    Stepper(pi, 13, 19, 26)]

steppers[0].set_velocity_setpoint(4000)
steppers[0].set_acceleration(1000)

steppers[1].set_velocity_setpoint(4000)
steppers[1].set_acceleration(1000)

def run_motor_func(stepper):
    def run_motor(queue_in, queue_out):
        while True:
            stepper.run()
            queue_out.put((stepper.curr_pos, stepper.velocity))
            # TODO it's OK to call set_velocity_setpoint probably...
            if queue_in.empty():
                continue
            while not queue_in.empty():
                vel_setpoint = queue_in.get()
            stepper.set_velocity_setpoint(vel_setpoint)
    return run_motor

if __name__ == '__main__':    
    try:
        stepper_comms = [StepperComm() for s in steppers]

        processes = [Process(target=run_motor_func(s), args=sc.get_args())
            for s, sc in zip(steppers, stepper_comms)]

        for p in processes:
            p.start()

        while True:
            for x in stepper_comms:
                x.run()
                print(x.position)
                x.set_velocity_setpoint(4000)

    except KeyboardInterrupt:
        print("Exiting...")
        pi.stop()
