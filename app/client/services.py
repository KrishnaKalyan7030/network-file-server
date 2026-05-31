import socket
import json

with open("app\client\config\config.json", "r") as file:
    config = json.load(file)

SERVER_IP = config["server_ip"]
SERVER_PORT = config["server_port"]

TIMEOUT = 15


def _connect():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(TIMEOUT)
    s.connect((SERVER_IP, SERVER_PORT))
    return s


def login_user(username, password):
    try:
        client_socket = _connect()
        client_socket.send(f"LOGIN {username} {password}".encode())
        response = client_socket.recv(1024).decode().strip()

        if response == "AUTH_SUCCESS":
            client_socket.settimeout(None)
            return True, client_socket

        client_socket.close()
        return False, None

    except Exception as e:
        print(f"[login_user] {e}")
        return False, None


def register_user(username, password):
    try:
        client_socket = _connect()
        client_socket.send(f"REGISTER {username} {password}".encode())
        response = client_socket.recv(1024).decode().strip()
        client_socket.close()
        return response

    except Exception as e:
        return str(e)