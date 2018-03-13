#!/usr/bin/env python2

import time
import nxt.usbsock
import nxt.locator

class CommunicatorNXT(object):
    def __init__(self):
        self.remote_inbox = 1
        self.local_inbox  = 2
        self.mac_address = '00:16:53:01:B8:C3'
        # self.brick = nxt.usbsock.USBSock(self.mac_address).connect()
        self.brick = nxt.locator.find_one_brick()

    def send_test(self):
        for inbox in range(20):
            self.brick.message_write(inbox, "{} test\n".format(inbox))

    def recv_test(self):
        for inbox in range(20):
            try:
                print(inbox, self.brick.message_read(inbox, 0, remove=True))
            except nxt.error.DirProtError:
                pass

    def send_msg(self, msg):
        self.brick.message_write(self.remote_inbox, msg)

    def recv_msg(self):
        msg = self.brick.message_read(self.local_inbox, 0, remove=True)[1][:-1]
        return msg

    # Averages ~3ms ping from USB test
    def ping_test(self):
        start_time = time.clock()
        msg = "ping {}".format(start_time)
        communicator.send_msg(msg)

        while True:
            reply = ""
            try:
                reply = communicator.recv_msg()
                print(reply)
            except nxt.error.DirProtError:
                pass

            if reply == msg:
                print(time.clock() - start_time)
                return

communicator = CommunicatorNXT()

while True:
    communicator.ping_test()
    print('Ping test success!')

    # communicator.send_msg("PC says hi")
    # try:
    #     print(communicator.recv_msg())
    # except nxt.error.DirProtError as ex:
    #     print(ex)
    #     pass
