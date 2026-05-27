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


================ File =======
Every file is bytes
Sockets fundamentally send files only.
file transfer = byte transfer

client
read bytes from file
↓
send bytes through socket

Server:
receive bytes from socket
↓
write bytes into new file


client opens file ,read chunk,send chunk,repeat .whereas server create empty file,receive chunk,write chunk,repeat.Eventually same file is reconstructed towards server.
EOF ->if file has no more bytes then it return b''

while True:

    chunk = file.read(1024)

    if not chunk:
        break

    send(chunk)

read small piece
↓
if file ended stop
↓
otherwise send piece

This is streaming architecture.


ENTIRE FILE TRANSFER LIFECYCLE
Clinet side->
open file
↓
read chunk
↓
send chunk
↓
repeat
↓
close socket

server side->
accept client
↓
create empty file
↓
recv chunk
↓
write chunk
↓
repeat
↓
recv empty
↓
close file



1.Chunks are used to stream files gradually instead of loading the entire file into memory, making file transfer memory-efficient and scalable for large files.
2.File data is already raw binary bytes. Decoding converts bytes into text, which may corrupt non-text files.


Situation | Empty bytes meaning
file.read() returns b''	file ended
recv() returns b''	connection closed 





protocol-> aggreed communication protocol.
server.py

import socket
import threading


def handle_client(client_socket, client_add):

    try:

        file = open('../uploads/received_sample.txt', 'wb')

        while True:

            # msg = client_socket.recv(1024).decode()
            

            # # Empty recv means disconnected
            # if not msg:
            #     print(f"{client_add} disconnected unexpectedly")
            #     break

            # if msg.lower() == 'exit':
            #     print(f"{client_add} disconnected gracefully")
            #     break

            # print(f"Message from {client_add}: {msg}")

            # client_socket.send(
            #     f"Server Received: {msg}".encode()
            # )

            msg = client_socket.recv(1024)

            if not msg:
                print("File transfer completed")
                break

            file.write(msg)

        file.close()

        print("File received successfully")

    except Exception as e:

        print(f"Error with {client_add}: {e}")

    finally:

        client_socket.close()

        print(f"Connection closed for {client_add}")


server_socket = socket.socket()

print("Server socket created...")

server_socket.bind(('localhost', 9999))

server_socket.listen(5)

print("Waiting for connection...")


while True:

    client_socket, client_add = server_socket.accept()

    print(f"Connection created with {client_add}")

    t = threading.Thread(
        target=handle_client,
        args=(client_socket, client_add),
        daemon=True
    )

    t.start()



    client.py
    import socket

client_socket = socket.socket()

try:

    client_socket.connect(('localhost', 9999))

    print("Connected to server")
    file=open('../files/sample.txt','rb')  #rb=> raw bytes
    while True:
        chunk=file.read(1024)
        
        if not chunk:
            break

        client_socket.send(chunk)
    print('File Uploaded Successfully.')
    # while True:

    #     msg = input("Enter message: ")

    #     client_socket.send(msg.encode())

    #     if msg.lower() == 'exit':
    #         print("Disconnected from server")
    #         break

    #     response = client_socket.recv(1024).decode()

    #     if not response:
    #         print("Server disconnected")
    #         break

    #     print(response)

except Exception as e:

    print(f"Error: {e}")

finally:

    client_socket.close()

    print("Socket closed")import socket

client_socket = socket.socket()

try:

    client_socket.connect(('localhost', 9999))

    print("Connected to server")
    file=open('../files/sample.txt','rb')  #rb=> raw bytes
    while True:
        chunk=file.read(1024)
        
        if not chunk:
            break

        client_socket.send(chunk)
    print('File Uploaded Successfully.')
    # while True:

    #     msg = input("Enter message: ")

    #     client_socket.send(msg.encode())

    #     if msg.lower() == 'exit':
    #         print("Disconnected from server")
    #         break

    #     response = client_socket.recv(1024).decode()

    #     if not response:
    #         print("Server disconnected")
    #         break

    #     print(response)

except Exception as e:

    print(f"Error: {e}")

finally:

    client_socket.close()

    print("Socket closed")

============ Dynamic Filename Transfer ========================

If you dont use dynamic filename then previous data from file at server side will be overwriiten.It becomes impossible to handle multiple files.So Dynamic Fielname is used.

Now client will send 1.Filename 2.file data and server will also follow the same order.

Simple protocol design
client -> 

connect
↓
send filename
↓
send file chunks
↓
close socket

Server->

accept
↓
recv filename
↓
create file using filename
↓
recv chunks
↓
write chunks



----------- Filename -------
Filename is metadata about file.In real system first filename,filesie and content type is send  before actual bytes.


======= TCP packet merging problem =======

Server expected 
recv 1 → filename
recv 2 → file data
but TCP does not gurantee this seperation.TCP is stream- oriented not message- oriented.
TCP is stream-oriented, meaning it treats data as a continuous, unstructured sequence of bytes rather than distinct, independent messages.
server received sample.txt + first file chunk together which leads to invalid filename.

TCP only gurantees bytes order not packet grouping.
This si resolved by delimitors or fixed size headers.
Ex: sample.txt<SEPARATOR> 
Server reads until separator found.


Suppose recv gets sample.txt<SEPARATOR>Hare Krishna...
then split('<SEPARATOR>') gives ['sample.txt', 'Hare Krishna...'] .Here filaname is extracted safely.

but here one bug is present.First chuk is lost because it was already consumed in first recv.So proper buffering is need to resolve this.

For simplicity we will use here small delay after sending filename.This gives TCP time separation.


=========== two-way communication architecture ===============

Here client will not only send data but request to server for files and server will send it .

clinet->
connect
↓
request filename
↓
recv chunks
↓
write file

server
accept
↓
receive requested filename
↓
open file
↓
read chunks
↓
send chunks


sockets are full duplex.


=========== Protocol Parsing Architecture ==============
Server can synamically decide operation to perform

Command	Parts
LIST	1
UPLOAD sample.txt	2
DOWNLOAD sample.txt	2


========== Authentication ==============
connect
↓
send LOGIN username password
↓
wait for auth result

if success:
    allow operations
else:
    disconnect


server
accept connection
↓
authenticate client
↓
if valid:
    continue
else:
    close connection





========== stateful session management =========



==== deterministic transfer protocol=====


=== synchronized transfer protocol ===


==== FILE OWNERSHIP SYSTEM =====
user identity
ownership storage
permission checking
protected operations

This is:

authorization architecture
Real backend systems are built on exactly these ideas.

server controls permissions not client.

=== Persistence ============


====== LOgging ==============
Logging means:server writes important events into a file
Ex: [10:45:11] krishna uploaded notes.pdf
[10:46:20] arjun downloaded report.pdf
[10:48:05] krishna deleted old.txt
This becomes server history.

Why Logging is needed?
-> Because if we want to track some previous files then server will go thorugh its history or logs.
If some unauthorized user tries to access system then that event is captured by server.It helps in protection.
Also for production monitoring-> uploads/day,failed logins,server crashes.

Security,Production Monitoring and Debugging.

Logs are eyes of backend systems.


This step teaches:
. file append mode
. timestamps
. backend monitoring
. server observability
. production thinking


Modularity means breaking large systems into resuable independent units.