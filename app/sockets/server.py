import socket
import threading

def handle_client(client_socket,client_add):
        while True:
            msg=client_socket.recv(1024).decode()
    
            if msg.lower()=='exit':
                print(f'client {client_add} disconnected')
                client_socket.close()
                break
            
            print(f'Message from {client_add}:{msg}')
    
            client_socket.send(f'Server Received:{msg}'.encode())

    
server_socket=socket.socket()

print("Server socket created...")

server_socket.bind(('localhost',9999))

server_socket.listen(5)
print("waiting for connection...")

while True:
    client_socket,client_add=server_socket.accept() #it returns tuple
    print(f"Connection created with {client_add}!")

    t=threading.Thread(target=handle_client,args=(client_socket,client_add))
    t.start()

    



