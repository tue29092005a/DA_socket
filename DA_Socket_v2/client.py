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
    fileInfo = f"{fileServer}|{fileSize}"#gdfgdgfd
    conn.send(fileInfo.encode(FORMAT))  

    """Data transfer"""
    bar = tqdm(range(fileSize), f"Sending {fileServer}", unit="B", unit_scale=True, unit_divisor=SIZE)

    print(conn.recv(SIZE).decode(FORMAT))
    #TODO lam 1 cai input file
    ifile = open(fileName, "rb")
    while True:
        data = ifile.read(SIZE)
        if not data:
            break
        conn.send(data)
        msg = conn.recv(SIZE).decode(FORMAT)
        # cap nhat bar
        bar.update(len(data))
    print(msg)
    ifile.close()
### yc 2
def recv_file_from_server(conn ):
    #lay thong tin ten file va file size cua client
    fileName = input("Nhap file can download from server: ")
    conn.send(fileName.encode(FORMAT))

    fileSize = conn.recv(SIZE).decode(FORMAT)

    print(f"fileSize {fileSize}")
    if fileSize == -1:
        print("File not valid")
        return
    
    #TODO nhap dir 
    newFile = r"D:\MMT\DA_Socket_v2\client_file"+ "\\" + fileName
    print(newFile)
    conn.send(f"Success recv {newFile}".encode(FORMAT))
    ##############################################
    """transfer file"""
    # bar  = tqdm(range(fileSize), f"RECV in {newFile}", unit = "B", unit_scale = True, unit_divisor = fileSize)
    ofile = open(newFile, "wb")
    if  ofile.closed :
        print("cannot open")
    while True:
        data = conn.recv(SIZE)
        if not data : 
                break
        ofile.write(data)
            #send tb nhan thanh cong
        conn.send("data received".encode(FORMAT))
        # bar.update(len(data))
    ofile.close()

def main():  
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #TODO cap nhat kha nang tu nhap server
    client.connect(ADDR)
    response = client.recv(SIZE).decode(FORMAT)
    print(response)

        #dieu lhien server  

    option = int(input("nhap yeu cau:\n 1. send file to server \n 2. recv file from server"))
    if option == 1:
        client.send("UPLD".encode(FORMAT))
        send_file_to_server(client)
    elif option == 2:
        client.send("DOWNLD".encode(FORMAT))
        recv_file_from_server(client)

if __name__ == "__main__":
    main()
