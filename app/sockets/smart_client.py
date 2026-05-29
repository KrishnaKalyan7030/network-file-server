import socket
import os

try:

    client_socket = socket.socket()

    client_socket.connect(
        ('192.168.0.175', 9999)
    )

    print('Connected to server')

    # AUTHENTICATION PHASE

    choice = input(
        "Choose LOGIN or REGISTER: "
    ).upper()

    username = input(
        "Enter username: "
    )

    password = input(
        "Enter password: "
    )

    command = (
        f'{choice} {username} {password}'
    )

    client_socket.send(
        command.encode()
    )

    response = client_socket.recv(
        1024
    ).decode()

    # REGISTER SUCCESS

    if response == 'REGISTER_SUCCESS':

        print(
            "Registration Successful"
        )

        client_socket.close()

        exit()

    # USER ALREADY EXISTS

    elif response == 'USER_EXISTS':

        print(
            "Username already exists"
        )

        client_socket.close()

        exit()

    # LOGIN FAILED

    elif response != 'AUTH_SUCCESS':

        print(
            "Authentication Failed"
        )

        client_socket.close()

        exit()

    # LOGIN SUCCESS

    else:

        print(
            "Authentication Successful"
        )

    # CREATE DOWNLOADS FOLDER IF NOT EXISTS

    os.makedirs(
        '../downloads',
        exist_ok=True
    )

    # OPERATION PHASE

    while True:

        print("""
                 == NETWORK FILE SERVER ==

                UPLOAD
                DOWNLOAD
                LIST
                RENAME
                DELETE
                HISTORY
                SHARE
                LOGOUT

              """)

        operation = input(
            "Enter operation: "
        ).upper()

        # LOGOUT OPERATION

        if operation == 'LOGOUT':

            client_socket.send(
                operation.encode()
            )

            print(
                "Logged out successfully"
            )

            break

        # LIST OPERATION

        elif operation == 'LIST':

            client_socket.send(
                operation.encode()
            )

            response = client_socket.recv(
                4096
            ).decode()

            print(
                "\nFiles available on server:\n"
            )

            print(response)

        # RENAME OPERATION

        elif operation == 'RENAME':

            old_filename = input(
                "Enter old filename: "
            )

            new_filename = input(
                "Enter new filename: "
            )

            command = (
                f'{operation} {old_filename} {new_filename}'
            )

            client_socket.send(
                command.encode()
            )

            response = client_socket.recv(
                1024
            ).decode()

            print(response)

        # HISTORY OPERATION

        elif operation == 'HISTORY':

            client_socket.send(
                operation.encode()
            )

            history = client_socket.recv(
                4096
            ).decode()

            # ACCESS DENIED

            if history == 'ACCESS_DENIED':

                print(
                    "Only admin can view server history"
                )

            else:

                print(
                    "\nSERVER HISTORY:\n"
                )

                print(history)

        # UPLOAD OPERATION

        elif operation == 'UPLOAD':

            filename = input(
                'Enter Filename: '
            )

            filepath = os.path.join(
                '../files',
                filename
            )

            # FILE EXISTENCE CHECK

            if not os.path.exists(filepath):

                print(
                    "File does not exist"
                )

                continue

            filesize = os.path.getsize(
                filepath
            )

            command = (
                f'{operation} {filename} {filesize}'
            )

            client_socket.send(
                command.encode()
            )

            file = open(filepath, 'rb')

            sent_size = 0

            while sent_size < filesize:

                data = file.read(1024)

                if not data:
                    break

                client_socket.send(data)

                sent_size += len(data)

                progress = (
                    sent_size / filesize
                ) * 100

                print(
                    f"Uploading: {progress:.2f}%",
                    end='\r'
                )

            file.close()

            response = client_socket.recv(
                1024
            ).decode()

            print(
                f"\n{response}"
            )

        # DOWNLOAD OPERATION

        elif operation == 'DOWNLOAD':

            filename = input(
                'Enter Filename: '
            )

            command = (
                f'{operation} {filename}'
            )

            client_socket.send(
                command.encode()
            )

            response = client_socket.recv(
                1024
            ).decode()

            # ACCESS DENIED

            if response == 'ACCESS_DENIED':

                print(
                    "You don't have permission to download this file"
                )

                continue

            # FILE NOT FOUND

            elif response == 'FILE_NOT_FOUND':

                print(
                    "File not found on server"
                )

                continue

            # FILESIZE RECEIVED

            filesize = int(response)

            client_socket.send(
                "READY".encode()
            )

            download_path = os.path.join(
                '../downloads',
                filename
            )

            file = open(
                download_path,
                'wb'
            )

            received_size = 0

            while received_size < filesize:

                data = client_socket.recv(
                    1024
                )

                if not data:
                    break

                file.write(data)

                received_size += len(data)

                progress = (
                    received_size / filesize
                ) * 100

                print(
                    f"Downloading: {progress:.2f}%",
                    end='\r'
                )

            file.close()

            print(
                "\nDownload completed"
            )

            print(
                f"File saved to {download_path}"
            )

        # DELETE OPERATION

        elif operation == 'DELETE':

            filename = input(
                'Enter Filename: '
            )

            command = (
                f'{operation} {filename}'
            )

            client_socket.send(
                command.encode()
            )

            response = client_socket.recv(
                1024
            ).decode()

            print(response)

        # SHARE OPERATION

        elif operation == 'SHARE':

            filename = input(
                "Enter Filename: "
            )

            target_user = input(
                "Enter username to share with: "
            )

            command = (
                f'{operation} {filename} {target_user}'
            )

            client_socket.send(
                command.encode()
            )

            response = client_socket.recv(
                1024
            ).decode()

            print(response)

        # INVALID OPERATION

        else:

            print(
                "Invalid operation"
            )

except Exception as e:

    print(f"Error : {e}")

finally:

    client_socket.close()

    print("Socket closed")