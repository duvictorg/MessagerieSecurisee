import socket
import ssl
import threading
from chiffrement import rsa_encrypt, rsa_decrypt
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


def broadcast_message(message, sender_socket=None, sender_address=None):
    """
    Envoie un message à tous les clients connectés, sauf à l'expéditeur.
    Chaque message est chiffré avec la clé du client destinataire.
    """
    with client_lock:
        disconnected_clients = []
        for client_socket, client_key in connected_clients.items():
            if client_socket != sender_socket:
                try:
                    # Chiffrer le message avec la clé du client destinataire
                    message_serveur = f"{sender_address} >> "
                    message_serveur += rsa_decrypt(message, private_key)
                    encrypted_message = rsa_encrypt(message_serveur, client_key)
                    client_socket.sendall(encrypted_message.encode())
                except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
                    disconnected_clients.append(client_socket)

        # Supprimer les clients déconnectés
        for client_socket in disconnected_clients:
            del connected_clients[client_socket]
            print(f"❌ Client removed: {client_socket}")


def on_new_client(client_socket, client_address):
    """
    Gère la connexion d'un nouveau client via SSL.
    """
    print(f"🔗 New connection from {client_address}")

    # Appliquer SSL au socket client
    secure_client_socket = context.wrap_socket(client_socket, server_side=True)
    with open("public_key.pem", "r", encoding="utf-8") as fichier:
        public_key = fichier.read()

    client_key = secure_client_socket.recv(2048)
    client_key = client_key.decode('utf-8')

    # Ajouter le client au dictionnaire des clients connectés
    with client_lock:
        connected_clients[secure_client_socket] = client_key

    try:
        # Envoyer la clé de chiffrement au client
        secure_client_socket.sendall(f"[CLÉ]{public_key}".encode())

        # Envoyer un message de bienvenue
        welcome_message = rsa_encrypt("Connected to the secure server!", client_key)
        secure_client_socket.sendall(welcome_message.encode())

        while True:
            msg = secure_client_socket.recv(MAX_DATA_SIZE)
            if not msg:
                break  # Déconnexion du client
            print(f"{client_address} >> {msg.decode('utf-8')}")

            broadcast_message(msg.decode('utf-8'), secure_client_socket, client_address)

    except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
        print(f"⚠️ Client {client_address} disconnected unexpectedly.")
    finally:
        # Nettoyage et fermeture
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