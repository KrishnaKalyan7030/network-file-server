import socket
import threading


def handle_client(client_socket, client_add):

    try:

        filename = client_socket.recv(1024).decode()

        print(f"Received request for {filename}")

        file = open(f'../uploads/{filename}', 'rb')

        while True:

            chunk = file.read(1024)

            if not chunk:
                break

            client_socket.send(chunk)

        file.close()

        print("File sent successfully")

    except Exception as e:

        print(f'Error with {client_add}: {e}')

    finally:

        client_socket.close()

        print(f"Connection closed for {client_add}")


# creates connection with client
server_socket = socket.socket()

server_socket.bind(('localhost', 9999))

server_socket.listen(5)

print("Download server started...")


while True:

    client_socket, client_add = server_socket.accept()

    print(f'Client with {client_add} is connected.')

    t = threading.Thread(
        target=handle_client,
        args=(client_socket, client_add),
        daemon=True
    )

    t.start()