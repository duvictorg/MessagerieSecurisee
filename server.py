import socket
import subprocess
from threading import Thread, Lock
from chiffrement import vigenere

# Configuration du serveur
hostname = subprocess.check_output("hostname", shell=True).decode().strip()
IP = socket.gethostbyname(hostname)
HOST_IP = str(IP)
HOST_PORT = 5555
MAX_DATA_SIZE = 1024

# Liste des clients connectés et verrou pour la synchronisation
connected_clients = []
client_lock = Lock()

# Création du socket serveur
server_socket = socket.socket()
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST_IP, HOST_PORT))
server_socket.listen(5)
print(f"Server listening on {HOST_IP}, port {HOST_PORT}")

def broadcast_message(message, sender_socket=None, client_address=None):
    """
    Envoie un message à tous les clients connectés, sauf à l'expéditeur.
    """
    with client_lock:
        for client in connected_clients:
            if client != sender_socket:  # Ne pas renvoyer le message à l'expéditeur
                try:
                    message_serveur = f"{client_address} >> "
                    message_serveur += vigenere(message.decode('utf-8'),'RuariPotts',encrypt=False)
                    message_serveur = vigenere(message_serveur,'RuariPotts')
                    client.sendall(message_serveur.encode())
                except (ConnectionResetError, ConnectionAbortedError):
                    # Si le client est déconnecté, retirez-le de la liste
                    connected_clients.remove(client)
                    print(f"Client disconnected: {client.getpeername()}")

def on_new_client(client_socket, client_address):
    """
    Gère la connexion d'un nouveau client.
    """
    print(f"Connection established with {client_address}")
    with client_lock:
        connected_clients.append(client_socket)  # Ajouter le client à la liste

    try:
        # Envoyer un message de bienvenue au client
        client_socket.sendall(bytes(vigenere("Connected to the server!","RuariPotts"), "utf-8"))

        while True:
            # Recevoir un message du client
            msg = client_socket.recv(MAX_DATA_SIZE)
            if not msg:
                break  # Si le message est vide, le client s'est déconnecté

            # Afficher le message sur le serveur
            print(f"{client_address} >> {msg.decode('utf-8')}")

            # Diffuser le message à tous les autres clients
            broadcast_message(msg, client_socket,client_address)

    except (ConnectionResetError, ConnectionAbortedError):
        print(f"Client {client_address} disconnected abruptly.")
    finally:
        # Fermer la connexion et retirer le client de la liste
        with client_lock:
            if client_socket in connected_clients:
                connected_clients.remove(client_socket)
        client_socket.close()
        print(f"Connection closed with {client_address}")

def create_server():
    """
    Accepte les connexions entrantes et démarre un thread pour chaque client.
    """
    while True:
        print(f"Waiting for a connection on {HOST_IP}, port {HOST_PORT}")
        client_socket, client_address = server_socket.accept()
        thread = Thread(target=on_new_client, args=(client_socket, client_address))
        thread.start()

# Démarrer le serveur
create_server()