import socket

class CommServer:
    IP = '169.254.171.204'  # ethernet
    #IP = '192.168.1.122'   # wifi
    PORT = 12345
    BUFFER_SIZE = 1024

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((CommServer.IP, CommServer.PORT))
        print("Listening on address: " + CommServer.IP)
        self.sock.listen(1)
        print("Waiting for connection...")
        self.conn, self.addr = self.sock.accept()
        print("Connection accepted.")

    def close(self):
        self.conn.close()

    def recv_msg(self):
        msg = self.conn.recv(CommServer.BUFFER_SIZE).decode()
        return msg

    def send_msg(self, msg):
        self.conn.send(msg.encode())

if __name__ == "__main__":
    comm = CommServer()
    print('Connection address:', comm.addr)

    while True:
        msg = comm.recv_msg()
        if not msg:
            break
        print(msg)
        comm.send_msg(msg)

    comm.close()

