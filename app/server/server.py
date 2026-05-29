import socket
import threading
import os
import json
import hashlib
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

LOG_FILE = os.path.join(
    BASE_DIR,
    '../../logs/server.log'
)

METADATA_FILE = os.path.join(
    BASE_DIR,
    '../../database/file_metadata.json'
)

USERS_FILE = os.path.join(
    BASE_DIR,
    '../../database/users.json'
)

SHARED_METADATA_FILE = os.path.join(
    BASE_DIR,
    '../../database/shared_metadata.json'
)

UPLOAD_FOLDER = os.path.join(
    BASE_DIR,
    'uploads'
)

# Create folders if not exist
os.makedirs(
    os.path.dirname(LOG_FILE),
    exist_ok=True
)

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)

# Load file ownership metadata
if os.path.exists(METADATA_FILE):

    with open(METADATA_FILE, 'r') as file:

        file_metadata = json.load(file)

else:

    file_metadata = {}

# Load users
if os.path.exists(USERS_FILE):

    with open(USERS_FILE, 'r') as file:

        users = json.load(file)

else:

    users = {}

# Load shared metadata
if os.path.exists(SHARED_METADATA_FILE):

    with open(SHARED_METADATA_FILE, 'r') as file:

        shared_metadata = json.load(file)

else:

    shared_metadata = {}

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

def hash_password(password):

    return hashlib.sha256(
        password.encode()
    ).hexdigest()

def handle_client(client_socket, client_add):

    try:

        # AUTHENTICATION PHASE

        login_data = client_socket.recv(
            1024
        ).decode()

        login_parts = login_data.split()

        if len(login_parts) != 3:

            client_socket.send(
                "AUTH_FAILED".encode()
            )

            client_socket.close()

            return

        command = login_parts[0].upper()

        username = login_parts[1]

        password = login_parts[2]

        # REGISTER OPERATION

        if command == 'REGISTER':

            if username in users:

                client_socket.send(
                    "USER_EXISTS".encode()
                )

                return

            hashed_password = hash_password(
                password
            )

            users[username] = {

                "password": hashed_password,

                "role": "user"
            }

            with open(
                USERS_FILE,
                'w'
            ) as file:

                json.dump(
                    users,
                    file,
                    indent=4
                )

            log_activity(
                f"New user registered: {username}"
            )

            client_socket.send(
                "REGISTER_SUCCESS".encode()
            )

            return

        # LOGIN OPERATION

        elif command == 'LOGIN':

            if (
                username in users and
                users[username]['password']
                ==
                hash_password(password)
            ):

                print(
                    f"{username} authenticated successfully"
                )

                user_role = users[username]['role']

                log_activity(
                    f"{username} logged in successfully"
                )

                client_socket.send(
                    "AUTH_SUCCESS".encode()
                )

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

                client_socket.send(
                    "AUTH_FAILED".encode()
                )

                client_socket.close()

                return

        else:

            client_socket.send(
                "AUTH_FAILED".encode()
            )

            client_socket.close()

            return

        # OPERATION PHASE

        while True:

            command = client_socket.recv(
                1024
            ).decode()

            if not command:

                break

            if command.upper() == 'LOGOUT':

                log_activity(
                    f"{username} logged out"
                )

                break

            parts = command.split()

            if len(parts) < 1:

                continue

            operation = parts[0].upper()

            print(
                f"Operation requested: {operation}"
            )

            # UPLOAD OPERATION

            if operation == 'UPLOAD':

                if len(parts) < 3:

                    continue

                filename = parts[1]

                filesize = int(parts[2])

                user_folder = os.path.join(
                    UPLOAD_FOLDER,
                    username
                )

                filepath = os.path.join(
                    user_folder,
                    filename
                )

                # duplicate file check

                if os.path.exists(filepath):

                    client_socket.send(
                        "FILE_ALREADY_EXISTS".encode()
                    )

                    continue

                client_socket.send(
                    "READY".encode()
                )

                with open(filepath, 'wb') as file:

                    received_size = 0
                    while received_size < filesize:

                        remaining = filesize - received_size
                    
                        data = client_socket.recv(
                            1024 if remaining > 1024 else remaining
                        )
                    
                        if not data:
                            break
                    
                        file.write(data)
                    
                        received_size += len(data)
                    
                                        

                    

                file_metadata[filename] = username

                with open(
                    METADATA_FILE,
                    'w'
                ) as file:

                    json.dump(
                        file_metadata,
                        file,
                        indent=4
                    )

                log_activity(
                    f"{username} uploaded {filename}"
                )

                client_socket.send(
                    "UPLOAD_SUCCESS".encode()
                )

            # DOWNLOAD OPERATION

            elif operation == 'DOWNLOAD':

                if len(parts) < 2:

                    continue

                filename = parts[1]

                owner = file_metadata.get(
                    filename
                )

                if not owner:

                    client_socket.send(
                        "FILE_NOT_FOUND".encode()
                    )

                    continue

                filepath = os.path.join(
                    UPLOAD_FOLDER,
                    owner,
                    filename
                )

                if not os.path.exists(filepath):

                    client_socket.send(
                        "FILE_NOT_FOUND".encode()
                    )

                    continue

                shared_users = shared_metadata.get(
                    filename,
                    []
                )

                if (
                    username != owner and
                    username not in shared_users and
                    user_role != 'admin'
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

                    continue

                with open(filepath, 'rb') as file:

                    while True:

                        chunk = file.read(1024)

                        if not chunk:
                            break

                        client_socket.send(chunk)

                log_activity(
                    f"{username} downloaded {filename}"
                )

            # RENAME OPERATION

            elif operation == 'RENAME':

                if len(parts) < 3:

                    client_socket.send(
                        "Invalid RENAME command".encode()
                    )

                    continue

                old_filename = parts[1]

                new_filename = parts[2]

                owner = file_metadata.get(
                    old_filename
                )

                if not owner:

                    client_socket.send(
                        "File not found".encode()
                    )

                    continue

                if (
                    owner != username and
                    user_role != 'admin'
                ):

                    client_socket.send(
                        "Access Denied".encode()
                    )

                    continue

                old_filepath = os.path.join(
                    UPLOAD_FOLDER,
                    owner,
                    old_filename
                )

                new_filepath = os.path.join(
                    UPLOAD_FOLDER,
                    owner,
                    new_filename
                )

                if not os.path.exists(old_filepath):

                    client_socket.send(
                        "File not found".encode()
                    )

                    continue

                if os.path.exists(new_filepath):

                    client_socket.send(
                        "New filename already exists".encode()
                    )

                    continue

                os.rename(
                    old_filepath,
                    new_filepath
                )

                file_metadata[new_filename] = (
                    file_metadata.pop(old_filename)
                )

                if old_filename in shared_metadata:

                    shared_metadata[new_filename] = (
                        shared_metadata.pop(old_filename)
                    )

                with open(
                    METADATA_FILE,
                    'w'
                ) as file:

                    json.dump(
                        file_metadata,
                        file,
                        indent=4
                    )

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
                    "File renamed successfully".encode()
                )

                log_activity(
                    f"{username} renamed {old_filename} to {new_filename}"
                )

            # LIST OPERATION

            elif operation == 'LIST':

                response = ""

                if not os.path.exists(UPLOAD_FOLDER):

                    os.makedirs(
                        UPLOAD_FOLDER,
                        exist_ok=True
                    )

                # admin can see everything

                if user_role == 'admin':

                    for owner_folder in os.listdir(
                        UPLOAD_FOLDER
                    ):

                        owner_path = os.path.join(
                            UPLOAD_FOLDER,
                            owner_folder
                        )

                        if os.path.isdir(owner_path):

                            for file in os.listdir(
                                owner_path
                            ):

                                response += (
                                    f"{file} -> {owner_folder}\n"
                                )

                # normal user

                else:

                    for owner_folder in os.listdir(
                        UPLOAD_FOLDER
                    ):

                        owner_path = os.path.join(
                            UPLOAD_FOLDER,
                            owner_folder
                        )

                        if os.path.isdir(owner_path):

                            for file in os.listdir(
                                owner_path
                            ):

                                owner = file_metadata.get(file)

                                shared_users = shared_metadata.get(
                                    file,
                                    []
                                )

                                if (
                                    username == owner
                                    or
                                    username in shared_users
                                ):

                                    response += (
                                        f"{file} -> {owner_folder}\n"
                                    )

                if response == "":

                    response = "No files available"

                client_socket.send(
                    response.encode()
                )

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

                owner = file_metadata.get(
                    filename
                )

                if not owner:

                    client_socket.send(
                        "File not found".encode()
                    )

                    continue

                filepath = os.path.join(
                    UPLOAD_FOLDER,
                    owner,
                    filename
                )

                if not os.path.exists(filepath):

                    client_socket.send(
                        "File not found".encode()
                    )

                    continue

                if owner != username:

                    client_socket.send(
                        "Access Denied".encode()
                    )

                    continue

                if target_user not in users:

                    client_socket.send(
                        "Target user does not exist".encode()
                    )

                    continue

                if filename not in shared_metadata:

                    shared_metadata[filename] = []

                if target_user in shared_metadata[filename]:

                    client_socket.send(
                        "File already shared".encode()
                    )

                    continue

                shared_metadata[filename].append(
                    target_user
                )

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

                log_activity(
                    f"{username} shared {filename} with {target_user}"
                )

            # DELETE OPERATION

            elif operation == 'DELETE':

                if len(parts) < 2:

                    continue

                filename = parts[1]

                owner = file_metadata.get(
                    filename
                )

                if not owner:

                    client_socket.send(
                        "File not found".encode()
                    )

                    continue

                filepath = os.path.join(
                    UPLOAD_FOLDER,
                    owner,
                    filename
                )

                if (
                    owner != username and
                    user_role != 'admin'
                ):

                    client_socket.send(
                        "Access Denied".encode()
                    )

                    continue

                if os.path.exists(filepath):

                    os.remove(filepath)

                    del file_metadata[filename]

                    if filename in shared_metadata:

                        del shared_metadata[filename]

                    with open(
                        METADATA_FILE,
                        'w'
                    ) as file:

                        json.dump(
                            file_metadata,
                            file,
                            indent=4
                        )

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

            # HISTORY OPERATION

            elif operation == 'HISTORY':

                if user_role != 'admin':

                    client_socket.send(
                        "ACCESS_DENIED".encode()
                    )

                    continue

                if not os.path.exists(LOG_FILE):

                    history = "No Logs Available"

                else:

                    with open(
                        LOG_FILE,
                        'r'
                    ) as file:

                        history = file.read()

                client_socket.send(
                    history.encode()
                )

                log_activity(
                    f"{username} viewed server history"
                )

            # INVALID OPERATION

            else:

                print("Invalid operation")

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