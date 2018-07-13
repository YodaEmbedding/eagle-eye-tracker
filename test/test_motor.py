import pytest
from pytest import approx

from simulation.motor import Motor
from simulation.virtualmotor import VirtualMotor

def test_motor_recommended_accel():
    motor = Motor(VirtualMotor(accel_max=1.0, velocity_max=2.0))
    f = motor.recommend_accel
    zero = approx(0.0)

    # TODO you should run through ranges of addition from [-pi, pi]
    # and also for ... motor.velocity?
    # and a bunch of motor.positions if desired
    def asserts():
        pos_stop = motor.get_stop_position()
        assert f(setpoint=pos_stop + 1.0) >  0.0
        # assert f(setpoint=pos_stop      ) == zero  # TODO
        assert f(setpoint=pos_stop - 1.0) <  0.0

    asserts()

    motor.motor.position = 1.0
    asserts()

    motor.motor.velocity = 0.8
    asserts()

    motor.motor.velocity = -0.8
    asserts()

    motor.motor.position = -1.0
    asserts()

    # TODO also try with recommended velocity, running update,
    # then checking final pos
    # try a bunch of random values of different params

