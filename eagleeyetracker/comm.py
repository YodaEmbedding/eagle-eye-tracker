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
                #print('server: waiting ; msg_out = ' + self.msg_out)
                status = self.socket.recv().decode('utf-8')
                if status == 'ready' and self.msg_out != "":
                    print('server: sending!')
                    self.socket.send(self.msg_out.encode('utf-8'))
                    print('server: sent!')
                    self.msg_out = ""
            except Exception:
                pass

    def format_msg(self, x, y):
        return '({},{})'.format(x, y)

    def send_msg(self, msg):
        self.msg_out = msg

        # try:
        #     # print('msg_out = ' + msg)
        #     # self.socket.send(msg.encode('utf-8'), flags=zmq.ZMQ_DONTWAIT)
        #     # self.socket.send(msg.encode('utf-8'))

        #     # msg = self.socket.recv(zmq.NOBLOCK).decode('utf-8')
        #     msg = self.socket.recv().decode('utf-8')
        #     if msg == 'ready':
        #         self.socket.send('ah ha!'.encode('utf-8'))
        # except Exception:
        #     # print('send_msg exception')
        #     pass

    def send_coords(self, x, y):
        """Sends coordinates to microcontroller"""
        self.send_msg(self.format_msg(x, y))

