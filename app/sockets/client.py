import socket

HOST = "127.0.0.1"
PORT = 5000
# AF_INET -> IPV4 communication
# SOCK_STREAM-> TCP Protocol
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client.connect((HOST, PORT))

client.send("Hello from client".encode())

response = client.recv(1024).decode()

print(f"Server response: {response}")

client.close()