import socket
client_socket=socket.socket()
client_socket.connect(('localhost',9999))

name=input("Enter name: ")
client_socket.send(bytes(name,'utf-8'))

print(client_socket.recv(1024).decode())