import time

import matplotlib as mpl
import matplotlib.pyplot as plt
import pytest
from pytest import approx

from rpi.stepper import Stepper

plt.style.use('dark_background')

class PiMock:
    """Fake pigpio.pi"""

    def gpio_trigger(self, user_gpio, pulse_len=10, level=1):
        pass

    def set_mode(self, gpio, mode):
        pass

    def write(self, gpio, level):
        pass

def mock_time(dt=None, mem=[0.0]):
    """Fake time.perf_counter()."""
    if dt is not None:
        mem[0] += dt
    return mem[0]

def run(stepper, pre_func, dt, freq=100000):
    """Run stepper for specified time dt at given clock frequency."""
    for _ in range(int(round(dt * freq))):
        pre_func(stepper)
        stepper.run()
        mock_time(1 / freq)

def test_stepper(monkeypatch):
    monkeypatch.setattr(time, 'perf_counter', mock_time)
    stepper = Stepper(PiMock(), 0, 1, 2, accel_max=1000, velocity_max=4000)

    approx_ = lambda x: approx(x, rel=0.1, abs=0.1)

    times = []
    position_hist = []
    velocity_hist = []

    def update_hist(stepper):
        times.append(mock_time())
        position_hist.append(stepper.position)
        velocity_hist.append(stepper.velocity)

    def plot():
        fig, ax = plt.subplots()
        ax.set_title('test_stepper')
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Position / Velocity')
        ax.axhline(y=0, linewidth=1, color='w')
        ax.plot(times, position_hist, label="position")
        ax.plot(times, velocity_hist, label="velocity")
        ax.legend()
        fig.savefig('log/test_stepper.png', dpi=150)

    try:
        # Move CW direction
        stepper.set_velocity_setpoint(1000)

        run(stepper, update_hist, 1.0)
        assert stepper.dir == Stepper.DIRECTION_CW
        assert stepper.position > 0
        assert stepper.velocity == approx_(1000.0)

        # Reverse direction, but not instantaneously!
        stepper.set_velocity_setpoint(-1000)

        run(stepper, update_hist, 1e-3)
        assert stepper.dir == Stepper.DIRECTION_CW
        assert stepper.position > 0
        assert stepper.velocity < 1000

        run(stepper, update_hist, 1.0 - 1e-3)
        assert stepper.position > 0
        assert stepper.velocity == approx_(0.0)

        run(stepper, update_hist, 1e-3)
        assert stepper.dir == Stepper.DIRECTION_CCW
        assert stepper.position > 0

        run(stepper, update_hist, 1.0 - 1e-3)
        assert stepper.dir == Stepper.DIRECTION_CCW
        assert stepper.position > 0
        assert stepper.velocity < 0

        run(stepper, update_hist, 1.0)
        assert stepper.dir == Stepper.DIRECTION_CCW
        assert stepper.position < 0
        assert stepper.velocity < 0
    except AssertionError as e:
        plot()
        raise e

    plot()

