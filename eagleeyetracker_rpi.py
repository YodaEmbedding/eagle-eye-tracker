#!/usr/bin/env python3

from multiprocessing import Process
import pigpio
import time
import math

from rpi.client import CommClient
from rpi.commcomm import CommComm
from rpi.stepper import Stepper
from rpi.steppercomm import StepperComm

from tracker.coordinategenerator import CoordinateGenerator
from tracker.motioncontroller import MotionController
from tracker.motor import Motor

# TODO might be cleaner to just put this inside stepper
def run_motor_func(stepper):
    def run_motor(position, velocity, velocity_setpoint):
        while True:
            stepper.run()
            position.value = stepper.position_rad
            velocity.value = stepper.velocity_rad
            stepper.set_velocity_setpoint_rad(velocity_setpoint.value)
    return run_motor

#def run_comm_func(comm):
#    def run_comm(queue_in, queue_out):
#        while True:
#            msg = comm.recv_msg()
#            queue_out.put((msg))
#            if queue_in.empty():
#                continue
#            while not queue_in.empty():
#                msg = queue_in.get()
#            comm.send_msg(msg)
#    return run_comm

if __name__ == '__main__':
    pi = pigpio.pi()
    if not pi.connected:
        exit()

    steppers = [
        Stepper(pi, 16, 20, 21, accel_max=2500, velocity_max=5000),
        Stepper(pi, 13, 19, 26, accel_max=2500, velocity_max=5000)]

    # TODO adapter with CoordinateGenerator (which, btw, is a really terrible name)
    #comm = CommClient()
    comm_comm = CommComm()
    coordinate_generator = CoordinateGenerator(lambda: comm_comm.latest_coord)

    stepper_comms = [StepperComm(s.accel_max_rad, s.velocity_max_rad) for s in steppers]
    motor_phi = Motor(stepper_comms[0], bound_min=-0.5*math.pi, bound_max=0.5*math.pi)
    motor_th  = Motor(stepper_comms[1], bound_min=-0.5*math.pi, bound_max=0.0)

    motion_controller = MotionController(coordinate_generator,
        motor_phi, motor_th)

    #processes = (
    #    [Process(target=run_motor_func(s), args=sc.get_args())
    #       for s, sc in zip(steppers, stepper_comms)] +
    #    [Process(target=run_comm_func(comm), args=comm_comm.get_args())])

    processes = [Process(target=run_motor_func(s), args=sc.get_args())
            for s, sc in zip(steppers, stepper_comms)]

    for p in processes:
        p.start()

    mc_prev_time = time.perf_counter()

    try:
        while True:
            comm_comm.run()
            curr_time = time.perf_counter()
            mc_dt = curr_time - mc_prev_time

            if mc_dt >= 2**-8:
                motion_controller.update(mc_dt)
                mc_prev_time = curr_time

            for x in stepper_comms:
                x.run()
                #print("Position: " + str(x.position))
                #print("Velocity: " + str(x.velocity))

    except KeyboardInterrupt:
        print("Exiting...")

    finally:
        steppers[0].enable_off()
        steppers[1].enable_off()

