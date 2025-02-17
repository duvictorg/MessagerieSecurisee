import socket
import subprocess


def create_server():
    hostname = subprocess.check_output("hostname", shell=True).decode()
    IP = socket.gethostbyname(hostname[:-2])
    HOST_IP = str(IP)
    HOST_PORT = 5555
    MAX_DATA_SIZE = 1024
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST_IP,HOST_PORT))
    s.listen(5)
    while True:
        print(f"Attente de connection sur {HOST_IP}, port {HOST_PORT} ")
        connection_socket, client_address = s.accept()
        print(f"Connexion établie avec {client_address}")
        connection_socket.sendall(bytes("Connecté", "utf-8"))

create_server()

