import socket
import subprocess
from threading import Thread

hostname = subprocess.check_output("hostname", shell=True).decode().strip()
IP = socket.gethostbyname(hostname)
HOST_IP = str(IP)
HOST_PORT = 5555
MAX_DATA_SIZE = 1024
s = socket.socket()


def create_server():
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST_IP, HOST_PORT))
    s.listen(5)
    print(f"Server listening on {HOST_IP}, port {HOST_PORT}")

    while True:
        print(f"Waiting for a connection on {HOST_IP}, port {HOST_PORT}")
        connection_socket, client_address = s.accept()
        thread = Thread(target=on_new_client, args=(connection_socket, client_address))
        thread.start()


def on_new_client(connection_socket, client_address):
    print(f"Connection established with {client_address}")
    connection_socket.send(bytes("Connected", "utf-8"))

    while True:
        msg = connection_socket.recv(MAX_DATA_SIZE)
        if not msg:
            break
        print(f"{client_address} >> {msg.decode('utf-8')}")
        msg = f"{client_address[0]} >> {msg.decode('utf-8')}".encode()
        connection_socket.sendall(msg)

    print(f"Closing connection with {client_address}")
    connection_socket.close()


create_server()
