import socket

class CommClient:
    IP = '169.254.171.204'  # ethernet
    #IP = '192.168.1.122'   # wifi
    PORT = 12345
    BUFFER_SIZE = 1024

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((CommClient.IP, CommClient.PORT))

    def close(self):
        self.sock.close()

    def recv_msg(self):
        msg = self.sock.recv(CommClient.BUFFER_SIZE).decode()
        return msg

    def send_msg(self, msg):
        self.sock.send(msg.encode())

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
