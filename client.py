import socket
import threading
import tkinter as tk

# Créer la fenêtre principale
root = tk.Tk()
root.title("Channel de discussion")
root.geometry("400x500")
root.maxsize(400, 500)

label = tk.Label(root, text="Bonjour, Tkinter avec limites de redimensionnement!")
label.pack(pady=20)

chat_display = tk.Text(root, height=22, width=48, state=tk.DISABLED)
chat_display.pack(pady=10)

input_field = tk.Text(root, height=2, width=32)
input_field.place(relx=0.365, rely=1.0, anchor="s", x=-10, y=-10)
def envoyer_message():
    message = input_field.get("1.0", tk.END).strip()
    if message:
        chat_display.config(state=tk.NORMAL)
        chat_display.insert(tk.END, f"Vous: {message}\n")
        chat_display.config(state=tk.DISABLED)
        input_field.delete("1.0", tk.END)

button = tk.Button(root, text="Envoyer", width=15, height=2, command=envoyer_message)
button.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)
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
    root.mainloop()
    while client.running:
        pass

    client.disconnect()