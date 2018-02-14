#!/usr/bin/env python2

import nxt.bluesock
import zmq

class CommunicatorNXT(object):
    def __init__(self):
        self.remote_inbox = 1
        self.local_inbox = 2
        self.mac_address = '00:16:53:01:B8:C3'

        self.brick = nxt.bluesock.BlueSock(self.mac_address).connect()

    def send_msg(self, msg):
        self.brick.message_write(self.remote_inbox, msg)

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind('tcp://127.0.0.1:5555')

communicator = CommunicatorNXT()

while True:
    msg = socket.recv().decode('utf-8')
    communicator.send_msg(msg)

