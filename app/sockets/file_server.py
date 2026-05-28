import socket
import threading
import os
import json
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

LOG_FILE = os.path.join(BASE_DIR,'../../logs/server.log')

METADATA_FILE = os.path.join(BASE_DIR,'../../file_metadata.json')

USERS_FILE = os.path.join(BASE_DIR,'../../users.json')

SHARED_METADATA_FILE = os.path.join(BASE_DIR,'../../shared_metadata.json')

UPLOAD_FOLDER = os.path.join(BASE_DIR,'../uploads')

# Load file ownership metadata
with open(METADATA_FILE, 'r') as file:
    file_metadata = json.load(file)

# Load users from JSON file
with open(USERS_FILE, 'r') as file:

    users = json.load(file)

# file sharing metadata
with open(SHARED_METADATA_FILE, 'r') as file:

    shared_metadata = json.load(file)

def log_activity(message):

    current_time = datetime.now()

    timestamp = current_time.strftime(
        '%Y-%m-%d %H:%M:%S'
    )

    log_message = (
        f"[{timestamp}] {message}\n"
    )

    with open(LOG_FILE, 'a') as file:

        file.write(log_message)

def handle_client(client_socket, client_add):

    try:
        # AUTHENTICATION PHASE
        login_data = client_socket.recv(
            1024
        ).decode()

        login_parts = login_data.split()

        # Validate login format
        if len(login_parts) != 3:

            client_socket.send(
                "AUTH_FAILED".encode()
            )

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

            if (
                username in users
                and
                users[username]['password']== password
            ):

                print(
                    f"{username} authenticated successfully"
                )

                log_activity(
                    f"{username} logged in successfully"
                )

                client_socket.send(
                    "AUTH_SUCCESS".encode()
                )

                user_role = users[username]["role"]

                print(f"{username} role is {user_role}")
                
                user_folder = os.path.join(
                    UPLOAD_FOLDER,
                    username
                )
                
                os.makedirs(
                    user_folder,
                    exist_ok=True
                )
            
            else:

                print(
                    f"Authentication failed for {username}"
                )

                log_activity(
                    f"Failed login attempt for {username}"
                )

                client_socket.send(
                    "AUTH_FAILED".encode()
                )

                client_socket.close()

                return

        else:

            client_socket.send(
                "AUTH_FAILED".encode()
            )

            log_activity(
                f"Unknown authentication command from {client_add}"
            )

            client_socket.close()

            return

        # OPERATION PHASE

        while True:

            command = client_socket.recv(
                1024
            ).decode()

            # client disconnected
            if not command:

                print(
                    f"{client_add} disconnected"
                )

                log_activity(
                    f"{username} disconnected"
                )

                break

            # logout operation
            if command.upper() == 'LOGOUT':

                print(
                    f"{username} logged out"
                )

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

            print(
                f"Operation requested: {operation}"
            )

            # UPLOAD OPERATION

            if operation == 'UPLOAD':

                if len(parts) < 3:

                    print(
                        "Filename or filesize missing"
                    )

                    log_activity(
                        f"{username} upload failed due to missing data"
                    )

                    continue

                filename = parts[1]

                filesize = int(parts[2])

                print(
                    f"UPLOAD request for {filename}"
                )
                
                user_folder = os.path.join(
                    UPLOAD_FOLDER,
                    username
                )
                
                filepath = os.path.join(
                    user_folder,
                    filename
                )

                with open(filepath, 'wb') as file:

                    received_size = 0

                    while received_size < filesize:

                        data = client_socket.recv(
                            1024
                        )

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
                with open(
                    METADATA_FILE,
                    'w'
                ) as file:

                    json.dump(
                        file_metadata,
                        file,
                        indent=4
                    )

                client_socket.send(
                    "UPLOAD_SUCCESS".encode()
                )

            # DOWNLOAD OPERATION

            elif operation == 'DOWNLOAD':

                if len(parts) < 2:

                    print(
                        "Filename missing"
                    )

                    log_activity(
                        f"{username} download failed due to missing filename"
                    )

                    continue

                filename = parts[1]

                print(
                    f"DOWNLOAD request for {filename}"
                )

                owner = file_metadata.get(filename)
                
                filepath = os.path.join(
                    UPLOAD_FOLDER,
                    owner,
                    filename
                )

                # file existence check
                if not os.path.exists(filepath):

                    client_socket.send(
                        "FILE_NOT_FOUND".encode()
                    )

                    log_activity(
                        f"{username} requested missing file {filename}"
                    )

                    continue

                # authorization check
                owner = file_metadata.get(
                    filename
                )

                shared_users = shared_metadata.get(
                    filename,
                    []
                )

                if (
                    username != owner and 
                  username not in shared_users and user_role != 'admin'
                ):

                    client_socket.send(
                        "ACCESS_DENIED".encode()
                    )

                    log_activity(
                        f"{username} unauthorized download attempt on {filename}"
                    )

                    continue

                filesize = os.path.getsize(
                    filepath
                )

                client_socket.send(
                    str(filesize).encode()
                )

                acknowledgement = client_socket.recv(
                    1024
                ).decode()

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

                response = ""
                
                # loop through every user folder
                for owner_folder in os.listdir(UPLOAD_FOLDER):
                
                    owner_path = os.path.join(
                        UPLOAD_FOLDER,
                        owner_folder
                    )
                
                    # ensure it is a folder
                    if os.path.isdir(owner_path):
                
                        # loop through files inside user folder
                        for file in os.listdir(owner_path):
                
                            response += (
                                f"{file} -> {owner_folder}\n"
                            )
                
                # no files found
                if response == "":
                
                    response = "No files available"

                client_socket.send(response.encode())

                print("File list sent")

                log_activity(
                    f"{username} viewed file list"
                )

            # SHARE OPERATION

            elif operation == 'SHARE':

                if len(parts) < 3:

                    client_socket.send(
                        "Invalid SHARE command".encode()
                    )

                    continue

                filename = parts[1]

                target_user = parts[2]

                filepath = os.path.join(
                    UPLOAD_FOLDER,
                    filename
                )

                # file existence check
                if not os.path.exists(filepath):

                    client_socket.send(
                        "File not found".encode()
                    )

                    continue

                # ownership check
                if (
                    file_metadata.get(filename)
                    != username
                ):

                    client_socket.send(
                        "Access Denied".encode()
                    )

                    log_activity(
                        f"{username} unauthorized share attempt on {filename}"
                    )

                    continue

                # user existence check
                if target_user not in users:

                    client_socket.send(
                        "Target user does not exist".encode()
                    )

                    continue

                # initialize sharing list
                if filename not in shared_metadata:

                    shared_metadata[filename] = []

                # duplicate sharing check
                if (
                    target_user
                    in shared_metadata[filename]
                ):

                    client_socket.send(
                        "File already shared".encode()
                    )

                    continue

                # add shared user
                shared_metadata[filename].append(
                    target_user
                )

                # save permanently
                with open(
                    SHARED_METADATA_FILE,
                    'w'
                ) as file:

                    json.dump(
                        shared_metadata,
                        file,
                        indent=4
                    )

                client_socket.send(
                    "File shared successfully".encode()
                )

                print(
                    f"{filename} shared with {target_user}"
                )

                log_activity(
                    f"{username} shared {filename} with {target_user}"
                )

            # DELETE OPERATION

            elif operation == 'DELETE':

                if len(parts) < 2:

                    print(
                        "Filename missing"
                    )

                    log_activity(
                        f"{username} delete failed due to missing filename"
                    )

                    continue

                filename = parts[1]

                filepath = os.path.join(
                    UPLOAD_FOLDER,
                    username,
                    filename
                )

                # Authorization check
                if (
                   file_metadata.get(filename) != username  and user_role != 'admin'):

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

                    # Remove sharing metadata
                    if filename in shared_metadata:

                        del shared_metadata[filename]

                    # Update metadata file
                    with open(
                        METADATA_FILE,
                        'w'
                    ) as file:

                        json.dump(
                            file_metadata,
                            file,
                            indent=4
                        )

                    # Update sharing metadata
                    with open(
                        SHARED_METADATA_FILE,
                        'w'
                    ) as file:

                        json.dump(
                            shared_metadata,
                            file,
                            indent=4
                        )

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

            # HISTORY OPERATION

            elif operation == 'HISTORY':

                if user_role != 'admin':

                    client_socket.send("ACCESS_DENIED".encode())
                
                    log_activity(f"{username} unauthorized history access attempt")
                
                    continue

                with open(
                    LOG_FILE,
                    'r'
                ) as file:

                    history = file.read()

                if not history:

                    history = (
                        'No Logs Available'
                    )

                client_socket.send(
                    history.encode()
                )

                print('History sent')

                log_activity(
                    f"{username} viewed server history"
                )

            # INVALID OPERATION

            else:

                print("Invalid operation")

                log_activity(
                    f"{username} sent invalid operation {operation}"
                )

    except Exception as e:

        print(
            f'Error with {client_add}: {e}'
        )

        log_activity(
            f"Server error with {client_add}: {str(e)}"
        )

    finally:

        client_socket.close()

        print(
            f"Connection closed for {client_add}"
        )


# SERVER SETUP

server_socket = socket.socket()

server_socket.bind(
    ('0.0.0.0', 9999)
)

server_socket.listen(5)

print("Waiting for connection...")

while True:

    client_socket, client_add = (
        server_socket.accept()
    )

    print(
        f'Server connected to {client_add}'
    )

    log_activity(
        f"New connection from {client_add}"
    )

    t = threading.Thread(
        target=handle_client,
        args=(client_socket, client_add),
        daemon=True
    )

    t.start()