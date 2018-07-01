import time
from collections import deque

class Latency:
    def __init__(self, latency, time_func=None):
        self.latency = latency
        self.buffer = deque()
        self._time_func = time_func if time_func is not None else time.time

    def __get__(self, instance, owner):
        self._trim()
        return self.buffer[0][1]

    def __set__(self, instance, value):
        self.buffer.append((self._time_func(), value))

    def _trim(self):
        now = self._time_func()
        expiration = now - self.latency

        while len(self.buffer) > 1 and self.buffer[1][0] < expiration:
            self.buffer.popleft()

# Decorator?
# setter, property?
# __setattr__? __call__ etc?

# Usage

# class Motor:
#     self.position = Latency(0.002)
#     # motor.position = Latency(motor.position)
#
# motor = Motor()
#
#
# motor.position = 420   # record time as well
# print(motor.position)  # delayed response
#
#
# # TODO consider... property()?
#
