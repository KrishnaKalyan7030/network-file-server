import socket
server_socket=socket.socket()

print("Server socket created...")

server_socket.bind(('localhost',9999))

server_socket.listen(5)
print("waiting for connection...")

while True:
    client_socket,client_add=server_socket.accept() #it returns tuple
    name=client_socket.recv(1024).decode()
    print(f'Server connected with client-{client_add},{name}')

    client_socket.send(bytes("Hello from server!",'utf-8'))
    client_socket.close()

