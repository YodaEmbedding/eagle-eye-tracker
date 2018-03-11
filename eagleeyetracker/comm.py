import subprocess
import threading
from time import sleep
import zmq

class Communicator(object):
    def __init__(self):
        self.msg_out = ""

        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)

        # TODO bind to random port
        port = 5555
        addr = 'tcp://127.0.0.1:' + str(port)
        self.socket.bind(addr)

        def worker():
            subprocess.call('py -2 ./eagleeyetracker/comm_server.py --port ' + str(port), shell=True)

        thread = threading.Thread(target=worker, daemon=True)
        thread.start()

        thread = threading.Thread(target=self.server, daemon=True)
        thread.start()

    def server(self):
        # TODO thread communication; race condition? doesn't matter?
        while True:
            try:
                # TODO make this... robust
                sleep(0.1)
                status = self.socket.recv().decode('utf-8')
                if status == 'ready' and self.msg_out != "":
                    self.socket.send(self.msg_out.encode('utf-8'))
                    self.msg_out = ""
            except Exception:
                pass

    def format_msg(self, x, y):
        return '({0},{1})'.format(int(1000 * x), int(1000 * y))

    def send_msg(self, msg):
        self.msg_out = msg

    def send_coords(self, x, y):
        """Sends coordinates to microcontroller"""
        self.send_msg(self.format_msg(x, y))
