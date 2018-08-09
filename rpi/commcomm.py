from multiprocessing import Value

from rpi.client import CommClient

class CommComm:
    def __init__(self, comm=None):
        self.comm = comm if comm is not None else CommClient()
        self.latest_msg = None
        self.latest_prob_s    = Value('f', 0.0)
        self.latest_coord_x_s = Value('f', 0.0)
        self.latest_coord_y_s = Value('f', 0.0)

    def run(self):
        self.comm.recv_msg()
        self.latest_prob_s   .value = self.comm.latest_prob
        self.latest_coord_x_s.value = self.comm.latest_coord[0]
        self.latest_coord_y_s.value = self.comm.latest_coord[1]

        if not self.comm.connected:
            self.comm.connect()

    def update(self, dt):
        pass

    def get_args(self):
        return self.latest_prob_s, self.latest_coord_x_s, self.latest_coord_y_s

