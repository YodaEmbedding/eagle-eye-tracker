#!/usr/bin/env python2

import argparse

import nxt.bluesock
import zmq

parser = argparse.ArgumentParser()
parser.add_argument('--port', help='give me a port')
args = parser.parse_args()

class CommunicatorNXT(object):
    def __init__(self):
        self.remote_inbox = 1
        self.local_inbox = 2
        self.mac_address = '00:16:53:01:B8:C3'

        self.brick = nxt.bluesock.BlueSock(self.mac_address).connect()

    def send_msg(self, msg):
        self.brick.message_write(self.remote_inbox, msg)

context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect('tcp://127.0.0.1:' + str(args.port))

communicator = CommunicatorNXT()

while True:
    msg = "no message"
    try:
        socket.send('ready'.encode('utf-8'))
        msg = socket.recv().decode('utf-8')
    except Exception:
        pass
    communicator.send_msg(str(msg))
