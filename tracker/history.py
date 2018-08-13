from collections import deque

class History:
    def __init__(self, max_age):
        self.max_age = max_age
        # TODO consider switching to RingBuffer if it's faster/reduces realloc?
        self.buffer = deque()
        self._time = 0.0

    def append(self, item, dt=0.0):
        """Update time and insert new item into history."""
        self.update(dt)
        self.buffer.append((self._time, item))
        self._trim()

    def get(self, dt):
        """Get latest item from a time of dt seconds ago."""
        return self.get_entry(dt)[1]

    def get_entry(self, dt):
        """Get latest entry from a time of dt seconds ago."""
        t_search = self._time - dt
        # return min(filter(lambda (t, x): t <= t_search, self.buffer),
        #     key=lambda t, x: t_search - t)
        return min(self.buffer, key=lambda kv: abs(t_search - kv[0]))

    def update(self, dt):
        """Increase internal timer by dt."""
        self._time += dt
        self._trim()

    def _trim(self):
        now = self._time
        expiration = now - self.max_age

        while len(self.buffer) > 1 and self.buffer[1][0] < expiration:
            self.buffer.popleft()
