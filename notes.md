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