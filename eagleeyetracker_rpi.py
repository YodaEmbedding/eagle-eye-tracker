#!/usr/bin/env python3

import multiprocessing as mp

from rpi.client import CommClient
from simulation.coordinategenerator import CoordinateGenerator
from simulation.motioncontroller import MotionController
from simulation.motor import Motor

# TODO adapter with CoordinateGenerator (which, btw, is a really terrible name)
comm = CommClient()

# TODO assign proper params
# TODO use MotorAdapter? MotorAdapter(VirtualMotor())...
# something that works with multiprocess and also provides useful functions
motor_phi = Motor()
motor_th  = Motor()
coordinate_generator = CoordinateGenerator()

motion_controller = MotionController(coordinate_generator,
    motor_phi, motor_th)

# TODO Ensure processes are run on different cores? Kinda not the best idea...
# We probably only need one processor anyways...
# Not sure why we're multiprocessing this.
# Just assign thread priorities and ensure we interrupt at scheduled intervals
processes = [
    mp.Process(target=comm     .run, args=()),
    mp.Process(target=motor_phi.run, args=()),
    mp.Process(target=motor_th .run, args=())]

for p in processes:
    p.start()

while True:
    # TODO setup interval callback?
    if mc_dt >= 50 / 1000:
        motion_controller.update(mc_dt)

    # sync timer?

