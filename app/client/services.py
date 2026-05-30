import socket

SERVER_IP = "127.0.0.1"   # Your server IP
SERVER_PORT = 9999


def login_user(username, password):

    try:

        client_socket = socket.socket()

        client_socket.connect(
            (SERVER_IP, SERVER_PORT)
        )

        command = (
            f"LOGIN {username} {password}"
        )

        client_socket.send(
            command.encode()
        )

        response = client_socket.recv(
            1024
        ).decode()

        if response == "AUTH_SUCCESS":

            return (
                True,
                client_socket
            )

        client_socket.close()

        return (
            False,
            None
        )

    except Exception as e:

        print(e)

        return (
            False,
            None
        )


def register_user(username, password):

    try:

        client_socket = socket.socket()

        client_socket.connect(
            (SERVER_IP, SERVER_PORT)
        )

        command = (
            f"REGISTER {username} {password}"
        )

        client_socket.send(
            command.encode()
        )

        response = client_socket.recv(
            1024
        ).decode()

        client_socket.close()

        return response

    except Exception as e:

        return str(e)