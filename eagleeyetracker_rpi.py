#!/usr/bin/env python3

from multiprocessing import Process, Queue
import pigpio
import time

from rpi.client import CommClient
from rpi.commcomm import CommComm
from rpi.stepper import Stepper
from rpi.steppercomm import StepperComm

from simulation.coordinategenerator import CoordinateGenerator
from simulation.motioncontroller import MotionController
from simulation.motor import Motor

def run_motor_func(stepper):
    def run_motor(queue_in, queue_out):
        while True:
            stepper.run()
            queue_out.put((stepper.position_rad, stepper.velocity_rad))
            # TODO it's OK to call set_velocity_setpoint probably...
            if queue_in.empty():
                continue
            while not queue_in.empty():
                setpoint = queue_in.get()
            stepper.set_velocity_setpoint_rad(setpoint)
    return run_motor

def run_comm_func(comm):
    def run_comm(queue_in, queue_out):
        while True:
            msg = comm.recv_msg()
            queue_out.put((msg))
            if queue_in.empty():
                continue
            while not queue_in.empty():
                msg = queue_in.get()
            comm.send_msg(msg)
    return run_comm

if __name__ == '__main__':
    pi = pigpio.pi()
    if not pi.connected:
        exit()

    steppers = [
        Stepper(pi, 16, 20, 21, accel_max=1000, velocity_max=4000),
        Stepper(pi, 13, 19, 26, accel_max=1000, velocity_max=4000)]

    steppers[0].set_acceleration(steppers[0].accel_max)
    steppers[1].set_acceleration(steppers[1].accel_max)

    # TODO adapter with CoordinateGenerator (which, btw, is a really terrible name)
    comm = CommClient()
    comm_comm = CommComm()
    coordinate_generator = CoordinateGenerator(lambda: comm.latest_coord)

    stepper_comms = [StepperComm(s.accel_max, s.velocity_max) for s in steppers]
    motor_phi = Motor(stepper_comm[0], bound_min=-0.5*np.pi, bound_max=0.5*np.pi)
    motor_th  = Motor(stepper_comm[1], bound_min=-0.5*np.pi, bound_max=0.0)

    motion_controller = MotionController(coordinate_generator,
        motor_phi, motor_th)

    processes = (
        [Process(target=run_motor_func(s), args=sc.get_args())
            for s, sc in zip(steppers, stepper_comms)] +
        [Process(target=run_comm_func(comm), args=comm_comm.get_args())])

    for p in processes:
        p.start()

    try:
        while True:
            comm_comm.run()

            if mc_dt >= 50 / 1000:
                motion_controller.update(mc_dt)

            for x in stepper_comms:
                x.run()

    except KeyboardInterrupt:
        print("Exiting...")
        pi.stop()
