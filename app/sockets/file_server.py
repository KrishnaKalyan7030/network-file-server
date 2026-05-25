import socket
import threading
import os

def handle_client(client_socket, client_add):

    try:

        command = client_socket.recv(1024).decode()

        parts = command.split()

        # Empty command validation
        if len(parts) < 1:

            print("Invalid Command")

            client_socket.close()

            return

        operation = parts[0].upper()

        print(f"Operation requested: {operation}")

        
        # UPLOAD OPERATION
       
        if operation == 'UPLOAD':

            if len(parts) < 2:

                print("Filename missing")

                return

            filename = parts[1]

            print(f"UPLOAD request for {filename}")

            file = open(f'../uploads/{filename}', 'wb')

            while True:

                data = client_socket.recv(1024)

                if not data:
                    break

                file.write(data)

            file.close()

            print('Upload Complete')

       
        # DOWNLOAD OPERATION
       
        elif operation == 'DOWNLOAD':

            if len(parts) < 2:

                print("Filename missing")

                return

            filename = parts[1]

            print(f"DOWNLOAD request for {filename}")

            file = open(f'../uploads/{filename}', 'rb')

            while True:

                chunk = file.read(1024)

                if not chunk:
                    break

                client_socket.send(chunk)

            file.close()

            print("Download Complete")

       
        # LIST OPERATION
      
        elif operation == 'LIST':

            files = os.listdir('../uploads')

            if not files:

                response = "No files available"

            else:

                response = '\n'.join(files)

            client_socket.send(response.encode())

            print("File list sent")
        
        # DELETE OPERATION
    
        elif operation == 'DELETE':
            if len(parts) < 2:
                print("Filename missing")            
                return
            filename = parts[1]
            filepath = f'../uploads/{filename}'

            if os.path.exists(filepath):
                os.remove(filepath)
                client_socket.send( "File deleted successfully".encode() )
            else:
                client_socket.send("File not found".encode() )

       
        # INVALID OPERATION
     
        else:

            print("Invalid operation")

    except Exception as e:

        print(f'Error with {client_add}: {e}')

    finally:

        client_socket.close()

        print(f"Connection closed for {client_add}")


server_socket = socket.socket()

server_socket.bind(('localhost', 9999))

server_socket.listen(5)

print("Waiting for connection...")


while True:

    client_socket, client_add = server_socket.accept()

    print(f'Server connected to {client_add}')

    t = threading.Thread(
        target=handle_client,
        args=(client_socket, client_add),
        daemon=True
    )

    t.start()