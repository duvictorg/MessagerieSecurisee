import socket
import threading
import tkinter as tk
from tkinter import simpledialog, messagebox, scrolledtext

class ChatClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = None
        self.running = False
        self.receive_thread = None
        self.message_queue = []
        self.lock = threading.Lock()

    def connect(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.running = True
            self.receive_thread = threading.Thread(target=self._receive_loop, daemon=True)
            self.receive_thread.start()
            return True
        except Exception as e:
            messagebox.showerror("Connection Error", f"Failed to connect: {str(e)}")
            return False

    def _receive_loop(self):
        while self.running:
            try:
                data = self.socket.recv(1024).decode('utf-8')
                if not data:
                    self.stop()
                    return
                with self.lock:
                    self.message_queue.append(data)
            except (ConnectionResetError, ConnectionAbortedError):
                self.stop()
                return
            except Exception as e:
                messagebox.showerror("Network Error", f"Connection lost: {str(e)}")
                self.stop()
                return

    def get_messages(self):
        with self.lock:
            messages = self.message_queue.copy()
            self.message_queue.clear()
        return messages

    def send(self, message):
        try:
            self.socket.sendall(message.encode('utf-8'))
            return True
        except Exception as e:
            messagebox.showerror("Send Error", f"Failed to send message: {str(e)}")
            return False

    def stop(self):
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
        self.root.title("Chat Client")
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
        if event.state & 0x0001:
            return  # Allow Shift+Enter for newline
        self.send_message()
        return "break"  # Prevent default Enter behavior

    def append_message(self, message):
        self.chat_history.config(state=tk.NORMAL)
        self.chat_history.insert(tk.END, message + "\n")
        self.chat_history.config(state=tk.DISABLED)
        self.chat_history.see(tk.END)

    def send_message(self):
        message = self.input_field.get("1.0", tk.END).strip()
        if message:
            if self.client.send(message):
                self.append_message(f"You: {message}")
                self.input_field.delete("1.0", tk.END)
        self.input_field.focus_set()

    def schedule_receive(self):
        if not self.running:
            return
        messages = self.client.get_messages()
        for msg in messages:
            self.append_message(msg)
        self.root.after(100, self.schedule_receive)

    def on_close(self):
        self.running = False
        self.client.stop()
        self.root.destroy()

class ConnectionDialog(simpledialog.Dialog):
    def body(self, master):
        tk.Label(master, text="Server IP:").grid(row=0, sticky=tk.W)
        tk.Label(master, text="Port:").grid(row=1, sticky=tk.W)

        self.ip_entry = tk.Entry(master)
        self.port_entry = tk.Entry(master)

        self.ip_entry.grid(row=0, column=1)
        self.port_entry.grid(row=1, column=1)

        self.ip_entry.insert(0, "172.20.10.7")
        self.port_entry.insert(0, "5555")
        return self.ip_entry

    def validate(self):
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
            messagebox.showwarning("Invalid Port", "Port must be a number between 1-65535")
            return False
        return True

    def apply(self):
        self.host = self.ip_entry.get()
        self.port = int(self.port_entry.get())

def main():
    root = tk.Tk()
    root.withdraw()

    # Get connection details
    dialog = ConnectionDialog(root, "Connect to Server")
    if not hasattr(dialog, 'host'):
        return  # User cancelled

    # Create client
    client = ChatClient(dialog.host, dialog.port)
    if not client.connect():
        return

    # Start GUI
    root.deiconify()
    ChatGUI(root, client)
    root.mainloop()

if __name__ == "__main__":
    main()