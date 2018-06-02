import socket
import time

IP = '169.254.203.248'  # ethernet
#IP = '192.168.1.122'   # wifi
PORT = 12345
BUFFER_SIZE = 1024

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((IP, PORT))
count = 0
t1 = time.time()
while count < 1000:
    sock.send(str(count).encode())
    data = sock.recv(BUFFER_SIZE).decode()
    print(data)
    count += 1
t2 = time.time()

print('Total time: ', t2 - t1, 'seconds')
print('Average time: ', (t2 - t1) / 1000, 'seconds')
sock.close()
