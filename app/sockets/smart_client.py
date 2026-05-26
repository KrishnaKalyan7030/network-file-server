import socket

try:

    client_socket = socket.socket()

    client_socket.connect(('localhost', 9999))

    print('Connected to server')


    username=input("Enter username: ")
    password=input('Enter password: ')
    login_command=f'LOGIN {username} {password}'
    client_socket.send(login_command.encode())
    auth_response=client_socket.recv(1024).decode()
    
    if auth_response != 'AUTH_SUCCESS':

        print("Authentication Failed")
    
        client_socket.close()
    
        exit()
    else:
        print("Authentication Successful")



    operation = input("Enter operation: ").upper()

   
    # LIST OPERATION
   
    if operation == 'LIST':

        client_socket.send(operation.encode())

        response = client_socket.recv(1024).decode()

        print("\nFiles available on server:\n")

        print(response)

  
    # UPLOAD / DOWNLOAD
    
    elif operation in ['UPLOAD', 'DOWNLOAD','DELETE']:

        filename = input('Enter Filename: ')

        command = f'{operation} {filename}'

        client_socket.send(command.encode())

  
        # UPLOAD
       
        if operation == 'UPLOAD':

            file = open(f'../files/{filename}', 'rb')

            while True:

                data = file.read(1024)

                # EOF
                if not data:
                    break

                client_socket.send(data)

            file.close()

            print("File uploaded successfully")

      
        # DOWNLOAD
       
        elif operation == 'DOWNLOAD':

            file = open(f'../downloads/{filename}', 'wb')

            while True:

                data = client_socket.recv(1024)

                if not data:
                    break

                file.write(data)

            file.close()

            print('Download completed')

        elif operation == 'DELETE':
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