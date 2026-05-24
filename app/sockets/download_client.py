import socket

try:

    client_socket = socket.socket()

    client_socket.connect(('localhost', 9999))

    print('Connected to server')

    filename = 'sample.txt'

    client_socket.send(filename.encode())

    file = open('../downloads/downloaded_sample.txt', 'wb')

    while True:

        data = client_socket.recv(1024)

        if not data:
            break

        file.write(data)

    file.close()

    print('File downloaded successfully')

except Exception as e:

    print(f"Error : {e}")

finally:

    client_socket.close()

    print("Socket closed")