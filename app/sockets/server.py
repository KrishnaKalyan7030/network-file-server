import socket
import threading


def handle_client(client_socket, client_add):

    try:
        
        #receive filaname first
        metadata=client_socket.recv(1024).decode()
        filename = metadata.split('<SEPARATOR>')[0]

        print(f"Receiving file:{filename}")

        file = open(f'../uploads/{filename}', 'wb')

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
print("you knocked it.")


while True:

    client_socket, client_add = server_socket.accept()

    print(f"Connection created with {client_add}")

    t = threading.Thread(
        target=handle_client,
        args=(client_socket, client_add),
        daemon=True
    )

    t.start()