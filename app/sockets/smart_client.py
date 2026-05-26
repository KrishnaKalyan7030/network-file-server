import socket
import os

try:

    client_socket = socket.socket()

    client_socket.connect(('192.168.0.175', 9999))

    print('Connected to server')

    username = input("Enter username: ")
    password = input('Enter password: ')

    login_command = f'LOGIN {username} {password}'

    client_socket.send(login_command.encode())

    auth_response = client_socket.recv(1024).decode()

    if auth_response != 'AUTH_SUCCESS':

        print("Authentication Failed")

        client_socket.close()

        exit()

    else:

        print("Authentication Successful")

    while True:
        print("""
                1. UPLOAD
                2. DOWNLOAD
                3. LIST
                4. DELETE
                5. LOGOUT
              """)

        operation = input("Enter operation: ").upper()

        # LOGOUT OPERATION

        if operation == 'LOGOUT':

            client_socket.send(operation.encode())

            print("Logged out successfully")

            break

        # LIST OPERATION

        elif operation == 'LIST':

            client_socket.send(operation.encode())

            response = client_socket.recv(1024).decode()

            print("\nFiles available on server:\n")

            print(response)

        # UPLOAD / DOWNLOAD / DELETE

        elif operation in ['UPLOAD', 'DOWNLOAD', 'DELETE']:

            filename = input('Enter Filename: ')

            # UPLOAD
            if operation == 'UPLOAD':

                filepath = f'../files/{filename}'

                if not os.path.exists(filepath):

                    print("File does not exist")

                    continue

                filesize = os.path.getsize(filepath)

                command = f'{operation} {filename} {filesize}'

                client_socket.send(command.encode())

                file = open(filepath, 'rb')

                sent_size = 0

                while sent_size < filesize:

                    data = file.read(1024)

                    if not data:
                        break

                    client_socket.send(data)

                    sent_size += len(data)

                    progress = (sent_size / filesize) * 100

                    print(f"Uploading: {progress:.2f}%", end='\r')

                file.close()

                print("\nFile uploaded successfully")

                response = client_socket.recv(1024).decode()

                print(response)

            # DOWNLOAD

            elif operation == 'DOWNLOAD':

                command = f'{operation} {filename}'

                client_socket.send(command.encode())

                response = client_socket.recv(1024).decode()

                # file not found
                if response == 'FILE_NOT_FOUND':

                    print("File not found on server")

                    continue

                filesize = int(response)

                client_socket.send("READY".encode())

                file = open(f'../downloads/{filename}', 'wb')

                received_size = 0

                while received_size < filesize:

                    data = client_socket.recv(1024)

                    if not data:
                        break

                    file.write(data)

                    received_size += len(data)

                    progress = (received_size / filesize) * 100

                    print(f"Downloading: {progress:.2f}%", end='\r')

                file.close()

                print("\nDownload completed")

            # DELETE

            elif operation == 'DELETE':

                command = f'{operation} {filename}'

                client_socket.send(command.encode())

                response = client_socket.recv(1024).decode()

                print(response)

        # INVALID OPERATION

        else:

            print("Invalid operation")

except Exception as e:

    print(f"Error : {e}")

finally:

    client_socket.close()

    print("Socket closed")