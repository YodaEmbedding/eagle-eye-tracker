import re
import socket

class CommClient:
    IP = '169.254.171.204'  # ethernet
    #IP = '192.168.1.122'   # wifi
    PORT = 12345
    BUFFER_SIZE = 1024

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((CommClient.IP, CommClient.PORT))
        self.latest_msg = ""
        self.latest_prob  = 0.0
        self.latest_coord = (0.0, 0.0)

    def close(self):
        self.sock.close()

    def recv_msg(self):
        self.latest_msg = self.sock.recv(CommClient.BUFFER_SIZE).decode()
        self._parse_msg()
        return self.latest_msg

    def send_msg(self, msg):
        self.sock.send(msg.encode())

    def _parse_msg(self):
        """Parses string of form (prob,x,y)"""
        # TODO handle illegal format?
        n = r'(\-?\d+\.?\d*)'
        regex = r'\({},\s*{},\s*{}\)'.format(n, n, n)
        matches = re.match(regex, self.latest_msg).groups()
        t = tuple(map(float, matches))
        self.latest_prob = t[0]
        self.latest_coord = t[1:3]

if __name__ == "__main__":
    import time

    comm = CommClient()
    t1 = time.time()

    for i in range(1000):
        comm.send_msg(str(i))
        msg = comm.recv_msg()
        print(msg)

    t2 = time.time()
    comm.close()

    print('Total time: ', t2 - t1, 'seconds')
    print('Average time: ', (t2 - t1) / 1000, 'seconds')
