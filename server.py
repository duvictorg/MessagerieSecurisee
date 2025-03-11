import socket
import ssl
import threading
from chiffrement import rsa_encrypt, rsa_decrypt
from auth import authenticate_user, register_user
import os

# Configuration du serveur
HOST_IP = socket.gethostbyname(socket.gethostname())
HOST_PORT = 5555
MAX_DATA_SIZE = 1024

# Dictionnaire des clients connectés et verrou pour la synchronisation
connected_clients = {}  # Format : {client_socket: encryption_key}
client_lock = threading.Lock()

# Création du socket serveur
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST_IP, HOST_PORT))
server_socket.listen(5)

# Configuration SSL
context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
context.load_cert_chain(certfile="certificate.pem", keyfile="private.key")
with open("private.key", "r", encoding="utf-8") as fichier:
    private_key = fichier.read()

print(f"🔒 Secure Server listening on {HOST_IP}, port {HOST_PORT}")


def generate_encryption_key():
    """
    Génère une clé de chiffrement unique pour chaque client.
    """
    return os.urandom(16).hex()  # Clé de 16 octets (32 caractères hexadécimaux)


def broadcast_message(message, sender_socket=None, sender_username=None):
    """ Envoie un message à tous les clients sauf l'expéditeur """
    with client_lock:
        disconnected_clients = []
        for client_socket, client_key in connected_clients.items():
            if client_socket != sender_socket:
                try:
                    message_serveur = f"{sender_username} >> "
                    message_serveur += rsa_decrypt(message, private_key)
                    encrypted_message = rsa_encrypt(message_serveur, client_key)
                    client_socket.sendall(encrypted_message.encode())
                except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
                    disconnected_clients.append(client_socket)

        for client_socket in disconnected_clients:
            del connected_clients[client_socket]
            print(f"❌ Client removed: {client_socket}")

        # Supprimer les clients déconnectés
        for client_socket in disconnected_clients:
            del connected_clients[client_socket]
            print(f"❌ Client removed: {client_socket}")


def on_new_client(client_socket, client_address):
    print(f"🔗 New connection from {client_address}")

    secure_client_socket = context.wrap_socket(client_socket, server_side=True)
    with open("public_key.pem", "r", encoding="utf-8") as fichier:
        public_key = fichier.read()

    client_key = secure_client_socket.recv(2048)
    client_key = client_key.decode('utf-8')
    try:
        response = secure_client_socket.recv(2048).decode('utf-8')

        if response.startswith("[REGISTER]"):
            _, username, password = response.split(":")
            success, message = register_user(username, password)
            secure_client_socket.sendall(message.encode())
            if not success:
                secure_client_socket.close()
                return

        elif response.startswith("[LOGIN]"):
            _, username, password = response.split(":")
            success, message = authenticate_user(username, password)
            secure_client_socket.sendall(message.encode())
            if not success:
                secure_client_socket.close()
                return
        else:
            secure_client_socket.sendall("❌ Commande invalide !".encode())
            secure_client_socket.close()
            return

        # Authentification réussie, on stocke le client
        with client_lock:
            connected_clients[secure_client_socket] = client_key
        # Envoyer la clé de chiffrement au client
        secure_client_socket.sendall(f"[CLÉ]{public_key}".encode())

        # Envoyer un message de bienvenue
        welcome_message = rsa_encrypt("Connected to the secure server!", client_key)
        secure_client_socket.sendall(welcome_message.encode())

        while True:
            msg = secure_client_socket.recv(MAX_DATA_SIZE)
            if not msg:
                break
            print(f"{username} >> {msg.decode('utf-8')}")
            broadcast_message(msg.decode('utf-8'), secure_client_socket, username)

    except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
        print(f"⚠️ Client {client_address}")
        with client_lock:
            if secure_client_socket in connected_clients:
                del connected_clients[secure_client_socket]
        secure_client_socket.close()
        print(f"🔒 Connection closed with {client_address}")


def create_server():
    """
    Accepte les connexions entrantes et démarre un thread sécurisé pour chaque client.
    """
    while True:
        print(f"⌛ Waiting for a connection on {HOST_IP}, port {HOST_PORT}")
        client_socket, client_address = server_socket.accept()
        thread = threading.Thread(target=on_new_client, args=(client_socket, client_address))
        thread.start()


# Démarrer le serveur
create_server()