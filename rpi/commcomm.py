import re
from rpi.client import CommClient

class CommComm:
    def __init__(self, comm=None):
        self.comm = comm if comm is not None else CommClient()
        self.latest_msg = None
        self.latest_prob = 0.0
        self.latest_coord = (0.0, 0.0)

    def run(self):
        self.latest_msg = self.comm.recv_msg()
        #print(self.latest_msg)
        self._parse_msg()  # TODO shouldn't this just be part of a setter

    def update(self, dt):
        pass

    def _parse_msg(self):
        """Parses string of form (prob,x,y)"""
        # TODO handle illegal format?
        n = r'(\-?\d+\.?\d*)'
        regex = r'\({},\s*{},\s*{}\)'.format(n, n, n)
        matches = re.match(regex, self.latest_msg).groups()
        t = tuple(map(float, matches))
        self.latest_prob = t[0]
        self.latest_coord = t[1:3]
