import socket
import ssl
import threading
import tkinter as tk
from tkinter import simpledialog, messagebox, scrolledtext
from chiffrement import vigenere

class ChatClient:
    def __init__(self, host, port):
        self.cle_chiffrement = "RuariPotts"
        self.host = host
        self.port = port
        self.socket = None
        self.running = False
        self.receive_thread = None
        self.message_queue = []
        self.lock = threading.Lock()

    def connect(self):
        """
        Connecte le client au serveur sécurisé via SSL.
        """
        try:
            # Création d'un contexte SSL sécurisé
            context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
            context.check_hostname = False  # Désactive la vérification du nom d'hôte
            context.verify_mode = ssl.CERT_NONE  # Désactive la vérification du certificat (⚠ uniquement pour le test)

            self.socket = socket.create_connection((self.host, self.port))
            self.socket = context.wrap_socket(self.socket, server_hostname=self.host)

            self.running = True
            self.receive_thread = threading.Thread(target=self._receive_loop, daemon=True)
            self.receive_thread.start()
            return True
        except Exception as e:
            messagebox.showerror("Connection Error", f"Failed to connect: {str(e)}")
            return False

    def _receive_loop(self):
        """
        Boucle d'écoute des messages reçus du serveur.
        """
        while self.running:
            try:
                data = self.socket.recv(1024)
                if not data:
                    print("Server closed the connection.")
                    self.stop()
                    return

                # Décryptage du message reçu

                if data.decode("utf-8").startswith("[CLÉ]"):
                    self.cle_chiffrement = data[5:]
                    print(self.cle_chiffrement)
                else:
                    decrypted_data = vigenere(data.decode("utf-8"), self.cle_chiffrement, encrypt=False)
                    print(f"📩 Received: {decrypted_data}")  # Debugging

                    with self.lock:
                        self.message_queue.append(decrypted_data)

            except (ConnectionResetError, ConnectionAbortedError, ssl.SSLError) as e:
                print(f"⚠ Connection error: {e}")
                self.stop()
                return

    def get_messages(self):
        """
        Récupère et efface la liste des messages reçus.
        """
        with self.lock:
            messages = self.message_queue.copy()
            self.message_queue.clear()
        return messages

    def send(self, message):
        """
        Envoie un message chiffré au serveur.
        """
        try:
            encrypted_message = vigenere(message, self.cle_chiffrement)
            self.socket.sendall(encrypted_message.encode("utf-8"))
            return True
        except Exception as e:
            messagebox.showerror("Send Error", f"Failed to send message: {str(e)}")
            return False

    def stop(self):
        """
        Ferme proprement la connexion client.
        """
        if self.running:
            self.running = False
            try:
                if self.socket:
                    self.socket.close()
            except Exception:
                pass

class ChatGUI:
    def __init__(self, root, client):
        self.root = root
        self.client = client
        self.setup_gui()
        self.running = True
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.schedule_receive()

    def setup_gui(self):
        """
        Crée l'interface graphique du chat.
        """
        self.root.title("Secure Chat Client")
        self.root.geometry("500x600")
        self.root.minsize(400, 300)

        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.chat_history = scrolledtext.ScrolledText(
            main_frame, wrap=tk.WORD, state=tk.DISABLED
        )
        self.chat_history.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        input_frame = tk.Frame(main_frame)
        input_frame.pack(fill=tk.X)

        self.input_field = tk.Text(input_frame, height=3)
        self.input_field.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.input_field.bind("<Return>", self.on_enter_pressed)

        send_button = tk.Button(
            input_frame,
            text="Send",
            command=self.send_message,
            width=10
        )
        send_button.pack(side=tk.RIGHT)

    def on_enter_pressed(self, event):
        """
        Permet d'envoyer un message en appuyant sur "Enter".
        """
        if event.state & 0x0001:
            return  # Shift+Enter permet d'ajouter une nouvelle ligne
        self.send_message()
        return "break"  # Empêche le saut de ligne par défaut

    def append_message(self, message):
        """
        Ajoute un message reçu dans la zone d'affichage du chat.
        """
        self.chat_history.config(state=tk.NORMAL)
        self.chat_history.insert(tk.END, message + "\n")
        self.chat_history.config(state=tk.DISABLED)
        self.chat_history.see(tk.END)

    def send_message(self):
        """
        Récupère le message entré par l'utilisateur et l'envoie au serveur.
        """
        message = self.input_field.get("1.0", tk.END).strip()
        if message:
            if self.client.send(message):
                self.append_message(f"You: {message}")
                self.input_field.delete("1.0", tk.END)
        self.input_field.focus_set()

    def schedule_receive(self):
        """
        Vérifie toutes les 100 ms s'il y a de nouveaux messages à afficher.
        """
        if not self.running:
            return
        messages = self.client.get_messages()
        for msg in messages:
            self.append_message(msg)
        self.root.after(100, self.schedule_receive)

    def on_close(self):
        """
        Arrête proprement le client lorsqu'on ferme la fenêtre.
        """
        self.running = False
        self.client.stop()
        self.root.destroy()

class ConnectionDialog(simpledialog.Dialog):
    def body(self, master):
        """
        Affiche une boîte de dialogue pour entrer l'IP et le port du serveur.
        """
        tk.Label(master, text="Server IP:").grid(row=0, sticky=tk.W)
        tk.Label(master, text="Port:").grid(row=1, sticky=tk.W)

        self.ip_entry = tk.Entry(master)
        self.port_entry = tk.Entry(master)

        self.ip_entry.grid(row=0, column=1)
        self.port_entry.grid(row=1, column=1)

        self.ip_entry.insert(0, "127.0.0.1")
        self.port_entry.insert(0, "5555")
        return self.ip_entry

    def validate(self):
        """
        Valide l'IP et le port entrés.
        """
        host = self.ip_entry.get()
        port = self.port_entry.get()
        if not host or not port:
            messagebox.showwarning("Invalid Input", "Please fill both fields")
            return False
        try:
            port = int(port)
            if not (0 < port <= 65535):
                raise ValueError
        except ValueError:
            messagebox.showwarning("Invalid Port", "Port must be between 1-65535")
            return False
        return True

    def apply(self):
        self.host = self.ip_entry.get()
        self.port = int(self.port_entry.get())

def main():
    root = tk.Tk()
    root.withdraw()

    dialog = ConnectionDialog(root, "Connect to Server")
    if not hasattr(dialog, 'host'):
        return

    client = ChatClient(dialog.host, dialog.port)
    if not client.connect():
        return

    root.deiconify()
    ChatGUI(root, client)
    root.mainloop()

if __name__ == "__main__":
    main()
