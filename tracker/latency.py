from collections import deque

# TODO consider using None as initial value before first value becomes readable?

class Latency:
    def __init__(self, latency):
        self.latency = latency
        self.buffer = deque()

    def __get__(self, instance, owner):
        self._trim(instance)
        return self.buffer[0][1]

    def __set__(self, instance, value):
        self.buffer.append((instance._time_func(), value))

    def _trim(self, instance):
        now = instance._time_func()
        expiration = now - self.latency

        while len(self.buffer) > 1 and self.buffer[1][0] < expiration:
            self.buffer.popleft()
