import socket
import ssl
import threading
from chiffrement import vigenere

# Configuration du serveur
HOST_IP = socket.gethostbyname(socket.gethostname())
HOST_PORT = 5555
MAX_DATA_SIZE = 1024

# Liste des clients connectés et verrou pour la synchronisation
connected_clients = []
client_lock = threading.Lock()

# Création du socket serveur (NON sécurisé à ce stade)
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST_IP, HOST_PORT))
server_socket.listen(5)

# Configuration SSL
context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
context.load_cert_chain(certfile="certificate.pem", keyfile="private.key")

print(f"🔒 Secure Server listening on {HOST_IP}, port {HOST_PORT}")


def broadcast_message(message, sender_socket=None, client_address=None):
    """
    Envoie un message à tous les clients connectés, sauf à l'expéditeur.
    """
    with client_lock:
        disconnected_clients = []
        for client in connected_clients:
            if client != sender_socket:
                try:
                    message_serveur = f"{client_address} >> "
                    message_serveur += vigenere(message.decode("utf-8"), "RuariPotts", encrypt=False)
                    message_serveur = vigenere(message_serveur, "RuariPotts")
                    client.sendall(message_serveur.encode())
                except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
                    disconnected_clients.append(client)

        # Supprimer les clients déconnectés
        for client in disconnected_clients:
            connected_clients.remove(client)
            print(f"❌ Client removed: {client}")


def on_new_client(client_socket, client_address):
    """
    Gère la connexion d'un nouveau client via SSL.
    """
    print(f"🔗 New connection from {client_address}")

    # Appliquer SSL au socket client
    secure_client_socket = context.wrap_socket(client_socket, server_side=True)

    with client_lock:
        connected_clients.append(secure_client_socket)

    try:
        # Envoyer un message de bienvenue
        welcome_message = vigenere("Connected to the secure server!", "RuariPotts")
        secure_client_socket.sendall(welcome_message.encode())

        while True:
            msg = secure_client_socket.recv(MAX_DATA_SIZE)
            if not msg:
                break  # Déconnexion du client

            # Afficher le message décrypté sur le serveur
            print(f"{client_address} >> {msg.decode('utf-8')}")

            # Diffuser le message aux autres clients
            broadcast_message(msg, secure_client_socket, client_address)

    except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
        print(f"⚠️ Client {client_address} disconnected unexpectedly.")
    finally:
        # Nettoyage et fermeture
        with client_lock:
            if secure_client_socket in connected_clients:
                connected_clients.remove(secure_client_socket)
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
