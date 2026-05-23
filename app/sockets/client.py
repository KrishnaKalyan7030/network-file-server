import socket

client_socket = socket.socket()

try:

    client_socket.connect(('localhost', 9999))

    print("Connected to server")
    file=open('../files/sample.txt','rb')  #rb=> raw bytes
    chunk=file.read(1024)
    print(chunk)
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