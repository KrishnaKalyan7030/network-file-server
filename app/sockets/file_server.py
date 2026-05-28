import socket
import threading
import os
import json
from datetime import datetime

# Load file ownership metadata
with open('../../file_metadata.json', 'r') as file:

    file_metadata = json.load(file)

# Load users from JSON file
with open('../../users.json', 'r') as file:

    users = json.load(file)


def log_activity(message):

    current_time = datetime.now()

    timestamp = current_time.strftime(
        '%Y-%m-%d %H:%M:%S'
    )

    log_message = f"[{timestamp}] {message}\n"

    with open('../../logs/server.log', 'a') as file:

        file.write(log_message)


def handle_client(client_socket, client_add):

    try:

        # AUTHENTICATION PHASE

        login_data = client_socket.recv(1024).decode()

        login_parts = login_data.split()

        # Validate login format
        if len(login_parts) != 3:

            client_socket.send("AUTH_FAILED".encode())

            log_activity(
                f"Invalid login format from {client_add}"
            )

            client_socket.close()

            return

        command = login_parts[0]

        username = login_parts[1]

        password = login_parts[2]

        # Verify credentials
        if command == 'LOGIN':

            if username in users and users[username] == password:

                print(f"{username} authenticated successfully")

                log_activity(
                    f"{username} logged in successfully"
                )

                client_socket.send("AUTH_SUCCESS".encode())

            else:

                print(f"Authentication failed for {username}")

                log_activity(
                    f"Failed login attempt for {username}"
                )

                client_socket.send("AUTH_FAILED".encode())

                client_socket.close()

                return

        else:

            client_socket.send("AUTH_FAILED".encode())

            log_activity(
                f"Unknown authentication command from {client_add}"
            )

            client_socket.close()

            return

        # OPERATION PHASE

        while True:

            command = client_socket.recv(1024).decode()

            # client disconnected
            if not command:

                print(f"{client_add} disconnected")

                log_activity(
                    f"{username} disconnected"
                )

                break

            # logout operation
            if command.upper() == 'LOGOUT':

                print(f"{username} logged out")

                log_activity(
                    f"{username} logged out"
                )

                break

            parts = command.split()

            # Empty command validation
            if len(parts) < 1:

                print("Invalid Command")

                log_activity(
                    f"{username} sent invalid command"
                )

                continue

            operation = parts[0].upper()

            print(f"Operation requested: {operation}")

            # UPLOAD OPERATION

            if operation == 'UPLOAD':

                if len(parts) < 3:

                    print("Filename or filesize missing")

                    log_activity(
                        f"{username} upload failed due to missing data"
                    )

                    continue

                filename = parts[1]

                filesize = int(parts[2])

                print(f"UPLOAD request for {filename}")

                with open(f'../uploads/{filename}', 'wb') as file:

                    received_size = 0

                    while received_size < filesize:

                        data = client_socket.recv(1024)

                        if not data:
                            break

                        file.write(data)

                        received_size += len(data)

                print('Upload Complete')

                log_activity(
                    f"{username} uploaded {filename}"
                )

                # Save file owner
                file_metadata[filename] = username

                # Save metadata permanently
                with open('../../file_metadata.json', 'w') as file:

                    json.dump(file_metadata, file, indent=4)

                client_socket.send(
                    "UPLOAD_SUCCESS".encode()
                )

            # DOWNLOAD OPERATION
            elif operation == 'DOWNLOAD':

                if len(parts) < 2:

                    print("Filename missing")

                    log_activity(
                        f"{username} download failed due to missing filename"
                    )

                    continue

                filename = parts[1]

                print(f"DOWNLOAD request for {filename}")

                filepath = f'../uploads/{filename}'

                if not os.path.exists(filepath):

                    client_socket.send(
                        "FILE_NOT_FOUND".encode()
                    )

                    log_activity(
                        f"{username} requested missing file {filename}"
                    )

                    continue

                filesize = os.path.getsize(filepath)

                client_socket.send(
                    str(filesize).encode()
                )

                acknowledgement = client_socket.recv(1024).decode()

                if acknowledgement != 'READY':

                    log_activity(
                        f"{username} download acknowledgement failed for {filename}"
                    )

                    continue

                with open(filepath, 'rb') as file:

                    while True:

                        chunk = file.read(1024)

                        if not chunk:
                            break

                        client_socket.send(chunk)

                print("Download Complete")

                log_activity(
                    f"{username} downloaded {filename}"
                )

            # LIST OPERATION
            elif operation == 'LIST':

                files = os.listdir('../uploads')

                if not files:

                    response = "No files available"

                else:

                    response = ""

                    for file in files:

                        owner = file_metadata.get(file, "Unknown")

                        response += f"{file} -> {owner}\n"

                client_socket.send(response.encode())

                print("File list sent")

                log_activity(
                    f"{username} viewed file list"
                )

            # DELETE OPERATION
            elif operation == 'DELETE':

                if len(parts) < 2:

                    print("Filename missing")

                    log_activity(
                        f"{username} delete failed due to missing filename"
                    )

                    continue

                filename = parts[1]

                filepath = f'../uploads/{filename}'

                # Authorization check
                if file_metadata.get(filename) != username:

                    client_socket.send(
                        "Access Denied".encode()
                    )

                    log_activity(
                        f"{username} unauthorized delete attempt on {filename}"
                    )

                    continue

                if os.path.exists(filepath):

                    os.remove(filepath)

                    # Remove ownership metadata
                    del file_metadata[filename]

                    # Update metadata file
                    with open('../../file_metadata.json', 'w') as file:

                        json.dump(file_metadata, file, indent=4)

                    client_socket.send(
                        "File deleted successfully".encode()
                    )

                    log_activity(
                        f"{username} deleted {filename}"
                    )

                else:

                    client_socket.send(
                        "File not found".encode()
                    )

                    log_activity(
                        f"{username} tried deleting missing file {filename}"
                    )

            elif operation == 'HISTORY':
                with open('../../logs/server.log', 'r') as file:
                    history = file.read()

                if not history:
                    history = 'No Logs Available'

                client_socket.send( history.encode() )

                print('History sent')

                log_activity( f"{username} viewed server history")


            # INVALID OPERATION
            else:
                print("Invalid operation")

                log_activity(
                    f"{username} sent invalid operation {operation}"
                )

    except Exception as e:

        print(f'Error with {client_add}: {e}')

        log_activity(
            f"Server error with {client_add}: {str(e)}"
        )

    finally:

        client_socket.close()

        print(f"Connection closed for {client_add}")


# SERVER SETUP
server_socket = socket.socket()

server_socket.bind(('0.0.0.0', 9999))

server_socket.listen(5)

print("Waiting for connection...")


while True:

    client_socket, client_add = server_socket.accept()

    print(f'Server connected to {client_add}')

    log_activity(
        f"New connection from {client_add}"
    )

    t = threading.Thread(
        target=handle_client,
        args=(client_socket, client_add),
        daemon=True
    )

    t.start()