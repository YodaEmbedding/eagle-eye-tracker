#!/usr/bin/env python3

from multiprocessing import Process
import pigpio
import time
import math

from rpi.client import CommClient
from rpi.commcomm import CommComm
from rpi.stepper import Stepper
from rpi.steppercomm import StepperComm
from rpi.laser import Laser

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

def run_comm(comm_comm):
    while True:
        comm_comm.run()

if __name__ == '__main__':

    pi = pigpio.pi()
    if not pi.connected:
        exit()

    laser = Laser(pi, 23)
    laser.laser_off()
    comm_comm = CommComm()
    steppers = [
        Stepper(pi, 13, 19, 26, accel_max=16000, velocity_max=4000),
        Stepper(pi, 16, 20, 21, accel_max=16000, velocity_max=4000)]

    coordinate_generator = CoordinateGenerator(lambda:
        (comm_comm.latest_coord_x_s.value, comm_comm.latest_coord_y_s.value))

    stepper_comms = [StepperComm(s.accel_max_rad, s.velocity_max_rad) for s in steppers]
    motor_phi = Motor(stepper_comms[0], direction=1,  bound_min=-0.3*math.pi, bound_max=0.3*math.pi)
    motor_th  = Motor(stepper_comms[1], direction=-1, bound_min=-0.3*math.pi, bound_max=0.0)

    motion_controller = MotionController(coordinate_generator,
        motor_phi, motor_th)

    processes = (
        [Process(target=run_motor_func(s), args=sc.get_args())
           for s, sc in zip(steppers, stepper_comms)] +
        [Process(target=run_comm, args=(comm_comm,))])

    for p in processes:
        p.start()

    mc_prev_time = time.perf_counter()

    laser.laser_on()
    try:
        while True:
            curr_time = time.perf_counter()
            mc_dt = curr_time - mc_prev_time

            if mc_dt >= 2**-8:
                motion_controller.update(mc_dt)
                mc_prev_time = curr_time

            for x in stepper_comms:
                x.run()

    except KeyboardInterrupt:
        print("Exiting...")

    finally:
        steppers[0].enable_off()
        steppers[1].enable_off()
        laser.laser_off()
