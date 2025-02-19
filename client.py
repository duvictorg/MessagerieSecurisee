import socket
import threading

HOST = '172.20.10.7'
PORT = 5555
MAX_DATA_SIZE = 1024

class Client:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.running = False

    def connect(self):
        try:
            self.client_socket.connect((self.host, self.port))
            print(f"Connecté au serveur {self.host}:{self.port}")
            self.running = True
            threading.Thread(target=self.receive_messages, daemon=True).start()
            threading.Thread(target=self.send_messages, daemon=True).start()
        except Exception as e:
            print(f"Erreur de connexion : {e}")

    def receive_messages(self):
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
        self.running = False
        self.client_socket.close()
        print("Déconnecté du serveur.")


if __name__ == "__main__":
    client = Client(HOST, PORT)
    client.connect()
    while client.running:
        pass

    client.disconnect()