import re
from rpi.client import CommClient

class CommComm:
    def __init__(self):
        self.comm = CommClient()
        self.latest_msg = None
        self.latest_coord = (0, 0)

    def run(self):
        self.latest_msg = self.comm.recv_msg()
        #print(self.latest_msg)
        self._parse_msg()  # TODO shouldn't this just be part of a setter

    def update(self, dt):
        pass

    def _parse_msg(self):
        m = re.match(r'\((\d+\.?\d*),(\d+\.?\d*)\)', self.latest_msg).groups()
        self.latest_coord = (float(m[0]), float(m[1]))

