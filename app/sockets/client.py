import socket
client_socket=socket.socket()
client_socket.connect(('localhost',9999))
print("connected to server")

while True:
    
    msg=input("Enter message: ")
    client_socket.send(msg.encode())


    if msg.lower()=='exit':
        client_socket.close()
        break
    
    response=client_socket.recv(1024).decode()
    print(response)