import socket
import threading

# Configuration du client
HOST = '172.20.10.7'  # Adresse IP du serveur
PORT = 5555         # Port du serveur
MAX_DATA_SIZE = 1024

class Client:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.running = False

    def connect(self):
        """Établit une connexion avec le serveur."""
        try:
            self.client_socket.connect((self.host, self.port))
            print(f"Connecté au serveur {self.host}:{self.port}")
            self.running = True
            # Démarrer les threads pour la réception et l'envoi de messages
            threading.Thread(target=self.receive_messages, daemon=True).start()
            threading.Thread(target=self.send_messages, daemon=True).start()
        except Exception as e:
            print(f"Erreur de connexion : {e}")

    def receive_messages(self):
        """Reçoit les messages du serveur en continu."""
        while self.running:
            try:
                message = self.client_socket.recv(MAX_DATA_SIZE).decode('utf-8')
                if not message:
                    print("Connexion au serveur perdue.")
                    self.running = False
                    break
                print(f"\nMessage reçu : {message}\n")
            except ConnectionResetError:
                print("Connexion au serveur perdue.")
                self.running = False
                break
            except Exception as e:
                print(f"Erreur lors de la réception du message : {e}")
                self.running = False
                break

    def send_messages(self):
        """Envoie des messages au serveur."""
        while self.running:
            try:
                message = input("Votre message : ")
                if message.lower() == "quit":
                    self.running = False
                    break
                self.client_socket.send(message.encode('utf-8'))
            except Exception as e:
                print(f"Erreur lors de l'envoi du message : {e}")
                self.running = False
                break

    def disconnect(self):
        """Ferme la connexion avec le serveur."""
        self.running = False
        self.client_socket.close()
        print("Déconnecté du serveur.")


if __name__ == "__main__":
    client = Client(HOST, PORT)
    client.connect()

    # Garder le programme principal en vie pour permettre aux threads de fonctionner
    while client.running:
        pass

    client.disconnect()