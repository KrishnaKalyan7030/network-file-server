import socket

HOST = "127.0.0.1"
PORT = 5000

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind((HOST, PORT))

server.listen()

print(f"Server running on {HOST}:{PORT}")

client_socket, client_address = server.accept()

print(f"Connected to {client_address}")

message = client_socket.recv(1024).decode()

print(f"Client says: {message}")

client_socket.send("Message received by server".encode())

client_socket.close()
server.close()