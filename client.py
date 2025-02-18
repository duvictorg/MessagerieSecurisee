import tkinter as tk

"""
# Créer la fenêtre principale
root = tk.Tk()
root.title("Channel de discussion")
root.geometry("400x500")
root.maxsize(400, 500)

# Ajouter un label
label = tk.Label(root, text="Bonjour, Tkinter avec limites de redimensionnement!")
label.pack(pady=20)

# Ajouter un widget Text pour afficher les messages de chat
chat_display = tk.Text(root, height=22, width=48, state=tk.DISABLED)
chat_display.pack(pady=10)

# Ajouter un champ d'entrée
input_field = tk.Text(root, height=2, width=32)
input_field.place(relx=0.365, rely=1.0, anchor="s", x=-10, y=-10)

# Fonction pour afficher le texte saisi lorsque le bouton est cliqué
def envoyer_message():
    message = input_field.get("1.0", tk.END).strip()
    if message:
        chat_display.config(state=tk.NORMAL)
        chat_display.insert(tk.END, f"Vous: {message}\n")
        chat_display.config(state=tk.DISABLED)
        input_field.delete("1.0", tk.END)

# Ajouter un bouton en bas à droite avec une taille spécifique
button = tk.Button(root, text="Envoyer", width=15, height=2, command=envoyer_message)
button.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)

# Lancer la boucle principale de l'application
root.mainloop()
"""

# Import socket module
import socket

# Créer un objet socket
s = socket.socket()

# Définir l'adresse IP et le port du serveur
HOST_IP = '172.20.10.7'  # Remplacez par l'adresse IP du serveur
PORT = 5555

# Se connecter au serveur
s.connect((HOST_IP, PORT))
print(f"Connecté au serveur {HOST_IP}:{PORT}")

# Recevoir le message de bienvenue du serveur
welcome_message = s.recv(1024).decode('utf-8')
print(welcome_message)

# Boucle pour envoyer et recevoir des messages
while True:
    # Saisir un message à envoyer au serveur
    message = input("Vous : ")

    # Envoyer le message au serveur
    s.send(message.encode('utf-8'))

    # Recevoir la réponse du serveur
    data = s.recv(1024)
    if data:
        print(f"{data.decode('utf-8')}")
    else:
        print("Connexion fermée par le serveur.")
        break

# Fermer la connexion
s.close()