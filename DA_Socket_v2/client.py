import threading
import os
import socket
from tqdm import tqdm
HOST = "127.0.0.1" 
PORT = 65432
ADDR = (HOST, PORT)
SERVER_PORT = 65432 
FORMAT = "utf8"
SIZE = 1024
def send_file_to_server(conn):
    fileName = r"D:\MMT\DA_Socket_v2\client_file\friends-final.txt"
    #TODO make send file name in here
    fileServer = fileName.rsplit("\\",1)
    fileServer = fileServer[1]
    fileSize = os.path.getsize(fileName)
    fileInfo = f"{fileServer}|{fileSize}"
    conn.send(fileInfo.encode(FORMAT))  

    """Data transfer"""
    bar = tqdm(range(fileSize), f"Sending {fileServer}", unit="B", unit_scale=True, unit_divisor=SIZE)

    print(conn.recv(SIZE).decode(FORMAT))
    #TODO lam 1 cai input file
    ifile = open(fileName, "r")
    while True:
        data = ifile.read(SIZE)
        if not data:
            break
        conn.send(data.encode(FORMAT))
        msg = conn.recv(SIZE).decode(FORMAT)
        # cap nhat bar
        bar.update(len(data))
    print(msg)
    ifile.close()
def main():  
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #TODO cap nhat kha nang tu nhap server
    client.connect(ADDR)
    response = client.recv(SIZE).decode(FORMAT)
    print(response)

        #dieu lhien server  
    client.send("SEND_FILE".encode(FORMAT))
    send_file_to_server(client)

if __name__ == "__main__":
    main()
