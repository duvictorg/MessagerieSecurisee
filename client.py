# Import socket module
import socket

# Create a socket object
s = socket.socket()

# Define the port on which you want to connect
port = 5555

# connect to the server on local computer
s.connect(('172.20.10.7', port))

# receive data from the server and decoding to get the string.
while True:
    data = s.recv(1024)
    if data:
        print(data.decode('utf-8'))