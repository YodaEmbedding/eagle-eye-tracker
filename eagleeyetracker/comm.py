import subprocess
import zmq

class Communicator(object):
    def __init__(self):
        self.context = zmq.Context()
        self.socket = context.socket(zmq.REQ)
        self.socket.connect('tcp://127.0.0.1:5555')

        subprocess.Popen(["py -2", "comm_server.py"])

    def format_msg(self, x, y):
        return '({},{})'.format(x, y)

    def send_msg(self, msg):
        self.socket.send(msg.encode('utf-8'))

    def send_coords(self, x, y):
        """Sends coordinates to microcontroller"""
        self.send_msg(self.format_msg(x, y))

