from socket import *
from threading import Thread
from time import ctime
import os

FILES_DIR = 'ServerFiles'
serverIP = "127.0.0.1"
serverPort = 12000

if not os.path.exists(FILES_DIR):
    os.makedirs(FILES_DIR)

def handle_download(connectionSocket, filename):
    file_path = os.path.join(FILES_DIR, filename)
    print(f"Requested file: {filename}")
    print(f"Constructed file path: {file_path}")
    print(f"File exists: {os.path.exists(file_path)}")
    if os.path.exists(file_path):
        connectionSocket.send("READY".encode())
        with open(file_path, 'rb') as f:
            while chunk := f.read(1024):
                connectionSocket.send(chunk)  
        connectionSocket.send(b"END")
    else:
        connectionSocket.send("File not found!".encode())

def handle_upload(connectionSocket, filename):
    file_path = os.path.join(FILES_DIR, filename)
    connectionSocket.send("READY".encode())
    with open(file_path, 'wb') as f:
        while True:
            chunk = connectionSocket.recv(2048)
            if "END" in chunk.decode():
                    chunk = chunk.replace(b"END", b"")
                    f.write(chunk)
                    break
            f.write(chunk)
    connectionSocket.send("Upload complete!".encode())

def serviceRequest(connectionSocket):
    print(f"New Thread started on {ctime()}")
    #files = os.listdir(FILES_DIR)
    #connectionSocket.send(f"Files available: {files}".encode())
    while True:
        
        option = connectionSocket.recv(2048).decode()

        if option == "exit":
            break
        elif option == "list_files":
                files = os.listdir(FILES_DIR)
                connectionSocket.send("\n".join(files).encode())

        elif option == "download":
            filename = connectionSocket.recv(2048).decode().strip()
            handle_download(connectionSocket, filename)

        elif option == "upload":
            filename = connectionSocket.recv(2048).decode()
            handle_upload(connectionSocket, filename)

        elif option == "delete":
            filename = connectionSocket.recv(2048).decode().strip()
            file_path = os.path.join(FILES_DIR, filename)
            if os.path.exists(file_path):
                os.remove(file_path)
                connectionSocket.send("File deleted!!!".encode())
            else:
                connectionSocket.send("File not found!!!".encode())

        else:
            connectionSocket.send("Invalid option!".encode())

    connectionSocket.close()

serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind((serverIP, serverPort))
serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
serverSocket.listen(5)
print(f"Server IP: {serverIP} , Server Port: {serverPort}")
threads = []
while True:
    connectionSocket, address = serverSocket.accept()
    print(f"Outside Thread new connectionSocket is made: {address}")
    newThread = Thread(target=serviceRequest, args=(connectionSocket,))
    newThread.start()
    threads.append(newThread)

serverSocket.close()