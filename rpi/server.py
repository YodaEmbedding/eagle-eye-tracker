import socket

IP = '169.254.203.248'
#IP = '192.168.1.122'
PORT = 12345
BUFFER_SIZE = 1024

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((IP, PORT))
sock.listen(1)
conn, addr = sock.accept()
print('Connection address:', addr)

while True:
    data = conn.recv(BUFFER_SIZE).decode()
    if not data:
        break
    print(data)
    conn.send(data.encode())

conn.close()
