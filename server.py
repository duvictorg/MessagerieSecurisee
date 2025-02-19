import socket
import subprocess
import threading

hostname = subprocess.check_output("hostname", shell=True).decode().strip()
HOST_IP = socket.gethostbyname(socket.gethostname())

HOST_PORT = 5555
MAX_DATA_SIZE = 1024

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

clients = []
clients_lock = threading.Lock()


def create_server():
    try:
        server_socket.bind((HOST_IP, HOST_PORT))
        server_socket.listen(5)
        print(f"Server listening on {HOST_IP}, port {HOST_PORT}")

        while True:
            print(f"Waiting for a connection on {HOST_IP}, port {HOST_PORT}")
            conn, addr = server_socket.accept()
            with clients_lock:
                clients.append(conn)

            print(f"New connection from {addr}")
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

    except Exception as e:
        print(f"Server error: {e}")
    finally:
        server_socket.close()


def handle_client(conn, addr):
    try:
        conn.sendall(b"Connected to the server.")

        while True:
            msg = conn.recv(MAX_DATA_SIZE)
            if not msg:
                break

            decoded_msg = msg.decode('utf-8')
            print(f"{addr} >> {decoded_msg}")

            message = f"{addr[0]} >> {decoded_msg}".encode('utf-8')
            broadcast(message)

    except ConnectionResetError:
        print(f"Client {addr} disconnected unexpectedly.")
    finally:
        with clients_lock:
            if conn in clients:
                clients.remove(conn)
        conn.close()
        print(f"Connection closed with {addr}")


def broadcast(message):
    with clients_lock:
        for client in clients[:]:
            client.send(message)

if __name__ == "__main__":
    create_server()
