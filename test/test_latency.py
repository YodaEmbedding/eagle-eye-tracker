import pytest

from tracker.latency import Latency

class FakeTime:
    def __init__(self):
        self._time = 0.0

    def time(self):
        return self._time

    def sleep(self, t):
        self._time += t

def test_latency():
    time = FakeTime()

    class Latent:
        obj = Latency(0.1)
        def __init__(self):
            self.obj = 0
        def _time_func(self):
            return time.time()
    latent = Latent()

    # Slow update test
    for i in range(1, 10):
        latent.obj = i
        assert latent.obj != i
        time.sleep(0.05)
        assert latent.obj != i
        time.sleep(1.0)
        assert latent.obj == i

    # Fast update test
    # Cycle through numbers 0, 1, 2, 3, 4 repeatedly, 5x faster than the latency
    for i in range(5):
        latent.obj = i
        time.sleep(0.02)
    time.sleep(0.01)

    for j in range(5):
        for i in range(5):
            latent.obj = i
            print(j, i, latent.obj)
            assert latent.obj == i
            time.sleep(0.02)
        time.sleep(0.01)

