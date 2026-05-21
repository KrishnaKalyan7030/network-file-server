Networking is a logical or physical link  between two or more devices.
In networking there are two programs:
   1.Client
   2.Server

What is Socket?
-> socket is a endpoint sommunication between two programs.
-> 'socket' Module of python provides socket to develop network enables application or programs

These Sockets communicate using two types of protocols:
   1.TCP(Connection oriented) -> Trusted,first connect then send data,continuous stream
   2.UDP (ConnectionLess) -> data is send in form of UDP packets(contains data ,dest address),no ackowledgement whether data is reached its destinatio or not,take help of routers to reach destination,fast,Broadcating,some people will recerive msg and some not,not secure Ex:sending SMS


ip address-> unique no used to identify each system in network.System/network administrators provide it.

port no-> it is asn integer no used to identify a server program.

s.accept() -> accept method returns tuple that contains info abotu client.client_socket,client_add 
#here s is server socket

Range of port no lies between 0 to 65535



================== Persistent Communication =====================
Client and Server continuous connection until exit occurs.
Server should run continuously to serve clients.So we use While True i.e loop concept.

Client connects
↓
Client sends message
↓
Server replies
↓
Client sends another message
↓
Server replies
↓
repeat...
↓
exit
↓
connection closes

Flowchart of Persistent Communication.



============ Single threading ============= 
#server.py
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

#client.py
import socket
server_socket=socket.socket()

print("Server socket created...")

server_socket.bind(('localhost',9999))

server_socket.listen(5)
print("waiting for connection...")

while True:
    client_socket,client_add=server_socket.accept() #it returns tuple
    print("Connection created!")

    while True:
        msg=client_socket.recv(1024).decode()

        if msg.lower()=='exit':
            print(f'client {client_add} disconnected')
            client_socket.close()
            break
        
        print(f'Message from {client_add}:{msg}')

        client_socket.send(f'Server Received:{msg}'.encode())

Here Client 1 recv() waiting forever until client1 is disconnected.


<!-- ============ Threading ====================== -->
If main server closes,
all worker threads terminate automatically.daemon=True


If main server closes,all worker threads terminate automatically by using deamon=True.

Sockets are designed such that:
bytes received → actual data
empty bytes → connection closed
This is standard TCP socket behavior.

when client sends data , server receives b'data' which is decoded to receive actual data.If clent didnt send any such data through send() then server receives b'' i.e. empty message it means client disconnected.

Bacially two types of disconnect. 
1. abrupt -> client crashes/closes suddenly

client force closes terminal
↓
OS kills socket immediately
↓
server recv() interrupted
↓
exception raised

2. graceful -> when user enters exit





================== Architecture of project ======================
Client
   ↓
FastAPI Backend
   ↓
Authentication Layer
   ↓
File Service
   ↓
PostgreSQL Database
   ↓
Local File Storage